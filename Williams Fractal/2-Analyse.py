import mplfinance as fplt
import pandas as pd
import matplotlib.dates as mpl_dates


# Extracting Data for plotting
data = pd.read_csv("BTCUSDT-1m-data.csv")

df = data[["timestamp", "open", "high", "low", "close"]].rename(
    {"timestamp":"Date", "open":"Open", "high":"High", "low":"Low", "close":"Close"},
    axis='columns'
)
df.Date = pd.to_datetime(df.Date, format='%Y-%m-%d %H:%M:%S')
df = df.set_index("Date")

fplt.plot(
            df,
            type='candle',
            style='charles',
            title='BTC USDT',
            ylabel='Price'
        )

