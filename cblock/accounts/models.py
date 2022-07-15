import logging

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _

from phone_field import PhoneField
from django_countries.fields import CountryField

from cblock.accounts.managers import MetamaskUserManager
from cblock.accounts.utils import get_controller_contract
from cblock.accounts.permissions import PERMISSION_LIST_USERS, PERMISSION_LIST_CONTRACTS, change_super_admin

class Profile(AbstractUser):
    """
    User profile
    """
    username = None
    email = models.EmailField(_('email address'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = MetamaskUserManager()

    owner_address = models.CharField(max_length=64, unique=True, blank=False)

    name = models.CharField(max_length=128, blank=True, null=True, default=None)
    company = models.CharField(max_length=129, blank=True, null=True, default=None)
    phone_number = PhoneField(blank=True, null=True, default=None)
    country = CountryField(blank=True, null=True, default=None)
    city = models.CharField(max_length=128, blank=True, null=True, default=None)
    street = models.CharField(max_length=128, blank=True, null=True, default=None)
    office = models.CharField(max_length=32, blank=True, null=True, default=None)
    building = models.CharField(max_length=32, blank=True, null=True, default=None)
    zipcode = models.CharField(max_length=32, blank=True, null=True, default=None)
    avatar = models.ImageField(null=True, upload_to='avatars/')

    freezed = models.BooleanField(default=False)
    is_contract_owner = models.BooleanField(default=False)

    class Meta:
        unique_together = (("email", "owner_address"),)
        permissions = [
            ('freeze_profile', 'Can freeze user profile by setting freezed status'),
            ('contact_profile', 'Can contact profile by using contract form')
        ]

    def __str__(self):
        return f'{self.email} - {self.owner_address}'

    def set_owner_adress(self, owner_address):
        self.owner_address = owner_address
        self.save()

    def is_completed_profile(self):
        profile_detail_fields = (
            self.name,
            self.company,
            self.phone_number,
            self.country,
            self.city,
            self.street,
            self.office,
            self.zipcode
        )
        return all(v is not None for v in profile_detail_fields)

    def is_contract_change_price_admin(self):
        controller_contract, network = get_controller_contract()

        user_address = network.w3.toChecksumAddress(self.owner_address)
        can_change_price = controller_contract.functions.canSetPrice(user_address).call()
        # logging.info(f'User {user_address} can change price: {can_change_price}')
        return can_change_price

    def is_contract_change_payment_addresses_admin(self):
        controller_contract, network = get_controller_contract()

        user_address = network.w3.toChecksumAddress(self.owner_address)
        can_change_payment_addresses = controller_contract.functions.canSetFeeReceiver(user_address).call()
        # logging.info(f'User {user_address} can change payment addresses: {can_change_payment_addresses}')
        return can_change_payment_addresses

    def get_role_system_permissions(self):
        contract_change_price = self.is_contract_change_price_admin()
        contract_change_payment_addresses = self.is_contract_change_payment_addresses_admin()

        # Enable/disable mainnet toggle
        from cblock.contracts.models import NetworkMode
        net_obj, _ = NetworkMode.objects.get_or_create(name='celo')
        can_change_network_mode = self.has_perm(PERMISSION_LIST_CONTRACTS.get('can_change_network_mode'), net_obj)

        # View user database
        can_view_users = self.has_perm(PERMISSION_LIST_USERS.get('can_view_users'))
        # Freeze users
        can_freeze_users = self.has_perm(PERMISSION_LIST_USERS.get('can_freeze_users'))
        # Contact users
        can_contact_users = self.has_perm(PERMISSION_LIST_USERS.get('can_contact_users'))

        return {
            'contract_super_admin': self.is_contract_owner,
            'can_change_price': contract_change_price,
            'can_change_payment_addresses': contract_change_payment_addresses,
            'can_change_network_mode': can_change_network_mode,
            'can_view_users': can_view_users,
            'can_freeze_users': can_freeze_users,
            'can_contact_users': can_contact_users,
        }

class ControllerOwnershipTransferred(models.Model):
    tx_hash = models.CharField(max_length=128, unique=True, help_text='Transaction hash')
    old_owner = models.ForeignKey(Profile, on_delete=models.CASCADE,
                                  related_name='old_owners', related_query_name='old_owner'
                                  )
    new_owner = models.ForeignKey(Profile, on_delete=models.CASCADE,
                                  related_name='new_owner', related_query_name='new_owner'
                                  )
    changed = models.BooleanField(default=False)

    def change_superuser(self):
        if self.changed:
            logging.warning('Super Admin already changed, skipping')
            return

        change_super_admin(self.old_owner, self.new_owner)
        self.changed = True
        self.save()

        logging.info(f'Super Admin changed: {self.old_owner} -> {self.new_owner}')