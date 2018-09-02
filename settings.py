import dotenv
from os import environ
from os.path import join, dirname


class Settings(object):
    def __init__(self, filename='.env'):
        env_path = join(dirname(__file__), filename)
        dotenv.load_dotenv(env_path)

        for key in environ.keys():
            setattr(self, key, environ[key])
