from web3 import Web3

from cblock.contracts.models import CONTRACT_MODELS, WeddingContract
from cblock.settings import config
from contract_abi import PROBATE_ABI

from django.core.mail import send_mail


def send_heirs_finished(owner_mail: str, heirs_mail_list: list) -> None:
    if not heirs_mail_list or len(heirs_mail_list) == 0:
        return

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
    if not contract.mails or len(contract.mails) == 0:
        return

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
    for network in config.networks:
        network_contracts = probates.filter(test_node=network.test)

        for probate in network_contracts:
            contract = network.w3.eth.contract(
                address=network.w3.toChecksumAddress(probate.address),
                abi=PROBATE_ABI
            )
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
