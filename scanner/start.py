import os
import sys
import asyncio

from web3 import Web3
from web3.middleware import geth_poa_middleware # only needed for PoA networks like BSC

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mywish2.settings")
import django
django.setup()

from mywish2.settings import config, BASE_DIR
from scanner.utils import get_event
import logging


if __name__ == "__main__":
    while True:
        futures = list()
        for network in [config.test_network, config.network]:
            logger = logging.getLogger(f'{network.ws_endpoint}_scanner')
            logger.info('Start scanner')

            loop = asyncio.get_event_loop()
            # List contract addresses
            token_contract = network.token_address
            probate_contract = network.probate_address
            provider_url = network.ws_endpoint
            w3 = Web3(Web3.WebsocketProvider(provider_url))
            w3.middleware_onion.inject(geth_poa_middleware, layer=0)  # only needed for PoA networks like BSC
            # add all contracts event
            futures += [get_event(address, provider_url, network.test, w3, '(address,uint8)', 'token') for address in token_contract]
            futures += [get_event(address, provider_url, network.test, w3,  '(address,uint256)', 'probate') for address in probate_contract]
        loop.run_until_complete(asyncio.wait(futures))
