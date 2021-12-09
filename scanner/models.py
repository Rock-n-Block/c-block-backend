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
    probatefabric_address = models.CharField(max_length=128, default='0x0a980179dd1aAa0eEaC71787C4Bdf5a362F0877d')

    def __str__(self):
        return f'{self.name}'


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
    address_list = ArrayField(models.CharField(max_length=128, blank=True), size=5, null=True)
    name = models.CharField(max_length=128, help_text='Contract name')
    contract_type = models.CharField(max_length=1, blank=False, help_text='0 or 1')
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=False,
                                  related_name='token_owner', related_query_name='tokens_owner')
    test_noda = models.BooleanField(null=True, help_text='Testnet or mainnet', blank=True)


class CrowdsaleContract(models.Model):
    """
    Token and crowdsale contracts
    """
    address = models.CharField(max_length=64, unique=True, blank=False, help_text='Contract address')
    name = models.CharField(max_length=128, help_text='Contract name')
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=False,
                                  related_name='crowdsale_owner', related_query_name='crowdsales_owner')
    test_noda = models.BooleanField(null=True, help_text='Testnet or mainnet', blank=True)


class WeddingContract(models.Model):
    """
    Wedding contract
    """
    address = models.CharField(max_length=64, unique=True, blank=False, help_text='Contract address')
    name = models.CharField(max_length=128, help_text='Contract name')
    mail_list = ArrayField(models.CharField(max_length=64, blank=True), size=2)
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=False,
                              related_name='wedding_owner', related_query_name='weddings_owner')
    test_noda = models.BooleanField(null=True, help_text='Testnet or mainnet', blank=True)


class ProbateContract(models.Model):
    """
    Probate contracts
    """
    address = models.CharField(max_length=64, unique=True, blank=False, help_text='Contract address')
    name = models.CharField(max_length=64, blank=True, help_text='Contract name')
    mails_array = ArrayField(models.EmailField(blank=True), null=True, blank=True, size=4, help_text='List heirs mails')
    dead = models.BooleanField(blank=False, default=False, help_text='Wallet status dead or alive')
    identifier = models.CharField(max_length=128, blank=False,
                                  help_text='ID for identification contract from event and user')
    owner = models.OneToOneField(Profile, on_delete=models.CASCADE, blank=True,
                                 related_name='probate_owner', related_query_name='probates_owner')
    owner_mail = models.EmailField(blank=True)
    test_noda = models.BooleanField(null=True, help_text='Testnet or mainnet', blank=True)

    def change_dead_status(self) -> None:
        self.dead = True
        self.save()

