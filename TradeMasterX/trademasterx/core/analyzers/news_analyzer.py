from trademasterx.utils.logger import get_logger

class NewsAnalyzer:
    """Analyzes news headlines for trading signals."""
    def __init__(self):
        self.logger = get_logger("NewsAnalyzer")

    def analyze(self, data):
        self.logger.info("Analyzing news...")
        news_data = data.get('news', [])
        if not news_data:
            return {"news": None}
        # Simple keyword-based news analysis
        bullish_keywords = ['record high', 'surge', 'rally', 'bull']
        bearish_keywords = ['plunge', 'selloff', 'bear', 'crash']
        score = 0
        for headline in news_data:
            for word in bullish_keywords:
                if word in headline.lower():
                    score += 1
            for word in bearish_keywords:
                if word in headline.lower():
                    score -= 1
        if score > 0:
            return {"news": "bullish"}
        elif score < 0:
            return {"news": "bearish"}
        else:
            return {"news": "neutral"} 