import logging

from rest_framework.permissions import BasePermission
from guardian.shortcuts import assign_perm, remove_perm

class IsAuthenticatedAndContractSuperAdmin(BasePermission):
    """
    Permission to check Super Admin on contract
    """
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False

        return request.user.is_contract_super_admin()

class IsAuthenticatedAndContractChangePricesAdmin(BasePermission):
    """
    Permission to check Price Admin on contract
    """
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False

        return request.user.is_contract_change_prices_admin()

class IsAuthenticatedAndContractChangePaymentAddressesAdmin(BasePermission):
    """
    Permission to check Payment Addresses Admin on contract
    """
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False

        return request.user.is_contract_change_payment_addresses_admin()


def update_permission_value(value, permission_name, user, obj=None):
    if value is None:
        logging.error('value for permission is None, cannot update')
        return

    if value:
        assign_perm(permission_name, user, obj)
    else:
        remove_perm(permission_name, user, obj)