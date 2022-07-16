import logging

from django.core.exceptions import ObjectDoesNotExist
from guardian.shortcuts import assign_perm, remove_perm

PERMISSION_LIST_USERS = {
    'can_view_users': 'accounts.view_profile',
    'can_freeze_users': 'accounts.freeze_profile',
    'can_contact_users': 'accounts.contact_profile',
}

PERMISSION_LIST_CONTRACTS = {
    'can_change_network_mode': 'contracts.change_networkmode'
}


def update_permission_value(value, permission_name, user, obj=None):
    if value is None:
        logging.error('value for permission is None, cannot update')
        return

    if value:
        assign_perm(permission_name, user, obj)
    else:
        remove_perm(permission_name, user, obj)

def check_admin_rights(user, admin_model=None, permission_name=None, permission_obj=None):
    is_controller_admin = False

    if admin_model:
        try:
            controller_admin = admin_model.objects.get(owner_address=user.owner_address.lower())
            is_controller_admin = controller_admin.is_admin
        except ObjectDoesNotExist:
            pass

    with_permission = False
    if permission_name:
        with_permission = user.has_perm(permission_name, permission_obj)

    logging.info(is_controller_admin)
    logging.info(with_permission)
    if (not is_controller_admin) and (not with_permission):
        return False

    return True
