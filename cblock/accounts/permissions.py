import logging

from rest_framework.permissions import BasePermission

from contract_abi import CONTROLLER_ABI
from cblock.settings import config


class IsAuthenticatedAndContractAdmin(BasePermission):
    """
    Permission to check Super Admin on contract
    """
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False

        return request.user.is_contract_super_admin()

class IsAuthenticatedAndContractChangePricesAdmin(BasePermission):
    """
    Permission to check Super Admin on contract
    """
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False

        return request.user.is_contract_change_prices_admin()

class IsAuthenticatedAndContractChangePaymentAddressesAdmin(BasePermission):
    """
    Permission to check Super Admin on contract
    """
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False

        return request.user.is_contract_change_payment_addresses_admin()