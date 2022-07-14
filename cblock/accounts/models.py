import logging

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _

from cblock.accounts.managers import MetamaskUserManager
from cblock.accounts.utils import get_controller_contract

class Profile(AbstractUser):
    """
    User profile
    """
    username = None
    email = models.EmailField(_('email address'), unique=True)


    freezed = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = MetamaskUserManager()

    owner_address = models.CharField(max_length=64, unique=True, blank=False)

    class Meta:
        unique_together = (("email", "owner_address"),)

    def __str__(self):
        return f'{self.email} - {self.owner_address}'

    def set_owner_adress(self, owner_address):
        self.owner_address = owner_address
        self.save()

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