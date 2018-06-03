import ccxt.async as ccxt

from ccxt.async.base.exchange import Exchange


class Symbol:
    base: str
    quote: str

    def __init__(self, base: str, quote: str):
        self.base = base.upper()
        self.quote = quote.upper()

    def __str__(self):
        return '%s/%s' % (self.base, self.quote)


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


class ExchangeProxy:
    exchange: Exchange

    def __init__(self, exchange: Exchange):
        self.exchange = exchange

    @staticmethod
    async def list():
        for key in ccxt.exchanges:
            exchange = ExchangeProxy.load(key)

            yield key, exchange

            await exchange.close()

    @staticmethod
    def load(name: str, params: dict = None):
        return ExchangeProxy(getattr(ccxt, name)(params or {}))

    def features(self) -> dict:
        return self.exchange.has

    async def symbols(self):
        await self.markets()

        return self.exchange.symbols

    async def currencies(self):
        await self.markets()

        return self.exchange.currencies

    async def markets(self):
        self._guard("fetchMarkets")

        await self.exchange.load_markets()

        return self.exchange.markets

    async def market(self, symbol: Symbol):
        await self.markets()

        return self.exchange.markets[str(symbol)]

    async def ticker(self, symbol: Symbol):
        self._guard("fetchTicker")

        return await self.exchange.fetch_ticker(str(symbol))

    async def ohlcv(self, symbol: Symbol, timeframe: str = None, since: int = None, limit: int = None):
        self._guard("fetchOHLCV")

        timeframes = self.exchange.timeframes if hasattr(self.exchange, 'timeframes') else {}
        if timeframe not in timeframes:
            timeframe = list(self.exchange.timeframes.keys())[0]

        since = int(since) if since else None
        limit = int(limit) if limit else None

        ohlcv = await self.exchange.fetch_ohlcv(str(symbol), timeframe, since, limit)

        return [OHLCV.map(v) for v in ohlcv]

    async def trades(self, symbol: Symbol, since: int = None, limit: int = None):
        self._guard("fetchTrades")

        since = int(since) if since else None
        limit = int(limit) if limit else None

        return await self.exchange.fetch_trades(str(symbol), since, limit)

    async def balance(self):
        self._guard("fetchBalance")

        return await self.exchange.fetch_balance()

    async def close(self):
        return await self.exchange.close()

    def _guard(self, ability: str):
        if not self.exchange.has[ability]:
            raise NotImplemented(ability)


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


class Currency:
    id = str
    code = str
    precision = int


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


class OrderItem:
    price = float
    amount = float


class Order:
    bids = [OrderItem]
    asks = [OrderItem]
    timestamp = int


class Balance:
    pass
