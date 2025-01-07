import yfinance as yf
from datetime import datetime, timedelta

def fetch_stock_data(ticker, start_date, group_by="ticker"):
    """
    Fetch historical stock data for a specific ticker.
    """
    try:
        data = yf.download(ticker, start=start_date, group_by=group_by,timeout=60)
        if data.empty:
            raise ValueError(f"No data available for {ticker}.")
        return data
    except Exception as e:
        raise RuntimeError(f"Error fetching data for {ticker}: {e}")
