from sanic.request import Request
from sanic.response import json
from sanic import Blueprint
from sanic_openapi3 import openapi

from domain.indicators import *
from domain.models import *
from domain.factory import ExchangeFactory


blueprint = Blueprint("ccxt")


def ccxt_headers(request: Request):
    params = {k.lower()[7:]: v for k, v in request.headers.items() if k.upper().startswith('X-CCXT-')}

    if 'apikey' in params:
        params['apiKey'] = params.pop('apikey')

    return params


@blueprint.get("/")
@openapi.summary("Fetches an exchanges list")
@openapi.tag("info")
@openapi.response(200, Dict[str, ExchangeFeatures])
async def exchanges_list(request):
    exchanges = {}

    async for key, exchange in ExchangeFactory.list():
        exchanges[key] = exchange.features()

    return json(exchanges)


@blueprint.get("/<name:[A-z]+>/symbols")
@openapi.summary("Fetches a exchange symbols list")
@openapi.tag("markets")
@openapi.response(200, List[str])
async def exchange_symbols(request, name):
    exchange = await ExchangeFactory.load(name)

    try:
        symbols = await exchange.symbols()

        return json(symbols)
    finally:
        await exchange.close()


@blueprint.get("/<name:[A-z]+>/currencies")
@openapi.summary("Fetches a exchange currencies list")
@openapi.tag("markets")
@openapi.response(200, List[Currency])
async def exchange_currencies(request, name):
    exchange = await ExchangeFactory.load(name)

    try:
        currencies = await exchange.currencies()

        return json(currencies)
    finally:
        await exchange.close()


@blueprint.get("/<name:[A-z]+>/markets")
@openapi.summary("Load exchange markets list")
@openapi.tag("markets")
@openapi.response(200, List[Market])
async def exchange_markets(request, name):
    exchange = await ExchangeFactory.load(name)

    try:
        markets = await exchange.markets()

        return json(markets)
    finally:
        await exchange.close()


@blueprint.get("/<name:[A-z]+>/markets/<base:[A-z]+>/<quote:[A-z]+>")
@openapi.summary("Fetches a list of all available markets from an exchange")
@openapi.tag("markets")
@openapi.response(200, Market)
async def exchange_market(request, name, base, quote):
    exchange = await ExchangeFactory.load(name)

    try:
        market = await exchange.market(Symbol(base, quote))

        return json(market)
    finally:
        await exchange.close()


@blueprint.get("/<name:[A-z]+>/tickers")
@openapi.summary("Fetch price tickers for all symbols")
@openapi.tag("tickers")
@openapi.response(200, List[Ticker])
async def exchange_tickers(request, name):
    exchange = await ExchangeFactory.load(name)

    try:
        tickers = await exchange.tickers()

        return json(tickers.values())
    finally:
        await exchange.close()


@blueprint.get("/<name:[A-z]+>/tickers/<base:[A-z]+>/<quote:[A-z]+>")
@openapi.summary("Fetch price tickers for a particular market/symbol")
@openapi.tag("tickers")
@openapi.response(200, Ticker)
async def exchange_ticker(request, name, base, quote):
    exchange = await ExchangeFactory.load(name)

    try:
        ticker = await exchange.ticker(Symbol(base, quote))

        return json(ticker)
    finally:
        await exchange.close()


@blueprint.get("/<name:[A-z]+>/ohlcv/<base:[A-z]+>/<quote:[A-z]+>")
@openapi.summary("Fetches OHLCV data for symbol")
@openapi.tag("chart")
@openapi.parameter("timeframe", str)
@openapi.parameter("since", int)
@openapi.parameter("limit", int)
@openapi.response(200, List[OHLCV])
async def exchange_ohlcv(request, name, base, quote):
    timeframe = request.args.get("timeframe", None)
    since = request.args.get("since", None)
    limit = request.args.get("limit", None)

    exchange = await ExchangeFactory.load(name)

    try:
        ohlcv = await exchange.ohlcv(Symbol(base, quote), timeframe, since, limit)

        return json(ohlcv)
    finally:
        await exchange.close()


@blueprint.get("/<name:[A-z]+>/trades/<base:[A-z]+>/<quote:[A-z]+>")
@openapi.summary("Fetches list of most recent trades for a particular symbol")
@openapi.tag("trades")
@openapi.parameter("since", int)
@openapi.parameter("limit", int)
@openapi.response(200, List[TradeItem])
async def exchange_trades(request, name, base, quote):
    since = request.args.get("since", None)
    limit = request.args.get("limit", None)

    exchange = await ExchangeFactory.load(name)

    try:
        trades = await exchange.trades(Symbol(base, quote), since, limit)

        return json(trades)
    finally:
        await exchange.close()


@blueprint.get("/<name:[A-z]+>/book/<base:[A-z]+>/<quote:[A-z]+>")
@openapi.summary("Fetch L2/L3 order book for a particular market trading symbol.")
@openapi.tag("trades")
@openapi.parameter("limit", int)
@openapi.response(200, OrderBook)
async def exchange_book(request, name, base, quote):
    limit = request.args.get("limit", None)

    exchange = await ExchangeFactory.load(name)

    try:
        book = await exchange.book(Symbol(base, quote), limit)

        return json(book)
    finally:
        await exchange.close()


@blueprint.get("/<name:[A-z]+>/wallet/")
@openapi.tag("account")
@openapi.summary("Fetches authorized account balances")
@openapi.response(200, Wallet)
async def exchange_wallets(request, name):
    exchange = await ExchangeFactory.load(name, ccxt_headers(request))

    try:
        wallet = await exchange.wallet()

        return json(wallet)
    finally:
        await exchange.close()


@blueprint.get("/<name:[A-z]+>/wallet/<base:[A-z]+>")
@openapi.tag("account")
@openapi.summary("Fetches authorized account balance")
@openapi.response(200, Balance)
async def exchange_wallet(request, name, base):
    exchange = await ExchangeFactory.load(name, ccxt_headers(request))

    try:
        balance = await exchange.balance(base)

        return json(balance)
    finally:
        await exchange.close()


@blueprint.get("/<name:[A-z]+>/orders/<base:[A-z]+>/<quote:[A-z]+>")
@openapi.summary("Fetch account orders for a particular market trading symbol.")
@openapi.tag("orders")
@openapi.parameter("since", int)
@openapi.parameter("limit", int)
@openapi.parameter("status", str)
@openapi.response(200, List[Order])
async def orders_list(request, name, base, quote):
    exchange = await ExchangeFactory.load(name, ccxt_headers(request))

    since = request.args.get("since", None)
    limit = request.args.get("limit", None)
    status = request.args.get("status", None)

    try:
        orders = await exchange.get_orders(Symbol(base, quote), status, since, limit)

        return json(orders)
    finally:
        await exchange.close()


@blueprint.get("/<name:[A-z]+>/orders/<base:[A-z]+>/<quote:[A-z]+>/<id>")
@openapi.summary("Get order with specified ID.")
@openapi.tag("orders")
@openapi.response(200, Order, desc="Order object")
@openapi.response(404, desc="Order not found")
async def orders_get(request, name, base, quote, id):
    exchange = await ExchangeFactory.load(name, ccxt_headers(request))

    try:
        order = await exchange.get_order(Symbol(base, quote), id)

        return json(order)
    finally:
        await exchange.close()


@blueprint.post("/<name:[A-z]+>/orders/<base:[A-z]+>/<quote:[A-z]+>")
@openapi.summary("Place order to exchange with given data.")
@openapi.tag("orders")
@openapi.response(201, Order, desc="Order created")
@openapi.response(406, desc="Min order amount not reached")
async def orders_place(request, name, base, quote):
    exchange = await ExchangeFactory.load(name, ccxt_headers(request))

    payload = request.json

    _type = payload["type"] if "type" in payload else "market"
    _side = payload["side"] if "side" in payload else "sell"
    _amount = float(payload["amount"])
    _price = float(payload["price"]) if _type == "limit" else None

    try:
        order = await exchange.create_order(Symbol(base, quote), _type, _side, _amount, _price)

        return json(order, 201)
    finally:
        await exchange.close()


@blueprint.delete("/<name:[A-z]+>/orders/<base:[A-z]+>/<quote:[A-z]+>/<id>")
@openapi.summary("Cancel with specified ID.")
@openapi.tag("orders")
@openapi.response(204, desc="Order removed")
@openapi.response(404, desc="Order not found")
async def orders_cancel(request, name, base, quote, id):
    exchange = await ExchangeFactory.load(name, ccxt_headers(request))

    try:
        await exchange.cancel_order(Symbol(base, quote), id)

        return json(None, 204)
    finally:
        await exchange.close()
