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
    logger.info(f'Owner reminder ({text_type}) mail sent (contract: {contract.address}, mail to: {contract.owner_mail}')


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
    logger.info(f'Heirs notification ({text_type}) mail sent (contract: {contract.address})')


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
        link_tx=explorer_uri.format(tx_hash=contract.distribution_tx_hash)
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
                link_tx=explorer_uri.format(tx_hash=event_data.tx_hash)
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
    logger.info(f'Funds distribution ({text_type}) mail sent (contract: {contract.address})')


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

    withdrawal_decision_days = int(contract.decision_time_withdrawal / day_seconds) if contract.decision_time_withdrawal else 0
    divorce_decision_days = int(contract.decision_time_divorce / day_seconds) if contract.decision_time_divorce else 0

    wedding_emails = EMAIL_TEXTS.get('wedding')
    message_subtype = email_type.split('_', 1)[-1]

    mails_to_send = []

    if message_subtype == 'divorce_proposed':
        for partners_mail in contract.mails.all():
            other_partner = contract.mails.exclude(pk=partners_mail.pk).get()

            proposer_message = wedding_emails.get('divorce_proposed_from_partner')
            executor_message = wedding_emails.get('divorce_proposed_to_partner')

            if wedding_action.proposed_by.owner_address == partners_mail.address.lower():
                message_title = proposer_message.get('title')
                message_body = proposer_message.get('body').format(
                    proposer_address=other_partner.address,
                    days=divorce_decision_days
                )
            else:
                message_title = executor_message.get('title')
                message_body = executor_message.get('body').format(
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
        proposer_mail = contract.mails.get(address=wedding_action.proposed_by.owner_address)
        executor_mail = contract.mails.exclude(address=wedding_action.proposed_by.owner_address).get()

        message_text = wedding_emails.get(message_subtype)
        message_title = message_text.get('title')

        if message_subtype in ['divorce_approved', 'divorce_rejected']:
            message_body = message_text.get('body').format(
                executor_address=executor_mail.address,
            )
            recipients = [proposer_mail.email]

        elif message_subtype in [
            'withdrawal_proposed',
            'withdrawal_rejected',
            'withdrawal_approved'
        ]:
            message_kwargs = {
                'amount': wedding_action.token_amount,
                'token_address': wedding_action.token_address,
            }

            if message_subtype == 'withdrawal_proposed':
                message_kwargs['proposer_address'] = wedding_action.proposed_by.owner_address
                message_kwargs['days'] = withdrawal_decision_days
                recipients = [executor_mail.email]
            else:
                message_kwargs['executor_address'] = executor_mail.address,
                recipients = [proposer_mail.email]

            message_body = message_text.get('body').format(**message_kwargs)
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
    logger.info(f'Wedding mail ({message_subtype}) swnt (contract: {contract.address}')
