from django.contrib.postgres.fields import ArrayField
from django.db import models


class Network(models.Model):
    """
    Fabrics list
    """
    name = models.CharField(max_length=100)
    erc20nmnffabric_address = models.CharField(max_length=128)
    erc20nmffabric_address = models.CharField(max_length=128)
    erc20mnffabric_address = models.CharField(max_length=128)
    erc20mffabric_address = models.CharField(max_length=128)

    def __str__(self):
        return self.name


class Profile(models.Model):
    """
    User profile
    """
    owner_address = models.CharField(max_length=64, unique=True, blank=False)


class TokenContract(models.Model):
    """
    Token and crowdsale contracts
    """
    address = models.CharField(max_length=64, unique=True, blank=False, help_text='Contract address')
    contract_type = models.CharField(max_length=1, blank=False, help_text='0 or 1')
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True,
                                  related_name='token_owner', related_query_name='tokens_owner')
    test_noda = models.BooleanField(null=False, help_text='Testnet or mainnet')


class ProbateContract(models.Model):
    """
    Probate contracts
    """
    address = models.CharField(max_length=64, unique=True, blank=False, help_text='Contract address')
    mails_array = ArrayField(models.EmailField(), size=4, help_text='List heirs mails')
    dead = models.BooleanField(default=False, help_text='Wallet status dead or alive')
    identifier = models.CharField(max_length=128, blank=False,
                                  help_text='ID for identification contract from event and user')
    owner = models.OneToOneField(Profile, on_delete=models.CASCADE, blank=True,
                                 related_name='probate_owner', related_query_name='probates_owner')
    owner_mail = models.EmailField(blank=False)
    test_noda = models.BooleanField(null=False, help_text='Testnet or mainnet')

    def change_dead_status(self):
        self.dead = True
        self.save()

