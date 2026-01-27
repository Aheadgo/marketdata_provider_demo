import websockets
import asyncio
import json
from typing import Dict, Any, List, Optional, Callable, Awaitable
from utility import Bardata
from interface import IBarCompletionNotifier, IMarketDataProvider, BarCallback


class Binance_md(IMarketDataProvider):
  def __init__(self):
    self.config: Dict[str, Any] = {}
    self.subscriptions: Dict[str, List[asyncio.Task]] = {}
    self.lock = asyncio.Lock()

  async def initialize(self, config: Dict[str, Any]) -> None:
    self.config = config
    self.base_url = self.config["url"]

  async def subscribe_bars(self, symbols: List[str], timeframe: str = "1m", callback: Optional[BarCallback] = None) -> str:
    # 生成uuid订阅编码
    subscription_id = f"{id(symbols)}"

    async with self.lock:
      # 用于收集为每一个symbol建立的asyncio.task
      self.subscriptions[subscription_id] = []

      for symbol in symbols:
        task = asyncio.create_task(self.ws_symbol(symbol, timeframe, callback))
        self.subscriptions[subscription_id].append(task)

    return subscription_id

  async def ws_symbol(self, symbol: str, timeframe: str, callback: Optional[BarCallback]) -> None:
    stream = f"{symbol.lower()}@kline_{timeframe}"
    url = f"{self.base_url}/{stream}"

    try:
      async with websockets.connect(url, ping_interval=20) as ws:
        async for msg in ws:
          # print(msg)
          data = json.loads(msg)

          k = data.get("k")

          if not k or not k["x"]:
            continue

          bar = Bardata(
            symbol=k["s"],
            timeframe=k["i"],
            timestamp=k["t"],
            open=float(k["o"]),
            high=float(k["h"]),
            low=float(k["l"]),
            close=float(k["c"])
          )
          if callback:
            await callback(bar)
    
    except asyncio.CancelledError:
      print(f"[{symbol}] websocket cancelled")
      raise 

    except Exception as e:
      print("error: ", e)
      self._on_disconnect()

  def _on_disconnect(self):
    pass

  async def unsubscribe(self, subscription_id: str) -> None:
    async with self.lock:
      subscribed_tasks = self.subscriptions.get(subscription_id, None)

      if subscribed_tasks is None:
        return

      for task in subscribed_tasks:
        task.cancel()

  async def shutdown(self) -> None:
    pass

class bar_notifier(IBarCompletionNotifier):
  def __init__(self):
    super().__init__()
    self.callback_list: Dict[str, List[BarCallback]] = {}

  def register_bar_callback(self, symbol: str, timeframe: str, callback: BarCallback) -> None:
    symbol_timeframe_key = f"{symbol}_{timeframe}"
    self.callback_list.setdefault(symbol_timeframe_key, []).append(callback)

    if symbol_timeframe_key not in self._events:
      self._events[symbol_timeframe_key] = asyncio.Event()

  async def _notify_bar_completion(self, bar: Bardata) -> None:
    symbol_timeframe_key = f"{bar.symbol}_{bar.timeframe}"

    self._latest_bars[symbol_timeframe_key] = Bardata

    # self._events[symbol_timeframe_key].set()

    symbol_callbacks = self.callback_list.get(symbol_timeframe_key, None)

    if symbol_callbacks is None:
      return
    
    for callback in symbol_callbacks:
      if callback:
        await callback(bar)

  

