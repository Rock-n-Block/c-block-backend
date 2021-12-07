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
from scanner.models import Network
from scanner.utils import get_event
import logging


if __name__ == "__main__":
    logger = logging.getLogger('testnet_scanner')
    provider_url = [config.TEST_ENDPOINT, 1]
    w3 = Web3(Web3.WebsocketProvider(provider_url[0]))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)  # only needed for PoA networks like BSC
    loop = asyncio.get_event_loop()
    network = Network.objects.first()
    # List contract addresses
    contract = [
        network.erc20nmnffabric_address,
        network.erc20nmffabric_address,
        network.erc20mnffabric_address,
        network.erc20mffabric_address
    ]
    logger.info(contract)

    while True:
        futures = [get_event(address, provider_url, w3) for address in contract]
        loop.run_until_complete(asyncio.wait(futures))
