import pandas as pd
import numpy as np
from trademasterx.utils.logger import get_logger

class VolatilityAnalyzer:
    """Analyzes market volatility patterns and indicators."""
    
    def __init__(self):
        self.logger = get_logger("VolatilityAnalyzer")
    
    def analyze(self, data):
        """Analyze volatility patterns in market data."""
        self.logger.info("Analyzing volatility...")
        
        prices = data.get('price', [])
        if len(prices) < 20:
            return {"volatility": None}
        
        # Calculate various volatility measures
        returns = pd.Series(prices).pct_change().dropna()
        
        # Historical volatility (20-period)
        hist_vol = returns.rolling(window=20).std().iloc[-1] * np.sqrt(252) * 100
        
        # Realized volatility (current period)
        realized_vol = returns.std() * np.sqrt(252) * 100
        
        # Volatility ratio (current vs historical)
        vol_ratio = realized_vol / hist_vol if hist_vol > 0 else 1
        
        # Volatility regime classification
        if realized_vol < 20:
            regime = "low"
        elif realized_vol < 40:
            regime = "medium"
        else:
            regime = "high"
        
        return {
            "historical_volatility": round(hist_vol, 2),
            "realized_volatility": round(realized_vol, 2),
            "volatility_ratio": round(vol_ratio, 2),
            "regime": regime,
            "volatility_trend": "increasing" if vol_ratio > 1.2 else "decreasing" if vol_ratio < 0.8 else "stable"
        } 