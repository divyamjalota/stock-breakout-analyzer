import pandas as pd

def backtest_breakout_strategy(
    stock_data, direction="long", volume_multiplier=2, min_daily_return=0.02, holding_period=10, trailing_stop_loss=0, wait_period=0, capital_constraint=True
):
    """
    Backtest the breakout strategy with options for long or short positions and capital constraint.

    Args:
        stock_data (DataFrame): Historical stock data.
        direction (str): "long" for long trades or "short" for short trades.
        volume_multiplier (float): Minimum volume threshold.
        min_daily_return (float): Minimum price return threshold (absolute value for both long and short).
        holding_period (int): Number of trading days to hold the investment.
        trailing_stop_loss (float): Trailing stop-loss percentage (0 to disable).
        wait_period (int): Days to wait after breakout before entering the trade.
        capital_constraint (bool): If True, allows only one active trade at a time.

    Returns:
        dict: Strategy performance metrics and trade results.
    """
    try:
        if isinstance(stock_data.columns, pd.MultiIndex):
            stock_data.columns = [col[1] for col in stock_data.columns]

        stock_data.dropna(inplace=True)

        stock_data['20_day_avg_vol'] = stock_data['Volume'].rolling(window=20).mean().shift(1)

        stock_data['Volume_Breakout'] = stock_data['Volume'] > (volume_multiplier * stock_data['20_day_avg_vol'])

        stock_data['Price_Change'] = stock_data['Close'].pct_change()
        if direction == "long":
            stock_data['Breakout'] = stock_data['Volume_Breakout'] & (stock_data['Price_Change'] > min_daily_return)
        elif direction == "short":
            stock_data['Breakout'] = stock_data['Volume_Breakout'] & (stock_data['Price_Change'] < -min_daily_return)
        else:
            raise ValueError("Invalid direction. Use 'long' or 'short'.")

        trades = []
        portfolio_value = 1.0
        max_drawdown = 0.0
        equity_curve = []
        max_equity = portfolio_value
        active_trade_end_date = None

        for i, row in stock_data.iterrows():
            if capital_constraint and active_trade_end_date and i <= active_trade_end_date:
                continue

            if row['Breakout']:
                entry_index = stock_data.index.get_loc(i) + wait_period
                if entry_index >= len(stock_data):
                    continue

                buy_date = stock_data.index[entry_index]
                buy_price = stock_data.loc[buy_date, 'Close']
                max_price_or_min_price = buy_price
                sell_price = None
                sell_date = None

                trade_days = stock_data.index.tolist()
                buy_index = trade_days.index(buy_date)

                for j in range(1, holding_period + 1):
                    if buy_index + j < len(trade_days):
                        current_date = trade_days[buy_index + j]
                        current_price = stock_data.loc[current_date, 'Close']

                        if direction == "long":
                            max_price_or_min_price = max(max_price_or_min_price, current_price)
                            if trailing_stop_loss > 0 and current_price < max_price_or_min_price * (1 - trailing_stop_loss / 100):
                                sell_date = current_date
                                sell_price = current_price
                                break
                        elif direction == "short":
                            max_price_or_min_price = min(max_price_or_min_price, current_price)
                            if trailing_stop_loss > 0 and current_price > max_price_or_min_price * (1 + trailing_stop_loss / 100):
                                sell_date = current_date
                                sell_price = current_price
                                break
                    else:
                        break

                if not sell_price:
                    if buy_index + holding_period < len(trade_days):
                        sell_date = trade_days[buy_index + holding_period]
                        sell_price = stock_data.loc[sell_date, 'Close']

                if sell_date and sell_price:
                    if direction == "long":
                        return_pct = ((sell_price - buy_price) / buy_price)
                    else:
                        return_pct = ((buy_price - sell_price) / buy_price)

                    trades.append({
                        'Trade Type': direction.capitalize(),
                        'Buy Date': buy_date.strftime('%Y-%m-%d'),
                        'Sell Date': sell_date.strftime('%Y-%m-%d'),
                        'Buy Price': buy_price,
                        'Sell Price': sell_price,
                        'Return (%)': return_pct * 100
                    })
                    portfolio_value *= (1 + return_pct)
                    equity_curve.append(portfolio_value)

                    max_equity = max(max_equity, portfolio_value)
                    drawdown = (max_equity - portfolio_value) / max_equity if max_equity > 0 else 0
                    max_drawdown = max(max_drawdown, drawdown)

                    if capital_constraint:
                        active_trade_end_date = sell_date

        total_years = (stock_data.index[-1] - stock_data.index[0]).days / 365.0
        annualized_return = (portfolio_value ** (1 / total_years)) - 1
        calmar_ratio = annualized_return / max_drawdown if max_drawdown > 0 else float('inf')

        return {
            'Trades': trades,
            'Portfolio Value': portfolio_value,
            'Annualized Return': annualized_return * 100,
            'Max Drawdown (%)': max_drawdown * 100,
            'Calmar Ratio': calmar_ratio,
        }

    except Exception as e:
        raise RuntimeError(f"Error analyzing stock data: {e}")