from web3 import Web3
from typing import Any, List
from dataclasses import dataclass

from cblock.config import config
from cblock.contracts.models import WeddingContract, LastWillContract, LostKeyContract, Profile
from cblock.mails.mail_messages import EMAIL_TEXTS
from cblock.settings import config

from django.core.mail import send_mail

import logging

logger = logging.getLogger(__name__)


@dataclass
class MailToSend:
    title: str
    body: str
    recipients: List[str]


def get_probate_text_type(contract: object) -> str:
    if contract.__class__.__name__ == 'LastWillContract':
        text_type = 'lastwill'
    else:
        text_type = 'lostkey'

    return text_type


def send_heirs_finished(contract) -> None:
    if not contract.mails or len(contract.mails) == 0:
        return

    if not contract.owner:
        return

    text_type = get_probate_text_type(contract)
    message_texts = EMAIL_TEXTS.get(text_type).get('triggered')
    title = message_texts.get('title')
    body = message_texts.get('body').format(
        user_address=contract.owner.owner_address
    )
    recipients = [mail for mail in contract.mails]
    recipients.append(contract.owner_mail)

    send_mail(
        title,
        body,
        from_email=config.email_host_user,
        recipient_list=recipients,
        fail_silently=True,
    )


def send_owner_reminder(contract, owner_mail: str, days: int) -> None:

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


def send_wedding_mail(
        contract: WeddingContract,
        email_type: str,
        proposed_by: Profile,
        mail_data: Any
) -> None:

    if not contract.mails.all() or len(list(contract.mails.all())) != 2:
        logger.info(f'No mails found for wedding contract {WeddingContract.__dict__}, skipping for now')
        return

    wedding_emails = EMAIL_TEXTS.get('wedding')

    mails_to_send = []

    if email_type == 'wedding_divorce_proposed':
        from_partner_message = wedding_emails.get('divorce_proposed_from_partner')
        to_partner_message = wedding_emails.get('divorce_proposed_to_partner')

        for partners_mail in contract.mails.all():
            other_partner = contract.mails.exclude(pk=partners_mail.pk).get()

            if proposed_by.owner_address == partners_mail.address:
                message_title = from_partner_message.get('title')
                message_body = from_partner_message.get('body').format(
                    user_address=other_partner.address,
                    days=1
                ),
            else:
                message_title = to_partner_message.get('title')
                message_body = to_partner_message.get('body').format(
                    user_address=other_partner.address,
                    days=1
                )

            recipients = [partners_mail.email]

            mails_to_send.append(
                MailToSend(
                    title=message_title,
                    body=message_body,
                    recipients=recipients
                )
            )

    else:
        to_partner_mail = contract.mails.exclude(address=proposed_by.owner_address).get()
        recipients = [to_partner_mail.email]

        message_title = None
        message_body = None

        if email_type == 'wedding_divorce_completed':
            message_text = wedding_emails.get('divorce_completed')
            message_title = message_text.get('title')
            message_body = message_text.get('body').format(
                user_address=mail_data.receiver,
                amount=mail_data.token_amount,
                token_address=mail_data.token,
                days=1
            )

        elif email_type == 'wedding_withdrawal_proposed':
            message_text = wedding_emails.get('withdraw_proposed')
            message_title = message_text.get('title')
            message_body = message_text.get('body').format(
                user_address=mail_data.receiver,
                amount=mail_data.token_amount,
                token_address=mail_data.token,
                days=1
            )

        mails_to_send.append(
            MailToSend(
                title=message_title,
                body=message_body,
                recipients=recipients
            )
        )

    for mail in mails_to_send:
        send_mail(
            mail.title,
            mail.body,
            recipient_list=mail.recipients,
            from_email=config.email_host_user,
            fail_silently=True
        )