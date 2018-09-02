import ccxt.async_support as ccxt

from domain.errors import InvalidExchange
from domain.crypstyx import CrypstyxProxy
from domain.ccxt import CCXTProxy


class ExchangeFactory:
    @staticmethod
    async def list():
        exchanges = ['crypstyx'] + ccxt.exchanges

        for key in exchanges:
            exchange = ExchangeFactory.load(key)

            yield key, exchange

            await exchange.close()

    @staticmethod
    def load(name: str, params: dict = None):
        params = params or {}
        params['timeout'] = 30000

        if name == 'crypstyx':
            return CrypstyxProxy(params)

        if not hasattr(ccxt, name):
            raise InvalidExchange(name)

        return CCXTProxy(name, getattr(ccxt, name)(params))
