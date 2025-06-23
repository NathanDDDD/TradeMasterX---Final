from trademasterx.core.analyzers.pattern_analyzer import PatternAnalyzer
from trademasterx.core.analyzers.indicator_analyzer import IndicatorAnalyzer
from trademasterx.core.analyzers.sentiment_analyzer import SentimentAnalyzer
from trademasterx.core.analyzers.news_analyzer import NewsAnalyzer
from trademasterx.core.analyzers.copytrading_analyzer import CopyTradingAnalyzer
from trademasterx.utils.logger import get_logger

class MasterBot:
    """Aggregates signals from all analyzers and makes trading decisions."""
    def __init__(self):
        self.logger = get_logger("MasterBot")
        self.analyzers = [
            PatternAnalyzer(),
            IndicatorAnalyzer(),
            SentimentAnalyzer(),
            NewsAnalyzer(),
            CopyTradingAnalyzer()
        ]

    def aggregate_signals(self, data):
        self.logger.info("Aggregating signals from analyzers...")
        results = {}
        for analyzer in self.analyzers:
            name = analyzer.__class__.__name__
            try:
                results[name] = analyzer.analyze(data)
            except Exception as e:
                self.logger.error(f"Error in {name}: {e}")
                results[name] = None
        return results 