import unirest
import json
import base64
import hashlib
import hmac
import datetime
import time
import ssl


api_key = ""
api_secret = ""
url = 'https://api.gemini.com'


def sign_payload(payload):
    j = json.dumps(payload)
    data = base64.standard_b64encode(j)
    signature = hmac.new(api_secret, data, hashlib.sha384).hexdigest()
    my_dick = {"X-GEMINI-APIKEY": api_key,
               "X-GEMINI-SIGNATURE": signature,
               "X-GEMINI-PAYLOAD": data}
    return my_dick


def balance(asset):
    payload = {'request': '/v1/balances',
               'nonce': '%i' % (time.time()*1000)}
    signed_payload = sign_payload(payload)
    r = ''
    try:
        r = unirest.post(url + '/v1/balances', headers=signed_payload)
    except Exception:
        print "Balance request timed out. Retrying..."
        balance(asset)
    balances_dict = r.body
    num = 0
    if asset == 'BTC':
        num = 0
    elif asset == 'ETH':
        num = 2
    balance_dict = balances_dict[num]
    return float(balance_dict['available'])


def withdrawal(coin, amount, address):
    print "Gemini withdrawal:"
    payload = {'request': '/v1/withdraw/{0:s}'.format(coin.lower()),
               'nonce': '%i' % (time.time()*1000),
               'amount': '%.9s' % amount,
               'address': address}
    signed_payload = sign_payload(payload)
    r = unirest.post(url + "/v1/withdraw/{0:s}".format(coin.lower()),
                     headers=signed_payload)
    return r.body


def ticker(asset):
    response = ''
    try:
        response = unirest.get(url + '/v1/pubticker/{0:s}'.format(asset))
    except Exception:
        print "Ticker request timed out. Retrying..."
        ticker(asset)
    return response.body


def buy(price):
    print "Gemini buy:"
    payload = {'request': '/v1/order/new',
               'nonce': '%i' % (time.time()*1000),
               'symbol': 'ethbtc',
               'amount': '0.2',
               'price': price,
               'side': 'buy',
               'type': "exchange limit"}
    signed_payload = sign_payload(payload)
    response = ''
    try:
        response = unirest.post(url + "/v1/order/new",  headers=signed_payload)
    except Exception:
        print "Buy request timed out. Retrying..."
        buy(price)
    if response.code != 200:
        return 'failed'
    else:
        return response.body


def sell(price):
    print "Gemini sell:"
    payload = {'request': '/v1/order/new',
               'nonce': '%i' % (time.time()*1000),
               'symbol': 'ethbtc',
               'amount': '0.02',
               'price': price,
               'side': 'sell',
               'type': "exchange limit"}
    signed_payload = sign_payload(payload)
    response = ''
    try:
        response = unirest.post(url + "/v1/order/new",  headers=signed_payload)
    except Exception:
        print "Sell request timed out. Retrying..."
        sell(price)
    if response.code != 200:
        return 'failed'
    else:
        return response.body
