from abc import abstractmethod
from typing import Dict, List


class Symbol:
    base: str
    quote: str

    def __init__(self, base: str, quote: str):
        self.base = base.upper()
        self.quote = quote.upper()

    def __str__(self):
        return '%s/%s' % (self.base, self.quote)

    def __hash__(self):
        return str(self)


class ExchangeFeatures:
    fetchClosedOrders: bool
    fetchCurrencies: bool
    fetchMarkets: bool
    fetchOHLCV: bool
    fetchOpenOrders: bool
    fetchOrder: bool
    fetchOrderBook: bool
    fetchOrders: bool
    fetchTicker: bool
    fetchTickers: bool
    fetchTrades: bool
    fetchBalance: bool
    createOrder: bool
    cancelOrder: bool
    deposit: bool
    withdraw: bool


class Currency:
    id: str
    code: str
    precision: int

    def __init__(self, _id: str, code: str, precision: int):
        self.id = _id
        self.code = code
        self.precision = precision


class Limit:
    min: float
    max: float


class MarketPrecision:
    price: int
    amount: int
    cost: int


class MarketLimits:
    price: Limit
    amount: Limit
    cost: Limit


class Market:
    id: str
    symbol: str
    base: str
    quote: str
    active: bool
    precision: MarketPrecision
    limits: MarketLimits


class Ticker:
    symbol: str
    timestamp: int
    bid: float
    bidVolume: float
    ask: float
    askVolume: float
    baseVolume: float
    quoteVolume: float


class OHLCV:
    t: int
    o: float
    h: float
    l: float
    c: float
    v: float

    def __init__(self, v: List):
        self.t = v[0]
        self.o = v[1]
        self.h = v[2]
        self.l = v[3]
        self.c = v[4]
        self.v = v[5]


class TradeItem:
    id: str
    timestamp: int
    order: str
    type: str
    side: str
    price: float
    amount: float


class Offer:
    price: float
    amount: float

    @staticmethod
    def map(v: list) -> dict:
        return {
            'price': v[0],
            'amount': v[1],
        }


class OrderBook:
    bids: List[Offer]
    asks: List[Offer]

    def __init__(self, bids: List[Offer], asks: List[Offer]):
        self.bids = bids
        self.asks = asks


class Wallet:
    free: Dict[str, float]
    used: Dict[str, float]
    total: Dict[str, float]

    def __init__(self, free: Dict, used: Dict, total: Dict):
        self.free = free
        self.used = used
        self.total = total


class Balance:
    free: float
    used: float
    total: float

    def __init__(self, values: Dict):
        for k, v in values.items():
            setattr(self, k, v or 0)


class OrderFee:
    currency: str
    cost: float
    rate: float


class Order:
    id: str
    timestamp: int
    last_trade: int
    status: str
    symbol: str
    type: str
    side: str
    price: float
    amount: float
    filled: float
    remaining: float
    cost: float
    fee: OrderFee


class ExchangeProxy:
    name: str

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def features(self) -> ExchangeFeatures:
        pass

    @abstractmethod
    async def symbols(self) -> List[str]:
        pass

    @abstractmethod
    async def currencies(self) -> Dict[str, Currency]:
        pass

    @abstractmethod
    async def markets(self) -> List[Market]:
        pass

    @abstractmethod
    async def market(self, symbol: Symbol) -> Market:
        pass

    @abstractmethod
    async def ticker(self, symbol: Symbol) -> Ticker:
        pass

    @abstractmethod
    async def ohlcv(self, symbol: Symbol, timeframe: str = '1m', since: int = None, limit: int = None) -> List[OHLCV]:
        pass

    @abstractmethod
    async def trades(self, symbol: Symbol, since: int = None, limit: int = None) -> List[TradeItem]:
        pass

    @abstractmethod
    async def book(self, symbol: Symbol, limit: int = None) -> OrderBook:
        pass

    @abstractmethod
    async def wallet(self) -> Wallet:
        pass

    @abstractmethod
    async def balance(self, base: str) -> Balance:
        pass

    @abstractmethod
    async def get_orders(self, symbol: Symbol, status: str = None, since: int = None, limit: int = None) -> List[Order]:
        pass

    @abstractmethod
    async def get_order(self, symbol: Symbol, _id: str) -> Order:
        pass

    @abstractmethod
    async def create_order(self, symbol: Symbol, type: str, side: str, amount: float, price: float = None) -> Order:
        pass

    @abstractmethod
    async def cancel_order(self, symbol: Symbol, _id: str):
        pass

    @abstractmethod
    async def close(self):
        pass


class MACD:
    macd: List[float]
    sig: List[float]
    hist: List[float]

    def __init__(self, macd: List[float], sig: List[float], hist: List[float]):
        self.macd = macd
        self.sig = sig
        self.hist = hist
    #
    # def slice(self, count: int):
    #     return MACD(self.macd[-count:], self.sig[-count:], self.hist[-count:])


class RSI:
    rsi: List[float]

    def __init__(self, rsi: List[float]):
        self.rsi = rsi
    #
    # def slice(self, count: int):
    #     return RSI(self.rsi[-count:])
