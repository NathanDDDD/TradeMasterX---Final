"""
TradeMasterX 2.0 - Analytics Bot
Comprehensive trading performance analysis and pattern recognition system.
PHASE_9_ANALYTICS_CONTINUATION
"""

import json
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import sqlite3

from ..bot_registry import BaseBot


@dataclass
class TradePattern:
    """Trade pattern analysis result"""
    pattern_type: str
    frequency: int
    success_rate: float
    avg_pnl: float
    confidence: float
    description: str


@dataclass
class BotPerformanceComparison:
    """Bot performance comparison result"""
    bot_name: str
    win_rate: float
    total_trades: int
    avg_pnl: float
    sharpe_ratio: float
    max_drawdown: float
    score: float


@dataclass
class PredictionAccuracySummary:
    """Prediction accuracy analysis summary"""
    overall_accuracy: float
    confidence_breakdown: Dict[str, float]
    accuracy_by_symbol: Dict[str, float]
    accuracy_by_timeframe: Dict[str, float]
    improvement_trend: str
    recommendations: List[str]


class AnalyticsBot(BaseBot):
    """
    Comprehensive Analytics Bot for TradeMasterX 2.0
    
    Provides:
    - Trade pattern analysis and recognition
    - Bot performance comparison and ranking
    - Prediction accuracy summarization
    - Visual-ready JSON output for reporting
    """
    
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        
        # Data paths
        self.data_path = Path(config.get('data_path', 'data'))
        self.trades_path = self.data_path / 'trades'
        self.performance_path = self.data_path / 'performance' 
        self.logs_path = Path(config.get('logs_path', 'logs'))
        
        # Analysis configuration
        self.analysis_window_days = config.get('analysis_window_days', 7)
        self.min_trades_for_pattern = config.get('min_trades_for_pattern', 50)
        self.confidence_thresholds = config.get('confidence_thresholds', [0.6, 0.7, 0.8, 0.9])
        
        # Results storage
        self.trade_patterns: List[TradePattern] = []
        self.bot_comparisons: List[BotPerformanceComparison] = []
        self.prediction_summary: Optional[PredictionAccuracySummary] = None
        
        self.logger.info(f"AnalyticsBot {name} configured")

    async def initialize(self) -> bool:
        """Initialize analytics bot resources"""
        try:
            # Ensure data directories exist
            self.trades_path.mkdir(parents=True, exist_ok=True)
            self.performance_path.mkdir(parents=True, exist_ok=True)
            
            # Validate database connections
            if await self._validate_data_sources():
                self.is_initialized = True
                self.logger.info("AnalyticsBot initialized successfully")
                return True
            else:
                self.logger.error("Data source validation failed")
                return False
                
        except Exception as e:
            self.logger.error(f"AnalyticsBot initialization failed: {e}")
            return False

    async def execute_cycle(self) -> Dict[str, Any]:
        """Execute complete analytics cycle"""
        try:
            self.logger.info("🔍 Starting analytics cycle...")
            
            # Analyze trade patterns
            patterns_result = await self.analyze_trade_patterns()
            
            # Compare bot performance
            comparison_result = await self.compare_bot_performance()
            
            # Summarize prediction accuracy
            accuracy_result = await self.summarize_prediction_accuracy()
            
            # Generate visual-ready output
            visual_output = self._generate_visual_output()
            
            cycle_result = {
                "timestamp": datetime.now().isoformat(),
                "trade_patterns": patterns_result,
                "bot_performance": comparison_result,
                "prediction_accuracy": accuracy_result,
                "visual_data": visual_output,
                "status": "success"
            }
            
            # Save results
            await self._save_analytics_results(cycle_result)
            
            self.logger.info("✅ Analytics cycle completed")
            return cycle_result
            
        except Exception as e:
            self.logger.error(f"Analytics cycle error: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "status": "error",
                "error": str(e)
            }

    async def analyze_trade_patterns(self) -> Dict[str, Any]:
        """
        Analyze trade patterns from historical data
        
        Returns:
            Dict containing identified patterns and their characteristics
        """
        try:
            self.logger.info("📊 Analyzing trade patterns...")
            
            # Load trade data
            trades_df = await self._load_trade_data()
            
            if trades_df.empty:
                return {"status": "no_data", "patterns": []}
            
            # Identify different pattern types
            patterns = []
            
            # 1. Time-based patterns
            time_patterns = self._analyze_time_patterns(trades_df)
            patterns.extend(time_patterns)
            
            # 2. Symbol-based patterns
            symbol_patterns = self._analyze_symbol_patterns(trades_df)
            patterns.extend(symbol_patterns)
            
            # 3. Confidence-based patterns
            confidence_patterns = self._analyze_confidence_patterns(trades_df)
            patterns.extend(confidence_patterns)
            
            # 4. Consecutive trade patterns
            sequence_patterns = self._analyze_sequence_patterns(trades_df)
            patterns.extend(sequence_patterns)
            
            # Store results
            self.trade_patterns = patterns
            
            result = {
                "status": "success",
                "patterns_found": len(patterns),
                "analysis_period_days": self.analysis_window_days,
                "total_trades_analyzed": len(trades_df),
                "patterns": [asdict(p) for p in patterns],
                "summary": self._generate_pattern_summary(patterns)
            }
            
            self.logger.info(f"Found {len(patterns)} trade patterns")
            return result
            
        except Exception as e:
            self.logger.error(f"Trade pattern analysis error: {e}")
            return {"status": "error", "error": str(e)}

    async def compare_bot_performance(self) -> Dict[str, Any]:
        """
        Compare performance across different bots/strategies
        
        Returns:
            Dict containing bot performance comparisons and rankings
        """
        try:
            self.logger.info("⚖️ Comparing bot performance...")
            
            # Load performance data for each bot
            bot_performances = await self._load_bot_performance_data()
            
            if not bot_performances:
                return {"status": "no_data", "comparisons": []}
            
            # Calculate comprehensive performance metrics
            comparisons = []
            
            for bot_name, perf_data in bot_performances.items():
                comparison = self._calculate_bot_metrics(bot_name, perf_data)
                comparisons.append(comparison)
            
            # Sort by overall score
            comparisons.sort(key=lambda x: x.score, reverse=True)
            
            # Store results
            self.bot_comparisons = comparisons
            
            result = {
                "status": "success",
                "bots_analyzed": len(comparisons),
                "analysis_period_days": self.analysis_window_days,
                "comparisons": [asdict(c) for c in comparisons],
                "rankings": self._generate_bot_rankings(comparisons),
                "best_performer": asdict(comparisons[0]) if comparisons else None,
                "performance_insights": self._generate_performance_insights(comparisons)
            }
            
            self.logger.info(f"Compared {len(comparisons)} bot performances")
            return result
            
        except Exception as e:
            self.logger.error(f"Bot performance comparison error: {e}")
            return {"status": "error", "error": str(e)}

    async def summarize_prediction_accuracy(self) -> Dict[str, Any]:
        """
        Summarize prediction accuracy across all models and timeframes
        
        Returns:
            Dict containing comprehensive prediction accuracy analysis
        """
        try:
            self.logger.info("🎯 Summarizing prediction accuracy...")
            
            # Load prediction data
            predictions_df = await self._load_prediction_data()
            
            if predictions_df.empty:
                return {"status": "no_data", "summary": {}}
            
            # Calculate overall accuracy
            overall_accuracy = predictions_df['correct'].mean()
            
            # Accuracy breakdown by confidence levels
            confidence_breakdown = {}
            for threshold in self.confidence_thresholds:
                high_conf_preds = predictions_df[predictions_df['confidence'] >= threshold]
                if not high_conf_preds.empty:
                    accuracy = high_conf_preds['correct'].mean()
                    confidence_breakdown[f"confidence_{threshold}+"] = round(accuracy, 3)
            
            # Accuracy by symbol
            accuracy_by_symbol = {}
            for symbol in predictions_df['symbol'].unique():
                symbol_preds = predictions_df[predictions_df['symbol'] == symbol]
                accuracy = symbol_preds['correct'].mean()
                accuracy_by_symbol[symbol] = round(accuracy, 3)
            
            # Accuracy by timeframe (hourly analysis)
            predictions_df['hour'] = pd.to_datetime(predictions_df['timestamp']).dt.hour
            accuracy_by_hour = predictions_df.groupby('hour')['correct'].mean().to_dict()
            accuracy_by_timeframe = {f"hour_{k}": round(v, 3) for k, v in accuracy_by_hour.items()}
            
            # Improvement trend analysis
            improvement_trend = self._analyze_accuracy_trend(predictions_df)
            
            # Generate recommendations
            recommendations = self._generate_accuracy_recommendations(
                overall_accuracy, confidence_breakdown, accuracy_by_symbol
            )
            
            # Create summary object
            summary = PredictionAccuracySummary(
                overall_accuracy=round(overall_accuracy, 3),
                confidence_breakdown=confidence_breakdown,
                accuracy_by_symbol=accuracy_by_symbol,
                accuracy_by_timeframe=accuracy_by_timeframe,
                improvement_trend=improvement_trend,
                recommendations=recommendations
            )
            
            self.prediction_summary = summary
            
            result = {
                "status": "success",
                "predictions_analyzed": len(predictions_df),
                "analysis_period_days": self.analysis_window_days,
                "summary": asdict(summary),
                "detailed_metrics": {
                    "accuracy_distribution": self._calculate_accuracy_distribution(predictions_df),
                    "confidence_distribution": self._calculate_confidence_distribution(predictions_df),
                    "temporal_analysis": self._analyze_temporal_accuracy(predictions_df)
                }
            }
            
            self.logger.info(f"Analyzed {len(predictions_df)} predictions")
            return result
            
        except Exception as e:
            self.logger.error(f"Prediction accuracy analysis error: {e}")
            return {"status": "error", "error": str(e)}

    async def cleanup(self):
        """Cleanup analytics bot resources"""
        try:
            # Clear cached data
            self.trade_patterns.clear()
            self.bot_comparisons.clear()
            self.prediction_summary = None
            
            self.logger.info("AnalyticsBot cleaned up")
            
        except Exception as e:
            self.logger.error(f"AnalyticsBot cleanup error: {e}")

    # Private helper methods
    
    async def _validate_data_sources(self) -> bool:
        """Validate that required data sources are accessible"""
        try:
            # Check for trade database
            trade_db = self.data_path / "trades.db"
            if trade_db.exists():
                conn = sqlite3.connect(trade_db)
                cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                conn.close()
                
                required_tables = ['trades', 'predictions', 'bot_performance']
                if all(table in tables for table in required_tables):
                    return True
                else:
                    self.logger.warning(f"Missing required tables: {set(required_tables) - set(tables)}")
            
            # If database doesn't exist, check for CSV files as fallback
            csv_files = list(self.trades_path.glob("*.csv"))
            if csv_files:
                self.logger.info(f"Found {len(csv_files)} CSV files as data source")
                return True
            
            self.logger.warning("No valid data sources found")
            return False
            
        except Exception as e:
            self.logger.error(f"Data source validation error: {e}")
            return False

    async def _load_trade_data(self) -> pd.DataFrame:
        """Load trade data from available sources"""
        try:
            # Try database first
            trade_db = self.data_path / "trades.db"
            if trade_db.exists():
                conn = sqlite3.connect(trade_db)
                cutoff_date = datetime.now() - timedelta(days=self.analysis_window_days)
                
                query = """
                SELECT * FROM trades 
                WHERE timestamp >= ? 
                ORDER BY timestamp DESC
                """
                
                df = pd.read_sql_query(query, conn, params=[cutoff_date.isoformat()])
                conn.close()
                return df
            
            # Fallback to CSV files
            csv_files = list(self.trades_path.glob("*.csv"))
            if csv_files:
                # Load most recent CSV file
                latest_csv = max(csv_files, key=lambda x: x.stat().st_mtime)
                df = pd.read_csv(latest_csv)
                
                # Filter by date if timestamp column exists
                if 'timestamp' in df.columns:
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                    cutoff_date = datetime.now() - timedelta(days=self.analysis_window_days)
                    df = df[df['timestamp'] >= cutoff_date]
                
                return df
            
            return pd.DataFrame()
            
        except Exception as e:
            self.logger.error(f"Trade data loading error: {e}")
            return pd.DataFrame()

    async def _load_bot_performance_data(self) -> Dict[str, pd.DataFrame]:
        """Load performance data for all bots"""
        try:
            bot_data = {}
            
            # Try database approach
            trade_db = self.data_path / "trades.db"
            if trade_db.exists():
                conn = sqlite3.connect(trade_db)
                
                # Get unique bot names
                cursor = conn.execute("SELECT DISTINCT bot_name FROM bot_performance")
                bot_names = [row[0] for row in cursor.fetchall()]
                
                cutoff_date = datetime.now() - timedelta(days=self.analysis_window_days)
                
                for bot_name in bot_names:
                    query = """
                    SELECT * FROM bot_performance 
                    WHERE bot_name = ? AND timestamp >= ?
                    ORDER BY timestamp DESC
                    """
                    
                    df = pd.read_sql_query(query, conn, params=[bot_name, cutoff_date.isoformat()])
                    if not df.empty:
                        bot_data[bot_name] = df
                
                conn.close()
            
            # Fallback to performance files
            if not bot_data:
                perf_files = list(self.performance_path.glob("*_performance.csv"))
                for file in perf_files:
                    bot_name = file.stem.replace('_performance', '')
                    df = pd.read_csv(file)
                    
                    if 'timestamp' in df.columns:
                        df['timestamp'] = pd.to_datetime(df['timestamp'])
                        cutoff_date = datetime.now() - timedelta(days=self.analysis_window_days)
                        df = df[df['timestamp'] >= cutoff_date]
                    
                    if not df.empty:
                        bot_data[bot_name] = df
            
            return bot_data
            
        except Exception as e:
            self.logger.error(f"Bot performance data loading error: {e}")
            return {}

    async def _load_prediction_data(self) -> pd.DataFrame:
        """Load prediction accuracy data"""
        try:
            # Try database first
            trade_db = self.data_path / "trades.db"
            if trade_db.exists():
                conn = sqlite3.connect(trade_db)
                cutoff_date = datetime.now() - timedelta(days=self.analysis_window_days)
                
                query = """
                SELECT * FROM predictions 
                WHERE timestamp >= ? 
                ORDER BY timestamp DESC
                """
                
                df = pd.read_sql_query(query, conn, params=[cutoff_date.isoformat()])
                conn.close()
                return df
            
            # Fallback to log files
            prediction_files = list(self.logs_path.glob("*prediction*.csv"))
            if prediction_files:
                latest_file = max(prediction_files, key=lambda x: x.stat().st_mtime)
                df = pd.read_csv(latest_file)
                
                if 'timestamp' in df.columns:
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                    cutoff_date = datetime.now() - timedelta(days=self.analysis_window_days)
                    df = df[df['timestamp'] >= cutoff_date]
                
                return df
            
            return pd.DataFrame()
            
        except Exception as e:
            self.logger.error(f"Prediction data loading error: {e}")
            return pd.DataFrame()

    def _analyze_time_patterns(self, trades_df: pd.DataFrame) -> List[TradePattern]:
        """Analyze time-based trading patterns"""
        patterns = []
        
        try:
            trades_df['timestamp'] = pd.to_datetime(trades_df['timestamp'])
            trades_df['hour'] = trades_df['timestamp'].dt.hour
            trades_df['day_of_week'] = trades_df['timestamp'].dt.dayofweek
            
            # Hourly patterns
            hourly_stats = trades_df.groupby('hour').agg({
                'result': lambda x: (x == 'WIN').mean(),
                'pnl': 'mean'
            }).reset_index()
            
            # Find best performing hours
            best_hours = hourly_stats.nlargest(3, 'result')
            for _, row in best_hours.iterrows():
                if trades_df[trades_df['hour'] == row['hour']].shape[0] >= self.min_trades_for_pattern:
                    pattern = TradePattern(
                        pattern_type="time_hourly",
                        frequency=trades_df[trades_df['hour'] == row['hour']].shape[0],
                        success_rate=row['result'],
                        avg_pnl=row['pnl'],
                        confidence=min(0.95, row['result'] * 1.2),
                        description=f"High performance during hour {int(row['hour'])}"
                    )
                    patterns.append(pattern)
            
            # Day of week patterns
            daily_stats = trades_df.groupby('day_of_week').agg({
                'result': lambda x: (x == 'WIN').mean(),
                'pnl': 'mean'
            }).reset_index()
            
            best_days = daily_stats.nlargest(2, 'result')
            day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            
            for _, row in best_days.iterrows():
                if trades_df[trades_df['day_of_week'] == row['day_of_week']].shape[0] >= self.min_trades_for_pattern:
                    pattern = TradePattern(
                        pattern_type="time_daily",
                        frequency=trades_df[trades_df['day_of_week'] == row['day_of_week']].shape[0],
                        success_rate=row['result'],
                        avg_pnl=row['pnl'],
                        confidence=min(0.9, row['result'] * 1.1),
                        description=f"High performance on {day_names[int(row['day_of_week'])]}"
                    )
                    patterns.append(pattern)
            
        except Exception as e:
            self.logger.error(f"Time pattern analysis error: {e}")
        
        return patterns

    def _analyze_symbol_patterns(self, trades_df: pd.DataFrame) -> List[TradePattern]:
        """Analyze symbol-specific patterns"""
        patterns = []
        
        try:
            if 'symbol' in trades_df.columns:
                symbol_stats = trades_df.groupby('symbol').agg({
                    'result': lambda x: (x == 'WIN').mean(),
                    'pnl': 'mean',
                    'confidence': 'mean'
                }).reset_index()
                
                # Find top performing symbols
                top_symbols = symbol_stats.nlargest(3, 'result')
                
                for _, row in top_symbols.iterrows():
                    symbol_trades = trades_df[trades_df['symbol'] == row['symbol']]
                    if len(symbol_trades) >= self.min_trades_for_pattern:
                        pattern = TradePattern(
                            pattern_type="symbol_performance",
                            frequency=len(symbol_trades),
                            success_rate=row['result'],
                            avg_pnl=row['pnl'],
                            confidence=row['confidence'],
                            description=f"Strong performance with {row['symbol']}"
                        )
                        patterns.append(pattern)
                        
        except Exception as e:
            self.logger.error(f"Symbol pattern analysis error: {e}")
        
        return patterns

    def _analyze_confidence_patterns(self, trades_df: pd.DataFrame) -> List[TradePattern]:
        """Analyze confidence level patterns"""
        patterns = []
        
        try:
            if 'confidence' in trades_df.columns:
                # Analyze performance at different confidence thresholds
                for threshold in self.confidence_thresholds:
                    high_conf_trades = trades_df[trades_df['confidence'] >= threshold]
                    
                    if len(high_conf_trades) >= self.min_trades_for_pattern:
                        success_rate = (high_conf_trades['result'] == 'WIN').mean()
                        avg_pnl = high_conf_trades['pnl'].mean()
                        
                        if success_rate > 0.6:  # Only include if decent performance
                            pattern = TradePattern(
                                pattern_type="confidence_threshold",
                                frequency=len(high_conf_trades),
                                success_rate=success_rate,
                                avg_pnl=avg_pnl,
                                confidence=threshold,
                                description=f"High success rate at {threshold}+ confidence"
                            )
                            patterns.append(pattern)
                            
        except Exception as e:
            self.logger.error(f"Confidence pattern analysis error: {e}")
        
        return patterns

    def _analyze_sequence_patterns(self, trades_df: pd.DataFrame) -> List[TradePattern]:
        """Analyze consecutive trade patterns"""
        patterns = []
        
        try:
            trades_df = trades_df.sort_values('timestamp')
            trades_df['win'] = (trades_df['result'] == 'WIN').astype(int)
            
            # Find winning streaks
            trades_df['streak_id'] = (trades_df['win'] != trades_df['win'].shift()).cumsum()
            winning_streaks = trades_df[trades_df['win'] == 1].groupby('streak_id').size()
            
            if len(winning_streaks) > 0:
                avg_win_streak = winning_streaks.mean()
                max_win_streak = winning_streaks.max()
                
                if max_win_streak >= 5:  # Significant streak
                    pattern = TradePattern(
                        pattern_type="winning_streak",
                        frequency=len(winning_streaks),
                        success_rate=1.0,  # By definition
                        avg_pnl=trades_df[trades_df['win'] == 1]['pnl'].mean(),
                        confidence=0.8,
                        description=f"Max winning streak: {max_win_streak}, Avg: {avg_win_streak:.1f}"
                    )
                    patterns.append(pattern)
                    
        except Exception as e:
            self.logger.error(f"Sequence pattern analysis error: {e}")
        
        return patterns

    def _calculate_bot_metrics(self, bot_name: str, perf_data: pd.DataFrame) -> BotPerformanceComparison:
        """Calculate comprehensive metrics for a bot"""
        try:
            # Basic metrics
            total_trades = len(perf_data)
            win_rate = (perf_data['result'] == 'WIN').mean() if 'result' in perf_data.columns else 0
            avg_pnl = perf_data['pnl'].mean() if 'pnl' in perf_data.columns else 0
            
            # Sharpe ratio calculation
            returns = perf_data['pnl'] if 'pnl' in perf_data.columns else pd.Series([0])
            sharpe_ratio = returns.mean() / returns.std() if returns.std() > 0 else 0
            
            # Maximum drawdown
            cumulative_returns = returns.cumsum()
            running_max = cumulative_returns.expanding().max()
            drawdowns = (running_max - cumulative_returns) / running_max
            max_drawdown = drawdowns.max() if len(drawdowns) > 0 else 0
            
            # Overall score calculation
            score = (
                win_rate * 40 +  # 40% weight for win rate
                min(sharpe_ratio / 2, 1) * 30 +  # 30% weight for Sharpe ratio
                max(0, 1 - max_drawdown) * 20 +  # 20% weight for drawdown control
                min(avg_pnl / 0.01, 1) * 10  # 10% weight for average PnL
            )
            
            return BotPerformanceComparison(
                bot_name=bot_name,
                win_rate=round(win_rate, 3),
                total_trades=total_trades,
                avg_pnl=round(avg_pnl, 4),
                sharpe_ratio=round(sharpe_ratio, 3),
                max_drawdown=round(max_drawdown, 3),
                score=round(score, 2)
            )
            
        except Exception as e:
            self.logger.error(f"Bot metrics calculation error for {bot_name}: {e}")
            return BotPerformanceComparison(
                bot_name=bot_name,
                win_rate=0, total_trades=0, avg_pnl=0,
                sharpe_ratio=0, max_drawdown=1, score=0
            )

    def _generate_visual_output(self) -> Dict[str, Any]:
        """Generate visual-ready JSON data for reports"""
        visual_data = {
            "charts": {
                "trade_patterns": {
                    "type": "bar",
                    "data": [
                        {
                            "pattern": p.pattern_type,
                            "success_rate": p.success_rate,
                            "frequency": p.frequency,
                            "avg_pnl": p.avg_pnl
                        }
                        for p in self.trade_patterns
                    ],
                    "config": {
                        "x_axis": "pattern",
                        "y_axis": "success_rate",
                        "title": "Trade Pattern Performance"
                    }
                },
                "bot_comparison": {
                    "type": "radar",
                    "data": [
                        {
                            "bot": c.bot_name,
                            "win_rate": c.win_rate,
                            "sharpe_ratio": min(c.sharpe_ratio / 2, 1),
                            "drawdown_control": max(0, 1 - c.max_drawdown),
                            "pnl_performance": min(c.avg_pnl / 0.01, 1)
                        }
                        for c in self.bot_comparisons
                    ],
                    "config": {
                        "dimensions": ["win_rate", "sharpe_ratio", "drawdown_control", "pnl_performance"],
                        "title": "Bot Performance Comparison"
                    }
                },
                "accuracy_breakdown": {
                    "type": "line",
                    "data": self._prepare_accuracy_chart_data(),
                    "config": {
                        "x_axis": "confidence_level",
                        "y_axis": "accuracy",
                        "title": "Prediction Accuracy by Confidence Level"
                    }
                }
            },
            "summary_stats": {
                "total_patterns_found": len(self.trade_patterns),
                "bots_analyzed": len(self.bot_comparisons),
                "best_pattern": max(self.trade_patterns, key=lambda x: x.success_rate).pattern_type if self.trade_patterns else None,
                "top_bot": max(self.bot_comparisons, key=lambda x: x.score).bot_name if self.bot_comparisons else None,
                "overall_accuracy": self.prediction_summary.overall_accuracy if self.prediction_summary else 0
            }
        }
        
        return visual_data

    async def _save_analytics_results(self, results: Dict[str, Any]):
        """Save analytics results to file"""
        try:
            results_dir = self.data_path / "analytics"
            results_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_file = results_dir / f"analytics_{timestamp}.json"
            
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            self.logger.info(f"Analytics results saved: {results_file}")
            
        except Exception as e:
            self.logger.error(f"Results saving error: {e}")

    # Additional helper methods for completeness...
    
    def _generate_pattern_summary(self, patterns: List[TradePattern]) -> Dict[str, Any]:
        """Generate summary of identified patterns"""
        if not patterns:
            return {"total": 0}
        
        by_type = {}
        for pattern in patterns:
            if pattern.pattern_type not in by_type:
                by_type[pattern.pattern_type] = []
            by_type[pattern.pattern_type].append(pattern)
        
        return {
            "total": len(patterns),
            "by_type": {k: len(v) for k, v in by_type.items()},
            "avg_success_rate": np.mean([p.success_rate for p in patterns]),
            "best_pattern": max(patterns, key=lambda x: x.success_rate).description
        }

    def _generate_bot_rankings(self, comparisons: List[BotPerformanceComparison]) -> Dict[str, Any]:
        """Generate bot performance rankings"""
        return {
            "overall_ranking": [{"rank": i+1, "bot": c.bot_name, "score": c.score} 
                              for i, c in enumerate(comparisons)],
            "win_rate_leader": max(comparisons, key=lambda x: x.win_rate).bot_name,
            "sharpe_leader": max(comparisons, key=lambda x: x.sharpe_ratio).bot_name,
            "consistency_leader": min(comparisons, key=lambda x: x.max_drawdown).bot_name
        }

    def _generate_performance_insights(self, comparisons: List[BotPerformanceComparison]) -> List[str]:
        """Generate performance insights and recommendations"""
        insights = []
        
        if not comparisons:
            return ["No performance data available for analysis"]
        
        # Best performer insight
        best_bot = max(comparisons, key=lambda x: x.score)
        insights.append(f"{best_bot.bot_name} is the top performer with {best_bot.score:.1f}/100 score")
        
        # Win rate insights
        avg_win_rate = np.mean([c.win_rate for c in comparisons])
        if avg_win_rate > 0.6:
            insights.append(f"Average win rate of {avg_win_rate:.1%} indicates strong strategy performance")
        elif avg_win_rate < 0.5:
            insights.append(f"Below-average win rate of {avg_win_rate:.1%} suggests strategy optimization needed")
        
        # Risk insights
        high_risk_bots = [c for c in comparisons if c.max_drawdown > 0.15]
        if high_risk_bots:
            insights.append(f"{len(high_risk_bots)} bots show high risk with >15% drawdown")
        
        return insights

    def _analyze_accuracy_trend(self, predictions_df: pd.DataFrame) -> str:
        """Analyze prediction accuracy trend over time"""
        try:
            predictions_df['timestamp'] = pd.to_datetime(predictions_df['timestamp'])
            predictions_df = predictions_df.sort_values('timestamp')
            
            # Calculate rolling accuracy
            window_size = min(100, len(predictions_df) // 4)
            if window_size < 10:
                return "insufficient_data"
            
            rolling_accuracy = predictions_df['correct'].rolling(window=window_size).mean()
            
            # Compare first half vs second half
            mid_point = len(rolling_accuracy) // 2
            first_half_avg = rolling_accuracy.iloc[:mid_point].mean()
            second_half_avg = rolling_accuracy.iloc[mid_point:].mean()
            
            if second_half_avg > first_half_avg * 1.05:
                return "improving"
            elif second_half_avg < first_half_avg * 0.95:
                return "declining"
            else:
                return "stable"
                
        except Exception as e:
            self.logger.error(f"Accuracy trend analysis error: {e}")
            return "unknown"

    def _generate_accuracy_recommendations(self, overall_accuracy: float, 
                                         confidence_breakdown: Dict[str, float],
                                         accuracy_by_symbol: Dict[str, float]) -> List[str]:
        """Generate recommendations for improving prediction accuracy"""
        recommendations = []
        
        if overall_accuracy < 0.6:
            recommendations.append("Overall accuracy below 60% - consider model retraining")
        
        if confidence_breakdown:
            high_conf_accuracy = confidence_breakdown.get("confidence_0.8+", 0)
            if high_conf_accuracy < 0.7:
                recommendations.append("High-confidence predictions underperforming - review confidence calibration")
        
        if accuracy_by_symbol:
            worst_symbol = min(accuracy_by_symbol.items(), key=lambda x: x[1])
            if worst_symbol[1] < 0.5:
                recommendations.append(f"Poor performance on {worst_symbol[0]} - symbol-specific optimization needed")
        
        if not recommendations:
            recommendations.append("Prediction accuracy is performing well - maintain current approach")
        
        return recommendations

    def _calculate_accuracy_distribution(self, predictions_df: pd.DataFrame) -> Dict[str, int]:
        """Calculate distribution of prediction accuracies"""
        try:
            bins = [0, 0.2, 0.4, 0.6, 0.8, 1.0]
            labels = ["0-20%", "20-40%", "40-60%", "60-80%", "80-100%"]
            
            # Calculate accuracy in chunks
            chunk_size = 100
            accuracies = []
            
            for i in range(0, len(predictions_df), chunk_size):
                chunk = predictions_df.iloc[i:i+chunk_size]
                accuracy = chunk['correct'].mean()
                accuracies.append(accuracy)
            
            distribution = pd.cut(accuracies, bins=bins, labels=labels).value_counts()
            return distribution.to_dict()
            
        except Exception as e:
            self.logger.error(f"Accuracy distribution calculation error: {e}")
            return {}

    def _calculate_confidence_distribution(self, predictions_df: pd.DataFrame) -> Dict[str, int]:
        """Calculate distribution of confidence levels"""
        try:
            bins = [0, 0.2, 0.4, 0.6, 0.8, 1.0]
            labels = ["0-20%", "20-40%", "40-60%", "60-80%", "80-100%"]
            
            distribution = pd.cut(predictions_df['confidence'], bins=bins, labels=labels).value_counts()
            return distribution.to_dict()
            
        except Exception as e:
            self.logger.error(f"Confidence distribution calculation error: {e}")
            return {}

    def _analyze_temporal_accuracy(self, predictions_df: pd.DataFrame) -> Dict[str, float]:
        """Analyze accuracy patterns over time"""
        try:
            predictions_df['timestamp'] = pd.to_datetime(predictions_df['timestamp'])
            predictions_df['hour'] = predictions_df['timestamp'].dt.hour
            predictions_df['day_of_week'] = predictions_df['timestamp'].dt.dayofweek
            
            hourly_accuracy = predictions_df.groupby('hour')['correct'].mean()
            daily_accuracy = predictions_df.groupby('day_of_week')['correct'].mean()
            
            return {
                "best_hour": int(hourly_accuracy.idxmax()),
                "best_hour_accuracy": float(hourly_accuracy.max()),
                "worst_hour": int(hourly_accuracy.idxmin()),
                "worst_hour_accuracy": float(hourly_accuracy.min()),
                "best_day": int(daily_accuracy.idxmax()),
                "best_day_accuracy": float(daily_accuracy.max())
            }
            
        except Exception as e:
            self.logger.error(f"Temporal accuracy analysis error: {e}")
            return {}

    def _prepare_accuracy_chart_data(self) -> List[Dict[str, Any]]:
        """Prepare data for accuracy visualization chart"""
        if not self.prediction_summary:
            return []
        
        chart_data = []
        for conf_level, accuracy in self.prediction_summary.confidence_breakdown.items():
            threshold = float(conf_level.replace("confidence_", "").replace("+", ""))
            chart_data.append({
                "confidence_level": threshold,
                "accuracy": accuracy,
                "label": f"{threshold:.0%}+ confidence"
            })
        
        return sorted(chart_data, key=lambda x: x["confidence_level"])
