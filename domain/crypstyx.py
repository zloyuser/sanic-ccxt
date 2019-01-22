import aiohttp
import base64
import hashlib
import hmac
import json

from datetime import datetime
from domain.errors import InvalidSymbol
from domain.models import *


class CrypstyxSecurity:
    _secret: str
    _app: str
    _nonce: int

    def __init__(self, params: dict):
        self._key = params['apiKey']
        self._secret = params['secret']
        self._nonce = 0

    def header(self, method: str, url: str, data=''):
        timestamp = int(datetime.utcnow().timestamp())

        request_md5 = CrypstyxSecurity.md5(data)
        request_base64 = base64.b64encode(request_md5)

        signature = self._key + method.upper() + url.lower() + str(timestamp)
        signature += str(self._nonce) + request_base64.decode()
        signature_hmac = hmac.new(base64.b64decode(self._secret), signature.encode(), hashlib.sha256).digest()

        hmac_signature = base64.b64encode(signature_hmac).decode()

        return "amx {}:{}:{}:{}".format(self._key, hmac_signature, self._nonce, timestamp)

    @staticmethod
    def md5(data):
        md5 = hashlib.md5()
        md5.update(data.encode())

        return md5.digest()


class CrypstyxProxy(ExchangeProxy):
    _security: CrypstyxSecurity
    _features: Dict[str, bool]
    _timeframes: Dict[str, str]
    _symbols: List[str]
    _currencies: Dict[str, Currency]
    _pairs: Dict[str, int]

    def __init__(self, params: dict):
        super().__init__('crypstyx')

        self._security = CrypstyxSecurity(params)
        self.features = {
            "fetchCurrencies": True,
            "fetchMarkets": False,
            "fetchOHLCV": True,
            "fetchTicker": False,
            "fetchTrades": False,
            "fetchBalance": False,
            "fetchOrders": False,
            "fetchOpenOrders": False,
            "fetchClosedOrders": False,
            "fetchOrder": False,
            "createOrder": False,
            "cancelOrder": False,
        }
        self._timeframes = {
            '1m': 'Minute1',
            '5m': 'Minute5',
            '15m': 'Minute15',
            '30m': 'Minute30',
            '1h': 'Hour1',
            '6h': 'Hour6',
            '12h': 'Hour12',
            '1d': 'Day1',
        }
        self._symbols = []
        self._currencies = {}
        self._pairs = {}
        self._nonce = 0

    def features(self) -> dict:
        return self._features

    async def symbols(self):
        await self.__load()

        return self._symbols

    async def currencies(self):
        await self.__load()

        return self._currencies

    async def markets(self):
        pass

    async def market(self, symbol: Symbol):
        pass

    async def ticker(self, symbol: Symbol):
        pass

    async def ohlcv(self, symbol: Symbol, timeframe: str = '1m', since: int = None, limit: int = None) -> List[dict]:
        await self.__load()

        if str(symbol) not in self._symbols:
            raise InvalidSymbol(symbol)

        if timeframe not in self._timeframes:
            timeframe = list(self._timeframes.keys())[0]

        limit = int(limit) if limit else 100
        now = datetime.utcnow()

        url = 'https://crypstyx.com/api/trade/graphdata'
        data = {
            "pairId": self._pairs[str(symbol)],
            "endDateTime": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "depth": limit,
            "chartType": self._timeframes[timeframe],
        }
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        k = ['t', 'o', 'h', 'l', 'c', 'v']
        ohlcv = []

        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=json.dumps(data), headers=headers) as resp:
                payload = json.loads(await resp.text())

                for item in payload:
                    _time = datetime.strptime(item['dateTime'], "%Y-%m-%dT%H:%M:%S")

                    ohlcv.append(dict(zip(k, [
                        int(_time.timestamp() * 1000),
                        item['open'],
                        item['high'],
                        item['low'],
                        item['close'],
                        item['volume'],
                    ])))

        return ohlcv

    async def trades(self, symbol: Symbol, since: int = None, limit: int = None):
        pass

    async def wallet(self) -> Wallet:
        url = 'https://api.crypstyx.com/api/tickers/1'
        headers = {
            "Accept": "application/json",
            "Authorization": self._security.header('GET', url)
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                return json.loads(await resp.text())

    async def balance(self, base: str) -> Balance:
        pass

    async def get_orders(self, symbol: Symbol, status: str = None, since: int = None, limit: int = None):
        pass

    async def get_order(self, symbol: Symbol, _id: str):
        pass

    async def create_order(self, symbol: Symbol, type: str, side: str, amount: float, price: float = None):
        pass

    async def cancel_order(self, symbol: Symbol, _id: str):
        pass

    async def close(self):
        pass

    async def __load(self):
        if len(self._symbols) != 0:
            return

        url = 'https://crypstyx.com/api/trade/currencypairs'

        async with aiohttp.ClientSession() as session:
            async with session.post(url) as resp:
                payload = json.loads(await resp.text())

                for currency in payload:
                    base = currency['firstCurrency']

                    self._currencies[base['code']] = Currency(base['id'], base['code'], base['scale'])

                    for pair in currency['pairs']:
                        quote = pair['secondCurrency']
                        symbol = str(Symbol(base['code'], quote['code']))

                        self._symbols.append(symbol)
                        self._pairs[symbol] = pair['id']
