import json
import asyncio
import logging

from websockets import connect
from eth_abi import decode_single

from .models import TokenContract, Profile, ProbateContract
from mywish2.settings import config
from django.core.mail import send_mail
from asgiref.sync import sync_to_async


def create_token(decoded: list, profile: Profile, test: bool):
    return TokenContract.objects.update_or_create(
        address=decoded[0],
        contract_type=decoded[1],
        owner=profile,
        test_node=test)


def create_probate(decoded: list, profile: Profile, test: bool):
    return ProbateContract.objects.update_or_create(
        address=decoded[0],
        identifier=str(decoded[1]),
        dead=False,
        owner=profile,
        test_node=test)




async def get_event(contract: str, node: str, test: bool, w3, event: str, event_type: str) -> None:
    """

    :param contract: contract address
    :param node: node url
    :param test: test or mainnet node
    :param w3: w3 instance
    :param event: event and event params
    :param event_type: type contract
    :return: None or exception
    """
    logger = logging.getLogger(f'{node}_scanner')
    logger.info(f'Node:{node}\nContract:{contract}')
    async with connect(node) as ws:
        # Send request to Celo with event structure
        await ws.send(json.dumps(
            {
                "id": 1,
                "method": "eth_subscribe",
                "params": [
                    "logs", {
                        "address": [contract],
                        "topics": [w3.keccak(text=f"NewContract{event}").hex()]
                    }
                ]
            })
        )
        while True:
            try:
                message = await asyncio.wait_for(ws.recv(), timeout=10)

                # Decoded response with event
                data = json.loads(message)['params']['result']['data'][2:]
                decoded = list(decode_single(f'{event}', bytearray.fromhex(data)))
                logger.info(f'New Event {decoded}')
                decoded.append('0xsssemyon') # Only for test
                profile, create = await sync_to_async(Profile.objects.get_or_create, thread_sensitive=True)(
                    owner_address__iexact=decoded[2])
                logger.info(decoded)
                if event_type == 'probate':
                    await sync_to_async(create_probate, thread_sensitive=True)(decoded, profile, test)
                    logger.info('Probate note')
                if event_type == 'token':
                    await sync_to_async(create_token, thread_sensitive=True)(decoded, profile, test)
                    logger.info('Token saved')
            except:
                # Celo disconnect sometimes and we need reconnect
                if not w3.isConnected():
                    w3.WebSocketProvider(node)
                else:
                    pass


def send_heirs_mail(owner_mail: str, heirs_mail_list: list) -> None:
    [send_mail(
        'Owner is dead',
        'My apologise, but owner is fucking dead.\nSadness =-(',
        from_email=config.email_host_user,
        recipient_list=[mail],
        fail_silently=True,
    ) for mail in heirs_mail_list]
    send_mail(
        'You are dead',
        'My apologise, but owner is fucking dead.\nSadness =-(',
        from_email=config.email_host_user,
        recipient_list=[owner_mail],
        fail_silently=True,
    )
