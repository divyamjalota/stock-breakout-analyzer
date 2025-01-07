import pandas as pd
from breakout_strategy.strategy import breakout_strategy

def test_breakout_strategy():
    data = pd.DataFrame({
        "Volume": [100, 200, 300, 400, 500],
        "Close": [10, 11, 12, 13, 14],
        "20-Day Avg Volume": [90, 95, 100, 105, 110]
    })
    data['Price Change (%)'] = data['Close'].pct_change() * 100
    results = breakout_strategy(data, 1.5, 2.0, 2)
    assert isinstance(results, pd.DataFrame)
