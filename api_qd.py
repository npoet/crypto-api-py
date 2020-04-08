import datetime
import time
import unirest
import hashlib
import hmac
import json
import requests
import ssl


api_key = ''
api_secret = ''
main_url = 'https://api.quadrigacx.com/v2/'
client_id = ''
MARKET_SET = {'sell', 'buy'}

ACCOUNT_SET = {'balance', 'withdraw', 'getorderhistory'}


def ticker(asset):
    response = ''
    try:
        response = unirest.get(main_url + 'ticker?book={0:s}'.format(asset))
    except Exception:
        print "Ticker request timed out. Retrying..."
        ticker(asset)
    return response.body


def balance(asset):
    url = main_url + 'balance'
    nonce = '%i' % (time.time()*1000)
    data = nonce + client_id + api_key
    signature = hmac.new(api_secret.encode(), data.encode(), hashlib.sha256).hexdigest().lower()
    params = {
        'key': api_key,
        'signature': signature,
        'nonce': nonce
    }
    response = ''
    try:
        response = unirest.post(url, params=params)
    except Exception:
        print "Balance request timed out. Retrying..."
        balance(asset)
    balance_dict = response.body
    if asset.lower() == 'btc':
        return float(balance_dict['btc_available'])
    elif asset.lower() == 'eth':
        return float(balance_dict['eth_available'])


def buy(price):
    print "Quadriga buy:"
    url = main_url + 'buy'
    nonce = '%i' % (time.time()*1000)
    data = nonce + client_id + api_key
    signature = hmac.new(api_secret, data, hashlib.sha256).hexdigest()
    params = {
        'key': api_key,
        'signature': signature,
        'nonce': nonce,
        'amount': '1.00',
        'price': price,
        'book': 'eth_btc'
    }
    response = ''
    try:
        response = unirest.post(url, params=params)
    except Exception:
        print "Buy request timed out. Retrying..."
        buy(price)
    if response.code != 200:
        return 'failed'
    else:
        return response.body


def sell(amount, price):
    print "Quadriga sell:"
    url = main_url + 'sell'
    nonce = '%i' % (time.time()*1000)
    data = nonce + client_id + api_key
    signature = hmac.new(api_secret, data, hashlib.sha256).hexdigest()
    params = {
        'key': api_key,
        'signature': signature,
        'nonce': nonce,
        'amount': amount,
        'price': price,
        'book': 'eth_btc'
    }
    response = ''
    try:
        response = unirest.post(url, params=params)
    except Exception:
        print "Sell request timed out. Retrying..."
        sell(amount, price)
    if response.code != 200:
        return 'failed'
    else:
        return response.body


def withdrawal(coin, amount, address):
    print "Quadriga withdrawal:"
    url = ''
    if coin.lower() == 'eth':
        url = main_url + 'ether_withdrawal'
    elif coin.lower() == 'btc':
        url = main_url + 'bitcoin_withdrawal'
    nonce = '%i' % (time.time()*1000)
    data = nonce + client_id + api_key
    signature = hmac.new(api_secret, data, hashlib.sha256).hexdigest()
    params = {
        'key': api_key,
        'signature': signature,
        'nonce': nonce,
        'amount': amount,
        'address': address
    }
    response = ''
    try:
        response = unirest.post(url, params=params)
    except Exception:
        print "Withdrawal request timed out. Retrying..."
        withdrawal(coin, amount, address)
    return response.body
