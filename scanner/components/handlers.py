from copy import deepcopy

from scanner.components.base import HandlerABC
from cblock.contracts.models import (
    CrowdsaleContract,
    TokenContract,
    WeddingContract,
    LastWillContract,
    LostKeyContract,
    CONTRACT_MODELS
)
from cblock.contracts.utils import send_wedding_mail


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
                'test_node': self.network.test
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
                'test_node': self.network.test
            })


class HandlerNewContractWedding(HandlerABC):
    TYPE = "new_contract_wedding"

    def save_event(self, event_data):
        data = self.scanner.parse_data_new_contract_wedding(event_data)
        self.logger.info(f"New event: {data}")

        owner_first_profile = self.get_owner(data.owner_first)
        owner_second_profile = self.get_owner(data.owner_second)
        self.logger.info(f'Owners addresses: {owner_first_profile.owner_address}, {owner_second_profile.owner_address}')

        wedding_contract, _ = WeddingContract.objects.update_or_create(
            tx_hash=data.tx_hash,
            defaults={
                'address': data.contract_address,
                'test_node': self.network.test
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

        LastWillContract.objects.update_or_create(
            tx_hash=data.tx_hash,
            defaults={
                'address': data.contract_address,
                'owner': owner_profile,
                'test_node': self.network.test,
            })


class HandlerNewContractLostkey(HandlerABC):
    TYPE = "new_contract_lostkey"

    def save_event(self, event_data):
        data = self.scanner.parse_data_new_contract_lostkey(event_data)
        self.logger.info(f"New event: {data}")

        owner_profile = self.get_owner(data.sender)
        self.logger.info(f'Owner address: {owner_profile.owner_address}')

        LostKeyContract.objects.update_or_create(
            tx_hash=data.tx_hash,
            defaults={
                'address': data.contract_address,
                'owner': owner_profile,
                'test_node': self.network.test,
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

        wedding_model = CONTRACT_MODELS.get('wedding')

        contract_filter = wedding_model.objects.filter(address=data.contract_address.lower())
        if contract_filter:
            contract_instance = contract_filter.get()
        else:
            self.logger.info(f'No contract found with address {data.contract_address.lower()}')
            return

        send_wedding_mail(contract=contract_instance, handler_type=self.TYPE)


class HandlerWeddingDivorceProposed(HandlerABC):
    TYPE = "wedding_divorce_proposed"

    def save_event(self, event_data):
        data = self.scanner.parse_data_wedding_divorce_proposed(event_data)
        self.logger.info(f"New event: {data}")

        wedding_model = CONTRACT_MODELS.get('wedding')

        contract_filter = wedding_model.objects.filter(address=data.contract_address.lower())
        if contract_filter:
            contract_instance = contract_filter.get()
        else:
            self.logger.info(f'No contract found with address {data.contract_address.lower()}')
            return

        send_wedding_mail(contract=contract_instance, handler_type=self.TYPE, event_data=event_data)

