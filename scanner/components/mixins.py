from web3._utils.filters import construct_event_filter_params
from web3._utils.events import get_event_data
from typing import List
from cblock.contracts.utils import get_contract_addresses

from contract_abi import (
    CROWDSALE_FACTORY_ABI,
    TOKEN_FACTORY_ABI,
    WEDDING_FACTORY_ABI,
    PROBATE_FACTORY_ABI,
    PROBATE_ABI,
    WEDDING_ABI,
    OWNABLE_ABI
)
from scanner.components.datatypes import (
    NewContractToken,
    NewContractCrowdsale,
    NewContractWedding,
    NewContractLastWill,
    NewContractLostKey,
    WeddingWithdrawalProposed,
    WeddingDivorceProposed,
    TransferOwnership
)


class EventMixinBase:
    def _get_events_base(self, contract_abi, event_name, from_block, to_block):
        argument_filters = {'address': self.contracts}
        contract = self.network.w3.eth.contract(abi=contract_abi)
        event = getattr(contract.events, event_name)
        event_abi = event._get_event_abi()

        data_filter_set, event_filter_params = construct_event_filter_params(
            event_abi,
            self.network.w3.codec,
            address=argument_filters.get("address"),
            argument_filters=argument_filters,
            fromBlock=from_block,
            toBlock=to_block
        )

        logs = self.network.w3.eth.getLogs(event_filter_params)
        all_events = []
        for log in logs:
            event = get_event_data(self.network.w3.codec, event_abi, log)
            all_events.append(event)
        return all_events

    def _parse_data_get_sender(self, event):
        tx_hash = event["transactionHash"].hex()
        return self.network.w3.eth.waitForTransactionReceipt(tx_hash, timeout=4)['from'].lower()


class NewContractMixinBase(EventMixinBase):
    def _get_events_new_contract(self, contract_abi, from_block, to_block):
        return self._get_events_base(
            contract_abi=contract_abi,
            event_name="NewContract",
            from_block=from_block,
            to_block=to_block
        )

    def _parse_data_get_owner(self, event):
        contract_address = event['args']['contractAddress'].lower()
        contract = self.network.w3.eth.contract(
            address=self.network.w3.toChecksumAddress(contract_address),
            abi=OWNABLE_ABI
        )
        return contract.functions.owner().call().lower()


class NewContractTokenMixin(NewContractMixinBase):
    def get_events_new_contract_token(self, last_checked_block, last_network_block):
        return self._get_events_new_contract(
            contract_abi=TOKEN_FACTORY_ABI,
            from_block=last_checked_block,
            to_block=last_network_block
        )

    def parse_data_new_contract_token(self, event) -> NewContractToken:
        return NewContractToken(
            tx_hash=event["transactionHash"].hex(),
            sender=self._parse_data_get_sender(event),
            contract_address=event['args']['contractAddress'].lower(),
            contract_type=event['args']['contractType'],
            owner=self._parse_data_get_owner(event)
        )


class NewContractCrowdsaleMixin(NewContractMixinBase):
    def get_events_new_contract_crowdsale(self, last_checked_block, last_network_block):
        return self._get_events_new_contract(
            contract_abi=CROWDSALE_FACTORY_ABI,
            from_block=last_checked_block,
            to_block=last_network_block
        )

    def parse_data_new_contract_crowdsale(self, event) -> NewContractCrowdsale:
        return NewContractCrowdsale(
            tx_hash=event["transactionHash"].hex(),
            sender=self._parse_data_get_sender(event),
            contract_address=event['args']['contractAddress'].lower(),
            contract_type=event['args']['contractType'],
            owner=self._parse_data_get_owner(event)
        )


class NewContractWeddingMixin(NewContractMixinBase):
    def get_events_new_contract_wedding(self, last_checked_block, last_network_block):
        return self._get_events_new_contract(
            contract_abi=WEDDING_FACTORY_ABI,
            from_block=last_checked_block,
            to_block=last_network_block
        )

    def _parse_data_get_decision_times(self, event):
        contract_address = event['args']['contractAddress'].lower()
        contract = self.network.w3.eth.contract(
            address=self.network.w3.toChecksumAddress(contract_address),
            abi=WEDDING_ABI
        )

        return {
            'withdrawal': int(contract.functions.decisionTimeWithdrawal().call()),
            'divorce': int(contract.functions.decisionTimeDivorce().call()),
        }

    def parse_data_new_contract_wedding(self, event) -> NewContractWedding:
        decision_times = self._parse_data_get_decision_times(event)
        return NewContractWedding(
            tx_hash=event["transactionHash"].hex(),
            sender=self._parse_data_get_sender(event),
            contract_address=event['args']['contractAddress'].lower(),
            owner_first=event['args']['firstPartner'].lower(),
            owner_second=event['args']['secondPartner'].lower(),
            decision_time_withdrawal=decision_times.get('withdrawal'),
            decision_time_divorce=decision_times.get('divorce')
        )


class NewContractProbateMixinBasae(NewContractMixinBase):
    def _parse_data_get_confirmation_period(self, event):
        contract_address = event['args']['contractAddress'].lower()
        contract = self.network.w3.eth.contract(
            address=self.network.w3.toChecksumAddress(contract_address),
            abi=PROBATE_ABI
        )

        return int(contract.functions.CONFIRMATION_PERIOD().call())


class NewContractLastwillMixin(NewContractProbateMixinBasae):
    def get_events_new_contract_lastwill(self, last_checked_block, last_network_block):
        return self._get_events_new_contract(
            contract_abi=PROBATE_FACTORY_ABI,
            from_block=last_checked_block,
            to_block=last_network_block
        )

    def parse_data_new_contract_lastwill(self, event) -> NewContractLastWill:
        return NewContractLastWill(
            tx_hash=event["transactionHash"].hex(),
            sender=self._parse_data_get_sender(event),
            contract_address=event['args']['contractAddress'].lower(),
            confirmation_period=self._parse_data_get_confirmation_period(event)
        )


class NewContractLostkeyMixin(NewContractProbateMixinBasae):
    def get_events_new_contract_lostkey(self, last_checked_block, last_network_block):
        return self._get_events_new_contract(
            contract_abi=PROBATE_FACTORY_ABI,
            from_block=last_checked_block,
            to_block=last_network_block
        )

    def parse_data_new_contract_lostkey(self, event) -> NewContractLostKey:
        return NewContractLostKey(
            tx_hash=event["transactionHash"].hex(),
            sender=self._parse_data_get_sender(event),
            contract_address=event['args']['contractAddress'].lower(),
            confirmation_period=self._parse_data_get_confirmation_period(event)
        )


class TransferOwnershipMixin(EventMixinBase):
    def get_events_transfer_ownership(self, last_checked_block, last_network_block):
        return self._get_events_base(
            contract_abi=PROBATE_ABI,
            event_name="OwnershipTransferred",
            from_block=last_checked_block,
            to_block=last_network_block
        )

    def parse_data_transfer_ownership(self, event) -> TransferOwnership:
        return TransferOwnership(
            tx_hash=event["transactionHash"].hex(),
            sender=self._parse_data_get_sender(event),
            contract_address=event['address'].lower(),
            previous_owner=event['args']['previousOwner'].lower(),
            new_owner=event['args']['newOwner'].lower()
        )

    def preload_contracts_transfer_ownership(self, network) -> List[str]:
        contract_addresses = get_contract_addresses(network.test)
        if 'wedding' in contract_addresses.keys():
            contract_addresses.pop('wedding')

        ownership_addresses = []
        for address_list in contract_addresses.values():
            ownership_addresses += address_list

        return ownership_addresses


class WeddingEventdMixinBase(EventMixinBase):
    def _get_events_wedding(self, event_name, last_checked_block, last_network_block):
        return self._get_events_base(
            contract_abi=WEDDING_ABI,
            event_name=event_name,
            from_block=last_checked_block,
            to_block=last_network_block
        )

    def preload_contracts_wedding(self, network) -> List[str]:
        contract_addresses = get_contract_addresses(network.test)
        wedding_addresses = []
        if 'wedding' in contract_addresses.keys():
            wedding_addresses = contract_addresses.pop('wedding')

        return wedding_addresses


class WeddingWithdrawalProposedMixin(WeddingEventdMixinBase):
    def get_events_wedding_withdrawal_proposed(self, last_checked_block, last_network_block):
        return self._get_events_wedding(
            event_name="WithdrawalProposed",
            last_checked_block=last_checked_block,
            last_network_block=last_network_block
        )

    def parse_data_wedding_withdrawal_proposed(self, event) -> WeddingWithdrawalProposed:
        return WeddingWithdrawalProposed(
            tx_hash=event["transactionHash"].hex(),
            sender=self._parse_data_get_sender(event),
            contract_address=event['address'].lower(),
            token=event['args']['token'].lower(),
            receiver=event['args']['receiver'].lower(),
            token_amount=event['args']['amount'],
            proposed_by=event['args']['proposedBy'].lower()
        )

    def preload_contracts_wedding_withdrawal_proposed(self, network) -> List[str]:
        return self.preload_contracts_wedding(network=network)


class WeddingDivorceProposedMixin(WeddingEventdMixinBase):
    def get_events_wedding_divorce_proposed(self, last_checked_block, last_network_block):
        return self._get_events_wedding(
            event_name="DivorceProposed",
            last_checked_block=last_checked_block,
            last_network_block=last_network_block
        )

    def parse_data_wedding_divorce_proposed(self, event) -> WeddingDivorceProposed:
        return WeddingDivorceProposed(
            tx_hash=event["transactionHash"].hex(),
            sender=self._parse_data_get_sender(event),
            contract_address=event['address'].lower(),
            proposed_by=event['args']['proposedBy'].lower()
        )

    def preload_contracts_wedding_divorce_proposed(self, network) -> List[str]:
        return self.preload_contracts_wedding(network=network)


