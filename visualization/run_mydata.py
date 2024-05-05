import pandas as pd
import matplotlib.pyplot as plot

from binance.client import Client
import binance
import os

api_key = os.environ.get('somekey1')
api_secret = os.environ.get('somekey2')

client = Client(api_key, api_secret)
print("account data")
df = client.get_account()
print("keys: ", df.keys())
balances = df["balances"]
df = pd.DataFrame.from_json( balances )
df.head()
# print("asset balance")
# print(client.get_asset_balance(asset='BTC'))
