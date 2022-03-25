from django.contrib.postgres.fields import ArrayField
from django.db import models


class Profile(models.Model):
    """
    User profile
    """
    owner_address = models.CharField(max_length=64, unique=True, blank=False)


class TokenContract(models.Model):
    """
    Token and crowdsale contract_abi
    """
    address = models.CharField(max_length=64, unique=False, blank=True, null=True, help_text='Contract address')
    # addresses = ArrayField(models.CharField(max_length=128, blank=True), size=5, null=True)
    name = models.CharField(max_length=128, help_text='Contract name')
    contract_type = models.CharField(max_length=1, blank=False, help_text='0 or 1')
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=False,
                              related_name='token_owner', related_query_name='tokens_owner')
    test_node = models.BooleanField(null=True, help_text='Testnet or mainnet', blank=True)
    tx_hash = models.CharField(max_length=128, unique=True, help_text='Transaction hash')


class TokenHolder(models.Model):
    token_contract = models.ForeignKey(TokenContract, on_delete=models.CASCADE, null=True, default=None,
                                       related_name='addresses', related_query_name='token_contract')
    name = models.CharField(max_length=128, blank=False, help_text='Token holder name')
    address = models.CharField(max_length=64, unique=False, blank=False, help_text='Token holder address')


class CrowdsaleContract(models.Model):
    """
    Token and crowdsale contract_abi
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
    # mails = ArrayField(models.EmailField(blank=True), size=2, blank=True, null=True)
    owner = models.ManyToManyField(Profile)  # wedding contract have 2 owner
    test_node = models.BooleanField(null=True, help_text='Testnet or mainnet', blank=True)
    tx_hash = models.CharField(max_length=128, unique=True, help_text='Transaction hash')
    decision_time_withdrawal = models.IntegerField(null=True, blank=True)
    decision_time_divorce = models.IntegerField(null=True, blank=True)


class WeddingActionStatus(models.TextChoices):
    NOT_PROPOSED_YET = 'Not proposed yet'
    PROPOSED = 'Proposed'
    APPROVED = 'Approved'
    REJECTED = 'Rejected'


class WeddingAction(models.Model):
    proposed_at = models.DateTimeField(blank=True, null=True, default=None)
    status = models.CharField(
        max_length=30,
        choices=WeddingActionStatus.choices,
        default=WeddingActionStatus.NOT_PROPOSED_YET
    )

    class Meta:
        abstract = True


class WeddingDivorce(WeddingAction):
    wedding_contract = models.ForeignKey(WeddingContract, on_delete=models.CASCADE, null=True, default=None,
                                         related_name='divorce', related_query_name='wedding_divorce')
    proposed_by = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=False,
                                    related_name='divorce_proposer', related_query_name='wedding_divorce_proposer')

    # def get_other_partner(self):
    #     parners = self.wedding_contract.owner


class WeddingWithdrawal(WeddingAction):
    wedding_contract = models.ForeignKey(WeddingContract, on_delete=models.CASCADE, null=True, default=None,
                                         related_name='withdraw', related_query_name='wedding_withdraw')
    receiver = models.CharField(max_length=64, unique=False, blank=False, help_text='Token address')
    token_address = models.CharField(max_length=64, unique=False, blank=False, help_text='Token address')
    token_amount = models.DecimalField(max_digits=100, decimal_places=0, null=True, default=None)
    proposed_by = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=False,
                                    related_name='withdraw_proposer', related_query_name='wedding_withdraw_proposer')
    # token_name = models.CharField(max_length=64, unique=False, blank=False, help_text='Token address')


class ProbateContract(models.Model):
    """
    Probate contract_abi
    """
    address = models.CharField(max_length=64, unique=False, blank=True, null=True, help_text='Contract address')
    name = models.CharField(max_length=64, blank=True, help_text='Contract name')
    # mails = ArrayField(models.EmailField(blank=True), null=True, blank=True, size=4, help_text='List heirs mails')
    dead = models.BooleanField(blank=False, default=False, help_text='Wallet status dead or alive')
    terminated = models.BooleanField(default=False, help_text='Terminated contract or not')
    owner_mail = models.EmailField(blank=True)
    test_node = models.BooleanField(null=True, help_text='Testnet or mainnet', blank=True)
    tx_hash = models.CharField(max_length=128, unique=True, help_text='Transaction hash')
    confirmation_period = models.IntegerField(null=True, blank=True)

    class Meta:
        abstract = True

    def change_dead_status(self) -> None:
        self.dead = True
        self.save()

    def change_terminated(self) -> None:
        self.terminated = True
        self.save()


class LastWillContract(ProbateContract):
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE, blank=True, null=True,
                              related_name='lastwill_owner', related_query_name='lastwills_owner')


class LostKeyContract(ProbateContract):
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE, blank=True, null=True,
                              related_name='lostkey_owner', related_query_name='lostkeys_owner')


class EmailAddressLinkAbstract(models.Model):
    email = models.EmailField(blank=True, help_text='Email')
    address = models.CharField(max_length=64, unique=False, blank=False, help_text='address')

    class Meta:
        abstract = True


class LastWillEmail(EmailAddressLinkAbstract):
    probate_contract = models.ForeignKey(LastWillContract, on_delete=models.CASCADE, null=True, default=None,
                                         related_name='mails', related_query_name='contract_mails')


class LostKeyEmail(EmailAddressLinkAbstract):
    probate_contract = models.ForeignKey(LostKeyContract, on_delete=models.CASCADE, null=True, default=None,
                                         related_name='mails', related_query_name='contract_mails')


class WeddingEmail(EmailAddressLinkAbstract):
    wedding_contract = models.ForeignKey(WeddingContract, on_delete=models.CASCADE, null=True, default=None,
                                         related_name='mails', related_query_name='contract_mails')


CONTRACT_MODELS = {
    'token': TokenContract,
    'crowdsale': CrowdsaleContract,
    'lastwill': LastWillContract,
    'lostkey': LostKeyContract,
    'wedding': WeddingContract
}