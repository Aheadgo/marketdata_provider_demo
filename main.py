import asyncio
from demo_md import Binance_md, bar_notifier
from utility import Bardata

# 使用on_bar作为回调函数
def on_bar(bar: Bardata):
  print(f"{bar.symbol} {bar.timestamp} {bar.close}")

async def main():
  Marketdata_Provider = Binance_md()
  Bar_Notifier = bar_notifier()

  await Marketdata_Provider.initialize({
    "url": "wss://stream.testnet.binance.vision:9443/ws"
  })

  Bar_Notifier.register_bar_callback("BTCUSDT", "1s", on_bar)

  await Marketdata_Provider.subscribe_bars(["BTCUSDT"], "1s", Bar_Notifier._notify_bar_completion)

  while True:
    await asyncio.sleep(1)

if __name__ == "__main__":
  asyncio.run(main())

