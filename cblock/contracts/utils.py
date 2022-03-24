from web3 import Web3

from cblock.contracts.models import CONTRACT_MODELS
from cblock.settings import config
from contract_abi import PROBATE_ABI


def check_terminated_contract(probates):
    """
    Check that contract is not terminated and change status if terminated
    """
    for network in config.networks:
        network_contracts = probates.filter(test_node=network.test)

        for probate in network_contracts:
            contract = network.w3.eth.contract(
                address=network.w3.toChecksumAddress(probate.address),
                abi=PROBATE_ABI
            )
            terminated = contract.functions.terminated().call()
            probate.terminated = terminated
            probate.save()
    return probates.filter(terminated=False)


def get_contract_addresses(test) -> dict:
    contract_addresses = {}
    for key, model in CONTRACT_MODELS.items():
        addresses = model.objects.filter(test_node=test).values_list('address', flat=True)
        contract_addresses[key] = [Web3.toChecksumAddress(address) for address in addresses]

    return contract_addresses
