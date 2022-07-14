import logging

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _

from phone_field import PhoneField
from django_countries.fields import CountryField

from cblock.accounts.managers import MetamaskUserManager
from cblock.accounts.utils import get_controller_contract

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

    class Meta:
        unique_together = (("email", "owner_address"),)

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

    def is_contract_super_admin(self):
        controller_contract, network = get_controller_contract()

        user_address = network.w3.toChecksumAddress(self.owner_address)
        contract_owner = controller_contract.functions.owner().call()
        is_admin = contract_owner == user_address
        logging.info(f'User {user_address} is_admin: {is_admin}')
        return is_admin

    def is_contract_change_price_admin(self):
        controller_contract, network = get_controller_contract()

        user_address = network.w3.toChecksumAddress(self.owner_address)
        can_change_price = controller_contract.functions.canSetPrice(user_address).call()
        logging.info(f'User {user_address} can change price: {can_change_price}')
        return can_change_price

    def is_contract_change_payment_addresses_admin(self):
        controller_contract, network = get_controller_contract()

        user_address = network.w3.toChecksumAddress(self.owner_address)
        can_change_payment_addresses = controller_contract.functions.canSetFeeReceiver(user_address).call()
        logging.info(f'User {user_address} can change payment addresses: {can_change_payment_addresses}')
        return can_change_payment_addresses

    def get_role_system_permissions(self):
        contract_super_admin = self.is_contract_super_admin()
        contract_change_price = self.is_contract_change_price_admin()
        contract_change_payment_addresses = self.is_contract_change_payment_addresses_admin()
        # Enable/disable mainnet toggle
        can_change_network_mode = self.has_perm('contracts.edit_networkmode')

        # View user database
        can_view_profiles = self.has_perm('accounts.view_profile')
        # Freeze users
        # Contact users

        return {
            'contract_super_admin': contract_super_admin,
            'can_change_price': contract_change_price,
            'can_change_payment_addresses': contract_change_payment_addresses,
            'can_change_network_mode': can_change_network_mode,
            'can_view_users': can_view_profiles,
            'can_freeze_users': False,
            'can_contact_users': False,
        }
