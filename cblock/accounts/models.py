from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _

from phone_field import PhoneField
from django_countries.fields import CountryField

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

    name = models.CharField(max_length=128, blank=True, default=None)
    company = models.CharField(max_length=129, blank=True, default=None)
    phone_number = PhoneField(blank=True, default=None)
    country = CountryField(blank=True, default=None)
    city = models.CharField(max_length=128, blank=True, default=None)
    street = models.CharField(max_length=128, blank=True, default=None)
    office = models.CharField(max_length=32, blank=True, default=None)
    zipcode = models.IntegerField(blank=True, default=None)


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
