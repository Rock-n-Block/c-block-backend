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
    address = models.CharField(max_length=64, unique=True, blank=False, help_text='Contract address')
    address_list = ArrayField(models.CharField(max_length=128, blank=True), size=5, null=True)
    name = models.CharField(max_length=128, help_text='Contract name')
    contract_type = models.CharField(max_length=1, blank=False, help_text='0 or 1')
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=False,
                                  related_name='token_owner', related_query_name='tokens_owner')
    test_node = models.BooleanField(null=True, help_text='Testnet or mainnet', blank=True)
    tx_hash = models.CharField(max_length=128, unique=True, help_text='Hash transaction')


class CrowdsaleContract(models.Model):
    """
    Token and crowdsale contracts
    """
    address = models.CharField(max_length=64, unique=True, blank=False, help_text='Contract address')
    name = models.CharField(max_length=128, help_text='Contract name')
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=False,
                                  related_name='crowdsale_owner', related_query_name='crowdsales_owner')
    test_node = models.BooleanField(null=True, help_text='Testnet or mainnet', blank=True)
    tx_hash = models.CharField(max_length=128, unique=True, help_text='Hash transaction')


class WeddingContract(models.Model):
    """
    Wedding contract
    """
    address = models.CharField(max_length=64, unique=True, blank=False, help_text='Contract address')
    name = models.CharField(max_length=128, help_text='Contract name')
    mail_list = ArrayField(models.CharField(max_length=64, blank=True), size=2)
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=False,
                              related_name='wedding_owner', related_query_name='weddings_owner')
    test_node = models.BooleanField(null=True, help_text='Testnet or mainnet', blank=True)
    tx_hash = models.CharField(max_length=128, unique=True, help_text='Hash transaction')


class ProbateContract(models.Model):
    """
    Probate contracts
    """
    address = models.CharField(max_length=64, unique=True, blank=False, help_text='Contract address')
    name = models.CharField(max_length=64, blank=True, help_text='Contract name')
    mails_array = ArrayField(models.EmailField(blank=True), null=True, blank=True, size=4, help_text='List heirs mails')
    dead = models.BooleanField(blank=False, default=False, help_text='Wallet status dead or alive')
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE, blank=True,
                                 related_name='probate_owner', related_query_name='probates_owner')
    terminated = models.BooleanField(default=False, help_text='Terminated contract or not')
    owner_mail = models.EmailField(blank=True)
    test_node = models.BooleanField(null=True, help_text='Testnet or mainnet', blank=True)
    tx_hash = models.CharField(max_length=128, unique=True, help_text='Hash transaction')

    def change_dead_status(self) -> None:
        self.dead = True
        self.save()

    def change_terminated(self) -> None:
        self.terminated = True
        self.save()

