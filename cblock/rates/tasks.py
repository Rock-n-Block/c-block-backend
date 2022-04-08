import logging
import dramatiq

from cblock.rates.utils import update_rates

logger = logging.getLogger(__name__)


@dramatiq.actor(max_retries=0)
def update_usd_rates_task() -> None:
    update_rates()
