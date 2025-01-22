import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
import yfinance as yf
import os
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from breakout_strategy.data_fetcher import fetch_stock_data
from breakout_strategy.strategy import backtest_breakout_strategy

# Streamlit app setup
st.title("Stock Breakout Strategy")

ticker = st.text_input("Enter stock ticker:", value="AAPL")
start_date = st.date_input("Start Date", value=pd.to_datetime("2023-01-01"))
end_date = st.date_input("End Date", value=pd.to_datetime("2023-12-31"))

direction = st.radio("Select Direction:", ("long", "short"))
volume_multiplier = float(st.text_input("Volume Multiplier:", value="2"))
min_daily_return = float(st.text_input("Minimum Daily Return (%):", value="2.0")) / 100
holding_period = int(st.text_input("Holding Period (Days):", value="10"))
trailing_stop_loss = float(st.text_input("Trailing Stop Loss (%):", value="0.0"))
wait_period = int(st.text_input("Wait Period (Days):", value="0"))
capital_constraint = st.checkbox("Apply Capital Constraint", value=True)

if st.button("Run Strategy"):
    try:
        data = yf.download(ticker, start=start_date, end=end_date,group_by="ticker")

        if data.empty:
            st.error("No data found for the specified ticker and date range.")
        else:
            results = backtest_breakout_strategy(
                data,
                direction=direction,
                volume_multiplier=volume_multiplier,
                min_daily_return=min_daily_return,
                holding_period=holding_period,
                trailing_stop_loss=trailing_stop_loss,
                wait_period=wait_period,
                capital_constraint=capital_constraint
            )

            st.subheader("Trades")
            trades_df = pd.DataFrame(results['Trades'])
            st.dataframe(trades_df)

            csv = trades_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                    label="Download Trades as CSV",
                    data=csv,
                    file_name="trades.csv",
                    mime="text/csv"
            )

            st.subheader("Performance Metrics")
            st.write(f"**Portfolio Value:** {results['Portfolio Value']:.2f}")
            st.write(f"**Annualized Return:** {results['Annualized Return']:.2f}%")
            st.write(f"**Max Drawdown:** {results['Max Drawdown (%)']:.2f}%")
            st.write(f"**Calmar Ratio:** {results['Calmar Ratio']:.2f}")
    except Exception as e:
        st.error(f"An error occurred: {e}")



