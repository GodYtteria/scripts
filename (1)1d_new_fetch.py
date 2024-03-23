import ccxt
import pandas as pd
from datetime import datetime

def fetch_data(symbol, timeframe):
    ohlcv = binance.fetch_ohlcv(symbol, timeframe)
    data = []
    for entry in ohlcv:  # Remove the sorting here if you don't need the data in descending order
        timestamp = entry[0]
        dt_object = datetime.fromtimestamp(timestamp / 1000)
        if dt_object.month in range(1, 13):  # Simplified range check for month
            data.append({
                'Date': dt_object.strftime('%Y-%m-%d %H:%M:%S'),  # Adjusted time format for consistency
                'Category': 'Crypto', 
                'Symbol': symbol,
                'Open': entry[1],
                'High': entry[2],
                'Low': entry[3],
                'Close': entry[4],
                'Volume': entry[5],
            })
    return data

def read_existing_data(filepath):
    try:
        return pd.read_csv(filepath)
    except FileNotFoundError:
        return pd.DataFrame()

def merge_and_update_data(new_data, existing_data):
    new_df = pd.DataFrame(new_data)
    new_df['Date'] = pd.to_datetime(new_df['Date'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
    
    if not existing_data.empty:
        existing_data['Date'] = pd.to_datetime(existing_data['Date'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
        updated_df = pd.concat([existing_data, new_df]).drop_duplicates(['Date', 'Symbol', 'Category'], keep='last')
    else:
        updated_df = new_df
    
    return updated_df

binance = ccxt.binance()
symbols = ['BTC/USDT', 'ETH/USDT', 'XRP/USDT', 'LTC/USDT', 'BNB/USDT', 'ADA/USDT', 'XLM/USDT', 'DOGE/USDT', 'SOL/USDT']  # Add more symbols here
timeframe = '1d'
all_new_data = []

for symbol in symbols:
    symbol_data = fetch_data(symbol, timeframe)
    all_new_data.extend(symbol_data)

csv_filename = '1d_crypto_data.csv'
existing_data = read_existing_data(csv_filename)
updated_data = merge_and_update_data(all_new_data, existing_data)

# Export the updated data without sorting it by 'Date'
updated_data.to_csv(csv_filename, index=False)
print(f'Data exported to {csv_filename}')
