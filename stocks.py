import requests
import pandas as pd
import numpy as np
import time
from alpha_vantage.timeseries import TimeSeries
import matplotlib.pyplot as plt
import seaborn as sns

# Replace '' with Alpha Vantage API token
API_KEY = ''

ts = TimeSeries(key=API_KEY, output_format='pandas')

nse_symbols = ['TCS','INFY','MSFT']

def get_stock_data(symbol):
    try:
        data, meta_data = ts.get_daily(symbol)
        # Saving data to a CSV file with company name as file name
        filename = f"{symbol}.csv"
        data.to_csv(filename)
        print(f"Data for {symbol} saved to {filename}")
        return data
    except Exception as e:
        print(f"Error fetching data for {symbol}: {str(e)}")
        return None

stock_data = {}
for symbol in nse_symbols:
    data = get_stock_data(symbol)
    if data is not None:
        stock_data[symbol] = data
    time.sleep(12)#to reduce to 5 calls per minute

def analyze_and_visualize(data, symbol):
    data['20_SMA'] = data['4. close'].rolling(window=20).mean()
    data['50_SMA'] = data['4. close'].rolling(window=50).mean()

    data['Daily_Return'] = data['4. close'].pct_change()

    # Plotting the stock's closing price and moving averages
    plt.figure(figsize=(14, 7))
    plt.plot(data.index, data['4. close'], label='Closing Price', color='blue')
    plt.plot(data.index, data['20_SMA'], label='20-Day SMA', color='red')
    plt.plot(data.index, data['50_SMA'], label='50-Day SMA', color='green')
    plt.title(f"{symbol} Closing Prices and Moving Averages")
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid()
    plt.show()

    plt.figure(figsize=(14, 7))
    sns.histplot(data['Daily_Return'].dropna(), bins=100, color='purple', kde=True)
    plt.title(f"{symbol} Daily Return Distribution")
    plt.xlabel('Daily Return')
    plt.ylabel('Frequency')
    plt.grid()
    plt.show()

for symbol, data in stock_data.items():
    analyze_and_visualize(data, symbol)

def feature_engineering(data):
    # Volatility is the Standard deviation of daily returns
    data['Volatility'] = data['Daily_Return'].rolling(window=20).std()

    # Momentum is the Difference between the current closing price and the closing price 10 days ago
    data['Momentum'] = data['4. close'] - data['4. close'].shift(10)

    return data

for symbol in stock_data:
    stock_data[symbol] = feature_engineering(stock_data[symbol])
