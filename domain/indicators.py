import talib as ta

from typing import List
from numpy import array, isnan
from domain.models import OHLCV


class AD:
    value: List[float]
    osc: List[float]

    def __init__(self, value: List[float], osc: List[float]):
        self.value = value
        self.osc = osc


class AROON:
    down: List[float]
    up: List[float]
    osc: List[float]

    def __init__(self, down: List[float], up: List[float], osc: List[float]):
        self.down = down
        self.up = up
        self.osc = osc


class MACD:
    macd: List[float]
    sig: List[float]
    hist: List[float]

    def __init__(self, macd: List[float], sig: List[float], hist: List[float]):
        self.macd = macd
        self.sig = sig
        self.hist = hist


class Indicators:
    open: array
    high: array
    low: array
    close: array
    volume: array
    count: int

    def __init__(self, candles: List[OHLCV], count: int = None):
        self.open = array([v.o for v in candles], float)
        self.high = array([v.h for v in candles], float)
        self.low = array([v.l for v in candles], float)
        self.close = array([v.c for v in candles], float)
        self.volume = array([v.v for v in candles], float)
        self.count = count

    # Momentum Indicators

    def adx(self, period: int = 14) -> List[float]:
        real = ta.ADX(self.high, self.low, self.close, timeperiod=period)

        return self._slice(real)

    def adxr(self, period: int = 14) -> List[float]:
        real = ta.ADXR(self.high, self.low, self.close, timeperiod=period)

        return self._slice(real)

    def apo(self, fast: int = 12, slow: int = 26, type=0) -> List[float]:
        real = ta.APO(self.close, fastperiod=fast, slowperiod=slow, matype=type)

        return self._slice(real)

    def aroon(self, period: int = 14) -> AROON:
        down, up = ta.AROON(self.high, self.low, timeperiod=period)
        osc = ta.AROONOSC(self.high, self.low, timeperiod=period)

        return AROON(self._slice(down), self._slice(up), self._slice(osc))

    def bop(self) -> List[float]:
        real = ta.BOP(self.open, self.high, self.low, self.close)

        return self._slice(real)

    def cci(self, period: int = 14) -> List[float]:
        real = ta.CCI(self.high, self.low, self.close, timeperiod=period)

        return self._slice(real)

    def cmo(self, period: int = 14) -> List[float]:
        real = ta.CMO(self.close, timeperiod=period)

        return self._slice(real)

    def dx(self, period: int = 14) -> List[float]:
        real = ta.DX(self.high, self.low, self.close, timeperiod=period)

        return self._slice(real)

    def macd(self, fast: int = 12, slow: int = 26, signal: int = 9) -> MACD:
        macd, sig, hist = ta.MACD(self.close, fastperiod=fast, slowperiod=slow, signalperiod=signal)

        return MACD(self._slice(macd), self._slice(sig), self._slice(hist))

    def mfi(self, period: int = 14) -> List[float]:
        real = ta.MFI(self.high, self.low, self.close, self.volume, timeperiod=period)

        return self._slice(real)

    def mom(self, period: int = 10) -> List[float]:
        real = ta.MOM(self.close, timeperiod=period)

        return self._slice(real)

    def ppo(self, fast: int = 12, slow: int = 26, matype: int = 0) -> List[float]:
        real = ta.PPO(self.close, fastperiod=fast, slowperiod=slow, matype=matype)

        return self._slice(real)

    def roc(self, period: int = 10) -> List[float]:
        real = ta.ROC(self.close, timeperiod=period)

        return self._slice(real)

    def rocp(self, period: int = 10) -> List[float]:
        real = ta.ROCP(self.close, timeperiod=period)

        return self._slice(real)

    def rocr(self, period: int = 10) -> List[float]:
        real = ta.ROCR(self.close, timeperiod=period)

        return self._slice(real)

    def rsi(self, period: int = 14) -> List[float]:
        real = ta.RSI(self.close, timeperiod=period)

        return self._slice(real)

    def trix(self, period: int = 30) -> List[float]:
        real = ta.TRIX(self.close, timeperiod=period)

        return self._slice(real)

    def ult(self, period_one: int = 7, period_two: int = 14, period_three: int = 28) -> List[float]:
        real = ta.ULTOSC(
            self.high, self.low, self.close,
            timeperiod1=period_one, timeperiod2=period_two, timeperiod3=period_three)

        return self._slice(real)

    def willr(self, period: int = 14) -> List[float]:
        real = ta.WILLR(self.high, self.low, self.close, timeperiod=period)

        return self._slice(real)

    # Volume Indicators

    def ad(self, fast: int = 3, slow: int = 10) -> AD:
        real = ta.AD(self.high, self.low, self.close, self.volume)
        osc = ta.ADOSC(
            self.high, self.low, self.close, self.volume,
            fastperiod=fast, slowperiod=slow
        )

        return AD(self._slice(real), self._slice(osc))

    def obv(self) -> List[float]:
        real = ta.OBV(self.close, self.volume)

        return self._slice(real)

    # Private methods
    def _slice(self, data: array) -> List[float]:
        values = data

        if self.count is not None:
            start = int(self.count) * -1
            values = data[start:]

        return [x if not isnan(x) else 0.0 for x in values]
