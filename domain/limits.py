import asyncio
import aiomysql

from os import environ
from collections import defaultdict
from urllib.parse import urlparse
from ccxt import Exchange


class Limits(object):
    values: defaultdict(float)

    def __init__(self, values: dict = None):
        self.values = defaultdict(float)
        self.values.update(values or {})

    def fetch(self, exchange: Exchange) -> float:
        return self.values[exchange.id]


class LimitsSource(object):
    @classmethod
    async def load(cls) -> Limits:
        values = {}

        try:
            dsn = environ.get('CCXT_LIMITS_DSN')
            parts = urlparse(dsn)

            conn = await aiomysql.connect(
                host=parts.hostname,
                port=parts.port,
                user=parts.username,
                password=parts.password,
                db=parts.path.strip('/'),
                loop=asyncio.get_event_loop()
            )

            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute("SELECT Exchange, MinOrderAmount FROM ExchangeSettings")

                results = await cur.fetchall()

                for item in results:
                    values.update({
                        item['Exchange']: float(item['MinOrderAmount']),
                    })

            conn.close()
        except Exception:
            pass

        return Limits(values)
