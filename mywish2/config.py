import os
import yaml
from dataclasses import dataclass
from marshmallow_dataclass import class_schema

@dataclass
class Config:
    ALLOWED_HOSTS: list
    SECRET_KEY: str
    DEBUG: bool
    TEST_ENDPOINT: str
    ENDPOINT: str
    REDIS_EXPIRATION_TIME: int
    REDIS_HOST: str
    REDIS_PORT: int
    EMAIL_HOST: str
    EMAIL_PASSWORD: str


config_path = '/../config.yaml'

with open(os.path.dirname(__file__) + config_path) as f:
    config_data = yaml.safe_load(f)

config: Config = class_schema(Config)().load(config_data)