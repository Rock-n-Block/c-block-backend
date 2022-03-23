import logging
import dramatiq
from typing import Optional, Tuple, Any, List
from web3 import Web3

from django.utils import timezone

from cblock.contracts.utils import send_heirs_finished, send_owner_reminder
from contract_abi import PROBATE_ABI
from cblock.contracts.models import LastWillContract, LostKeyContract
from cblock import config

logger = logging.getLogger(__name__)


def initalize_checks(rpc_endpoint: str, test_network: bool) -> Optional[Tuple[List[Any], Web3]]:
    # Platform do not support test probate contract_abi
    alive_lastwills = LastWillContract.objects.filter(dead=False, test_node=test_network)\
        .exclude(owner_mail=None, mails=None)
    alive_lostkeys = LostKeyContract.objects.filter(dead=False, test_node=test_network)\
        .exclude(owner_mail=None, mails=None)
    alive_contracts = list(alive_lastwills) + list(alive_lostkeys)

    w3 = Web3(Web3.HTTPProvider(rpc_endpoint))

    return alive_contracts, w3


@dramatiq.actor(max_retries=0)
def check_dead_wallets(rpc_endpoint: str, test_network: bool) -> None:
    """
    Take all the contract_abi of users with the status dead=False in node
    and turn to the contract method to find out if the status has changed
    :return: None
    """
    alive_contracts, w3 = initalize_checks(rpc_endpoint=rpc_endpoint, test_network=test_network)

    if len(alive_contracts) == 0:
        logger.info('DEAD WALLETS: No alive contract_abi to process')
        return

    for alive_contract in alive_contracts:
        # Get contract method for check wallet status
        contract = w3.eth.contract(address=w3.toChecksumAddress(alive_contract.address), abi=PROBATE_ABI)

        if not alive_contract.confirmation_period:
            alive_contract.confirmation_period = int(contract.functions.CONFIRMATION_PERIOD().call())
            alive_contract.save()
            logger.info(f'DEAD WALLETS: Set confirmation period of contract {alive_contract.address} '
                        f'to {alive_contract.confirmation_period} seconds')

        if contract.functions.isLostKey().call() and not contract.functions.terminated().call():
            logger.info(f'DEAD WALLETS: Send death notification to {alive_contract.owner_mail} '
                        f'and {alive_contract.mails} (contract {alive_contract.address})')
            alive_contract.change_dead_status()
            send_heirs_finished(alive_contract.owner_mail, alive_contract.mails)


@dramatiq.actor(max_retries=0)
def check_and_send_notifications(
        rpc_endpoint: str,
        test_network: bool,
        day_seconds: int,
        confirmation_checkpoints: list
) -> None:
    alive_contracts, w3 = initalize_checks(rpc_endpoint=rpc_endpoint, test_network=test_network)

    if len(alive_contracts) == 0:
        logger.info('NOTIFICATIONS: No alive contracts to process')
        return

    for alive_contract in alive_contracts:
        contract = w3.eth.contract(address=w3.toChecksumAddress(alive_contract.address), abi=PROBATE_ABI)
        last_recorded_time = int(contract.functions.lastRecordedTime().call())

        if not alive_contract.confirmation_period:
            alive_contract.confirmation_period = int(contract.functions.CONFIRMATION_PERIOD().call())
            alive_contract.save()
            logger.info(f'NOTIFICATIONS: Set confirmation period of contract {alive_contract.address} '
                        f'to {alive_contract.confirmation_period} seconds')

        deadline = last_recorded_time + alive_contract.confirmation_period
        current_time = timezone.now().timestamp()

        time_delta_days = int((deadline - current_time) / day_seconds)

        if time_delta_days in confirmation_checkpoints:
            logger.info(f'NOTIFICATIONS: Send {time_delta_days}-day reminder to {alive_contract.owner_mail} '
                        f'(contract {alive_contract.address})')
            send_owner_reminder(alive_contract, alive_contract.owner_mail, time_delta_days)

