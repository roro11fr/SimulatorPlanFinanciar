import yfinance as yf
import numpy as np
import pandas as pd

# Funcție pentru a obține date istorice pentru un simbol
def get_historical_data(symbol, start_date, end_date):
    """
    Obține date istorice pentru un simbol specificat (ex: '^GSPC' pentru S&P 500)
    """
    ticker = "^GSPC"  # Simbolul S&P 500
    data = yf.download(ticker, start="2013-01-01", end="2023-01-01")

    print(f"Columns in historical data: {data.columns}")  # Verifică ce coloane sunt disponibile

    return data

