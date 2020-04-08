import hashlib
import hmac
import random
import string
import time
import unirest
import ssl

key = ""
secret = ""

clientOrderId = "".join(random.choice(string.digits + string.ascii_lowercase)
                        for _ in range(30))


def truncate(num):
    num1 = str(num)
    trunc = '%.5s' % num1
    if 'e' in trunc:
        return 0.0
    return float(trunc)


def timestamp():
    path_timestamp = "/api/1/public/time"
    result = ''
    try:
        result = unirest.get("http://api.hitbtc.com" + path_timestamp)
    except Exception:
        print "Timestamp request timed out. Retrying..."
        timestamp()
    return result.body["timestamp"]


def ticker(asset):
    path_ticker = "/api/1/public/{0:s}/ticker".format(asset)
    result = ''
    try:
        result = unirest.get("http://api.hitbtc.com" + path_ticker)
    except Exception:
        print "Ticker request timed out. Retrying..."
        ticker(asset)
    return result.body


def buy(price):
    print "HitBTC buy:"
    nonce4 = str(int(time.time() * 1000))
    path_trade = "/api/1/trading/new_order?apikey=%s&nonce=%s" % (key, str(int(time.time() * 1000)))
    parameters = "clientOrderId=" \
                 + clientOrderId \
                 + "&symbol=ETHBTC&side=buy&price={0:f}&quantity=1&type=limit"\
                 .format(price)
    payload = path_trade + parameters
    signature = hmac.new(secret, payload, hashlib.sha512).hexdigest().lower()
    result = ''
    try:
        result = unirest.post("http://api.hitbtc.com" + path_trade,
                              headers={"X-Signature": signature}, params=parameters)
    except Exception:
        print "Buy request timed out. Retrying..."
        buy(price)
    r = result.body
    report = r['ExecutionReport']
    if report['execReportType'] == 'rejected':
        return 'failed'
    else:
        return result.body


def sell(price):
    print "HitBTC sell:"
    nonce4 = str(int(time.time() * 1000))
    path_trade = "/api/1/trading/new_order?apikey=%s&nonce=%s" % (key, str(int(time.time() * 1000)))
    parameters = "&clientOrderId=" \
                 + clientOrderId \
                 + "&symbol=ETHBTC&side=sell&price={0:f}&quantity=1&type=limit"\
                 .format(price)
    signature = hmac.new(secret, path_trade + parameters,
                         hashlib.sha512).hexdigest().lower()
    result = ''
    try:
        result = unirest.post("http://api.hitbtc.com" + path_trade,
                              headers={"X-Signature": signature}, params=parameters)
    except:
        print "Sell request timed out. Retrying..."
        sell(price)
    r = result.body
    report = r['ExecutionReport']
    if report['execReportType'] == 'rejected':
        return 'failed'
    else:
        return result.body


def get_main_bal(asset):
    num = 0
    if asset == 'ETH':
        num = 1
    path = '/api/1/payment/balance?apikey=%s&nonce=%s' % (key, str(int(time.time() * 1000)))
    signature = hmac.new(secret, path, hashlib.sha512).hexdigest().lower()
    result = ''
    try:
        result = unirest.get("http://api.hitbtc.com" + path,
                             headers={"X-Signature": signature})
    except Exception:
        print "Main balance request timed out. Retrying..."
        get_main_bal(asset)
    balance_dict = result.body
    bals = balance_dict['balance']
    bal = bals[num]
    return float(bal['balance'])


def balance(asset):
    if truncate(get_main_bal(asset)) != 0:
        coins_from_main(asset)
    num = 0
    path_balance = "/api/1/trading/balance?apikey=%s&nonce=%s" % (key, str(int(time.time() * 1000)))
    signature = hmac.new(secret, path_balance,
                         hashlib.sha512).hexdigest().lower()
    result = ''
    try:
        result = unirest.get("http://api.hitbtc.com" + path_balance,
                             headers={"X-Signature": signature})
    except Exception:
        print "Balance request timed out. Retrying..."
        balance(asset)
    balances_dict = result.body
    if asset == 'BTC':
        num = 2
    if asset == 'ETH':
        num = 7
    balance_dict = balances_dict['balance'][num]
    return float(balance_dict['cash'])


def withdrawal(coin, amount, address):
    print "HitBTC withdrawal:"
    coins_to_main('ETH')
    coins_to_main('BTC')
    time.sleep(5)
    path_transfer = "/api/1/payment/payout?apikey=%s&nonce=%s" % (key, str(int(time.time() * 1000)))
    parameters = "clientOrderId=" \
                 + clientOrderId \
                 + "&amount={0:f}&currency_code={1:s}&address={2:s}"\
                 .format(amount, coin, address)
    signature = hmac.new(secret, path_transfer
                         + parameters, hashlib.sha512).hexdigest()
    result = ''
    try:
        result = unirest.post("http://api.hitbtc.com" + path_transfer,
                              headers={"X-Signature": signature}, params=parameters)
    except Exception:
        print "Withdrawal request timed out. Retrying..."
        withdrawal(coin, amount, address)
    return result.body


def coins_to_main(asset):
    bal = truncate(balance(asset))
    path = '/api/1/payment/transfer_to_main?apikey=%s&nonce=%s' % (key, str(int(time.time() * 1000)))
    parameters = "&amount={0:f}&currency_code={1:s}".format(bal, asset)
    signature = hmac.new(secret, path + parameters,
                         hashlib.sha512).hexdigest().lower()
    result = ''
    try:
        result = unirest.post("http://api.hitbtc.com" + path,
                              headers={"X-Signature": signature},
                              params=parameters)
    except Exception:
        print "Coins to main request timed out. Retrying..."
        coins_to_main(asset)
    return result.body


def coins_from_main(asset):
    bal = truncate(get_main_bal(asset))
    path = '/api/1/payment/transfer_to_trading?apikey=%s&nonce=%s' % (key, str(int(time.time() * 1000)))
    parameters = "&amount={0:f}&currency_code={1:s}".format(bal, asset)
    signature = hmac.new(secret, path + parameters,
                         hashlib.sha512).hexdigest().lower()
    result = ''
    try:
        result = unirest.post("http://api.hitbtc.com" + path,
                          headers={"X-Signature": signature},
                          params=parameters)
    except Exception:
        print "Coins from main request timed out. Retrying..."
        coins_from_main(asset)
    return result.body
