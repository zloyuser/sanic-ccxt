import ccxt.async_support as ccxt

from domain.errors import InvalidExchange
from domain.ccxt import CCXTProxy


class ExchangeFactory(object):
    @staticmethod
    async def list():
        exchanges = ccxt.exchanges

        for key in exchanges:
            exchange = await ExchangeFactory.load(key)

            yield key, exchange

            await exchange.close()

    @staticmethod
    async def load(name: str, params: dict = None):
        params = params or {}
        params['timeout'] = 30000

        if not hasattr(ccxt, name):
            raise InvalidExchange(name)

        return CCXTProxy(name, getattr(ccxt, name)(params))
