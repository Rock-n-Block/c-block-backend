import logging

from rest_framework.permissions import BasePermission
from guardian.shortcuts import assign_perm, remove_perm

PERMISSION_LIST_USERS = {
    'can_view_users': 'accounts.view_profile',
    'can_freeze_users': 'accounts.freeze_profile',
    'can_contact_users': 'accounts.contact_profile',
}

PERMISSION_LIST_CONTRACTS = {
    'can_change_network_mode': 'contracts.change_networkmode'
}


class IsAuthenticatedAndContractSuperAdmin(BasePermission):
    """
    Permission to check Super Admin on contract
    """
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False

        return request.user.is_contract_owner

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

def change_super_admin(old_user, new_user):
    if old_user == new_user:
        logging.error('old user == new user')
        return

    for profile_perm_slug, profile_perm_value in PERMISSION_LIST_USERS.items():
        update_permission_value(True, profile_perm_value, new_user)
        update_permission_value(False, profile_perm_value, old_user)

    for contracts_perm_slug, contracts_perm_value in PERMISSION_LIST_CONTRACTS.items():
        if contracts_perm_slug == 'can_change_network_mode':
            from cblock.contracts.models import NetworkMode
            contracts_obj, _ = NetworkMode.objects.get_or_create(name='celo')
        else:
            contracts_obj = None
        update_permission_value(True, contracts_perm_value, new_user, contracts_obj)
        update_permission_value(False, contracts_perm_value, old_user, contracts_obj)

    new_user.is_contract_owner = True
    new_user.save()

    old_user.is_contract_owner = False
    old_user.save()

    logging.info(f'superuser updated {old_user} -> {new_user}')