from http import HTTPStatus
from ccxt import ExchangeError, OrderNotFound, InvalidOrder
from sanic import Blueprint
from sanic.exceptions import NotFound
from sanic.response import json
from core.helpers import jsonapi
from domain.errors import *

blueprint = Blueprint('core.extentions.exceptions')


@blueprint.exception(InvalidExchange)
def handle_invalid_exchange(request, exception):
    return json(jsonapi.error(exception, 'Invalid Exchange'), status=HTTPStatus.UNPROCESSABLE_ENTITY)


@blueprint.exception(InvalidSymbol)
def handle_invalid_symbol(request, exception):
    return json(jsonapi.error(exception, 'Invalid Symbol'), status=HTTPStatus.UNPROCESSABLE_ENTITY)


@blueprint.exception(InvalidOperation)
def handle_invalid_operation(request, exception):
    return json(jsonapi.error(exception, 'Invalid Operation'), status=HTTPStatus.UNPROCESSABLE_ENTITY)


@blueprint.exception(OrderNotFound)
def handle_order_not_found(request, exception):
    return json(jsonapi.error(exception, 'Order Not Found'), status=HTTPStatus.NOT_FOUND)


@blueprint.exception(InvalidOrder)
def handle_invalid_order(request, exception):
    return json(jsonapi.error(exception, 'Invalid Order'), status=HTTPStatus.UNPROCESSABLE_ENTITY)


@blueprint.exception(MinOrderAmount)
def handle_invalid_order(request, exception):
    return json(jsonapi.error(exception, 'Min Order Amount'), status=HTTPStatus.NOT_ACCEPTABLE)


@blueprint.exception(ExchangeError)
def handle_exchange_error(request, exception):
    return json(jsonapi.error(exception, 'Exchange Error'), status=HTTPStatus.UNPROCESSABLE_ENTITY)


@blueprint.exception(NotFound)
def handle_resource_not_found(request, exception):
    return json(jsonapi.error(exception, 'Resource not found'), status=HTTPStatus.NOT_FOUND)


@blueprint.exception(Exception)
def handle_exception(request, exception):
    return json(jsonapi.error(exception, 'Unexpected Behavior'), status=HTTPStatus.BAD_REQUEST)
