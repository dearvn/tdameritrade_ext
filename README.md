# Information
This package extend from https://github.com/timkpaine/tdameritrade
I crawled data options from TD Ameritrade API with thousand requests by hour 
and my application has generated over 11k tokens in the last few hours when I use tdameritrade package
maybe when I send a get request to TDA then a token generated so TD Ameritrade API team notice me. Then I used redis to keep token and using it in 30minute before re-generated.
I only modified session.py file and keep others.
Bonus, I created 2 methods to get history stock price and options straddle as Yahoo Options.
## Installation
```bash
pip install pip install tdameritrade-ext --upgrade

```
## Get Options
* Get options
```bash
from tdameritrade_ext.client import TDClient
import time
c = TDClient()
data = c.options('AAPL', fromDate=time.strftime("%Y-%m-%d"))
```
## Get Options Chain as Straddle (similar Yahoo Options)
```bash
def get_option_chain(ticker):
    df = None
    try:
        c = TDClient()
        df = c.options(ticker, fromDate=time.strftime("%Y-%m-%d"))
    except AssertionError as e:
        print("error 1", e)
        log.exception(e)
    except Exception as e:
        print("error 2", e)
        log.exception(e)

    if df == None:
        return None

    putExp = df['putExpDateMap']
    puts = {}
    for date, put in putExp.items():
        dates = date.split(":")
        date_expiration = dates[0]
        itemputs = {}
        for strike, itemstrikes in put.items():
            if strike[-2:] == '.0':
                strike = round(float(strike))
            itemstrike = itemstrikes[0]
            itemput = {
                'strike': strike,
                'put': {
                    'contractSymbol': itemstrike['symbol'],
                    'strike': strike,
                    'lastPrice': itemstrike['last'],
                    'change': itemstrike['netChange'],
                    'percentChange': itemstrike['percentChange'],
                    'volume': itemstrike['totalVolume'],
                    'openInterest': itemstrike['openInterest'],
                    'impliedVolatility': itemstrike['volatility'],
                    'open': itemstrike['openPrice'],
                    'high': itemstrike['highPrice'],
                    'low': itemstrike['lowPrice'],
                    'close': itemstrike['closePrice'],
                    'date': itemstrike['tradeTimeInLong'],
                    'bid': itemstrike['bid'],
                    'ask': itemstrike['ask']
                }
            }
            itemputs[strike] = itemput
        puts[date_expiration] = itemputs

    callExp = df['callExpDateMap']
    calls = {}
    for date, call in callExp.items():
        dates = date.split(":")
        date_expiration = dates[0]

        put = puts[date_expiration] if date_expiration in puts else {}
        itemcalls = []
        for strike, itemstrikes in call.items():
            if strike[-2:] == '.0':
                strike = round(float(strike))
            itemstrike = itemstrikes[0]
            itemcall = {
                'strike': strike,
                'call': {
                    'contractSymbol': itemstrike['symbol'],
                    'strike': strike,
                    'lastPrice': itemstrike['last'],
                    'change': itemstrike['netChange'],
                    'percentChange': itemstrike['percentChange'],
                    'volume': itemstrike['totalVolume'],
                    'openInterest': itemstrike['openInterest'],
                    'impliedVolatility': itemstrike['volatility'],
                    'open': itemstrike['openPrice'],
                    'high': itemstrike['highPrice'],
                    'low': itemstrike['lowPrice'],
                    'close': itemstrike['closePrice'],
                    'date': itemstrike['tradeTimeInLong'],
                    'bid': itemstrike['bid'],
                    'ask': itemstrike['ask']
                },
                'put': put[strike]['put'] if strike in put else {}
            }
            itemcalls.append(itemcall)
        calls[date_expiration] = itemcalls

    return calls
```

* Get history by ticker and interval: 1m, 5m, 10m, 15m, 30m, 1h, 1d

```bash
def get_data_ticker(ticker, interval):
    c = TDClient()
    period_type = 'day'
    period = 1
    frequency_type = 'minute'
    frequency = 1

    if (interval == '5m'):
        frequency = 5
        period = 2
    elif (interval == '10m'):
        frequency = 10
        period = 3
    elif (interval == '15m'):
        frequency = 15
        period = 5
    elif (interval == '30m'):
        frequency = 30
        period = 10
    elif (interval == '1h'):
        frequency = 30
        period = 2
    elif (interval == '1d'):
        period_type = 'month'
        period = 6
        frequency_type = 'daily'
        frequency = 1

    resp = c.history(symbol=ticker,
                               periodType=period_type,
                               period=period,
                               frequencyType=frequency_type,
                               frequency=frequency)

    if 'candles' not in resp:
        return None
    candles = resp['candles']

    if (interval == '1h'):
        datas = []
        for item in candles:
            date_time = datetime.fromtimestamp(item['datetime'] / 1000)
            m = date_time.minute
            if m == 0:
                datas.append(item)
    else:
        datas = candles
    
    return datas
```
