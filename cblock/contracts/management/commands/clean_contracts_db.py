from django.core.management.base import BaseCommand
from cblock.accounts.models import ControllerOwnershipTransferred
from cblock.contracts.models import (
TokenContract,
CrowdsaleContract,
WeddingContract,
LastWillContract,
LostKeyContract
)

class Command(BaseCommand):
    help = 'Drop contracts from db for testing'

    def add_arguments(self, parser):
        parser.add_argument('network', type=str, help='network to drop contracts (mainnet/testnet)')

    def handle(self, *args, **options):
        network = options['network']
        if network not in ['testnet', 'mainnet']:
            self.stdout.write(f'no network found: {network}')
        if network == 'testnet':
            is_testnet = True
        else:
            is_testnet = False

        for model in [
            TokenContract,
            CrowdsaleContract,
            WeddingContract,
            LastWillContract,
            LostKeyContract
        ]:
            res = model.objects.filter(is_testnet=is_testnet).delete()
            self.stdout.write(str(res))

        self.stdout.write(self.style.SUCCESS('cleanup completed'))

