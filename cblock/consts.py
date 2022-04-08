from os.path import join

MAX_AMOUNT_LEN = len(str(2 ** 256))
COINGECKO_BASE_URI = "https://api.coingecko.com/api/v3/"
COINGECKO_PRICE_ENDPOINT = join(COINGECKO_BASE_URI, "simple", "price")
COINGECKO_CELO_ID = "celo"
