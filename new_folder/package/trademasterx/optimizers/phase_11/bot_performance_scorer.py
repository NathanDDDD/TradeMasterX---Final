"""
TradeMasterX 2.0 - Phase 11: Bot Performance Scorer
Tracks individual bot performance and maintains reliability scores
"""

import json
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import asyncio


@dataclass
class BotReliabilityMetrics:
    """Bot reliability metrics structure"""
    bot_id: str
    total_predictions: int
    correct_predictions: int
    accuracy_rate: float
    average_confidence: float
    confidence_accuracy_correlation: float
    win_rate: float
    average_return: float
    sharpe_ratio: float
    max_drawdown: float
    uptime_percentage: float
    error_count: int
    last_active: str
    reliability_score: float
    trend: str  # 'improving', 'stable', 'declining'
    rank: int


@dataclass
class BotPerformanceSnapshot:
    """Single performance snapshot for trend analysis"""
    timestamp: str
    accuracy: float
    win_rate: float
    return_rate: float
    confidence: float
    reliability_score: float


class BotPerformanceScorer:
    """
    Tracks individual bot performance and maintains comprehensive reliability scores.
    Analyzes bot accuracy, confidence calibration, uptime, and error patterns.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize BotPerformanceScorer"""
        self.config = config or {}
        self.logger = self._setup_logging()
        
        # File paths
        self.data_dir = Path(self.config.get('data_dir', 'reports'))
        self.data_dir.mkdir(exist_ok=True)
        
        self.scores_file = self.data_dir / 'bot_reliability_scores.json'
        self.performance_history_file = self.data_dir / 'bot_performance_history.json'
        self.bot_errors_file = self.data_dir / 'bot_errors.json'
        
        # Performance thresholds
        self.thresholds = {
            'excellent_accuracy': 0.85,
            'good_accuracy': 0.70,
            'poor_accuracy': 0.50,
            'excellent_win_rate': 0.65,
            'good_win_rate': 0.55,
            'poor_win_rate': 0.45,
            'min_predictions': 10,
            'lookback_hours': 24
        }
        
        # Bot tracking data
        self.bot_scores: Dict[str, BotReliabilityMetrics] = {}
        self.performance_history: Dict[str, List[BotPerformanceSnapshot]] = {}
        self.bot_errors: Dict[str, List[Dict]] = {}
        
        # Load existing data
        self._load_existing_data()
        
        self.logger.info("BotPerformanceScorer initialized successfully")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for BotPerformanceScorer"""
        logger = logging.getLogger("BotPerformanceScorer")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _load_existing_data(self):
        """Load existing bot performance data"""
        try:
            # Load reliability scores
            if self.scores_file.exists():
                with open(self.scores_file, 'r') as f:
                    scores_data = json.load(f)
                    for bot_id, data in scores_data.items():
                        self.bot_scores[bot_id] = BotReliabilityMetrics(**data)
                self.logger.info(f"Loaded {len(self.bot_scores)} bot reliability scores")
            
            # Load performance history
            if self.performance_history_file.exists():
                with open(self.performance_history_file, 'r') as f:
                    history_data = json.load(f)
                    for bot_id, snapshots in history_data.items():
                        self.performance_history[bot_id] = [
                            BotPerformanceSnapshot(**snapshot) for snapshot in snapshots
                        ]
                self.logger.info(f"Loaded performance history for {len(self.performance_history)} bots")
            
            # Load error tracking
            if self.bot_errors_file.exists():
                with open(self.bot_errors_file, 'r') as f:
                    self.bot_errors = json.load(f)
                self.logger.info(f"Loaded error history for {len(self.bot_errors)} bots")
                
        except Exception as e:
            self.logger.error(f"Error loading existing data: {e}")
    
    def _save_data(self):
        """Save all bot performance data"""
        try:
            # Save reliability scores
            scores_data = {
                bot_id: asdict(metrics) for bot_id, metrics in self.bot_scores.items()
            }
            with open(self.scores_file, 'w') as f:
                json.dump(scores_data, f, indent=2)
            
            # Save performance history
            history_data = {
                bot_id: [asdict(snapshot) for snapshot in snapshots]
                for bot_id, snapshots in self.performance_history.items()
            }
            with open(self.performance_history_file, 'w') as f:
                json.dump(history_data, f, indent=2)
            
            # Save error tracking
            with open(self.bot_errors_file, 'w') as f:
                json.dump(self.bot_errors, f, indent=2)
                
            self.logger.info("Bot performance data saved successfully")
            
        except Exception as e:
            self.logger.error(f"Error saving data: {e}")
    
    def record_bot_prediction(self, bot_id: str, prediction_data: Dict[str, Any]):
        """Record a bot prediction for later scoring"""
        try:
            timestamp = datetime.now().isoformat()
            
            # Initialize bot tracking if needed
            if bot_id not in self.bot_scores:
                self._initialize_bot_tracking(bot_id)
            
            # Store prediction data for later scoring
            prediction_record = {
                'timestamp': timestamp,
                'prediction': prediction_data,
                'scored': False
            }
            
            # You might want to store this temporarily until trade outcome is known
            # For now, we'll update the last_active timestamp
            self.bot_scores[bot_id].last_active = timestamp
            
            self.logger.debug(f"Recorded prediction for bot {bot_id}")
            
        except Exception as e:
            self.logger.error(f"Error recording prediction for {bot_id}: {e}")
    
    def score_bot_prediction(self, bot_id: str, prediction_data: Dict[str, Any], 
                           trade_outcome: Dict[str, Any]):
        """Score a bot prediction against actual trade outcome"""
        try:
            if bot_id not in self.bot_scores:
                self._initialize_bot_tracking(bot_id)
            
            metrics = self.bot_scores[bot_id]
            
            # Extract prediction details
            predicted_signal = prediction_data.get('signal')
            confidence = prediction_data.get('confidence', 0.5)
            expected_return = prediction_data.get('expected_return', 0)
            
            # Extract trade outcome
            actual_signal = trade_outcome.get('signal')
            actual_return = trade_outcome.get('actual_return', 0)
            was_profitable = actual_return > 0
            
            # Update prediction counters
            metrics.total_predictions += 1
            
            # Check if prediction was correct
            prediction_correct = (predicted_signal == actual_signal)
            if prediction_correct:
                metrics.correct_predictions += 1
            
            # Update win rate tracking
            if was_profitable:
                win_count = int(metrics.win_rate * (metrics.total_predictions - 1))
                metrics.win_rate = (win_count + 1) / metrics.total_predictions
            else:
                win_count = int(metrics.win_rate * (metrics.total_predictions - 1))
                metrics.win_rate = win_count / metrics.total_predictions
            
            # Update accuracy rate
            metrics.accuracy_rate = metrics.correct_predictions / metrics.total_predictions
            
            # Update average confidence
            total_confidence = metrics.average_confidence * (metrics.total_predictions - 1)
            metrics.average_confidence = (total_confidence + confidence) / metrics.total_predictions
            
            # Update average return
            total_return = metrics.average_return * (metrics.total_predictions - 1)
            metrics.average_return = (total_return + actual_return) / metrics.total_predictions
            
            # Calculate reliability score
            metrics.reliability_score = self._calculate_reliability_score(metrics)
            
            # Update performance snapshot
            self._add_performance_snapshot(bot_id, metrics)
            
            # Update trend analysis
            metrics.trend = self._analyze_performance_trend(bot_id)
            
            self.logger.info(f"Scored prediction for {bot_id}: "
                           f"Accuracy={metrics.accuracy_rate:.3f}, "
                           f"Reliability={metrics.reliability_score:.3f}")
            
        except Exception as e:
            self.logger.error(f"Error scoring prediction for {bot_id}: {e}")
    
    def record_bot_error(self, bot_id: str, error_type: str, error_message: str, 
                        severity: str = "medium"):
        """Record a bot error for reliability tracking"""
        try:
            if bot_id not in self.bot_scores:
                self._initialize_bot_tracking(bot_id)
            
            timestamp = datetime.now().isoformat()
            
            # Update error count
            self.bot_scores[bot_id].error_count += 1
            
            # Store error details
            if bot_id not in self.bot_errors:
                self.bot_errors[bot_id] = []
            
            error_record = {
                'timestamp': timestamp,
                'error_type': error_type,
                'message': error_message,
                'severity': severity
            }
            
            self.bot_errors[bot_id].append(error_record)
            
            # Keep only last 100 errors per bot
            if len(self.bot_errors[bot_id]) > 100:
                self.bot_errors[bot_id] = self.bot_errors[bot_id][-100:]
            
            # Recalculate reliability score
            metrics = self.bot_scores[bot_id]
            metrics.reliability_score = self._calculate_reliability_score(metrics)
            
            self.logger.warning(f"Recorded {severity} error for {bot_id}: {error_type}")
            
        except Exception as e:
            self.logger.error(f"Error recording bot error for {bot_id}: {e}")
    
    def update_bot_uptime(self, bot_id: str, is_active: bool):
        """Update bot uptime percentage"""
        try:
            if bot_id not in self.bot_scores:
                self._initialize_bot_tracking(bot_id)
            
            timestamp = datetime.now().isoformat()
            metrics = self.bot_scores[bot_id]
            
            if is_active:
                metrics.last_active = timestamp
                # For simplicity, we'll track uptime as a simple percentage
                # In a real implementation, you'd track actual uptime periods
                if metrics.uptime_percentage < 100:
                    metrics.uptime_percentage = min(100, metrics.uptime_percentage + 0.1)
            else:
                # Slight decrease in uptime if bot goes inactive
                metrics.uptime_percentage = max(0, metrics.uptime_percentage - 0.05)
            
            # Recalculate reliability score
            metrics.reliability_score = self._calculate_reliability_score(metrics)
            
        except Exception as e:
            self.logger.error(f"Error updating uptime for {bot_id}: {e}")
    
    def _initialize_bot_tracking(self, bot_id: str):
        """Initialize tracking for a new bot"""
        self.bot_scores[bot_id] = BotReliabilityMetrics(
            bot_id=bot_id,
            total_predictions=0,
            correct_predictions=0,
            accuracy_rate=0.0,
            average_confidence=0.5,
            confidence_accuracy_correlation=0.0,
            win_rate=0.0,
            average_return=0.0,
            sharpe_ratio=0.0,
            max_drawdown=0.0,
            uptime_percentage=100.0,
            error_count=0,
            last_active=datetime.now().isoformat(),
            reliability_score=0.5,
            trend='stable',
            rank=0
        )
        
        self.performance_history[bot_id] = []
        self.bot_errors[bot_id] = []
        
        self.logger.info(f"Initialized tracking for bot {bot_id}")
    
    def _calculate_reliability_score(self, metrics: BotReliabilityMetrics) -> float:
        """Calculate comprehensive reliability score for a bot"""
        try:
            if metrics.total_predictions < self.thresholds['min_predictions']:
                return 0.5  # Default score for new bots
            
            # Component weights
            weights = {
                'accuracy': 0.30,
                'win_rate': 0.25,
                'confidence_calibration': 0.15,
                'uptime': 0.15,
                'error_rate': 0.10,
                'consistency': 0.05
            }
            
            # Accuracy score (0-1)
            accuracy_score = min(1.0, metrics.accuracy_rate / self.thresholds['excellent_accuracy'])
            
            # Win rate score (0-1)
            win_rate_score = min(1.0, metrics.win_rate / self.thresholds['excellent_win_rate'])
            
            # Confidence calibration (how well confidence matches accuracy)
            conf_diff = abs(metrics.average_confidence - metrics.accuracy_rate)
            confidence_score = max(0, 1.0 - (conf_diff * 2))  # Penalty for miscalibration
            
            # Uptime score (0-1)
            uptime_score = metrics.uptime_percentage / 100.0
            
            # Error rate score (0-1) - fewer errors = higher score
            max_allowed_errors = max(10, metrics.total_predictions * 0.1)
            error_score = max(0, 1.0 - (metrics.error_count / max_allowed_errors))
            
            # Consistency score based on trend
            trend_scores = {'improving': 1.0, 'stable': 0.8, 'declining': 0.4}
            consistency_score = trend_scores.get(metrics.trend, 0.6)
            
            # Calculate weighted score
            reliability_score = (
                accuracy_score * weights['accuracy'] +
                win_rate_score * weights['win_rate'] +
                confidence_score * weights['confidence_calibration'] +
                uptime_score * weights['uptime'] +
                error_score * weights['error_rate'] +
                consistency_score * weights['consistency']
            )
            
            return min(1.0, max(0.0, reliability_score))
            
        except Exception as e:
            self.logger.error(f"Error calculating reliability score: {e}")
            return 0.5
    
    def _add_performance_snapshot(self, bot_id: str, metrics: BotReliabilityMetrics):
        """Add a performance snapshot for trend analysis"""
        try:
            timestamp = datetime.now().isoformat()
            
            snapshot = BotPerformanceSnapshot(
                timestamp=timestamp,
                accuracy=metrics.accuracy_rate,
                win_rate=metrics.win_rate,
                return_rate=metrics.average_return,
                confidence=metrics.average_confidence,
                reliability_score=metrics.reliability_score
            )
            
            if bot_id not in self.performance_history:
                self.performance_history[bot_id] = []
            
            self.performance_history[bot_id].append(snapshot)
            
            # Keep only last 100 snapshots
            if len(self.performance_history[bot_id]) > 100:
                self.performance_history[bot_id] = self.performance_history[bot_id][-100:]
                
        except Exception as e:
            self.logger.error(f"Error adding performance snapshot for {bot_id}: {e}")
    
    def _analyze_performance_trend(self, bot_id: str) -> str:
        """Analyze performance trend for a bot"""
        try:
            if bot_id not in self.performance_history:
                return 'stable'
            
            history = self.performance_history[bot_id]
            
            if len(history) < 5:
                return 'stable'
            
            # Look at last 10 snapshots for trend
            recent_snapshots = history[-10:]
            reliability_scores = [s.reliability_score for s in recent_snapshots]
            
            # Calculate trend slope
            x = np.arange(len(reliability_scores))
            slope = np.polyfit(x, reliability_scores, 1)[0]
            
            if slope > 0.01:
                return 'improving'
            elif slope < -0.01:
                return 'declining'
            else:
                return 'stable'
                
        except Exception as e:
            self.logger.error(f"Error analyzing trend for {bot_id}: {e}")
            return 'stable'
    
    def rank_bots(self) -> List[BotReliabilityMetrics]:
        """Rank all bots by reliability score"""
        try:
            # Filter bots with minimum predictions
            qualified_bots = [
                metrics for metrics in self.bot_scores.values()
                if metrics.total_predictions >= self.thresholds['min_predictions']
            ]
            
            # Sort by reliability score
            ranked_bots = sorted(qualified_bots, key=lambda x: x.reliability_score, reverse=True)
            
            # Update rank in metrics
            for i, bot_metrics in enumerate(ranked_bots):
                self.bot_scores[bot_metrics.bot_id].rank = i + 1
            
            self.logger.info(f"Ranked {len(ranked_bots)} qualified bots")
            return ranked_bots
            
        except Exception as e:
            self.logger.error(f"Error ranking bots: {e}")
            return []
    
    def get_top_performers(self, limit: int = 5) -> List[BotReliabilityMetrics]:
        """Get top performing bots"""
        ranked_bots = self.rank_bots()
        return ranked_bots[:limit]
    
    def get_underperformers(self, threshold: float = 0.4) -> List[BotReliabilityMetrics]:
        """Get bots with reliability scores below threshold"""
        return [
            metrics for metrics in self.bot_scores.values()
            if metrics.reliability_score < threshold and 
               metrics.total_predictions >= self.thresholds['min_predictions']
        ]
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive bot performance report"""
        try:
            ranked_bots = self.rank_bots()
            
            report = {
                'timestamp': datetime.now().isoformat(),
                'total_bots': len(self.bot_scores),
                'qualified_bots': len(ranked_bots),
                'summary_statistics': {
                    'average_reliability': np.mean([b.reliability_score for b in ranked_bots]) if ranked_bots else 0,
                    'average_accuracy': np.mean([b.accuracy_rate for b in ranked_bots]) if ranked_bots else 0,
                    'average_win_rate': np.mean([b.win_rate for b in ranked_bots]) if ranked_bots else 0,
                    'total_predictions': sum(b.total_predictions for b in ranked_bots),
                    'total_errors': sum(b.error_count for b in self.bot_scores.values())
                },
                'top_performers': [asdict(bot) for bot in ranked_bots[:5]],
                'underperformers': [asdict(bot) for bot in self.get_underperformers()],
                'trending_up': [
                    asdict(bot) for bot in ranked_bots if bot.trend == 'improving'
                ][:3],
                'trending_down': [
                    asdict(bot) for bot in ranked_bots if bot.trend == 'declining'
                ][:3],
                'recommendations': self._generate_recommendations(ranked_bots)
            }
            
            self.logger.info("Generated comprehensive performance report")
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating performance report: {e}")
            return {}
    
    def _generate_recommendations(self, ranked_bots: List[BotReliabilityMetrics]) -> List[str]:
        """Generate performance improvement recommendations"""
        recommendations = []
        
        try:
            if not ranked_bots:
                recommendations.append("No qualified bots found - need more prediction data")
                return recommendations
            
            # Overall system recommendations
            avg_reliability = np.mean([b.reliability_score for b in ranked_bots])
            if avg_reliability < 0.6:
                recommendations.append("Overall bot reliability is low - consider retraining or strategy review")
            
            # Top performer insights
            top_bot = ranked_bots[0]
            if top_bot.reliability_score > 0.8:
                recommendations.append(f"Bot {top_bot.bot_id} shows excellent performance - consider increasing allocation")
            
            # Underperformer alerts
            underperformers = self.get_underperformers()
            if len(underperformers) > len(ranked_bots) * 0.3:
                recommendations.append("High number of underperforming bots - system-wide optimization needed")
            
            # Trend analysis
            declining_bots = [b for b in ranked_bots if b.trend == 'declining']
            if len(declining_bots) > len(ranked_bots) * 0.4:
                recommendations.append("Many bots showing declining performance - market conditions may have changed")
            
            # Error rate analysis
            high_error_bots = [b for b in ranked_bots if b.error_count > b.total_predictions * 0.1]
            if high_error_bots:
                recommendations.append(f"{len(high_error_bots)} bots have high error rates - investigate system issues")
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")
            return ["Error generating recommendations - manual review needed"]
    
    async def start_continuous_monitoring(self, interval_seconds: int = 300):
        """Start continuous bot performance monitoring"""
        self.logger.info("Starting continuous bot performance monitoring")
        
        while True:
            try:
                # Update all bot rankings
                self.rank_bots()
                
                # Save current state
                self._save_data()
                
                # Log summary statistics
                if self.bot_scores:
                    avg_reliability = np.mean([m.reliability_score for m in self.bot_scores.values()])
                    active_bots = len([m for m in self.bot_scores.values() 
                                     if m.total_predictions >= self.thresholds['min_predictions']])
                    
                    self.logger.info(f"Monitoring update: {active_bots} active bots, "
                                   f"avg reliability: {avg_reliability:.3f}")
                
                await asyncio.sleep(interval_seconds)
                
            except Exception as e:
                self.logger.error(f"Error in continuous monitoring: {e}")
                await asyncio.sleep(interval_seconds)
    
    def export_scores_to_json(self, filepath: Optional[str] = None) -> str:
        """Export bot reliability scores to JSON file"""
        try:
            export_path = filepath or str(self.scores_file)
            
            export_data = {
                'export_timestamp': datetime.now().isoformat(),
                'scores': {bot_id: asdict(metrics) for bot_id, metrics in self.bot_scores.items()},
                'summary': {
                    'total_bots': len(self.bot_scores),
                    'qualified_bots': len([m for m in self.bot_scores.values() 
                                         if m.total_predictions >= self.thresholds['min_predictions']]),
                    'avg_reliability': np.mean([m.reliability_score for m in self.bot_scores.values()]) if self.bot_scores else 0
                }
            }
            
            with open(export_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            self.logger.info(f"Exported bot scores to {export_path}")
            return export_path
            
        except Exception as e:
            self.logger.error(f"Error exporting scores: {e}")
            return ""


# Example usage and testing
if __name__ == "__main__":
    # Initialize scorer
    scorer = BotPerformanceScorer()
    
    # Simulate some bot predictions and outcomes
    test_data = [
        {
            'bot_id': 'analytics_bot_1',
            'prediction': {'signal': 'BUY', 'confidence': 0.8, 'expected_return': 0.02},
            'outcome': {'signal': 'BUY', 'actual_return': 0.018}
        },
        {
            'bot_id': 'strategy_bot_1', 
            'prediction': {'signal': 'SELL', 'confidence': 0.7, 'expected_return': -0.01},
            'outcome': {'signal': 'SELL', 'actual_return': -0.008}
        },
        {
            'bot_id': 'analytics_bot_1',
            'prediction': {'signal': 'HOLD', 'confidence': 0.6, 'expected_return': 0.0},
            'outcome': {'signal': 'BUY', 'actual_return': 0.015}  # Wrong prediction
        }
    ]
    
    # Score predictions
    for data in test_data:
        scorer.score_bot_prediction(data['bot_id'], data['prediction'], data['outcome'])
    
    # Generate report
    report = scorer.generate_performance_report()
    print(json.dumps(report, indent=2))
    
    # Export scores
    scorer.export_scores_to_json()
