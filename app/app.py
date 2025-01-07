import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from breakout_strategy.data_fetcher import fetch_stock_data
from breakout_strategy.strategy import check_breakout_signals

# Streamlit app setup
st.title("Stock Breakout Monitor with Returns Analysis")

# Input fields
stocks = st.text_input("Enter stock tickers (comma-separated, e.g., AAPL, MSFT)", "AAPL, MSFT")
start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=60))
end_date = st.date_input("End Date", value=datetime.now())
volume_multiplier = st.number_input("Volume Multiplier (e.g., 2 for 200%)", value=2.0)
min_daily_return = st.number_input("Minimum Daily Return (e.g., 0.02 for 2%)", value=0.02)
holding_period = st.number_input("Holding Period (days)", value=10, step=1)

# Analyze stocks
if st.button("Analyze Breakouts"):
    buy_signals = []
    for stock in stocks.split(","):
        stock = stock.strip()
        try:
            stock_data = fetch_stock_data(stock, start_date.strftime("%Y-%m-%d"), group_by="ticker")
            signals = check_breakout_signals(stock_data, volume_multiplier, min_daily_return, holding_period)
            if not signals.empty:
                signals['Stock'] = stock
                buy_signals.append(signals)
        except Exception as e:
            st.error(f"Error analyzing {stock}: {e}")

    # Display results
    if buy_signals:
        combined_results = pd.concat(buy_signals)
        st.write("Breakout Signals with Returns:")
        st.dataframe(combined_results)

        # Downloadable CSV
        csv = combined_results.to_csv(index=False)
        st.download_button(label="Download CSV", data=csv, file_name="breakout_signals_with_returns.csv")
    else:
        st.write("No breakout signals found.")
