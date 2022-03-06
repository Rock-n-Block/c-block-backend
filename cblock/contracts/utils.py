from web3 import Web3

from cblock.contracts.models import CONTRACT_MODELS, WeddingContract
from cblock.settings import config
from contract_abi import PROBATE_FACTORY_ABI

from django.core.mail import send_mail


def send_heirs_finished(owner_mail: str, heirs_mail_list: list) -> None:
    for mail in heirs_mail_list:
        send_mail(
            'Owner is dead',
            'My apologise, but owner is dead.\nSadness =-(',
            from_email=config.email_host_user,
            recipient_list=[mail],
            fail_silently=True,
        )
    send_mail(
        'You are dead',
        'My apologise, but owner is dead.\nSadness =-(',
        from_email=config.email_host_user,
        recipient_list=[owner_mail],
        fail_silently=True,
    )


def send_owner_reminder(owner_mail: str, days: int) -> None:
    send_mail(
        'Contract notification',
        f'Your contract confirmation period will be ended in {days} days',
        from_email=config.email_host_user,
        recipient_list=[owner_mail],
        fail_silently=True,
    )


def send_wedding_mail(contract: WeddingContract, title: str, body: str) -> None:
    for mail in contract.mails:
        send_mail(
            title,
            body,
            from_email=config.email_host_user,
            recipient_list=[mail],
            fail_silently=True,
        )


def check_terminated_contract(probates):
    """
    Check that contract is not terminated and change status if terminated
    """
    w3 = config.network.w3
    for probate in probates:
        contract = w3.eth.contract(address=w3.toChecksumAddress(probate.address), abi=PROBATE_FACTORY_ABI)
        terminated = contract.functions.terminated().call()
        probate.terminated = terminated
        probate.save()
    return probates.filter(terminated=False)


def get_contract_addresses(test) -> dict:
    contract_addresses = {}
    for key, model in CONTRACT_MODELS.items():
        addresses = model.objects.filter(test_node=test).values_list('address', flat=True)
        contract_addresses[key] = [Web3.toChecksumAddress(address) for address in addresses]

    return contract_addresses
