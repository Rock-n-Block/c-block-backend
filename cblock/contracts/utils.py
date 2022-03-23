from web3 import Web3
from typing import Any

from cblock.contracts.models import CONTRACT_MODELS, WeddingContract, LastWillContract, LostKeyContract
from cblock.contracts.mail_messages import EMAIL_TEXTS
from cblock.settings import config
from contract_abi import PROBATE_ABI

from django.core.mail import send_mail


def get_probate_text_type(contract: Any[LastWillContract, LostKeyContract]) -> str:
    if contract.__class__.__name__ == 'LastWillContract':
        text_type = 'lastwill'
    else:
        text_type = 'lostkey'

    return text_type


def send_heirs_finished(
        contract: Any[LastWillContract, LostKeyContract],
        owner_mail: str,
        heirs_mail_list: list
) -> None:
    if not heirs_mail_list or len(heirs_mail_list) == 0:
        return

    if not contract.owner:
        return

    text_type = get_probate_text_type(contract)
    message_texts = EMAIL_TEXTS.get(text_type).get('triggered')
    title = message_texts.get('title')
    body = message_texts.get('body').format(
        user_address=contract.owner.owner_address
    )

    heirs_mail_list.append(owner_mail)
    for mail in heirs_mail_list:
        send_mail(
            title,
            body,
            from_email=config.email_host_user,
            recipient_list=[mail],
            fail_silently=True,
        )


def send_owner_reminder(contract: Any[LastWillContract, LostKeyContract], owner_mail: str, days: int) -> None:

    text_type = get_probate_text_type(contract)
    message_texts = EMAIL_TEXTS.get(text_type).get('reminder')
    title = message_texts.get('title')
    body = message_texts.get('body').format(
        days=days
    )

    send_mail(
        title,
        body,
        from_email=config.email_host_user,
        recipient_list=[owner_mail],
        fail_silently=True,
    )


def send_wedding_mail(contract: WeddingContract, handler_type: str, event_data: Any) -> None:

    wedding_emails = EMAIL_TEXTS.get('wedding')

    if handler_type == 'wedding_withdrawal_proposed':
        from_partner_message = wedding_emails.get('divorce_from_partner')
        to_partner_message = wedding_emails.get('divorce_from_partner')




    elif handler_type == 'wedding_divorce_proposed':

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
