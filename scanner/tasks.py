from celery import shared_task
from web3 import Web3

import logging

from scanner.utils import send_heirs_mail
from scanner.contracts import PROBATE_FABRIC_ABI
from scanner.models import LastWillContract, LostKeyContract


@shared_task
def check_dead_wallets(node: str, test: bool) -> None:
    """
    Take all the contracts of users with the status dead=False in node
    and turn to the contract method to find out if the status has changed
    :return: None
    """
    logger = logging.getLogger('tasks')
    # Platform do not support test probate contracts
    alive_lastwills = list(LastWillContract.objects.filter(dead=False, test_node=test))
    alive_lostkeys = list(LostKeyContract.objects.filter(dead=False, test_node=test))
    alive_contracts = alive_lastwills + alive_lostkeys

    if len(alive_contracts) == 0:
        logger.info('Alive probate contract not exists')
        return
    w3 = Web3(Web3.HTTPProvider(node))
    for alive_contract in alive_contracts:
        # Get contract method for check wallet status
        contract = w3.eth.contract(address=w3.toChecksumAddress(alive_contract.address), abi=PROBATE_FABRIC_ABI)
        if contract.functions.isLostKey().call() and not contract.functions.terminated().call():
            logger.info('Send mails and change status')
            alive_contract.change_dead_status()
            send_heirs_mail(alive_contract.owner_mail, alive_contract.mails_list)
