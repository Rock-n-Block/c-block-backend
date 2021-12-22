import os
import sys
import asyncio
from web3 import Web3

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mywish2.settings")
import django
django.setup()

from mywish2.settings import config
from scanner.utils import get_event, create_token, create_probate, create_wedding
import logging


if __name__ == "__main__":
    while True:
        futures = list()
        loop = asyncio.get_event_loop()
        for network in [config.test_network, config.network]:
            logger = logging.getLogger(f'{network.name}_scanner')
            logger.info('Start scanner')
            network.w3 = Web3(Web3.WebsocketProvider(network.ws_endpoint))
            # List contract addresses
            token_contracts = network.token_factories
            probate_contracts = network.probate_factories
            wedding_contracts = network.wedding_factories
            provider_url = network.ws_endpoint
            # add all contracts event
            futures += [get_event(
                address, provider_url,
                network.test, network.w3, '(address,uint8)',
                create_token, logger
            ) for address in token_contracts]
            futures += [get_event(
                address, provider_url,
                network.test, network.w3, '(address,uint256)',
                create_probate, logger
            ) for address in probate_contracts]
            futures += [get_event(
                address, provider_url,
                network.test, network.w3, '(address,address)',
                create_wedding, logger
            ) for address in probate_contracts]
        loop.run_until_complete(asyncio.wait(futures))
