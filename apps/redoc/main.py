from sanic.blueprints import Blueprint
from os import path

blueprint = Blueprint('redoc')

dir_path = path.dirname(path.realpath(__file__))
dir_path = path.abspath(dir_path + '/public')

blueprint.static('/docs', dir_path)
blueprint.static('/docs', dir_path + '/index.html')
