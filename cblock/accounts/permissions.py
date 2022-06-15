import logging

from rest_framework.permissions import BasePermission

from contract_abi import CONTROLLER_ABI
from cblock.settings import config


class IsAuthenticatedAndContractAdmin(BasePermission):

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False

        networks = config.networks
        network = [network for network in networks if network.is_testnet == config.debug]
        if not network:
            raise Exception('Misconfiguration: no network found to check admin rights')

        network = network[0]
        controller_address = network.w3.toChecksumAddress(network.controller_contract)
        controller_contract = network.w3.eth.contract(
            address=controller_address,
            abi=CONTROLLER_ABI
        )

        user_address = network.w3.toChecksumAddress(request.user.owner_address)
        admin_role = controller_contract.functions.DEFAULT_ADMIN_ROLE().call()
        is_admin = controller_contract.functions.hasRole(admin_role, user_address).call()
        logging.info(f'User {user_address} is_admin: {is_admin}')
        return is_admin