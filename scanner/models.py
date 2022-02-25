from django.contrib.postgres.fields import ArrayField
from django.db import models


class Profile(models.Model):
    """
    User profile
    """
    owner_address = models.CharField(max_length=64, unique=True, blank=False)


class TokenContract(models.Model):
    """
    Token and crowdsale contracts
    """
    address = models.CharField(max_length=64, unique=False, blank=True, null=True, help_text='Contract address')
    addresses = ArrayField(models.CharField(max_length=128, blank=True), size=5, null=True)
    name = models.CharField(max_length=128, help_text='Contract name')
    contract_type = models.CharField(max_length=1, blank=False, help_text='0 or 1')
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=False,
                              related_name='token_owner', related_query_name='tokens_owner')
    test_node = models.BooleanField(null=True, help_text='Testnet or mainnet', blank=True)
    tx_hash = models.CharField(max_length=128, unique=True, help_text='Transaction hash')


class CrowdsaleContract(models.Model):
    """
    Token and crowdsale contracts
    """
    address = models.CharField(max_length=64, unique=False, blank=True, null=True, help_text='Contract address')
    name = models.CharField(max_length=128, help_text='Contract name')
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=False,
                              related_name='crowdsale_owner', related_query_name='crowdsales_owner')
    test_node = models.BooleanField(null=True, help_text='Testnet or mainnet', blank=True)
    tx_hash = models.CharField(max_length=128, unique=True, help_text='Transaction hash')


class WeddingContract(models.Model):
    """
    Wedding contract
    """
    address = models.CharField(max_length=64, unique=False, blank=True, null=True, help_text='Contract address')
    name = models.CharField(max_length=128, help_text='Contract name', blank=True)
    mails = ArrayField(models.EmailField(blank=True), size=2, blank=True, null=True)
    owner = models.ManyToManyField(Profile)  # wedding contract have 2 owner
    test_node = models.BooleanField(null=True, help_text='Testnet or mainnet', blank=True)
    tx_hash = models.CharField(max_length=128, unique=True, help_text='Transaction hash')


class ProbateContract(models.Model):
    """
    Probate contracts
    """
    address = models.CharField(max_length=64, unique=False, blank=True, null=True, help_text='Contract address')
    name = models.CharField(max_length=64, blank=True, help_text='Contract name')
    mails = ArrayField(models.EmailField(blank=True), null=True, blank=True, size=4, help_text='List heirs mails')
    dead = models.BooleanField(blank=False, default=False, help_text='Wallet status dead or alive')
    terminated = models.BooleanField(default=False, help_text='Terminated contract or not')
    owner_mail = models.EmailField(blank=True)
    test_node = models.BooleanField(null=True, help_text='Testnet or mainnet', blank=True)
    tx_hash = models.CharField(max_length=128, unique=True, help_text='Transaction hash')

    class Meta:
        abstract = True


class LastWillContract(ProbateContract):
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE, blank=True, null=True,
                              related_name='lastwill_owner', related_query_name='lastwills_owner')


class LostKeyContract(ProbateContract):
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE, blank=True, null=True,
                              related_name='lostkey_owner', related_query_name='lostkeys_owner')
