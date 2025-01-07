from breakout_strategy.data_fetcher import fetch_stock_data

def test_fetch_stock_data():
    data = fetch_stock_data("AAPL", "2023-01-01", "2023-01-31")
    assert not data.empty
    assert "20-Day Avg Volume" in data.columns
