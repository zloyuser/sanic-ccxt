import talib as ta
import numpy as np

from domain.models import *


def filter_nan(data):
    return data[~np.isnan(data)]


class Indicators:
    exchange: ExchangeProxy
    symbol: Symbol
    timeframe: str

    def __init__(self, exchange: ExchangeProxy, symbol: Symbol, timeframe: str):
        self.exchange = exchange
        self.symbol = symbol
        self.timeframe = timeframe

    async def macd(self, fast=12, slow=26, signal=9) -> MACD:
        candles = await self.candles()
        close = [v.c for v in candles]

        macd, sig, hist = ta.MACD(np.array(close, float), fastperiod=fast, slowperiod=slow, signalperiod=signal)

        return MACD(filter_nan(macd), filter_nan(sig), filter_nan(hist))

    async def rsi(self, period=14) -> RSI:
        candles = await self.candles()
        close = [v.c for v in candles]

        rsi = ta.RSI(np.array(close, float), timeperiod=period)

        return RSI(filter_nan(rsi))

    async def candles(self) -> List[OHLCV]:
        candles = await self.exchange.ohlcv(self.symbol, self.timeframe)

        return candles
