from sanic.response import json
from sanic import Blueprint
from sanic_openapi3 import openapi

from domain.indicators import *
from domain.models import *
from domain.factory import ExchangeFactory


blueprint = Blueprint("ta")


@blueprint.get("/<name:[A-z]+>/indicators/<base:[A-z]+>/<quote:[A-z]+>/macd")
@openapi.summary("Fetches MACD indicators for symbol")
@openapi.tag("indicators")
@openapi.parameter("timeframe", str)
@openapi.parameter("count", int)
@openapi.parameter("fast", int)
@openapi.parameter("slow", int)
@openapi.parameter("signal", int)
@openapi.response(200, MACD)
async def exchange_indicators_macd(request, name, base, quote):
    timeframe = request.args.get("timeframe", "5m")
    count = request.args.get("count", None)
    fast = request.args.get("fast", 12)
    slow = request.args.get("slow", 26)
    signal = request.args.get("signal", 9)

    exchange = await ExchangeFactory.load(name)
    candles = await exchange.ohlcv(Symbol(base, quote), timeframe)

    value = Indicators(candles, count).macd(fast, slow, signal)

    try:
        return json(value)
    finally:
        await exchange.close()


@blueprint.get("/<name:[A-z]+>/indicators/<base:[A-z]+>/<quote:[A-z]+>/rsi")
@openapi.summary("Fetches RSI indicators for symbol")
@openapi.tag("indicators")
@openapi.parameter("timeframe", str)
@openapi.parameter("count", int)
@openapi.parameter("period", int)
@openapi.response(200, List[float])
async def exchange_indicators_rsi(request, name, base, quote):
    timeframe = request.args.get("timeframe", "5m")
    count = request.args.get("count", None)
    period = request.args.get("period", 14)

    exchange = await ExchangeFactory.load(name)
    candles = await exchange.ohlcv(Symbol(base, quote), timeframe)

    value = Indicators(candles, count).rsi(period)

    try:
        return json(value)
    finally:
        await exchange.close()


@blueprint.get("/<name:[A-z]+>/indicators/<base:[A-z]+>/<quote:[A-z]+>/obv")
@openapi.summary("Fetches RSI indicators for symbol")
@openapi.tag("indicators")
@openapi.parameter("timeframe", str)
@openapi.parameter("count", int)
@openapi.response(200, List[float])
async def exchange_indicators_obv(request, name, base, quote):
    timeframe = request.args.get("timeframe", "5m")
    count = request.args.get("count", None)

    exchange = await ExchangeFactory.load(name)
    candles = await exchange.ohlcv(Symbol(base, quote), timeframe)

    value = Indicators(candles, count).obv()

    try:
        return json(value)
    finally:
        await exchange.close()
