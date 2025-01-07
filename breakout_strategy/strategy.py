import pandas as pd

def check_breakout_signals(stock_data, volume_multiplier=2, min_daily_return=0.02, holding_period=10):
    """
    Analyze stock data for breakout signals and calculate returns over a holding period.

    Args:
        stock_data (DataFrame): Historical stock data.
        volume_multiplier (float): Minimum volume threshold.
        min_daily_return (float): Minimum price return threshold.
        holding_period (int): Number of **trading days** to hold the investment.

    Returns:
        DataFrame: Breakout signals with calculated returns.
    """
    try:
        # Simplify multi-level columns if present
        if isinstance(stock_data.columns, pd.MultiIndex):
            stock_data.columns = [col[1] for col in stock_data.columns]

        # Drop rows with missing data
        stock_data.dropna(inplace=True)

        # Calculate the 20-day rolling average volume (exclude today by shifting)
        stock_data['20_day_avg_vol'] = stock_data['Volume'].rolling(window=20).mean().shift(1)

        # Volume breakout condition
        stock_data['Volume_Breakout'] = stock_data['Volume'] > (volume_multiplier * stock_data['20_day_avg_vol'])

        # Price breakout condition
        stock_data['Price_Change'] = stock_data['Close'].pct_change()
        stock_data['Price_Breakout'] = stock_data['Price_Change'] > min_daily_return

        # Identify breakout days
        stock_data['Breakout Day'] = stock_data['Volume_Breakout'] & stock_data['Price_Breakout']

        results = []
        for i, row in stock_data[stock_data['Breakout Day']].iterrows():
            buy_date = i
            buy_price = row['Close']

            # Adjust sell date for trading days only
            trade_days = stock_data.index.tolist()
            buy_index = trade_days.index(buy_date)
            sell_index = buy_index + holding_period

            if sell_index < len(trade_days):
                sell_date = trade_days[sell_index]
                sell_price = stock_data.loc[sell_date, 'Close']
                return_pct = ((sell_price - buy_price) / buy_price) * 100
                results.append({
                    'Buy Date': buy_date.strftime('%Y-%m-%d'),
                    'Sell Date': sell_date.strftime('%Y-%m-%d'),
                    'Buy Price': buy_price,
                    'Sell Price': sell_price,
                    'Return (%)': return_pct
                })

        return pd.DataFrame(results)

    except Exception as e:
        raise RuntimeError(f"Error analyzing stock data: {e}")


   