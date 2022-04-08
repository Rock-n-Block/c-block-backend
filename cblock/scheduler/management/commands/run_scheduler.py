from apscheduler.schedulers.background import BlockingScheduler
from django.core.management.base import BaseCommand

from cblock.settings import config
from cblock.contracts.tasks import check_alive_wallets, check_and_send_notifications, check_wedding_divorce_timed_out
from cblock.rates.tasks import update_usd_rates_task


class Command(BaseCommand):
    help = 'Run blocking scheduler to create periodical tasks'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Preparing scheduler'))
        scheduler = BlockingScheduler()

        # Rates fetcher
        scheduler.add_job(
            func=update_usd_rates_task.send,
            trigger='interval',
            seconds=config.rates_checker_interval
        )

        for network in config.networks:
            if network.tracking_disabled:
                continue
            # Alive wallets job
            scheduler.add_job(
                func=check_alive_wallets.send,
                trigger='interval',
                args=[
                    network.rpc_endpoint,
                    network.is_testnet
                ],
                seconds=network.dead_wallets_check_interval,
            )

            # Reminders job
            scheduler.add_job(
                func=check_and_send_notifications.send,
                trigger='interval',
                args=[
                    network.rpc_endpoint,
                    network.is_testnet,
                    network.day_seconds,
                    network.confirmation_checkpoints
                ],
                seconds=network.day_seconds,
            )

            # Divorce timeout job
            scheduler.add_job(
                func=check_wedding_divorce_timed_out.send,
                trigger='interval',
                args=[
                    network.rpc_endpoint,
                    network.is_testnet,
                    network.day_seconds,
                ],
                seconds=network.day_seconds,
            )

        self.stdout.write(self.style.NOTICE('Start scheduler'))
        scheduler.start()
