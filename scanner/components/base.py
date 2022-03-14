import logging
import sys
import time
import traceback
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from cblock.settings import config
from cblock.contracts.models import Profile
from scanner.components.redis import RedisClient

_log_format = (
    "%(asctime)s - [%(levelname)s] - %(filename)s (line %(lineno)d) - %(message)s"
)

_datetime_format = "%d.%m.%Y %H:%M:%S"

loggers = {}


def never_fall(func):
    def wrapper(*args, **kwargs):
        while True:
            try:
                func(*args, **kwargs)
            except Exception as e:
                _, _, stacktrace = sys.exc_info()
                error = (
                   f"\n {''.join(traceback.format_tb(stacktrace)[-2:])}"
                   f"{type(e).__name__} {e}"
                )

                logging.error(error)
                if str(e) != "{'code': -32000, 'message': 'filter not found'}":
                    message = f"Scanner error in {args[0].network}: {error}"
                    # send_message(message, ["dev"])
                    logging.error(message)
                    time.sleep(60)

    return wrapper


class HandlerABC(ABC):
    def __init__(self, network, scanner) -> None:
        self.network = network
        self.scanner = scanner

        logger_name = f"scanner_{self.TYPE}_{self.network.name}"

        # This is necessary so that records are not duplicated.
        if not loggers.get(logger_name):
            loggers[logger_name] = self.get_logger(logger_name)
        self.logger = loggers.get(logger_name)

    def get_owner(self, owner_address: str) -> Optional[Profile]:
        user, _ = Profile.objects.get_or_create(owner_address=owner_address)
        return user

    def get_file_handler(self, name):
        file_handler = logging.FileHandler(f"scanner_logs/{name}.log")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(
            logging.Formatter(_log_format, datefmt=_datetime_format)
        )
        return file_handler

    def get_stream_handler(self):
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG)
        stream_handler.setFormatter(
            logging.Formatter(_log_format, datefmt=_datetime_format)
        )
        return stream_handler

    def get_logger(self, name):
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(self.get_file_handler(name))
        # logger.addHandler(self.get_stream_handler())
        return logger

    @abstractmethod
    def save_event(self, event_data) -> None:
        ...


class ScannerABC(ABC):
    def __init__(self, network, contracts=None):
        self.network = network
        self.contracts = contracts

    def sleep(self) -> None:
        time.sleep(config.scanner_sleep)

    def save_last_block(self, name, block) -> None:
        redis_ = RedisClient()
        redis_.connection.set(name, block)

    def get_last_block(self, name) -> int:
        redis_ = RedisClient()
        last_block_number = redis_.connection.get(name)
        if not last_block_number:
            last_block_number = self.get_last_network_block()
            self.save_last_block(name, last_block_number)
        return int(last_block_number)

    @abstractmethod
    def get_last_network_block(self) -> int:
        ...


@dataclass
class EventBase:
    tx_hash: str
    sender: str


@dataclass
class NewContractBase(EventBase):
    contract_address: str


@dataclass
class NewContractWithType(NewContractBase):
    contract_type: int
    owner: str

@dataclass
class NewContract(NewContractBase):
    pass


@dataclass
class WeddingBase(EventBase):
    proposed_by: str
