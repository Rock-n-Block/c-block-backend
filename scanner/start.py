import os
import sys
import time
import logging
from web3 import Web3
from web3.middleware import geth_poa_middleware


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cblock.settings")
import django

django.setup()

from scanner.components.absolute import ScannerAbsolute
from scanner.components.handlers import (
    HandlerNewContractToken,
    HandlerNewContractCrowdsale,
    HandlerNewContractWedding,
    HandlerNewContractLastwill,
    HandlerNewContractLostkey,
    HandlerTransferOwnership,
    HandlerWeddingWithdrawalProposed,
    HandlerWeddingWithdrawalStatusChanged,
    HandlerWeddingDivorceProposed,
    HandlerWeddingDivorceStatusChanged,
    HandlerProbateFundsDistributed
)

from cblock.settings import config

if __name__ == "__main__":
    for network in config.networks:

        provider = Web3.HTTPProvider(network.rpc_endpoint)
        provider.middlewares.clear()
        network.w3 = Web3(provider)
        network.w3.middleware_onion.inject(geth_poa_middleware, layer=0)

        # Factories

        # New Contract scanner (Token)
        ScannerAbsolute(
            network=network,
            handler=HandlerNewContractToken,
            contracts=network.token_factories
        ).start()

        # New Contract scanner (Crowdsale)
        ScannerAbsolute(
            network=network,
            handler=HandlerNewContractCrowdsale,
            contracts=network.crowdsale_factories
        ).start()
        #
        # New Contract scanner (Weddings)
        ScannerAbsolute(
            network=network,
            handler=HandlerNewContractWedding,
            contracts=network.wedding_factories,
        ).start()

        # New Contract scanner (Lastwill)
        ScannerAbsolute(
            network=network,
            handler=HandlerNewContractLastwill,
            contracts=network.lastwill_factories,
        ).start()

        # New Contract scanner (Lostkey)
        ScannerAbsolute(
            network=network,
            handler=HandlerNewContractLostkey,
            contracts=network.lostkey_factories,
        ).start()

        # Transfer ownership scanner
        ScannerAbsolute(
            network=network,
            handler=HandlerTransferOwnership,
            preload_contracts=True
        ).start()

        # Wedding withdrawal scanner
        ScannerAbsolute(
            network=network,
            handler=HandlerWeddingWithdrawalProposed,
            preload_contracts=True
        ).start()

        # Wedding withdrawal status scanner
        ScannerAbsolute(
            network=network,
            handler=HandlerWeddingWithdrawalStatusChanged,
            preload_contracts=True
        ).start()

        # Wedding divorce scanner
        ScannerAbsolute(
            network=network,
            handler=HandlerWeddingDivorceProposed,
            preload_contracts=True
        ).start()

        # Wedding divorce status scanner
        ScannerAbsolute(
            network=network,
            handler=HandlerWeddingDivorceStatusChanged,
            preload_contracts=True
        ).start()

        # Lastwill/Lostkey funds distribution scanner
        ScannerAbsolute(
            network=network,
            handler=HandlerProbateFundsDistributed,
            preload_contracts=True
        ).start()


