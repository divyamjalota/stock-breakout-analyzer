def validate_inputs(ticker, start_date, end_date, volume_threshold, price_threshold, holding_period):
    """
    Validate user inputs.

    Args:
        ticker (str): Stock ticker.
        start_date (str): Start date in 'YYYY-MM-DD' format.
        end_date (str): End date in 'YYYY-MM-DD' format.
        volume_threshold (float): Minimum volume multiplier.
        price_threshold (float): Minimum daily return.
        holding_period (int): Holding period in days.

    Returns:
        bool: True if inputs are valid, raises ValueError otherwise.
    """
    if not ticker:
        raise ValueError("Ticker cannot be empty.")
    if not 0 < volume_threshold:
        raise ValueError("Volume threshold must be greater than 0.")
    if not 0 < price_threshold:
        raise ValueError("Price threshold must be greater than 0.")
    if not holding_period > 0:
        raise ValueError("Holding period must be a positive integer.")
    return True
