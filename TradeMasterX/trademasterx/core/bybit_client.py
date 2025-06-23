import os
import ccxt
from trademasterx.utils.logger import get_logger
from trademasterx.utils.mini_log import log_event

class BybitClient:
    """Bybit exchange client for live trading operations."""
    
    def __init__(self):
        self.logger = get_logger("BybitClient")
        self.api_key = os.getenv('BYBIT_API_KEY')
        self.api_secret = os.getenv('BYBIT_API_SECRET')
        self.exchange = None
        self.is_connected = False
        
        if self.api_key and self.api_secret:
            self._initialize_exchange()
        else:
            self.logger.warning("Bybit API keys not configured. Running in demo mode.")
    
    def _initialize_exchange(self):
        """Initialize the Bybit exchange connection."""
        try:
            self.exchange = ccxt.bybit({
                'apiKey': self.api_key,
                'secret': self.api_secret,
                'sandbox': True,  # Use testnet for safety
                'enableRateLimit': True,
            })
            self.is_connected = True
            self.logger.info("Bybit client initialized successfully")
            log_event("Bybit client initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Bybit client: {e}")
            log_event(f"Bybit client initialization failed: {e}")
    
    def get_balance(self):
        """Get account balance."""
        if not self.is_connected:
            return {"error": "Bybit not connected"}
        
        try:
            balance = self.exchange.fetch_balance()
            return {
                "USDT": balance.get('USDT', {}).get('free', 0),
                "BTC": balance.get('BTC', {}).get('free', 0),
                "total": balance.get('total', {})
            }
        except Exception as e:
            self.logger.error(f"Error fetching balance: {e}")
            return {"error": str(e)}
    
    def get_ticker(self, symbol='BTC/USDT'):
        """Get current market price for a symbol."""
        if not self.is_connected:
            return {"error": "Bybit not connected"}
        
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return {
                "symbol": symbol,
                "last": ticker['last'],
                "bid": ticker['bid'],
                "ask": ticker['ask'],
                "volume": ticker['baseVolume'],
                "change": ticker['change'],
                "change_percent": ticker['percentage']
            }
        except Exception as e:
            self.logger.error(f"Error fetching ticker: {e}")
            return {"error": str(e)}
    
    def place_order(self, symbol, side, amount, order_type='market'):
        """Place a trading order."""
        if not self.is_connected:
            return {"error": "Bybit not connected"}
        
        try:
            order = self.exchange.create_order(
                symbol=symbol,
                type=order_type,
                side=side,
                amount=amount
            )
            
            self.logger.info(f"Order placed: {side} {amount} {symbol}")
            log_event(f"Order placed: {side} {amount} {symbol}")
            
            return {
                "id": order['id'],
                "symbol": order['symbol'],
                "side": order['side'],
                "amount": order['amount'],
                "status": order['status'],
                "timestamp": order['timestamp']
            }
        except Exception as e:
            self.logger.error(f"Error placing order: {e}")
            log_event(f"Order placement failed: {e}")
            return {"error": str(e)}
    
    def get_orders(self, symbol='BTC/USDT', limit=10):
        """Get recent orders."""
        if not self.is_connected:
            return {"error": "Bybit not connected"}
        
        try:
            orders = self.exchange.fetch_orders(symbol, limit=limit)
            return [{
                "id": order['id'],
                "symbol": order['symbol'],
                "side": order['side'],
                "amount": order['amount'],
                "status": order['status'],
                "timestamp": order['timestamp']
            } for order in orders]
        except Exception as e:
            self.logger.error(f"Error fetching orders: {e}")
            return {"error": str(e)}
    
    def cancel_order(self, order_id, symbol='BTC/USDT'):
        """Cancel an existing order."""
        if not self.is_connected:
            return {"error": "Bybit not connected"}
        
        try:
            result = self.exchange.cancel_order(order_id, symbol)
            self.logger.info(f"Order cancelled: {order_id}")
            log_event(f"Order cancelled: {order_id}")
            return {"success": True, "order_id": order_id}
        except Exception as e:
            self.logger.error(f"Error cancelling order: {e}")
            return {"error": str(e)}
    
    def get_status(self):
        """Get client connection status."""
        return {
            "connected": self.is_connected,
            "api_configured": bool(self.api_key and self.api_secret),
            "exchange": "bybit" if self.exchange else None
        } 