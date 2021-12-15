import os
import sys
import asyncio

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mywish2.settings")
import django
django.setup()

from mywish2.settings import config
from scanner.utils import get_event, create_token, create_probate
import logging


if __name__ == "__main__":
    while True:
        futures = list()
        loop = asyncio.get_event_loop()
        for network in [config.test_network, config.network]:
            logger = logging.getLogger(f'{network.name}_scanner')
            logger.info('Start scanner')
            # List contract addresses
            token_contract = network.token_factories
            probate_contract = network.probate_factories
            provider_url = network.ws_endpoint
            # add all contracts event
            futures += [get_event(
                address, provider_url,
                network.test, network.w3, '(address,uint8)',
                create_token, logger
            ) for address in token_contract]
            futures += [get_event(
                address, provider_url,
                network.test, network.w3, '(address,uint256)',
                create_probate, logger
            ) for address in probate_contract]
        loop.run_until_complete(asyncio.wait(futures))
