# %%
import pandas as pd
import math, os
import time
from binance.client import Client

from datetime import datetime, timedelta

from ta import add_all_ta_features
from ta.utils import dropna


# %%

BINANCE_KEY = os.environ.get['BINANCE_KEY']
BINANCE_SECRET = os.environ.get['BINANCE_SECRET']

# %%
