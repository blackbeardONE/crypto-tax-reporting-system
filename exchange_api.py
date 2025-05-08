def fetch_mock_transactions(address):
    """
    Return mock transaction data for the given address.
    This is used when no real API key is configured.
    """
    # Example mock data structure
    return [
        {
            "type": "buy",
            "asset": "ETH",
            "amount": 1.0,
            "price": 1000.0,
            "timestamp": 1650000000
        },
        {
            "type": "sell",
            "asset": "ETH",
            "amount": 0.5,
            "price": 1500.0,
            "timestamp": 1650003600
        }
    ]
