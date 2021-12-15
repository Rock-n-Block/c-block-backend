import os
import yaml
from dataclasses import dataclass
from marshmallow_dataclass import class_schema


@dataclass
class Network:
    ws_endpoint: str
    rpc_endpoint: str
    token_address: list
    crowdsale_address: list
    probate_address: list
    wedding_address: list
    test: bool



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