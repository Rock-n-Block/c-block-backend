from web3 import Web3

from contract_abi import PROBATE_ABI
from cblock.settings import config
from cblock.contracts.models import (
    CONTRACT_MODELS,
    LastWillContract,
    LostKeyContract,
    WeddingContract,
    WeddingActionStatus
)

def get_web3(rpc_endpoint):
    return Web3(Web3.HTTPProvider(rpc_endpoint))


def check_terminated_contract(probates):
    """
    Check that contract is not terminated and change status if terminated
    """
    for network in config.networks:
        network_contracts = probates.filter(is_testnet=network.is_testnet)

        for probate in network_contracts:
            contract = network.w3.eth.contract(
                address=network.w3.toChecksumAddress(probate.address),
                abi=PROBATE_ABI
            )
            terminated = contract.functions.terminated().call()
            probate.terminated = terminated
            probate.save()
    return probates.filter(terminated=False)


def rewrap_addresses_to_checksum(addresses):
    return [Web3.toChecksumAddress(address) for address in addresses]


def get_contract_addresses(test) -> dict:
    contract_addresses = {}
    for key, model in CONTRACT_MODELS.items():
        addresses = model.objects.filter(is_testnet=test).exclude(address__in=[None, ''])\
            .values_list('address', flat=True)
        contract_addresses[key] = rewrap_addresses_to_checksum(addresses)

    return contract_addresses


def get_probates(dead: bool, test_network: bool):

    lastwills = LastWillContract.objects.filter(dead=dead, is_testnet=test_network, distribution_tx_hash=None)\
        .exclude(owner_mail=None, contract_mails=None, address__in=[None, ''])
    lostkeys = LostKeyContract.objects.filter(dead=dead, is_testnet=test_network, distribution_tx_hash=None)\
        .exclude(owner_mail=None, contract_mails=None, address__in=[None, ''])
    contracts = list(lastwills) + list(lostkeys)

    return contracts


def get_weddings_pending_divorce(test_network: bool):
    return WeddingContract.objects.filter(is_testnet=test_network, wedding_divorce__status=WeddingActionStatus.PROPOSED)

