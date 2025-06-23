class BybitClient:
    """Bybit API client supporting testnet and live trading."""
    def __init__(self, config):
        self.config = config
        self.testnet = config.get('testnet', True)
        self.api_key = config.get('api_key', 'demo')
        self.api_secret = config.get('api_secret', 'demo')
        self.base_url = 'https://api-testnet.bybit.com' if self.testnet else 'https://api.bybit.com'

    def get_market_data(self, symbol):
        """Stub: Return fake market data."""
        return {"price": 100, "volume": 1000}

    def place_order(self, symbol, action, quantity):
        """Stub: Print order action and endpoint."""
        print(f"Placing {action} order for {quantity} {symbol} on {'testnet' if self.testnet else 'live'} ({self.base_url})") 