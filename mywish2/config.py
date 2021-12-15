import os
import yaml
from dataclasses import dataclass, field
from marshmallow_dataclass import class_schema

from web3 import Web3
from web3.middleware import geth_poa_middleware


@dataclass
class Network:
    name: str
    ws_endpoint: str
    rpc_endpoint: str
    token_factories: list
    crowdsale_factories: list
    probate_factories: list
    wedding_factories: list
    test: bool
    w3: Web3 = field(init=False, default=None)

    def __post_init__(self):
        self.w3 = Web3(Web3.WebsocketProvider(self.ws_endpoint))
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)


@dataclass
class Config:
    allowed_hosts: list
    secret_key: str
    debug: bool
    static_url: str
    static_root: str
    redis_expiration_time: int
    redis_host: str
    redis_port: int
    email_host: str
    email_host_user: str
    email_password: str
    email_port: int
    test_network: Network
    network: Network


config_path = '/../config.yaml'

with open(os.path.dirname(__file__) + config_path) as f:
    config_data = yaml.safe_load(f)

config: Config = class_schema(Config)().load(config_data)