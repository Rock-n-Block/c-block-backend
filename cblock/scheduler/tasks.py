import logging
import dramatiq
from typing import Optional, Tuple, Any, List

from django.utils import timezone

from cblock.mails.services import send_heirs_notification, send_owner_reminder, send_probate_transferred
from contract_abi import PROBATE_ABI
from cblock.contracts.models import LastWillContract, LostKeyContract, WeddingContract
from cblock.contracts.utils import get_web3
from cblock import config

logger = logging.getLogger(__name__)


def get_probates(dead: bool, test_network: bool):

    alive_lastwills = LastWillContract.objects.filter(dead=dead, test_node=test_network)\
        .exclude(owner_mail=None, mails=None)
    alive_lostkeys = LostKeyContract.objects.filter(dead=dead, test_node=test_network)\
        .exclude(owner_mail=None, mails=None)
    alive_contracts = list(alive_lastwills) + list(alive_lostkeys)

    return alive_contracts


def get_active_wedding_contracts(test_network: bool):
    return list(WeddingContract.objects.filter(test_node=test_network))


@dramatiq.actor(max_retries=0)
def check_alive_wallets(rpc_endpoint: str, test_network: bool) -> None:
    """
    Take all the contracts of users with the status dead=False in node
    and turn to the contract method to find out if the status has changed
    :return: None
    """
    alive_contracts = get_probates(dead=False, test_network=test_network)
    w3 = get_web3(rpc_endpoint)

    if len(alive_contracts) == 0:
        logger.info('DEAD WALLETS: No alive contracts to process')
        return

    for alive_contract in alive_contracts:
        contract = w3.eth.contract(address=w3.toChecksumAddress(alive_contract.address), abi=PROBATE_ABI)

        if contract.functions.isLostKey().call() and not contract.functions.terminated().call():
            logger.info(f'DEAD WALLETS: Send death notification to {alive_contract.owner_mail} '
                        f'and {alive_contract.mails} (contract {alive_contract.address})')
            alive_contract.change_dead_status()
            send_heirs_notification(alive_contract)


@dramatiq.actor(max_retries=0)
def check_and_send_notifications(
        rpc_endpoint: str,
        test_network: bool,
        day_seconds: int,
        confirmation_checkpoints: list
) -> None:
    alive_contracts = get_probates(dead=False, test_network=test_network)
    w3 = get_web3(rpc_endpoint)

    if len(alive_contracts) == 0:
        logger.info('NOTIFICATIONS: No alive contracts to process')
        return

    for alive_contract in alive_contracts:
        contract = w3.eth.contract(address=w3.toChecksumAddress(alive_contract.address), abi=PROBATE_ABI)
        last_recorded_time = int(contract.functions.lastRecordedTime().call())

        deadline = last_recorded_time + alive_contract.confirmation_period
        current_time = timezone.now().timestamp()

        time_delta_days = int((deadline - current_time) / day_seconds)

        if time_delta_days in confirmation_checkpoints:
            logger.info(f'NOTIFICATIONS: Send {time_delta_days}-day reminder to {alive_contract.owner_mail} '
                        f'(contract {alive_contract.address})')
            send_owner_reminder(alive_contract, time_delta_days)


@dramatiq.actor(max_retries=0)
def check_dead_wallets(rpc_endpoint: str, test_network: bool) -> None:
    """
    Take all the contracts of users with the status dead=True in node
    and turn to the contract method to find out if the status has changed
    :return: None
    """
    dead_contracts = get_probates(dead=True, test_network=test_network)
    w3 = get_web3(rpc_endpoint)

    if len(dead_contracts) == 0:
        logger.info('DEAD WALLETS: No alive contracts to process')
        return

    for dead_contract in dead_contracts:
        contract = w3.eth.contract(address=w3.toChecksumAddress(dead_contract.address), abi=PROBATE_ABI)

        if contract.functions.isLostKey().call() and contract.functions.terminated().call():
            logger.info(f'DEAD WALLETS: Send death notification to {dead_contract.owner_mail} '
                        f'and {dead_contract.mails} (contract {dead_contract.address})')
            dead_contract.change_terminated_status()
            send_probate_transferred(dead_contract)
