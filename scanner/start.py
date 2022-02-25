import os
import sys
import asyncio
from web3 import Web3

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mywish2.settings")
import django
django.setup()

from mywish2.settings import config
from scanner.utils import EventScanner
from scanner.models import WeddingContract

import logging


if __name__ == "__main__":
    while True:
        futures = list()
        loop = asyncio.get_event_loop()
        for network in [config.test_network, config.network]:
            network.w3 = Web3(Web3.WebsocketProvider(network.ws_endpoint))
            logger = logging.getLogger(f'{network.name}_scanner')
            logger.info('Start scanner')

            network.w3 = Web3(Web3.WebsocketProvider(network.ws_endpoint))
            # Add all fabrics contract event
            scanner = EventScanner(network.ws_endpoint, network.test, network.w3,  logger, loop)
            futures += [scanner.get_event(
                address,
                ['NewContract', '(address,uint8)'],
                scanner.create_token
            ) for address in network.token_factories]
            futures += [scanner.get_event(
                address,
                ['NewContract', '(address)'],
                scanner.create_lostkey
            ) for address in network.lastwill_factories]
            futures += [scanner.get_event(
                address,
                ['NewContract', '(address)'],
                scanner.create_lostkey
            ) for address in network.lostkey_factories]
            futures += [scanner.get_event(
                address,
                ['NewContract', '(address,address,address)'],
                scanner.create_wedding
            ) for address in network.wedding_factories]
            futures += [scanner.get_event(
                address,
                ['NewContract', '(address,uint8)'],
                scanner.create_crowdsale
            ) for address in network.crowdsale_factories]

            """Check contract events"""
            futures += [scanner.get_event(
                address, ['WithdrawalProposed', '(address,address,uint256,address)'],
                scanner.send_wedding_mail
            ) for address in WeddingContract.objects.all().values_list('address', flat=True)]
            futures += [scanner.get_event(
                address, ['DivorceProposed', '(address)'],
                scanner.send_wedding_mail
            ) for address in WeddingContract.objects.all().values_list('address', flat=True)]
        loop.run_until_complete(asyncio.wait(futures))
