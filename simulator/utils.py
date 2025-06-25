import yfinance as yf
import numpy as np
import pandas as pd

# Funcție pentru a obține date istorice pentru un simbol
import yfinance as yf
import pandas as pd

import yfinance as yf
import pandas as pd

def get_historical_data(symbol, start_date, end_date):
    """
    Obține date istorice ajustate pentru simbol, randamente anuale.
    """
    data = yf.download(symbol, start="1994-01-01", end="2024-12-31", auto_adjust=True, progress=False)

    if data.empty:
        raise ValueError(f"Nu s-au găsit date pentru simbolul {symbol}")

    if 'Close' not in data.columns:
        raise ValueError(f"Coloana 'Close' nu există în datele pentru {symbol}")

    df = data[['Close']].copy()

    # Randamente anuale
    df = df.resample('YE').last()
    df['Annual Return (%)'] = df['Close'].pct_change() * 100

    print(f"\n📈 Randamente anuale pentru {symbol}:")
    for date, val in df['Annual Return (%)'].dropna().items():
        print(f"  {date.year}: {val:.2f}%")

    return df
