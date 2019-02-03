from datetime import datetime
from collections import defaultdict

from ccxt import RequestTimeout, OrderNotFound, InvalidOrder
from ccxt.async_support.base.exchange import Exchange

from domain.limits import Limits
from domain.models import *
from domain.errors import InvalidSymbol, InvalidOperation, MinOrderAmount


class CCXTProxy(ExchangeProxy):
    exchange: Exchange
    retries: {}
    limits: Limits

    def __init__(self, name: str, exchange: Exchange, limits: Limits):
        super().__init__(name)

        self.exchange = exchange
        self.retries = defaultdict(int)
        self.limits = limits

    def features(self) -> Dict:
        return self.exchange.has

    async def symbols(self) -> List[str]:
        await self.markets()

        return self.exchange.symbols

    async def currencies(self) -> Dict[str, Currency]:
        self._guard("fetchCurrencies")

        await self.markets()

        return self.exchange.currencies

    async def markets(self):
        self._guard("fetchMarkets")

        await self.exchange.load_markets()

        return self.exchange.markets

    async def market(self, symbol: Symbol):
        await self.markets()

        if symbol not in self.exchange.markets:
            raise InvalidSymbol(symbol)

        return self.exchange.markets[symbol]

    async def ticker(self, symbol: Symbol):
        self._guard("fetchTicker")

        return await self.exchange.fetch_ticker(str(symbol))

    async def ohlcv(self, symbol: Symbol, timeframe: str = '1m', since: int = None, limit: int = None) -> List[dict]:
        self._guard("fetchOHLCV")

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

        since = int(since) if since else None
        limit = int(limit) if limit else None

        return await self.exchange.fetch_trades(str(symbol), since, limit)

    async def book(self, symbol: Symbol, limit: int = None):
        self._guard("fetchOrderBook")

        limit = int(limit) if limit else None
        items = await self.exchange.fetch_order_book(str(symbol), limit)

        bids = [Offer.map(v) for v in items['bids']]
        asks = [Offer.map(v) for v in items['asks']]

        return OrderBook(bids, asks)

    async def wallet(self) -> Wallet:
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

        return await self.exchange.fetch_order(_id, str(symbol))

    async def create_order(self, symbol: Symbol, type: str, side: str, amount: float, price: float = None):
        self._guard("createOrder")

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
        except InvalidOrder as error:
            limit = self.limits.fetch(self.exchange)

            if limit >= amount * price:
                raise MinOrderAmount(str(error))

            raise error

    async def cancel_order(self, symbol: Symbol, _id: str):
        self._guard("cancelOrder")

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
