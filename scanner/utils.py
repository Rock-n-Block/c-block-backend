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

from .models import TokenContract, Profile
from django.core.mail import send_mail
import logging


async def get_event(contract, noda, w3) -> None:
    if noda[1]:
        logger = logging.getLogger('testnet_scanner')
    else:
        logger = logging.getLogger('mainnet_scanner')
    logger.info(f'Contract:{contract}')
    logger.info(f'Noda:{noda[0]}')
    async with connect(noda[0]) as ws:
        # Send request to Celo with event structure
        await ws.send(json.dumps({"id": 1, "method": "eth_subscribe", "params": ["logs", {
                    "address": [contract],
                    "topics": [w3.keccak(text="NewContract(address,uint8,address)").hex()]}]}))
        while True:
            try:
                message = await asyncio.wait_for(ws.recv(), timeout=60)
                # Decoded response with event
                decoded = list(decode_single('(address,uint8,address)',bytearray.fromhex(json.loads(message)['params']['result']['data'][2:])))
                logger.info(f'New Event {decoded}')
                profile = Profile.objects.filter(owner_address__iexact=decoded[2]).first()
                if not profile.exists():
                    logger.warning('profile not exists')
                    profile = Profile.objects.create(owner_address=decoded[2])
                if not TokenContract.objects.filter(address__iexact=decoded[0]):
                    # Save new events history
                    TokenContract.objects.create(
                        address=decoded[0],
                        contract_type=decoded[1],
                        contracts=profile,
                        test_noda=noda[1]
                    )
                    logger.info('New history note')
                pass
            except:
                pass


def send_heirs_mail(owner_mail, heirs_mail_list) -> None:
    send_mail(
        'Owner is dead',
        'My apologise, but owner is fucking dead.\nSadness =-(',
        heirs_mail_list,
        fail_silently=True,
    )
    send_mail(
        'You are dead',
        'My apologise, but owner is fucking dead.\nSadness =-(',
        owner_mail,
        fail_silently=True,
    )
