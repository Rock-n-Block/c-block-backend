from celery import shared_task
from web3 import Web3

import logging

from scanner.utils import send_heirs_mail
from scanner.contracts import PROBATE_FABRIC_ABI
from scanner.models import ProbateContract


@shared_task
def check_dead_wallets(node: str, test: bool) -> None:
    """
    Take all the contracts of users with the status dead=False in node
    and turn to the contract method to find out if the status has changed
    :return: None
    """
    logger = logging.getLogger('tasks')
    alive_probates = ProbateContract.objects.filter(dead=False, test_node=test)
    if not alive_probates.exists():
        logger.info('Alive probate contract not exists')
        return
    w3 = Web3(Web3.HTTPProvider(node))
    for probate in alive_probates:
        # Get contract method for check wallet status
        contract = w3.eth.contract(address=w3.toChecksumAddress(probate.address), abi=PROBATE_FABRIC_ABI)
        if contract.functions.isLostKey().call() and not contract.functions.terminated().call():
            logger.info('Send mails and change status')
            probate.change_dead_status()
            send_heirs_mail(probate.owner_mail, probate.mails_array)

