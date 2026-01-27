from dataclasses import dataclass

@dataclass
class Bardata:
  """
  定义Bardata数据格式
  """
  symbol : str
  timeframe : str
  timestamp : int
  open : float
  high : float
  low : float
  close : float
