import logging
import dramatiq

from django.utils import timezone

from cblock.mails.services import send_heirs_notification, send_owner_reminder, send_wedding_mail
from contract_abi import PROBATE_ABI
from cblock.contracts.utils import get_web3, get_probates, get_weddings_pending_divorce

logger = logging.getLogger(__name__)


@dramatiq.actor(max_retries=0)
def check_alive_wallets(rpc_endpoint: str, test_network: bool) -> None:
    """
    Take all the contracts of users with the status dead=False in node
    and turn to the contract method to find out if the status has changed
    :return: None
    """
    alive_contracts = get_probates(dead=False, test_network=test_network)

    if len(alive_contracts) == 0:
        logger.info('DEAD WALLETS: No alive contracts to process')
        return

    w3 = get_web3(rpc_endpoint)

    for alive_contract in alive_contracts:
        contract = w3.eth.contract(address=w3.toChecksumAddress(alive_contract.address), abi=PROBATE_ABI)

        if contract.functions.isLostKey().call() and not contract.functions.terminated().call():
            mail_list = list(alive_contract.mails.values_list("email", flat=True))
            logger.info(f'DEAD WALLETS: Send alive notification to {alive_contract.owner_mail} '
                        f'and {mail_list} (contract {alive_contract.address})')
            alive_contract.change_dead_status()
            send_heirs_notification(alive_contract)


@dramatiq.actor(max_retries=0)
def check_and_send_notifications(
        rpc_endpoint: str,
        test_network: bool,
        day_seconds: int,
        confirmation_checkpoints: list
) -> None:
    alive_contracts = get_probates(dead=False, test_network=test_network)

    if len(alive_contracts) == 0:
        logger.info('NOTIFICATIONS: No alive contracts to process')
        return

    w3 = get_web3(rpc_endpoint)
    for alive_contract in alive_contracts:
        contract = w3.eth.contract(address=w3.toChecksumAddress(alive_contract.address), abi=PROBATE_ABI)
        last_recorded_timestamp = int(contract.functions.lastRecordedTime().call())
        contract_last_recorded_time = timezone.datetime.fromtimestamp(last_recorded_timestamp,
                                                                      tz=timezone.get_default_timezone()
                                                                      )
        if contract_last_recorded_time > alive_contract.last_recorded_time:
            alive_contract.sent_notification_mails = 0
            alive_contract.last_recorded_time = contract_last_recorded_time
            alive_contract.save()
            logger.info('NOTIFICATIONS: Alive status was previously confirmed')

        deadline = int(alive_contract.last_recorded_time.timestamp()) + alive_contract.confirmation_period
        current_time = timezone.now().timestamp()

        time_delta_days = int((deadline - current_time) / day_seconds)

        if time_delta_days in confirmation_checkpoints and \
                alive_contract.sent_notification_mails <= len(confirmation_checkpoints):

            logger.info(f'NOTIFICATIONS: Send {time_delta_days}-day reminder to {alive_contract.owner_mail} '
                        f'(contract {alive_contract.address})')
            alive_contract.sent_notification_mails += 1
            alive_contract.save()
            send_owner_reminder(alive_contract, time_delta_days)


@dramatiq.actor(max_retries=0)
def check_wedding_divorce_timed_out(
        rpc_endpoint: str,
        test_network: bool,
        day_seconds: int,
) -> None:
    pending_contracts = get_weddings_pending_divorce(test_network=test_network)

    if len(pending_contracts) == 0:
        logger.info('DIVORCE TIMEOUT CHECK: No pending contracts to process')
        return

    w3 = get_web3(rpc_endpoint)

    for pending_wedding in pending_contracts:
        divorce = pending_wedding.divorce.all().order_by('-proposed_at').first()
        deadline = divorce.proposed_at + timezone.timedelta(seconds=pending_wedding.decision_time_divorce)
        current_time = timezone.now()

        if current_time > deadline:
            send_wedding_mail(
                contract=pending_wedding,
                wedding_action=divorce,
                email_type='wedding_divorce_approved',
                day_seconds=day_seconds
            )
            divorce.change_status_approved()
