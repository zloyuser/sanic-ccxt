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
    id = str
    code = str
    precision = int

    def __init__(self, id: str, code: str, precision: int):
        self.id = id
        self.code = code
        self.precision = precision


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
    def features(self) -> Dict:
        pass

    @abstractmethod
    async def symbols(self) -> List[str]:
        pass

    @abstractmethod
    async def currencies(self) -> Dict[str, Currency]:
        pass

    @abstractmethod
    async def markets(self):
        pass

    @abstractmethod
    async def market(self, symbol: Symbol):
        pass

    @abstractmethod
    async def ticker(self, symbol: Symbol):
        pass

    @abstractmethod
    async def ohlcv(self, symbol: Symbol, timeframe: str = '1m', since: int = None, limit: int = None) -> List[dict]:
        pass

    @abstractmethod
    async def trades(self, symbol: Symbol, since: int = None, limit: int = None):
        pass

    @abstractmethod
    async def wallet(self) -> Wallet:
        pass

    @abstractmethod
    async def balance(self, base: str) -> Balance:
        pass

    @abstractmethod
    async def get_orders(self, symbol: Symbol, status: str = None, since: int = None, limit: int = None):
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


class Limit:
    min = float
    max = float


class MarketPrecision:
    price = int
    amount = int
    cost = int


class MarketLimits:
    price = Limit
    amount = Limit
    cost = Limit


class Market:
    id = str
    symbol = str
    base = str
    quote = str
    active = bool
    precision = MarketPrecision
    limits = MarketLimits


class OHLCV:
    t = int
    o = float
    h = float
    l = float
    c = float
    v = float

    @staticmethod
    def map(v: list) -> dict:
        k = ['t', 'o', 'h', 'l', 'c', 'v']

        return dict(zip(k, v))


class Trade:
    id = str
    timestamp = int
    order = str
    type = str
    side = str
    price = float
    amount = float


class Ticker:
    symbol = str
    timestamp = int
    bid = float
    bidVolume = float
    ask = float
    askVolume = float
    baseVolume = float
    quoteVolume = float
