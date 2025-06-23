from trademasterx.utils.logger import get_logger

class SentimentAnalyzer:
    """Analyzes sentiment from news and social data."""
    def __init__(self):
        self.logger = get_logger("SentimentAnalyzer")

    def analyze(self, data):
        self.logger.info("Analyzing sentiment...")
        sentiment_data = data.get('sentiment', [])
        if not sentiment_data:
            return {"sentiment": None}
        # Simple keyword-based sentiment
        positive_keywords = ['bull', 'up', 'positive', 'gain']
        negative_keywords = ['bear', 'down', 'negative', 'loss']
        score = 0
        for text in sentiment_data:
            for word in positive_keywords:
                if word in text.lower():
                    score += 1
            for word in negative_keywords:
                if word in text.lower():
                    score -= 1
        if score > 0:
            return {"sentiment": "positive"}
        elif score < 0:
            return {"sentiment": "negative"}
        else:
            return {"sentiment": "neutral"} 