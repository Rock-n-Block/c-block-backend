from copy import deepcopy
from django.utils import timezone

from scanner.components.base import HandlerABC
from cblock.contracts.models import (
    CrowdsaleContract,
    TokenContract,
    WeddingContract,
    WeddingWithdrawal,
    WeddingDivorce,
    WeddingActionStatus,
    LastWillContract,
    LostKeyContract,
    CONTRACT_MODELS
)
from cblock.mails.services import send_wedding_mail, send_probate_transferred


class HandlerNewContractCrowdsale(HandlerABC):
    TYPE = "new_contract_crowdsale"

    def save_event(self, event_data):
        data = self.scanner.parse_data_new_contract_crowdsale(event_data)
        self.logger.info(f"New event: {data}")

        owner_profile = self.get_owner(data.owner)
        self.logger.info(f'Owner address: {owner_profile.owner_address}')

        CrowdsaleContract.objects.update_or_create(
            tx_hash=data.tx_hash,
            defaults={
                'address': data.contract_address,
                'owner': owner_profile,
                'is_testnet': self.network.is_testnet
            })


class HandlerNewContractToken(HandlerABC):
    TYPE = "new_contract_token"

    def save_event(self, event_data):
        data = self.scanner.parse_data_new_contract_token(event_data)
        self.logger.info(f"New event: {data}")

        owner_profile = self.get_owner(data.owner)
        self.logger.info(f'Owner address: {owner_profile.owner_address}')

        TokenContract.objects.update_or_create(
            tx_hash=data.tx_hash,
            defaults={
                'address': data.contract_address,
                'owner': owner_profile,
                'is_testnet': self.network.is_testnet
            })


class HandlerNewContractWedding(HandlerABC):
    TYPE = "new_contract_wedding"

    def save_event(self, event_data):
        data = self.scanner.parse_data_new_contract_wedding(event_data)
        self.logger.info(f"New event: {data}")

        owner_first_profile = self.get_owner(data.owner_first)
        owner_second_profile = self.get_owner(data.owner_second)
        self.logger.info(f'Owners addresses: {owner_first_profile.owner_address}, {owner_second_profile.owner_address}')

        self.logger.info(f'Wedding decision times will be set, '
                         f'withdrawal: {data.decision_time_withdrawal}, '
                         f'divorce: {data.decision_time_divorce}'
                         )

        wedding_contract, _ = WeddingContract.objects.update_or_create(
            tx_hash=data.tx_hash,
            defaults={
                'address': data.contract_address,
                'is_testnet': self.network.is_testnet,
                'decision_time_withdrawal': data.decision_time_withdrawal,
                'decision_time_divorce': data.decision_time_divorce
            })
        wedding_contract.owner.add(owner_first_profile)
        wedding_contract.owner.add(owner_second_profile)
        wedding_contract.save()


class HandlerNewContractLastwill(HandlerABC):
    TYPE = "new_contract_lastwill"

    def save_event(self, event_data):
        data = self.scanner.parse_data_new_contract_lastwill(event_data)
        self.logger.info(f"New event: {data}")

        owner_profile = self.get_owner(data.sender)
        self.logger.info(f'Owner address: {owner_profile.owner_address}')

        self.logger.info(f"LastWill confirmation period will be set: {data.confirmation_period}")
        LastWillContract.objects.update_or_create(
            tx_hash=data.tx_hash,
            defaults={
                'address': data.contract_address,
                'owner': owner_profile,
                'is_testnet': self.network.is_testnet,
                'confirmation_period': data.confirmation_period
            })


class HandlerNewContractLostkey(HandlerABC):
    TYPE = "new_contract_lostkey"

    def save_event(self, event_data):
        data = self.scanner.parse_data_new_contract_lostkey(event_data)
        self.logger.info(f"New event: {data}")

        owner_profile = self.get_owner(data.sender)
        self.logger.info(f'Owner address: {owner_profile.owner_address}')

        self.logger.info(f"LostKey confirmation period will be set: {data.confirmation_period}")
        LostKeyContract.objects.update_or_create(
            tx_hash=data.tx_hash,
            defaults={
                'address': data.contract_address,
                'owner': owner_profile,
                'is_testnet': self.network.is_testnet,
                'confirmation_period': data.confirmation_period
            })


class HandlerTransferOwnership(HandlerABC):
    TYPE = "transfer_ownership"

    def save_event(self, event_data):
        data = self.scanner.parse_data_transfer_ownership(event_data)
        self.logger.info(f"New event: {data}")

        ownable_models = deepcopy(CONTRACT_MODELS)
        if 'wedding' in ownable_models.keys():
            ownable_models.pop('wedding')

        contract_instance = None
        for model in ownable_models.values():
            contract = model.objects.filter(address=data.contract_address.lower())
            if contract:
                contract_instance = contract.get()
                break

        if not contract_instance:
            self.logger.info(f'No contract found with address {data.contract_address}')
            return

        self.logger.info(f'Changing owner {data.previous_owner} -> {data.new_owner} (contract {data.contract_address})')
        new_owner_profile = self.get_owner(data.new_owner)
        self.logger.info(f'New Owner address: {new_owner_profile.owner_address}')

        contract_instance.owner = new_owner_profile
        contract_instance.save()


class HandlerWeddingWithdrawalProposed(HandlerABC):
    TYPE = "wedding_withdrawal_proposed"

    def save_event(self, event_data):
        data = self.scanner.parse_data_wedding_withdrawal_proposed(event_data)
        self.logger.info(f"New event: {data}")

        contract_filter = WeddingContract.objects.filter(address=data.contract_address.lower())
        if contract_filter:
            contract_instance = contract_filter.get()
        else:
            self.logger.info(f'No contract found with address {data.contract_address.lower()}')
            return

        proposer = self.get_owner(data.proposed_by)

        withdrawal, created = WeddingWithdrawal.objects.update_or_create(
            wedding_contract=contract_instance,
            tx_hash=data.tx_hash,
            defaults={
                'status': WeddingActionStatus.PROPOSED,
                'proposed_at': timezone.datetime.fromtimestamp(data.proposed_at, tz=timezone.get_default_timezone()),
                'proposed_by': proposer,
                'receiver': self.get_owner(data.receiver),
                'token_address': data.token.lower(),
                'token_amount': int(data.token_amount)

            })
        if created:
            send_wedding_mail(
                contract=contract_instance,
                wedding_action=withdrawal,
                email_type=self.TYPE,
                day_seconds=self.network.day_seconds
            )


class HandlerWeddingWithdrawalStatusChanged(HandlerABC):
    TYPE = "wedding_withdrawal_status_changed"

    def save_event(self, event_data):
        data = self.scanner.parse_data_wedding_withdrawal_status_changed(event_data)
        self.logger.info(f"New event: {data}")

        contract_filter = WeddingContract.objects.filter(address=data.contract_address.lower())
        if contract_filter:
            contract_instance = contract_filter.get()
        else:
            self.logger.info(f'No contract found with address {data.contract_address.lower()}')
            return

        withdrawal = contract_instance.withdraw.filter(
            status=WeddingActionStatus.PROPOSED
        ).order_by('-proposed_at').first()

        if not withdrawal:
            self.logger.info(f'No withdrawal found on contract address {data.contract_address.lower()}')
            return

        if withdrawal.status_change_tx_hash or withdrawal.status in [
            WeddingActionStatus.APPROVED,
            WeddingActionStatus.REJECTED
        ]:
            self.logger.info(f'Already processed tx {withdrawal.status_change_tx_hash}')
            return

        if data.agreed:
            withdrawal.change_status_approved()
            email_type = 'wedding_withdrawal_approved'
        else:
            withdrawal.change_status_rejected()
            email_type = 'wedding_withdrawal_rejected'

        withdrawal.status_change_tx_hash = data.tx_hash
        withdrawal.save()

        send_wedding_mail(
            contract=contract_instance,
            wedding_action=withdrawal,
            email_type=email_type,
            day_seconds=self.network.day_seconds
        )


class HandlerWeddingDivorceProposed(HandlerABC):
    TYPE = "wedding_divorce_proposed"

    def save_event(self, event_data):
        data = self.scanner.parse_data_wedding_divorce_proposed(event_data)
        self.logger.info(f"New event: {data}")

        contract_filter = WeddingContract.objects.filter(address=data.contract_address.lower())
        if contract_filter:
            contract_instance = contract_filter.get()
        else:
            self.logger.info(f'No contract found with address {data.contract_address.lower()}')
            return

        proposer = self.get_owner(data.proposed_by)

        divorce, created = WeddingDivorce.objects.update_or_create(
            wedding_contract=contract_instance,
            tx_hash=data.tx_hash,
            defaults={
                'status': WeddingActionStatus.PROPOSED,
                'proposed_at': timezone.datetime.fromtimestamp(data.proposed_at, tz=timezone.get_default_timezone()),
                'proposed_by': proposer,
            })

        if created:
            send_wedding_mail(
                contract=contract_instance,
                wedding_action=divorce,
                email_type=self.TYPE,
                day_seconds=self.network.day_seconds,
            )


class HandlerWeddingDivorceStatusChanged(HandlerABC):
    TYPE = "wedding_divorce_status_changed"

    def save_event(self, event_data):
        data = self.scanner.parse_data_wedding_divorce_status_changed(event_data)
        self.logger.info(f"New event: {data}")

        contract_filter = WeddingContract.objects.filter(address=data.contract_address.lower())
        if contract_filter:
            contract_instance = contract_filter.get()
        else:
            self.logger.info(f'No contract found with address {data.contract_address.lower()}')
            return

        divorce = contract_instance.divorce.filter(
            status=WeddingActionStatus.PROPOSED
        ).order_by('-proposed_at').first()

        if not divorce:
            self.logger.info(f'No divorce model found {contract_instance.address}')
            return

        if divorce.status_change_tx_hash or divorce.status in [
            WeddingActionStatus.APPROVED,
            WeddingActionStatus.REJECTED
        ]:
            self.logger.info(f'Already processed tx {divorce.status_change_tx_hash}')
            return

        if data.agreed:
            divorce.change_status_approved()
            email_type = 'wedding_divorce_approved'
        else:
            divorce.change_status_rejected()
            email_type = 'wedding_divorce_rejected'

        divorce.status_change_tx_hash = data.tx_hash
        divorce.save()

        send_wedding_mail(
            contract=contract_instance,
            wedding_action=divorce,
            email_type=email_type,
            day_seconds=self.network.day_seconds
        )


class HandlerProbateFundsDistributed(HandlerABC):
    TYPE = "probate_funds_distributed"

    def save_event(self, event_data):
        data = self.scanner.parse_data_probate_funds_distributed(event_data)
        self.logger.info(f"New event: {data}")

        contract_instance = None
        for model in [LastWillContract, LostKeyContract]:
            contract = model.objects.filter(address=data.contract_address.lower())
            if contract:
                contract_instance = contract.get()
                break

        if not contract_instance:
            self.logger.info(f'No contract found with address {data.contract_address}')
            return

        if contract_instance.distribution_tx_hash:
            self.logger.info(f'Already processed funds distribution {contract_instance.distribution_tx_hash}')
            return

        self.logger.info(f'Funds are distributed on contract {data.contract_address}) to {data.backup_addresses}')

        contract_instance.change_terminated()
        contract_instance.distribution_tx_hash = data.tx_hash
        contract_instance.save()
        send_probate_transferred(self.network.explorer_tx_uri, contract_instance, data)
