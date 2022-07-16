from django.core.management.base import BaseCommand

from scanner.components.redis import RedisClient

class Command(BaseCommand):
    help = 'Rollback scanner to specific block number'

    def add_arguments(self, parser):
        parser.add_argument('filter', type=str, help='pattern to match keys in redis (mainnet/testnet)')
        parser.add_argument('block_number', type=int, help='block number to set')

    def handle(self, *args, **options):
        redis_ = RedisClient()
        scan_query = redis_.connection.scan(
            cursor=0,
            match=f'*{options["filter"]}',
            count=50
        )
        scan_query = scan_query[1]
        if len(scan_query) == 0:
            self.stdout.write('no keys found to set')
            return

        for redis_key in scan_query:
            redis_key = redis_key.decode('utf-8')
            block_number = str(options['block_number'])
            redis_.connection.set(redis_key, block_number)
            self.stdout.write(f'key {redis_key} set to {redis_.connection.get(redis_key).decode("utf-8")}')

        self.stdout.write(self.style.SUCCESS('rollback completed'))

