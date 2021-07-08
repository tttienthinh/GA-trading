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
# import matplotlib.pyplot as plt
# from IPython.display import clear_output

import ta, pickle, json, time, requests
from bsf import BSF, Keys, webdriver

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

def atr_calcul(df, window=14):
    atr = ta.volatility.AverageTrueRange(high=df.high, low=df.low, close=df.close, 
                                         window=window, fillna=True)
    return atr.average_true_range()

def telegram_bot_sendtext(bot_message):
    
    bot_token = '1806732732:AAFxtjvhsucDPbOjBYSUzCNztqjntoI4Q-E'
    bot_chatID = '-572290585'
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message

    response = requests.get(send_text)

    return response.json()


def add(timestamp, action, price, TP, SL, avbl):
    with open("data.csv", "a+") as file:
        file.write("\n" + ", ".join([str(x) for x in [timestamp, action, price, TP, SL, avbl]]))
        file.close()

"""
b_driver = BSF(webdriver.Chrome(executable_path="/home/tttienthinh/Documents/Programmation\
/Bash/StartupApp/driver/chromedriver91")

b_driver = BSF(webdriver.Firefox(executable_path="/home/pi/Documents/GA-trading/drivers/geckodriver32"))
"""

# Raspberry
b_driver = BSF(webdriver.Chrome())

input("Click 'ENTER' when connected !")


def open_order(timestamp, leverage, price, TP, SL, action):
    # b_driver.refresh()
    avbl = b_driver.get_avbl()
    if avbl > 25:
        # b_driver.set_leverage(int(leverage))
        b_driver.set_price(price)
        b_driver.set_TPSL(
            TP=TP,
            SL=SL
        )
        if action == "BUY":
            b_driver.buy()
        elif action == "SELL":
            b_driver.sell()
        add(timestamp, action, price, TP, SL, avbl)
        opened = True
    else:
        avbl = f"Actual pocket have {avbl} no trade"
        opened = False
    # b_driver.refresh()
    return avbl, opened


while True:
    print(now())
    try:
        kline = '1m'
        try:
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
            df['atr'] = atr_calcul(df)

            df = df.iloc[-120:].reset_index(drop=True)
        except:
            print("erreur getting data")
            pass

        timestamp, o, h, l, c, v, bear, bull, ema20, ema50, ema100, atr = df.iloc[-3]
        start = df.iloc[-1].close
        if ema20 < ema50 < ema100: # SELL only
            if bear:
                print("SELL BEAR")
                if ema20 < h < ema50:
                    print("GOT TRIGGER")
                    SL = ema100
                    if SL - start > 2*atr:
                        print("GOT ATR")
                        # leverage = round(0.01/(SL/start-1), 1) set leverage to earn 1%
                        leverage = 5
                        TP = start - (SL - start) - 2 * atr
                        print("-----     -----     -----     -----     -----")
                        try:
                            avbl, opened = open_order(
                                timestamp, leverage, start, TP, SL, "SELL"
                            )
                        except IndexError as e:
                            avbl = f"Error while selling {e}"
                            opened = False
                        message = "\n".join([timestamp,
                        f"message : {avbl}",
                        f"OPEN SELL AT {start} BTC/USDT",
                        f"SL at {round(SL, 2)}",
                        f"TP at {round(TP, 2)}",
                        f"Leverage {leverage} to have : ",
                        f"   - Profit {round(100*leverage* (1 - TP/start), 2)} %",
                        f"   - Loss   {round(100*leverage* (SL/start - 1), 2)} %"])

                        print(message)
                        if opened:
                            telegram_bot_sendtext(message)
        
        if ema20 > ema50 > ema100: # BUY only
            if bull:
                print("BUY BULL")
                if ema20 > h > ema50:
                    print("GOT TRIGGER")
                    SL = ema100
                    if start-SL > 2*atr:
                        print("GOT ATR")
                        TP = start + (start - SL) + 2 * atr
                        # leverage = round(0.01/(1-SL/start), 1) # set leverage to earn 1%
                        leverage = 5
                        print("-----     -----     -----     -----     -----")
                        try:
                            avbl, opened = open_order(
                                timestamp, leverage, start, TP, SL, "BUY"
                            )
                        except IndexError as e:
                            avbl = f"Error while selling {e}"
                            opened = False
                        message = "\n".join([timestamp,
                        f"message : {avbl}",
                        f"OPEN BUY AT {start} BTC/USDT",
                        f"SL at {round(SL, 2)}",
                        f"TP at {round(TP, 2)}",
                        f"Leverage {leverage} to have : ",
                        f"   - Profit {round(100*leverage* (TP/start - 1), 2)} %",
                        f"   - Loss   {round(100*leverage* (1 - SL/start), 2)} %"])

                        print(message)
                        if opened:
                            telegram_bot_sendtext(message)
                    

        date = np.array(
            [datetime.strptime(df.timestamp[i], '%Y-%m-%d %H:%M:%S') 
            for i in range(len(df))]
        )
        """
        # Plotting data
        plt.plot(date, df.close, label='Price')
        plt.plot(date, df.ema20, label='EMA20')
        plt.plot(date, df.ema50, label='EMA50')
        plt.plot(date, df.ema100, label='EMA100')
        plt.plot(date[df.bear], df.close[df.bear] + 100, 
                "vr", label='Bear')
        plt.plot(date[df.bull], df.close[df.bull] - 100, 
                "^g", label='Bull')
        plt.legend()
        plt.grid()
        plt.title(df.timestamp[len(df)-1])

        plt.pause(60 - now().second)
        plt.clf()
        """
        b_driver.refresh()
        time.sleep(60 - now().second)

    except IndexError as e:
        try:
            telegram_bot_sendtext(f"J'arrive pas à prendre les données sur Binance !!! {e}")
        except IndexError as e2:
            print(f"Problem de connection surement, j'ai pas réussi à envoyé de message avec le bot {e2}")

        print(f"Problem, pas possible de télécharger les données. {e}")
        time.sleep(60 - now().second)

