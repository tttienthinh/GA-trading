# IMPORTS
import pandas as pd
import math
import os.path
import time
from binance.client import Client
from datetime import date, timedelta, datetime
from dateutil import parser

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import clear_output

import ta, pickle, json, time

now = datetime.now


client = Client("0YoXpNjk2J0rwPmIDFlgRuu2fFHKHSADD6qUNoRVTr3N9Rddjdbg3AFP7jzyxvly")


### FUNCTIONS
binsizes = {"1m": 1, "5m": 5, "1h": 60, "1d": 1440}
batch_size = 750

def minutes_of_new_data(symbol, kline_size, data, source):
    if len(data) > 0:  
        old = parser.parse(data["timestamp"].iloc[-1])
    elif source == "binance": 
        old = datetime.strptime('1 Jan 2017', '%d %b %Y')
    if source == "binance": 
        new = pd.to_datetime(
            client.get_klines(symbol=symbol, 
                                      interval=kline_size)[-1][0], 
            unit='ms'
        )
    return old, new

def get_all_binance(symbol, kline_size, save = False):
    filename = '%s-%s-data.csv' % (symbol, kline_size)
    if os.path.isfile(filename): 
        data_df = pd.read_csv(filename)
    else: 
        data_df = pd.DataFrame()
    oldest_point, newest_point = minutes_of_new_data(symbol, 
                                                     kline_size, 
                                                     data_df, 
                                                     source = "binance")
    delta_min = (newest_point - oldest_point).total_seconds()/60
    available_data = math.ceil(delta_min/binsizes[kline_size])
    if oldest_point == datetime.strptime('1 Jan 2017', '%d %b %Y'): 
        print('Downloading all available %s data for %s. \
        Be patient..!' % (kline_size, symbol))
    else: 
        print('Downloading %d minutes of new data available \
        for %s, i.e. %d instances of %s data.' \
              % (delta_min, symbol, available_data, kline_size))
    klines = client.get_historical_klines(symbol, 
                                          kline_size, 
                                          oldest_point.strftime("%d %b %Y %H:%M:%S"), 
                                          newest_point.strftime("%d %b %Y %H:%M:%S"))
    data = pd.DataFrame(klines, 
                        columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 
                                   'close_time', 'quote_av', 'trades', 'tb_base_av', 
                                   'tb_quote_av', 'ignore' ])
    data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
    if len(data_df) > 0:
        temp_df = pd.DataFrame(data)
        data_df = data_df.append(temp_df)
    else: 
        data_df = data
    data_df.set_index('timestamp', inplace=True)
    if save: 
        data_df.to_csv(filename)
    print('All caught up..!')
    return data_df

def get_delta_binance(symbol, kline_size, save = False, delta=timedelta(days=7)):
    filename = '%s-%s-data.csv' % (symbol, kline_size)
    data_df = pd.DataFrame()
    oldest_point, newest_point = minutes_of_new_data(symbol, 
                                                     kline_size, 
                                                     data_df, 
                                                     source = "binance")
    oldest_point = newest_point - delta
    delta_min = (newest_point - oldest_point).total_seconds()/60
    available_data = math.ceil(delta_min/binsizes[kline_size])
    print('Downloading %d minutes of new data available \
    for %s, i.e. %d instances of %s data.' \
          % (delta_min, symbol, available_data, kline_size))
    klines = client.get_historical_klines(symbol, 
                                          kline_size, 
                                          oldest_point.strftime("%d %b %Y %H:%M:%S"), 
                                          newest_point.strftime("%d %b %Y %H:%M:%S"))
    data = pd.DataFrame(klines, 
                        columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 
                                   'close_time', 'quote_av', 'trades', 'tb_base_av', 
                                   'tb_quote_av', 'ignore' ])
    data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
    if len(data_df) > 0:
        temp_df = pd.DataFrame(data)
        data_df = data_df.append(temp_df)
    else: 
        data_df = data
    data_df.set_index('timestamp', inplace=True)
    if save: 
        data_df.to_csv(filename)
    print('All caught up..!')
    return data_df


def wilFractal(df):
        bear = (
                df['high'].shift(2).lt(df['high']) &
                df['high'].shift(1).lt(df['high']) &
                df['high'].shift(-1).lt(df['high']) &
                df['high'].shift(-2).lt(df['high'])
        )
    
        bull = (
                df['low'].shift(2).gt(df['low']) &
                df['low'].shift(1).gt(df['low']) &
                df['low'].shift(-1).gt(df['low']) &
                df['low'].shift(-2).gt(df['high'])
        )
    
        return bear, bull
    
def ema(df, windows=[20]):
    emas = []
    for x in windows:
        emas.append(
            ta.trend.ema_indicator(close=df.close, window=x, fillna=True)
        )
    return emas

while True:

    kline = '1m'
    get_delta_binance("BTCUSDT", 
                    kline, 
                    save = True, 
                    delta=timedelta(hours=2))
    df = pd.read_csv(f"BTCUSDT-{kline}-data.csv")
    df = df.drop(
        ["quote_av", 
        "trades", 
        "tb_base_av", 
        "tb_quote_av", 
        "ignore", 
        "close_time"], axis=1)

    df['bear'], df['bull'] = wilFractal(df)
    df['ema20'], df['ema50'], df['ema100'] = ema(df, [20, 50, 100])

    date = np.array(
        [datetime.datetime.strptime(df.timestamp[i], '%Y-%m-%d %H:%M:%S') 
        for i in range(len(df[:100]))]
    )
    plt.plot(date, df.close[:100], label='Price')
    plt.plot(date, df.ema20[:100], label='EMA20')
    plt.plot(date, df.ema50[:100], label='EMA50')
    plt.plot(date, df.ema100[:100], label='EMA100')
    plt.plot(date[df.bear[:100]], df.close[:100][df.bear[:100]] + 100, 
            "vr", label='Bear')
    plt.plot(date[df.bull[:100]], df.close[:100][df.bull[:100]] - 100, 
            "^g", label='Bull')
    plt.legend()
    plt.grid()
    plt.title(df.timestamp[len(df)-1])

    plt.pause(60 - now().second)


