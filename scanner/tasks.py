from logging import Logger
from typing import Optional, Tuple, Any, List

from celery import shared_task
from web3 import Web3

import logging

from django.utils import timezone

from scanner.utils import send_heirs_finished, send_owner_reminder
from scanner.contracts import PROBATE_FABRIC_ABI
from scanner.models import LastWillContract, LostKeyContract


def initalize_checks(node: str, test: bool) -> Optional[Tuple[Logger, List[Any], Web3]]:
    logger = logging.getLogger('tasks')
    # Platform do not support test probate contracts
    alive_lastwills = LastWillContract.objects.filter(dead=False, test_node=test).exclude(owner_mail=None, mails=None)
    alive_lostkeys = LostKeyContract.objects.filter(dead=False, test_node=test).exclude(owner_mail=None, mails=None)
    alive_contracts = list(alive_lastwills) + list(alive_lostkeys)

    w3 = Web3(Web3.HTTPProvider(node))

    return logger, alive_contracts, w3


@shared_task
def check_dead_wallets(node: str, test: bool) -> None:
    """
    Take all the contracts of users with the status dead=False in node
    and turn to the contract method to find out if the status has changed
    :return: None
    """
    logger, alive_contracts, w3 = initalize_checks(node=node, test=test)

    if len(alive_contracts) == 0:
        logger.info('DEAD WALLETS: No alive contracts to process')
        return

    for alive_contract in alive_contracts:
        # Get contract method for check wallet status
        contract = w3.eth.contract(address=w3.toChecksumAddress(alive_contract.address), abi=PROBATE_FABRIC_ABI)

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


@shared_task()
def check_and_send_notifications(node: str, test: bool, day_seconds: int, checkpoints: list) -> None:
    logger, alive_contracts, w3 = initalize_checks(node=node, test=test)

    if len(alive_contracts) == 0:
        logger.info('NOTIFICATIONS: No alive contracts to process')
        return

    for alive_contract in alive_contracts:
        contract = w3.eth.contract(address=w3.toChecksumAddress(alive_contract.address), abi=PROBATE_FABRIC_ABI)
        last_recorded_time = int(contract.functions.lastRecordedTime().call())
        deadline = last_recorded_time + alive_contract.confirmation_period
        current_time = timezone.now().timestamp()

        time_delta_days = int((deadline - current_time) / day_seconds)

        if time_delta_days in checkpoints:
            logger.info(f'NOTIFICATIONS: Send {time_delta_days}-day reminder to {alive_contract.owner_mail}'
                        f'(contract {alive_contract.address})')
            send_owner_reminder(alive_contract.owner_mail, time_delta_days)


