import unittest
from trademasterx.core.analyzers.pattern_analyzer import PatternAnalyzer
from trademasterx.core.analyzers.indicator_analyzer import IndicatorAnalyzer
from trademasterx.core.analyzers.sentiment_analyzer import SentimentAnalyzer
from trademasterx.core.analyzers.news_analyzer import NewsAnalyzer
from trademasterx.core.analyzers.copytrading_analyzer import CopyTradingAnalyzer

class TestAnalyzers(unittest.TestCase):
    def test_pattern_analyzer(self):
        analyzer = PatternAnalyzer()
        self.assertEqual(analyzer.analyze({'price': [1,2,3]})['pattern'], '3-bar bullish')
        self.assertEqual(analyzer.analyze({'price': [3,2,1]})['pattern'], '3-bar bearish')
        self.assertIsNone(analyzer.analyze({'price': [1,2]})['pattern'])

    def test_indicator_analyzer(self):
        analyzer = IndicatorAnalyzer()
        # Not enough data for RSI
        self.assertIsNone(analyzer.analyze({'price': [1]*10})['indicator'])
        # Enough data for RSI
        result = analyzer.analyze({'price': list(range(1, 20))})
        self.assertIn('sma_3', result)
        self.assertIn('rsi_14', result)

    def test_sentiment_analyzer(self):
        analyzer = SentimentAnalyzer()
        self.assertEqual(analyzer.analyze({'sentiment': ['bullish rally']})['sentiment'], 'positive')
        self.assertEqual(analyzer.analyze({'sentiment': ['bearish crash']})['sentiment'], 'negative')
        self.assertEqual(analyzer.analyze({'sentiment': ['neutral']})['sentiment'], 'neutral')

    def test_news_analyzer(self):
        analyzer = NewsAnalyzer()
        self.assertEqual(analyzer.analyze({'news': ['record high']})['news'], 'bullish')
        self.assertEqual(analyzer.analyze({'news': ['plunge']})['news'], 'bearish')
        self.assertEqual(analyzer.analyze({'news': ['no change']})['news'], 'neutral')

    def test_copytrading_analyzer(self):
        analyzer = CopyTradingAnalyzer()
        self.assertIsNone(analyzer.analyze({}))

if __name__ == '__main__':
    unittest.main() 