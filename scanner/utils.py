import json
import asyncio
import os
import sys

from websockets import connect
from eth_abi import decode_single

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mywish2.settings")
import django
django.setup()

from .models import TokenContract, Profile, ProbateContract
from mywish2.settings import config
from django.core.mail import send_mail
import logging
from asgiref.sync import sync_to_async


def create_token(decoded: list, profile: Profile, noda: list):
    return TokenContract.objects.update_or_create(
        address=decoded[0],
        contract_type=decoded[1],
        owner=profile,
        test_noda=noda[1])


def create_probate(decoded: list, profile: Profile, noda: list):
    return ProbateContract.objects.update_or_create(
        address=decoded[0],
        identifier=str(decoded[1]),
        dead=False,
        owner=profile,
        test_noda=noda[1])




async def get_event(contract: str, noda: list, w3, event: str, fabrics: dict) -> None:
    if noda[1]:
        logger = logging.getLogger('testnet_scanner')
    else:
        logger = logging.getLogger('mainnet_scanner')
    logger.info(f'Contract:{contract}')
    logger.info(f'Noda:{noda[0]}')
    async with connect(noda[0]) as ws:
        # Send request to Celo with event structure
        await ws.send(json.dumps({
            "id": 1, "method": "eth_subscribe", "params": ["logs", {
                "address": [contract],
                "topics": [w3.keccak(text=f"NewContract{event}").hex()]
            }]
        }))
        while True:
            try:
                message = await asyncio.wait_for(ws.recv(), timeout=10)
                # Decoded response with event
                decoded = list(decode_single(f'{event}',bytearray.fromhex(
                    json.loads(message)['params']['result']['data'][2:]
                )))
                logger.info(f'New Event {decoded}')
                decoded.append('0xemyon')
                try:
                    profile = await sync_to_async(Profile.objects.get, thread_sensitive=True)(
                        owner_address__iexact=decoded[2])
                except:
                    logger.warning('Profile not exists')
                    profile = await sync_to_async(Profile.objects.create, thread_sensitive=True)(
                        owner_address=decoded[2])
                logger.info(decoded)
                if contract in fabrics['probate']:
                    logger.info('test')
                    await sync_to_async(create_probate, thread_sensitive=True)(decoded, profile, noda)
                    logger.info('Probate note')
                if contract in fabrics['token']:
                    await sync_to_async(create_token, thread_sensitive=True)(decoded, profile, noda)
                    logger.info('Token saved')
            except Exception as e:
                if not w3.isConnected():
                    w3.WebSocketProvider(noda[0])
                else:
                    pass


def send_heirs_mail(owner_mail: str, heirs_mail_list: list) -> None:
    send_mail(
        'Owner is dead',
        'My apologise, but owner is fucking dead.\nSadness =-(',
        from_email=config.EMAIL_HOST,
        recipient_list=heirs_mail_list,
        fail_silently=True,
    )
    send_mail(
        'You are dead',
        'My apologise, but owner is fucking dead.\nSadness =-(',
        from_email=config.EMAIL_HOST,
        recipient_list=[owner_mail],
        fail_silently=True,
    )
