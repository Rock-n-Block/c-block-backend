import json
import asyncio
from typing import Callable
from websockets import connect
from eth_abi import decode_single

from .models import TokenContract, Profile, ProbateContract, WeddingContract, CrowdsaleContract
from mywish2.settings import config
from .contracts import PROBATE_FABRIC_ABI

from django.core.mail import send_mail
from asgiref.sync import sync_to_async


class EventScanner:
    def __init__(self, node: str, test: bool, w3, logger, loop) -> None:
        super().__init__()
        self.node = node
        self.test = test
        self.w3 = w3
        self.logger = logger
        self.loop = loop

    def create_token(self, decoded: list, tx_hash: str) -> None:
        owner_address = self.w3.eth.waitForTransactionReceipt(tx_hash, timeout=4)['from']
        self.logger.info(f'Owner address: {owner_address}')
        profile, _ = Profile.objects.get_or_create(
            owner_address=owner_address)
        TokenContract.objects.update_or_create(
            tx_hash=tx_hash,
            defaults={
                'address': decoded[0],
                'contract_type': decoded[1],
                'owner': profile,
                'test_node': self.test,
            })
        self.logger.info('New token contract saved')

    def create_probate(self, decoded: list, tx_hash: str) -> None:
        owner_address = self.w3.eth.waitForTransactionReceipt(tx_hash, timeout=4)['from']
        self.logger.info(f'Owner address: {owner_address}')
        profile, _ = Profile.objects.get_or_create(
            owner_address=owner_address)
        ProbateContract.objects.update_or_create(
            tx_hash=tx_hash,
            defaults={
                'address': decoded[0],
                'dead': False,
                'owner': profile,
                'test_node': self.test
            })
        self.logger.info('New probate contract saved')

    def create_wedding(self, decoded: list, tx_hash: str, ) -> None:
        profile_one, _ = Profile.objects.get_or_create(owner_address=self.w3.toChecksumAddress(decoded[1]))
        profile_two, _ = Profile.objects.get_or_create(owner_address=self.w3.toChecksumAddress(decoded[2]))
        self.logger.info('New wedding contract saved')
        wedding_contract, _ = WeddingContract.objects.update_or_create(
            tx_hash=tx_hash,
            defaults={
                'address': decoded[0],
                'test_node': self.test,
            })
        wedding_contract.owner.add(profile_one)
        wedding_contract.owner.add(profile_two)
        wedding_contract.save()
        tasks = list()
        tasks.append(self.get_event(
            decoded[0], ['DivorceProposed', '(address)'],
            self.send_wedding_mail
        ))

        tasks.append(self.get_event(
            decoded[0], ['WithdrawalProposed', '(address,address,uint256,address)'],
            self.send_wedding_mail
        ))
        self.loop.create_task(asyncio.wait(tasks))
        self.logger.info('Add new address for check in scanner')

    def create_crowdsale(self, decoded: list, tx_hash: str) -> None:
        owner_address = self.w3.eth.waitForTransactionReceipt(tx_hash, timeout=4)['from']
        self.logger.info(f'Owner address: {owner_address}')
        profile, _ = Profile.objects.get_or_create(
            owner_address=owner_address)
        CrowdsaleContract.objects.update_or_create(
            tx_hash=tx_hash,
            defaults={
                'address': decoded[0],
                'owner': profile,
                'test_node': self.test
            })
        self.logger.info('New crowdsale contract saved')

    def send_wedding_mail(self, decoded: list, tx_hash: str) -> None:
        address = dict(self.w3.eth.get_transaction(tx_hash))['to']  # Get contract address
        self.logger.info(f'Contract address: {address}')
        wedding = WeddingContract.objects.get(address__iexact=address)
        title = 'divorce'
        body = f'Sorry {decoded[0]}, but we need divorce, because u r whore!'
        if len(decoded) > 1:
            title = 'withdraw'
            body = f'{decoded[1]} want withdraw {decoded[2]} tokens'
        for mail in wedding.mails:
            send_mail(
                title,
                body,
                from_email=config.email_host_user,
                recipient_list=[mail],
                fail_silently=True,
            )

    async def get_event(self, contract: str, event: list, handler: Callable) -> None:
        """
        Catch contract events and call view for create objects
        :param contract: contract address
        :param event: event and event params
        :param handler: handler function
        :return: None
        """
        self.logger.info(f'Node:{self.node}\nContract:{contract}')
        async with connect(self.node) as ws:
            # Send request to Celo with event structure
            await ws.send(json.dumps(
                {
                    "id": 1,
                    "method": "eth_subscribe",
                    "params": [
                        "logs", {
                            "address": [contract],
                            "topics": [self.w3.keccak(text=f"{event[0] + event[1]}").hex()]
                        }
                    ]
                })
            )
            while True:
                try:
                    message = await asyncio.wait_for(ws.recv(), timeout=40)

                    # Decoded response with event
                    data = json.loads(message)['params']['result']['data'][2:]
                    tx_hash = json.loads(message)['params']['result']['transactionHash']
                    decoded = list(decode_single(f'{event[1]}', bytearray.fromhex(data)))
                    self.logger.info(f'Catch new Event {decoded}\nHash: {tx_hash}')

                    await sync_to_async(handler, thread_sensitive=True)(decoded=decoded, tx_hash=tx_hash)
                    self.logger.info('Event processed')
                except:
                    # Celo disconnect sometimes and we need reconnect
                    if not self.w3.isConnected():
                        self.logger.warning('Connection reset')
                        return self.w3.WebSocketProvider(self.node)
                    pass


def send_heirs_mail(owner_mail: str, heirs_mail_list: list) -> None:
    for mail in heirs_mail_list:
        send_mail(
            'Owner is dead',
            'My apologise, but owner is fucking dead.\nSadness =-(',
            from_email=config.email_host_user,
            recipient_list=[mail],
            fail_silently=True,
        )
    send_mail(
        'You are dead',
        'My apologise, but owner is fucking dead.\nSadness =-(',
        from_email=config.email_host_user,
        recipient_list=[owner_mail],
        fail_silently=True,
    )


def check_terminated_contract(probates):
    """
    Check that contract is not terminated and change status if terminated
    """
    w3 = config.network.w3
    for probate in probates:
        contract = w3.eth.contract(address=w3.toChecksumAddress(probate.address), abi=PROBATE_FABRIC_ABI)
        terminated = contract.functions.terminated().call()
        probate.terminated = terminated
        probate.save()
    return probates.filter(terminated=False)
