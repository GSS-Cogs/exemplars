import os

import configparser
from typing import NamedTuple, Optional

from pymongo import MongoClient


# Note: keep it generic so its easier to interface this out if we want
# to change database solution later
class Store:

    def __init__(self, config):
        self.config = config
        
    def get_client(self):
        client = MongoClient(
            self.mongo_host,
            self.mongo_post
        )




class Config(NamedTuple):
    # Use env vars, fall back on defaults
    config = configparser.ConfigParser()

    mongo_host: Optional[str] = os.getenv("MongoHost", config["default"]["MongoHost"])
    mongo_port: Optional[str] = os.getenv("MongoHost", config["default"]["MongoPort"])

def get_store():
    return Store(Config())


store = get_store()