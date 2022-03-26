from web3 import Web3
from typing import Any, List, Optional
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


def send_owner_reminder(contract, days: int) -> None:
    if not contract.owner or not contract.owner_mail:
        return

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
        recipient_list=[contract.owner_mail],
        fail_silently=True,
    )


def send_heirs_notification(contract) -> None:
    if contract.mails.count() == 0:
        return

    if not contract.owner or not contract.owner_mail:
        return

    text_type = get_probate_text_type(contract)
    message_texts = EMAIL_TEXTS.get(text_type).get('triggered')

    mails_to_send = []
    for mail_address in contract.mails.all():
        heir_mail = MailToSend(
            title=message_texts.get('title'),
            body=message_texts.get('body').format(
                owner_address=contract.owner.owner_address,
                receiver_address=mail_address.address
            ),
            recipients=[mail_address.email]
        )
        mails_to_send.append(heir_mail)

    for mail in mails_to_send:
        send_mail(
            mail.title,
            mail.body,
            from_email=config.email_host_user,
            recipient_list=mail.recipients,
            fail_silently=True,
        )


def send_probate_transferred(explorer_uri, contract, event_data) -> None:
    if contract.mails.count() == 0:
        return

    if not contract.owner or not contract.owner_mail:
        return

    mails_to_send = []
    text_type = get_probate_text_type(contract)
    to_owner_message = EMAIL_TEXTS.get(text_type).get('transferred_from_owner')

    to_owner_title = to_owner_message.get('title')
    to_owner_body = to_owner_message.get('body').format(
        backup_addresses=event_data.backup_addresses,
        link_tx=explorer_uri.format(link_tx=event_data.tx_hash)
    )

    mails_to_send.append(
        MailToSend(
            title=to_owner_title,
            body=to_owner_body,
            recipients=[contract.owner_mail]
        )
    )

    to_heirs_message = EMAIL_TEXTS.get(text_type).get('transferred_to_heirs')
    to_heirs_title = to_heirs_message.get('title')
    to_heirs_body = to_heirs_message.get('body')

    for mail_address in contract.mails.all():
        heir_mail = MailToSend(
            title=to_heirs_title,
            body=to_heirs_body.format(
                owner_address=contract.owner.owner_address,
                receiver_address=mail_address.address,
                link_tx=explorer_uri.format(link_tx=event_data.tx_hash)
            ),
            recipients=[mail_address.email]
        )
        mails_to_send.append(heir_mail)

    for mail in mails_to_send:
        send_mail(
            mail.title,
            mail.body,
            from_email=config.email_host_user,
            recipient_list=mail.recipients,
            fail_silently=True,
        )


def send_wedding_mail(
        contract: WeddingContract,
        wedding_action: Any,
        email_type: str,
        day_seconds: int,
        # explorer_uri: str
) -> None:

    if not contract.mails.all() or len(list(contract.mails.all())) != 2:
        logger.info(f'No mails found for wedding contract {WeddingContract.__dict__}, skipping for now')
        return

    divorce_decision_days = int(contract.decision_time_divorce / day_seconds) if contract.decision_time_divorce else 0

    wedding_emails = EMAIL_TEXTS.get('wedding')
    message_subtype = email_type.split('_', 1)[-1]

    mails_to_send = []

    if message_subtype == 'divorce_proposed':
        for partners_mail in contract.mails.all():
            other_partner = contract.mails.exclude(pk=partners_mail.pk).get()

            from_partner_message = wedding_emails.get('divorce_proposed_from_partner')
            to_partner_message = wedding_emails.get('divorce_proposed_to_partner')

            if wedding_action.proposed_by.owner_address == partners_mail.address.lower():
                message_title = from_partner_message.get('title')
                message_body = from_partner_message.get('body').format(
                    proposer_address=other_partner.address,
                    days=divorce_decision_days
                ),
            else:
                message_title = to_partner_message.get('title')
                message_body = to_partner_message.get('body').format(
                    proposer_address=other_partner.address,
                    days=divorce_decision_days
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
        to_partner_mail = contract.mails.exclude(address=wedding_action.proposed_by.owner_address).get()
        recipients = [to_partner_mail.email]

        message_text = wedding_emails.get(message_subtype)
        message_title = message_text.get('title')

        if message_subtype in ['divorce_approved', 'divorce_rejected']:
            message_body = message_text.get('body').format(
                not_proposer_address=to_partner_mail.address,
            )

        elif message_subtype in [
            'withdrawal_proposed',
            'withrawal_rejected',
            'withdrawal_approved'
        ]:
            message_body = message_text.get('body').format(
                user_address=wedding_action.receiver.owner_address,
                amount=wedding_action.token_amount,
                token_address=wedding_action.token,
            )
        else:
            logger.error(f'SEND WEDDING_MAIL: Cannot find specified message subtype: {message_subtype}')
            return

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