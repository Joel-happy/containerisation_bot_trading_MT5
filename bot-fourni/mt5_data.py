# mt5_data.py
import MetaTrader5 as mt5
import pandas as pd

def get_candles(symbol: str, timeframe: int, num_bars: int = None, from_date=None, to_date=None):
    if from_date and to_date:
        from_timestamp = pd.Timestamp(from_date).timestamp()
        to_timestamp = pd.Timestamp(to_date).timestamp()
        rates = mt5.copy_rates_range(symbol, timeframe, from_timestamp, to_timestamp)
    else:
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, num_bars or 100)

    if rates is None:
        print(f"Erreur récupération des bougies pour {symbol}")
        return None

    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    return df
