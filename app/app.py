import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
import os
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from breakout_strategy.data_fetcher import fetch_stock_data
from breakout_strategy.strategy import backtest_breakout_strategy_with_short

# Streamlit app setup
st.title("Breakout Strategy with Long and Short Trades")

# Input fields
stocks = st.text_input("Enter stock tickers (comma-separated, e.g., AAPL, MSFT)", "AAPL, MSFT")
start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=1825))  # Default 5 years back
end_date = st.date_input("End Date", value=datetime.now())
volume_multiplier = st.number_input("Volume Multiplier (e.g., 2 for 200%)", value=2.0)
min_daily_return = st.number_input("Minimum Daily Return (e.g., 0.02 for 2%)", value=0.02)
holding_period = st.number_input("Holding Period (days)", value=10, step=1)
trailing_stop_loss = st.number_input("Trailing Stop Loss (%) (Set 0 to disable)", value=0.0)
wait_period = st.number_input("Wait Period (days before entering trade)", value=0, step=1)

# Analyze stocks
if st.button("Analyze Strategy"):
    buy_signals = []
    for stock in stocks.split(","):
        stock = stock.strip()
        try:
            stock_data = fetch_stock_data(stock, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
            metrics = backtest_breakout_strategy_with_short(
                stock_data,
                volume_multiplier,
                min_daily_return,
                holding_period,
                trailing_stop_loss,
                wait_period
            )
            trades_df = pd.DataFrame(metrics['Trades'])
            st.write(f"Trades for {stock}:")
            st.dataframe(trades_df)

            # Display metrics
            st.write(f"Performance Metrics for {stock}:")
            st.write(f"- **Portfolio Value**: {metrics['Portfolio Value']:.2f}")
            st.write(f"- **Annualized Return**: {metrics['Annualized Return']:.2f}%")
            st.write(f"- **Max Drawdown**: {metrics['Max Drawdown (%)']:.2f}%")
            st.write(f"- **Calmar Ratio**: {metrics['Calmar Ratio']:.2f}")

            # Downloadable CSV
            csv = trades_df.to_csv(index=False)
            st.download_button(label=f"Download {stock} Trades CSV", data=csv, file_name=f"{stock}_trades.csv")
        except Exception as e:
            st.error(f"Error analyzing {stock}: {e}")
