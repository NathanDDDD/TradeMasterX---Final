"""
Market Analysis Bot Module
Provides market analysis functionality for TradeMasterX
"""

from .analytics_bot import AnalyticsBot

class MarketAnalysisBot(AnalyticsBot):
    """Market Analysis Bot - extends AnalyticsBot with market-specific functionality"""
    
    def __init__(self, config=None):
        super().__init__(config)
        self.bot_type = "market_analysis"
        self.name = "Market Analysis Bot"
        
    def analyze_market_trends(self):
        """Analyze current market trends"""
        return self.get_market_analysis()
        
    def get_support_resistance(self, symbol):
        """Get support and resistance levels"""
        return self.analyze_price_levels(symbol)

# Export the bot for registration
__all__ = ['MarketAnalysisBot']
