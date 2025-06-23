from trademasterx.core.analyzers.pattern_analyzer import PatternAnalyzer
from trademasterx.core.analyzers.indicator_analyzer import IndicatorAnalyzer
from trademasterx.core.analyzers.sentiment_analyzer import SentimentAnalyzer
from trademasterx.core.analyzers.news_analyzer import NewsAnalyzer
from trademasterx.core.analyzers.copytrading_analyzer import CopyTradingAnalyzer
from trademasterx.core.ai_assistant import AIAssistant
from trademasterx.core.emergency_control import EmergencyControl
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
        self.ai_assistant = AIAssistant()
        self.emergency_control = EmergencyControl()

    def aggregate_signals(self, data):
        """Aggregate signals from all analyzers with emergency control check."""
        if not self.emergency_control.can_trade():
            self.logger.warning("Trading blocked by emergency stop")
            return {"error": "Trading blocked by emergency stop"}
            
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
    
    def get_ai_advice(self, market_data, question):
        """Get AI trading advice."""
        return self.ai_assistant.get_trading_advice(market_data, question)
    
    def emergency_stop(self):
        """Activate emergency stop."""
        return self.emergency_control.emergency_stop()
    
    def reset_emergency_stop(self):
        """Reset emergency stop."""
        return self.emergency_control.reset_emergency_stop()
    
    def get_system_status(self):
        """Get comprehensive system status."""
        return {
            "emergency_control": self.emergency_control.get_status(),
            "analyzers_count": len(self.analyzers),
            "ai_available": bool(self.ai_assistant.anthropic_api_key or self.ai_assistant.openai_api_key)
        } 