import time
import unirest
import hmac
import hashlib
import base64
import json
from collections import OrderedDict
import ssl

api_key = ""
api_secret = ""
main_url = 'https://api.btcmarkets.net'
key = api_key.encode("utf-8")


def ticker():
    path = main_url + '/market/ETH/BTC/tick'
    result = ''
    try:
        result = unirest.get(path)
    except Exception:
        print "Ticker request timed out. Retrying..."
        ticker()
    return result.body


def balance():
    path_part = "/account/balance"
    path = main_url + path_part
    nonce = '%i' % (time.time()*1000)
    data = path_part + "\n" + nonce + "\n"
    edata = data.encode("utf-8")
    secret = base64.standard_b64decode(api_secret.encode("utf-8"))
    signature = hmac.new(secret, edata, hashlib.sha512)
    sig = base64.standard_b64encode(signature.digest()).decode("utf-8")

    result = ''
    try:
        result = unirest.get(path,
                              headers={"Accept": "application/json",
                                       "Accept-Charset": "utf-8",
                                       "Content-Type": "application/json",
                                       "apikey": key,
                                       "timestamp": nonce,
                                       "signature": sig})
    except Exception:
        print "Balance request timed out. Retrying..."
        balance()
    return result.body


def buy(price):
    print "BTC Markets buy:"
    amount = 1 * 100000000
    params = OrderedDict([("currency", "BTC"),
                               ("instrument", "ETH"),
                               ("price", int(price * 100000000)),
                               ("volume", amount),
                               ("orderSide", "Bid"),
                               ("ordertype", "Limit"),
                               ("clientRequestId", "abc-cdf-1000")])
    path_part = "/order/create"
    path = main_url + path_part
    nonce = '%i' % (time.time()*1000)
    post_data = json.dumps(params, separators=(',', ':'))
    data = path_part + "\n" + nonce + "\n" + str(post_data)
    edata = data.encode("utf-8")
    secret = base64.standard_b64decode(api_secret.encode("utf-8"))
    signature = hmac.new(secret, edata, hashlib.sha512)
    sig = base64.standard_b64encode(signature.digest()).decode("utf-8")
    result = ''
    try:
        result = unirest.post(path, params=post_data, headers={"Accept": "application/json",
                                       "Accept-Charset": "utf-8",
                                       "Content-Type": "application/json",
                                       "apikey": key,
                                       "timestamp": nonce,
                                       "signature": sig})
    except Exception:
        print "Buy request timed out. Retrying..."
        buy(price)
    if result.code != 200:
        return 'buy failed'
    else:
        return result.body


def sell(amount, price):
    print "BTC Markets sell:"
    params = OrderedDict([("currency", "BTC"),
                          ("instrument", "ETH"),
                          ("price", int(price * 100000000)),
                          ("volume", int(amount * 100000000)),
                          ("orderSide", "Ask"),
                          ("ordertype", "Limit"),
                          ("clientRequestId", "abc-cdf-1000")])
    path_part = "/order/create"
    path = main_url + path_part
    nonce = '%i' % (time.time()*1000)
    post_data = json.dumps(params, separators=(',', ':'))
    data = path_part + "\n" + nonce + "\n" + str(post_data)
    edata = data.encode("utf-8")
    secret = base64.standard_b64decode(api_secret.encode("utf-8"))
    signature = hmac.new(secret, edata, hashlib.sha512)
    sig = base64.standard_b64encode(signature.digest()).decode("utf-8")
    result = ''
    try:
        result = unirest.post(path, params=post_data, headers={"Accept": "application/json",
                                                              "Accept-Charset": "utf-8",
                                                              "Content-Type": "application/json",
                                                              "apikey": key,
                                                              "timestamp": nonce,
                                                              "signature": sig})
    except Exception:
        print "Sell request timed out. Retrying..."
        sell(amount, price)
    if result.code != 200:
        return 'failed'
    else:
        return result.body


def withdraw(coin, amount, address):
    print "BTC Markets withdrawal:"
    params = OrderedDict([("amount", int(amount * 100000000)),
                          ("address", address),
                          ("currency", coin)])
    path_part = "/fundtransfer/withdrawCrypto"
    path = main_url + path_part
    nonce = '%i' % (time.time()*1000)
    post_data = json.dumps(params, separators=(',', ':'))
    data = path_part + "\n" + nonce + "\n" + str(post_data)
    edata = data.encode("utf-8")
    secret = base64.standard_b64decode(api_secret.encode("utf-8"))
    signature = hmac.new(secret, edata, hashlib.sha512)
    sig = base64.standard_b64encode(signature.digest()).decode("utf-8")
    result = ''
    try:
        result = unirest.post(path, params=post_data, headers={"Accept": "application/json",
                                                              "Accept-Charset": "utf-8",
                                                              "Content-Type": "application/json",
                                                              "apikey": key,
                                                              "timestamp": nonce,
                                                              "signature": sig})
    except Exception:
        print "Withdraw request timed out. Retrying..."
        withdraw(coin, amount, address)
    return result.body
