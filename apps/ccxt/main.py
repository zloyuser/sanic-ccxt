from sanic.request import Request
from sanic.response import json
from sanic import Blueprint
from sanic_openapi3 import openapi
from domain.models import *


blueprint = Blueprint("ccxt")


def ccxt_headers(request: Request):
    params = {k.lower()[7:]: v for k, v in request.headers.items() if k.upper().startswith('X-CCXT-')}

    if 'apikey' in params:
        params['apiKey'] = params.pop('apikey')

    return params


@blueprint.get("/")
@openapi.summary("Fetches an exchanges list")
@openapi.tag("info")
@openapi.response(200, [ExchangeFeatures])
async def exchanges_list(request):
    exchanges = {}

    async for key, exchange in ExchangeProxy.list():
        exchanges[key] = exchange.features()

    return json(exchanges)


@blueprint.get("/<name:[A-z]+>/symbols")
@openapi.summary("Fetches a exchange symbols list")
@openapi.tag("markets")
@openapi.response(200, [str])
async def exchange_symbols(request, name):
    exchange = ExchangeProxy.load(name)
    symbols = await exchange.symbols()

    await exchange.close()

    return json(symbols)


@blueprint.get("/<name:[A-z]+>/currencies")
@openapi.summary("Fetches a exchange currencies list")
@openapi.tag("markets")
@openapi.response(200, [Currency])
async def exchange_currencies(request, name):
    exchange = ExchangeProxy.load(name)
    currencies = await exchange.currencies()

    await exchange.close()

    return json(currencies)


@blueprint.get("/<name:[A-z]+>/markets")
@openapi.summary("Load exchange markets list")
@openapi.tag("markets")
@openapi.response(200, [Market])
async def exchange_markets(request, name):
    exchange = ExchangeProxy.load(name)
    markets = await exchange.markets()

    await exchange.close()

    return json(markets)


@blueprint.get("/<name:[A-z]+>/markets/<base:[A-z]+>/<quote:[A-z]+>")
@openapi.summary("Fetches a list of all available markets from an exchange")
@openapi.tag("markets")
@openapi.response(200, Market)
async def exchange_market(request, name, base, quote):
    exchange = ExchangeProxy.load(name)
    market = await exchange.market(Symbol(base, quote))

    await exchange.close()

    return json(market)


@blueprint.get("/<name:[A-z]+>/tickers/<base:[A-z]+>/<quote:[A-z]+>")
@openapi.summary("Fetch price tickers for a particular market/symbol")
@openapi.tag("tickers")
@openapi.response(200, Ticker)
async def exchange_ticker(request, name, base, quote):
    exchange = ExchangeProxy.load(name)
    tick = await exchange.ticker(Symbol(base, quote))

    await exchange.close()

    return json(tick)


@blueprint.get("/<name:[A-z]+>/ohlcv/<base:[A-z]+>/<quote:[A-z]+>")
@openapi.summary("Fetches OHLCV data for symbol")
@openapi.tag("chart")
@openapi.parameter("timeframe", str)
@openapi.parameter("since", int)
@openapi.parameter("limit", int)
@openapi.response(200, [OHLCV])
async def exchange_ohlcv(request, name, base, quote):
    timeframe = request.args.get("timeframe", None)
    since = request.args.get("since", None)
    limit = request.args.get("limit", None)

    exchange = ExchangeProxy.load(name)
    ohlcv = await exchange.ohlcv(Symbol(base, quote), timeframe, since, limit)

    await exchange.close()

    return json(ohlcv)


@blueprint.get("/<name:[A-z]+>/trades/<base:[A-z]+>/<quote:[A-z]+>")
@openapi.summary("Fetches list of most recent trades for a particular symbol")
@openapi.tag("trades")
@openapi.parameter("since", int)
@openapi.parameter("limit", int)
@openapi.response(200, [Trade])
async def exchange_trades(request, name, base, quote):
    since = request.args.get("since", None)
    limit = request.args.get("limit", None)

    exchange = ExchangeProxy.load(name)
    trades = await exchange.trades(Symbol(base, quote), since, limit)

    await exchange.close()

    return json(trades)


@blueprint.get("/<name:[A-z]+>/balance")
@openapi.tag("account")
@openapi.summary("Fetches authorized account balance")
@openapi.response(200, [Balance])
async def exchange_balance(request, name):
    exchange = ExchangeProxy.load(name, ccxt_headers(request))
    balance = await exchange.balance()

    await exchange.close()

    return json(balance)


# @blueprint.get("/<name:[A-z]+>/orders/<base:[A-z]+>/<quote:[A-z]+>")
# @openapi.summary("Fetch L2/L3 order book for a particular market trading symbol.")
# @openapi.tag("orders")
# @openapi.parameter("limit", int)
# @openapi.response(200, [Order])
# async def exchange_orders(request, name, base, quote):
#     exchange = get_exchange(name)
#
#     if not exchange.has["fetchOrderBook"]:
#         return json(NotImplemented)
#
#     limit = request.args.get("limit", None)
#
#     orders = await exchange.fetch_order_book(symbol(base, quote), limit)
#
#     await exchange.close()
#
#     return json(orders)
#
#
# @blueprint.post("/<name:[A-z]+>/orders/<base:[A-z]+>/<quote:[A-z]+>")
# @openapi.summary("Place order to exchange with given data.")
# @openapi.tag("orders")
# @openapi.response(201, desc="Order created")
# async def orders_place(request, name, base, quote):
#     exchange = get_exchange(name)
#
#     if not exchange.has["createOrder"]:
#         return json(NotImplemented)
#
#     payload = request.json()
#
#     _type = payload["type"] if "type" in payload else "market"
#     _side = payload["side"] if "side" in payload else "sell"
#     _amount = float(payload["amount"])
#     _price = float(payload["price"]) if _type == "limit" else None
#
#     await exchange.create_order(symbol(base, quote), _type, _side, _amount, _price)
#     await exchange.close()
#
#     return json(None, 201)
#
#
# @blueprint.delete("/<name:[A-z]+>/orders/<base:[A-z]+>/<quote:[A-z]+>/<id>")
# @openapi.summary("Cancel with specified ID.")
# @openapi.tag("orders")
# @openapi.response(204, desc="Order removed")
# @openapi.response(404, desc="Order not found")
# async def orders_cancel(request, name, base, quote, id):
#     exchange = get_exchange(name)
#
#     if not exchange.has["cancelOrder"]:
#         return json(NotImplemented)
#
#     await exchange.cancel_order(id, symbol(base, quote))
#     await exchange.close()
#
#     return json(None, 204)
