import datetime
import time
import hmac
import hashlib
from urllib import urlencode
import requests
import ssl

api_key = ""
api_secret = ""

BASE_URL = 'https://bittrex.com/api/v1.1/%s/'

MARKET_SET = {'selllimit', 'buylimit'}

ACCOUNT_SET = {'getbalance', 'withdraw', 'getorderhistory'}


def api_query(method, options=None):
    if not options:
        options = {}
    nonce = str(int(time.mktime(datetime.datetime.now().timetuple()) * 1000
                + datetime.datetime.now().microsecond / 1000))
    method_set = 'public'

    if method in MARKET_SET:
        method_set = 'market'
    elif method in ACCOUNT_SET:
        method_set = 'account'

    request_url = (BASE_URL % method_set) + method + '?'

    if method_set != 'public':
        request_url += 'apikey=' + api_key + "&nonce=" + nonce + '&'

    request_url += urlencode(options)
    response = ''
    try:
        response = requests.get(
            request_url,
            headers={"apisign": hmac.new(api_secret.encode(), request_url.encode(),
                                         hashlib.sha512).hexdigest()}).json()
    except Exception:
        print "{0:s} request timed out. Retrying...".format(method)
        api_query(method, options)
    if not response['success']:
        return 'failed'
    else:
        return response


def get_ticker(asset):
    return api_query('getticker', {'market': asset})


def buy(price):
    print "Bittrex buy:"
    return api_query('buylimit',
                     {'market': 'BTC-ETH',
                      'quantity': '.2',
                      'rate': price})


def sell(price):
    print "Bittrex sell:"
    return api_query('selllimit',
                     {'market': 'BTC-ETH',
                      'quantity': '.02',
                      'rate': price})


def balance(asset):
    balances_dict = api_query('getbalance', {'currency': asset})
    balances = balances_dict['result']
    return float(balances['Available'])


def withdrawal(coin, amount, address):
    print "Bittrex withdrawal:"
    return api_query('withdraw',
                     {'currency': coin,
                      'quantity': amount,
                      'address': address})
