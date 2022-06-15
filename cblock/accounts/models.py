from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _

from cblock.accounts.managers import MetamaskUserManager


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

    class Meta:
        unique_together = (("email", "owner_address"),)

    def __str__(self):
        return f'{self.email} - {self.owner_address}'

    def set_owner_adress(self, owner_address):
        self.owner_address = owner_address
        self.save()
