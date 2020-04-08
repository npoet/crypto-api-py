import time
import hashlib
import hmac
import base64
import requests
from requests.auth import AuthBase
import ssl

api_key = ""
api_secret = ""
passphrase = ""
api_url = 'https://api.gdax.com/'


class CoinbaseExchangeAuth(AuthBase):
    def __init__(self, api_key, secret_key, passphrase):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase

    def __call__(self, request):
        timestamp = str(time.time())
        message = timestamp + request.method + request.path_url \
                + (request.body or '')
        hmac_key = base64.b64decode(self.secret_key)
        signature = hmac.new(hmac_key, message, hashlib.sha256)
        signature_b64 = signature.digest().encode('base64').rstrip('\n')

        request.headers.update({
            'CB-ACCESS-SIGN': signature_b64,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-KEY': api_key,
            'CB-ACCESS-PASSPHRASE': passphrase,
            'Content-Type': 'application/json'
        })
        return request

auth = CoinbaseExchangeAuth(api_key, api_secret, passphrase)


def balance(asset):
    id_num = ''
    if asset == 'ETH':
        id_num = 'c2657ec0-7f4b-4013-be33-2abaf0d4086e'
    elif asset == 'BTC':
        id_num = '41a69bbe-293d-4833-b163-683769f33082'
    balances_dict = {}
    try:
        balances_dict = requests.get(api_url + 'accounts/{0:s}'.format(id_num),
                                     auth=auth)
    except Exception:
        print "Balance request timed out. Retrying..."
        balance(asset)
    balances = balances_dict.json()
    return float(balances['available'])


def ticker(asset):
    r = ''
    try:
        r = requests.get(api_url + 'products/' + asset + '/ticker')
    except Exception:
        print "Ticker request timed out. Retrying..."
        ticker(asset)
    return r.json()


def buy(price):
    print "GDAX buy:"
    order = {'size': 0.2,
             'price': price,
             'side': 'buy',
             'product_id': 'ETH-BTC'}
    r = ''
    try:
        r = requests.post(api_url + 'orders', json=order, auth=auth)
    except Exception:
        print "Buy request timed out. Retrying..."
        buy(price)
    if r.status_code != 200:
        return 'failed'
    else:
        return r.json()


def sell(price):
    print "GDAX sell:"
    order = {'size': 0.02,
             'price': price,
             'side': 'sell',
             'product_id': 'ETH-BTC'}
    r = ''
    try:
        r = requests.post(api_url + 'orders', json=order, auth=auth)
    except Exception:
        print "Sell request timed out. Retrying..."
        sell(price)
    if r.status_code != 200:
        return 'failed'
    else:
        return r.json()


def withdrawal(coin, amount, address):
    print "GDAX withdrawal:"
    params = {'amount': amount,
              'currency': coin,
              'crypto_address': address}
    r = ''
    try:
        r = requests.post(api_url + 'withdrawals/crypto', json=params, auth=auth)
    except Exception:
        print "Withdrawal request timed out. Retrying..."
        withdrawal(coin, amount, address)
    return r.json()
