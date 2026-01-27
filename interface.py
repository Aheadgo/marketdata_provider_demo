from typing import List, Callable, Awaitable, AsyncIterator, Set, Dict, Any, Optional
import asyncio
from utility import Bardata

# 回调函数类型定义
BarCallback = Callable[[Bardata], Awaitable[None]]

class IMarketDataProvider:
    """
    行情数据提供者接口
    """
    
    async def initialize(self, config: Dict[str, Any]) -> None:
        """
        初始化行情系统
        
        参数:
            config: 配置字典，包含交易所API密钥、订阅列表等
        要求:
            - 支持从配置加载，建议从yaml拉取配置
            - 建立WebSocket连接池
            - 实现连接状态监控
        """
        pass
    
    async def subscribe_bars(
        self,
        symbols: List[str],
        timeframe: str = "1m",
        callback: Optional[BarCallback] = None
    ) -> str:
        """
        订阅K线数据
        
        参数:
            symbols: 交易对列表，如 ["BTCUSDT", "ETHUSDT"]
            timeframe: 时间周期，必须支持 "1m"
            callback: 数据回调函数，每收到一个BarData调用一次
            
        返回:
            subscription_id: 订阅ID，用于后续取消订阅
            
        要求:
            1. 支持批量订阅
            2. 立即开始推送数据到callback
            3. 每个symbol独立推送
            4. 保证数据顺序性
        """
        pass
    
    async def unsubscribe(self, subscription_id: str) -> None:
        """
        取消订阅
        
        参数:
            subscription_id: subscribe_bars返回的订阅ID
        """
        pass
    
    async def shutdown(self) -> None:
        """
        关闭行情系统
        
        要求:
            1. 关闭所有WebSocket连接
            2. 清理所有资源
            3. 等待所有异步任务完成
        """
        pass

class IBarCompletionNotifier:
  """
  K线完成通知器接口
  用于事件驱动模式
  """
  
  def __init__(self):
      # 建议使用asyncio.Event实现
      self._events: Dict[str, asyncio.Event] = {}
      self._latest_bars: Dict[str, BarData] = {}
  
  def register_bar_callback(
      self,
      symbol: str,
      timeframe: str,
      callback: BarCallback
  ) -> None:
    """
    注册K线完成回调
    
    参数:
        symbol: 交易对
        timeframe: 时间周期
        callback: 回调函数
        
    要求:
        1. 每个symbol+timeframe可注册多个回调
        2. 回调异步执行，不阻塞主流程
    """
    pass
  
  # 内部方法：由行情系统调用
  def _notify_bar_completion(self, bar: Bardata) -> None:
    """
    【内部方法】通知K线完成
    
    参数:
      bar: 完整的K线数据
        
    要求:
      1. 在确认K线完整后调用
      2. 设置is_complete=True
      3. 异步触发所有注册的回调
    """
    pass

