from trademasterx.utils.logger import get_logger
import pandas as pd
import pandas_ta as ta

class IndicatorAnalyzer:
    """Analyzes technical indicators in market data."""
    def __init__(self):
        self.logger = get_logger("IndicatorAnalyzer")

    def analyze(self, data):
        self.logger.info("Analyzing indicators...")
        prices = data.get('price', [])
        if len(prices) < 14:
            return {"indicator": None}
        df = pd.DataFrame({'close': prices})
        df['sma_3'] = ta.sma(df['close'], length=3)
        df['rsi_14'] = ta.rsi(df['close'], length=14)
        return {
            "sma_3": df['sma_3'].iloc[-1],
            "rsi_14": df['rsi_14'].iloc[-1]
        } 