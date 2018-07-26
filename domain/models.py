import ccxt.async_support as ccxt

from datetime import datetime
from collections import defaultdict
from typing import Dict
from ccxt import RequestTimeout, OrderNotFound
from ccxt.async_support.base.exchange import Exchange
from domain.errors import *


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


class ExchangeProxy:
    name: str
    exchange: Exchange
    retries: {}

    def __init__(self, name: str, exchange: Exchange):
        self.name = name
        self.exchange = exchange
        self.retries = defaultdict(int)

    @staticmethod
    async def list():
        for key in ccxt.exchanges:
            exchange = ExchangeProxy.load(key)

            yield key, exchange

            await exchange.close()

    @staticmethod
    def load(name: str, params: dict = None):
        if not hasattr(ccxt, name):
            raise InvalidExchange(name)

        params = params or {}
        params['timeout'] = 30000

        return ExchangeProxy(name, getattr(ccxt, name)(params))

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

        symbol = self._coerce_symbol(symbol)

        if symbol not in self.exchange.markets:
            raise InvalidSymbol(symbol)

        return self.exchange.markets[symbol]

    async def ticker(self, symbol: Symbol):
        self._guard("fetchTicker")

        symbol = self._coerce_symbol(symbol)

        return await self.exchange.fetch_ticker(str(symbol))

    async def ohlcv(self, symbol: Symbol, timeframe: str = '1m', since: int = None, limit: int = None):
        self._guard("fetchOHLCV")

        symbol = self._coerce_symbol(symbol)

        if not hasattr(self.exchange, 'timeframes'):
            timeframe = '1m'
        else:
            if timeframe not in self.exchange.timeframes:
                timeframe = list(self.exchange.timeframes.keys())[0]

        since = int(since) if since else None
        limit = int(limit) if limit else None

        ohlcv = await self.exchange.fetch_ohlcv(str(symbol), timeframe, since, limit)

        return [OHLCV.map(v) for v in ohlcv]

    async def trades(self, symbol: Symbol, since: int = None, limit: int = None):
        self._guard("fetchTrades")

        symbol = self._coerce_symbol(symbol)

        since = int(since) if since else None
        limit = int(limit) if limit else None

        return await self.exchange.fetch_trades(str(symbol), since, limit)

    async def wallet(self):
        self._guard("fetchBalance")

        balances = await self.exchange.fetch_balance()

        return Wallet(balances['free'], balances['used'], balances['total'])

    async def balance(self, base: str):
        self._guard("fetchBalance")

        currency = base.upper()
        balances = await self.exchange.fetch_balance()

        return Balance(balances[currency] if currency in balances else {})

    async def get_orders(self, symbol: Symbol, status: str = None, since: int = None, limit: int = None):
        since = int(since) if since else None
        limit = int(limit) if limit else None

        symbol = self._coerce_symbol(symbol)

        if status == 'open':
            self._guard("fetchOpenOrders")

            return await self.exchange.fetch_open_orders(str(symbol), since, limit)
        elif status == 'closed':
            self._guard("fetchClosedOrders")

            return await self.exchange.fetch_closed_orders(str(symbol), since, limit)
        else:
            self._guard("fetchOrders")

            return await self.exchange.fetch_orders(str(symbol), since, limit)

    async def get_order(self, symbol: Symbol, _id: str):
        self._guard("fetchOrder")

        symbol = self._coerce_symbol(symbol)

        await self.exchange.fetch_order(_id, str(symbol))

    async def create_order(self, symbol: Symbol, type: str, side: str, amount: float, price: float = None):
        self._guard("createOrder")

        symbol = self._coerce_symbol(symbol)

        time = int(datetime.utcnow().timestamp())

        try:
            order = await self.exchange.create_order(str(symbol), type, side, amount, price)

            return order
        except RequestTimeout as error:
            # TODO !!!
            if 'fetchOpenOrders' in self.exchange.has:
                orders = await self.exchange.fetch_open_orders(str(symbol), time)

                for order in orders:
                    if order.side == side and order.type == type and order.amount == amount:
                        return order

            raise error

    async def cancel_order(self, symbol: Symbol, _id: str):
        self._guard("cancelOrder")

        symbol = self._coerce_symbol(symbol)

        try:
            await self.exchange.cancel_order(_id, str(symbol))
        except OrderNotFound as error:
            if self.retries[_id] > 0:
                # Update Order Cache
                if 'fetchOrder' in self.exchange.has:
                    await self.exchange.fetch_order(_id, str(symbol))

                self.retries[_id] = 0

                return

            raise error
        except RequestTimeout as error:
            self.retries[_id] += 1

            if self.retries[_id] > 5:
                self.retries[_id] = 0

                raise error
            else:
                self.cancel_order(symbol, _id)

    async def close(self):
        return await self.exchange.close()

    def _guard(self, ability: str):
        if not self.exchange.has[ability]:
            raise InvalidOperation(ability)

    def _coerce_symbol(self, symbol: Symbol):
        # if self.name == 'poloniex' or self.name == 'bittrex':
        #     return Symbol(symbol.quote, symbol.base)

        return symbol


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
