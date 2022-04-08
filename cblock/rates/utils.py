import sys
import traceback
import requests
import logging

from cblock.consts import COINGECKO_PRICE_ENDPOINT, COINGECKO_CELO_ID
from cblock.rates.models import UsdRate

logger = logging.getLogger(__name__)


def fetch_rates() -> float:
    res = requests.get(
        url=COINGECKO_PRICE_ENDPOINT,
        params={
            'ids': COINGECKO_CELO_ID,
            'vs_currencies': 'usd'
        })

    if res.status_code != 200:
        logger.error(res.text)
        raise Exception(f"Cannot fetch usd rate from coingecko: {res.text}")

    response = res.json()

    rate = response.get(COINGECKO_CELO_ID).get('usd')
    return rate


def update_rates() -> None:
    rate_object, _ = UsdRate.objects.get_or_create(symbol='CELO', name='Celo')

    try:
        celo_rate = fetch_rates()
        rate_object.rate = celo_rate
        rate_object.save()
        logger.info(f"Fetched rate: 1 CELO = {celo_rate} USD")
    except Exception:
        logger.error("\n".join(traceback.format_exception(*sys.exc_info())))


