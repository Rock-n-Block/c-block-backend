from celery import shared_task
from web3 import Web3

# from .contracts import PROBATE_CONTRACT
from scanner.utils import send_heirs_mail
from scanner.models import ProbateContract


@shared_task
def check_dead_wallets(noda, test) -> None:
    """
    Take all the contracts of users with the status dead=False in noda
    and turn to the contract method to find out if the status has changed
    :return: None
    """
    alive_probates = ProbateContract.objects.filter(dead=False, test_noda=test)
    if not alive_probates.exists():
        return
    w3 = Web3(Web3.HTTPProvider(noda))
    for probate in alive_probates:
        # Get contract method for check wallet status
        contract = w3.eth.contract(address=probate.address, abi=PROBATE_CONTRACT)
        if contract.functions.someMethod().call():
            send_heirs_mail(probate.owner_mail, probate.mails_array)
            probate.change_dead_status()
