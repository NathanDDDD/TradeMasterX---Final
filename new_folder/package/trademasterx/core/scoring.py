"""
TradeMasterX 2.0 - Scoring Engine
Comprehensive performance scoring, assessment, and reporting system.
Consolidates functionality from readiness_estimator.py and daily_reporter.py.
"""

import asyncio
import json
import logging
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
from dataclasses import dataclass, asdict

from ..config.config_loader import ConfigLoader


@dataclass
class PerformanceMetrics:
    """Performance metrics container"""
    win_rate: float
    total_trades: int
    profit_loss_ratio: float
    sharpe_ratio: float
    max_drawdown: float
    prediction_accuracy: float
    avg_confidence: float
    api_reliability: float
    retraining_success_rate: float
    timestamp: datetime


@dataclass
class ComponentScore:
    """Individual component score"""
    name: str
    raw_value: float
    normalized_score: float  # 0-100
    weight: float
    weighted_contribution: float


class ScoringEngine:
    """Comprehensive scoring and assessment engine with real-time performance scoring,
    live trading readiness assessment, reporting, and component-based scoring system."""
    
    def __init__(self, config: Dict[str, Any] = None):
        # If no config is provided, load default configuration
        if config is None:
            config_loader = ConfigLoader()
            self.config = config_loader.get_config('system', {})
        else:
            self.config = config
            
        self.logger = logging.getLogger("ScoringEngine")
        
        # Paths
        self.data_path = Path(self.config.get('paths', {}).get('data', 'data'))
        self.reports_path = Path(self.config.get('paths', {}).get('reports', 'reports'))
          # Scoring configuration
        self.scoring_config = self.config.get('scoring', {})
        self._setup_scoring_weights()
        self._setup_thresholds()
        
        # Performance tracking
        self.performance_history: List[PerformanceMetrics] = []
        self.component_scores: Dict[str, ComponentScore] = {}
        self.latest_score: Optional[float] = None
        
        # Database setup
        self._setup_database()
        
        self.logger.info("ScoringEngine initialized")

    def _setup_scoring_weights(self):
        """Setup scoring weights for different components"""
        default_weights = {
            'win_rate': 25,           # 25% weight
            'sharpe_ratio': 20,       # 20% weight  
            'prediction_accuracy': 20, # 20% weight
            'drawdown_control': 15,   # 15% weight
            'api_reliability': 10,    # 10% weight
            'retraining_success': 10  # 10% weight
        }
        
        self.scoring_weights = self.scoring_config.get('weights', default_weights)
        
        # Normalize weights to sum to 100
        total_weight = sum(self.scoring_weights.values())
        if total_weight != 100:
            self.scoring_weights = {
                k: (v / total_weight) * 100 
                for k, v in self.scoring_weights.items()
            }

    def _setup_thresholds(self):
        """Setup minimum thresholds for live trading approval"""
        default_thresholds = {
            'win_rate': 0.55,         # 55% minimum win rate
            'sharpe_ratio': 1.0,      # Sharpe ratio >= 1.0
            'prediction_accuracy': 0.70, # 70% prediction accuracy
            'max_drawdown': 0.15,     # Max 15% drawdown
            'api_reliability': 0.95,  # 95% API success rate
            'retraining_success': 0.80, # 80% retraining success
            'live_trading_score': 90.0  # 90+ score for approval
        }
        
        self.min_thresholds = self.scoring_config.get('thresholds', default_thresholds)

    def _setup_database(self):
        """Setup database for performance tracking"""
        self.data_path.mkdir(exist_ok=True)
        self.db_path = self.data_path / "performance.db"
        
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Create tables
            conn.execute("""
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    win_rate REAL,
                    total_trades INTEGER,
                    profit_loss_ratio REAL,
                    sharpe_ratio REAL,
                    max_drawdown REAL,
                    prediction_accuracy REAL,
                    avg_confidence REAL,
                    api_reliability REAL,
                    retraining_success_rate REAL,
                    overall_score REAL
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS component_scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    component_name TEXT NOT NULL,
                    raw_value REAL,
                    normalized_score REAL,
                    weight REAL,
                    weighted_contribution REAL
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS assessments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    assessment_type TEXT NOT NULL,
                    overall_score REAL,
                    approval_status TEXT,
                    report_data TEXT
                )
            """)
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Database setup error: {e}")

    async def update_scores(self, force_update: bool = False) -> Dict[str, Any]:
        """
        Update all performance scores
        
        Args:
            force_update: Force update regardless of timing
            
        Returns:
            Dict containing updated scores and metrics
        """
        try:
            # Collect latest performance data
            metrics = await self._collect_performance_metrics()
            
            if not metrics:
                self.logger.warning("No performance metrics available")
                return {"status": "no_data"}
            
            # Calculate component scores
            self.component_scores = self._calculate_component_scores(metrics)
            
            # Calculate overall score
            overall_score = self._calculate_overall_score(self.component_scores)
            self.latest_score = overall_score
            
            # Store metrics in database
            await self._store_performance_data(metrics, overall_score)
            
            # Update performance history
            self.performance_history.append(metrics)
            self._trim_performance_history()
            
            result = {
                "status": "updated",
                "timestamp": datetime.now().isoformat(),
                "overall_score": overall_score,
                "component_scores": {
                    name: asdict(score) for name, score in self.component_scores.items()
                },
                "metrics": asdict(metrics),
                "thresholds_met": self._check_thresholds(metrics, overall_score)
            }
            
            self.logger.info(f"Scores updated - Overall: {overall_score:.1f}/100")
            return result
            
        except Exception as e:
            self.logger.error(f"Score update error: {e}")
            return {"status": "error", "error": str(e)}

    async def _collect_performance_metrics(self) -> Optional[PerformanceMetrics]:
        """Collect current performance metrics from various sources"""
        try:
            # Connect to databases and collect metrics
            # This would integrate with actual trading data
            
            # For now, return simulated metrics based on configuration
            # In production, this would query actual trading databases
            
            current_time = datetime.now()
            
            # Simulate data collection
            metrics = PerformanceMetrics(
                win_rate=0.68,  # 68% win rate
                total_trades=1500,
                profit_loss_ratio=1.2,
                sharpe_ratio=1.45,
                max_drawdown=0.12,  # 12% max drawdown
                prediction_accuracy=0.74,  # 74% prediction accuracy
                avg_confidence=0.81,
                api_reliability=0.996,  # 99.6% API reliability
                retraining_success_rate=0.85,  # 85% retraining success
                timestamp=current_time
            )
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Metrics collection error: {e}")
            return None

    def _calculate_component_scores(self, metrics: PerformanceMetrics) -> Dict[str, ComponentScore]:
        """Calculate normalized scores for each component"""
        scores = {}
        
        # Win Rate Score (0-100)
        win_rate_score = min(100, (metrics.win_rate / 0.8) * 100)  # 80% = perfect score
        scores['win_rate'] = ComponentScore(
            name='win_rate',
            raw_value=metrics.win_rate,
            normalized_score=win_rate_score,
            weight=self.scoring_weights['win_rate'],
            weighted_contribution=(win_rate_score * self.scoring_weights['win_rate']) / 100
        )
        
        # Sharpe Ratio Score (0-100)
        sharpe_score = min(100, (metrics.sharpe_ratio / 2.0) * 100)  # Sharpe 2.0 = perfect
        scores['sharpe_ratio'] = ComponentScore(
            name='sharpe_ratio',
            raw_value=metrics.sharpe_ratio,
            normalized_score=sharpe_score,
            weight=self.scoring_weights['sharpe_ratio'],
            weighted_contribution=(sharpe_score * self.scoring_weights['sharpe_ratio']) / 100
        )
        
        # Prediction Accuracy Score (0-100)
        accuracy_score = min(100, (metrics.prediction_accuracy / 0.9) * 100)  # 90% = perfect
        scores['prediction_accuracy'] = ComponentScore(
            name='prediction_accuracy',
            raw_value=metrics.prediction_accuracy,
            normalized_score=accuracy_score,
            weight=self.scoring_weights['prediction_accuracy'],
            weighted_contribution=(accuracy_score * self.scoring_weights['prediction_accuracy']) / 100
        )
        
        # Drawdown Control Score (0-100) - inverse scoring
        drawdown_score = max(0, 100 - (metrics.max_drawdown * 500))  # 20% drawdown = 0 points
        scores['drawdown_control'] = ComponentScore(
            name='drawdown_control',
            raw_value=metrics.max_drawdown,
            normalized_score=drawdown_score,
            weight=self.scoring_weights['drawdown_control'],
            weighted_contribution=(drawdown_score * self.scoring_weights['drawdown_control']) / 100
        )
        
        # API Reliability Score (0-100)
        api_score = metrics.api_reliability * 100
        scores['api_reliability'] = ComponentScore(
            name='api_reliability',
            raw_value=metrics.api_reliability,
            normalized_score=api_score,
            weight=self.scoring_weights['api_reliability'],
            weighted_contribution=(api_score * self.scoring_weights['api_reliability']) / 100
        )
        
        # Retraining Success Score (0-100)
        retraining_score = metrics.retraining_success_rate * 100
        scores['retraining_success'] = ComponentScore(
            name='retraining_success',
            raw_value=metrics.retraining_success_rate,
            normalized_score=retraining_score,
            weight=self.scoring_weights['retraining_success'],
            weighted_contribution=(retraining_score * self.scoring_weights['retraining_success']) / 100
        )
        
        return scores

    def _calculate_overall_score(self, component_scores: Dict[str, ComponentScore]) -> float:
        """Calculate weighted overall score"""
        total_weighted_score = sum(score.weighted_contribution for score in component_scores.values())
        return round(total_weighted_score, 1)

    def _check_thresholds(self, metrics: PerformanceMetrics, overall_score: float) -> Dict[str, bool]:
        """Check if metrics meet minimum thresholds"""
        return {
            "win_rate_threshold": metrics.win_rate >= self.min_thresholds['win_rate'],
            "sharpe_threshold": metrics.sharpe_ratio >= self.min_thresholds['sharpe_ratio'],
            "prediction_threshold": metrics.prediction_accuracy >= self.min_thresholds['prediction_accuracy'],
            "drawdown_threshold": metrics.max_drawdown <= self.min_thresholds['max_drawdown'],
            "api_threshold": metrics.api_reliability >= self.min_thresholds['api_reliability'],
            "retraining_threshold": metrics.retraining_success_rate >= self.min_thresholds['retraining_success'],
            "overall_score_threshold": overall_score >= self.min_thresholds['live_trading_score']
        }

    async def _store_performance_data(self, metrics: PerformanceMetrics, overall_score: float):
        """Store performance data in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Store metrics
            conn.execute("""
                INSERT INTO performance_metrics 
                (timestamp, win_rate, total_trades, profit_loss_ratio, sharpe_ratio, 
                 max_drawdown, prediction_accuracy, avg_confidence, api_reliability, 
                 retraining_success_rate, overall_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metrics.timestamp.isoformat(),
                metrics.win_rate,
                metrics.total_trades,
                metrics.profit_loss_ratio,
                metrics.sharpe_ratio,
                metrics.max_drawdown,
                metrics.prediction_accuracy,
                metrics.avg_confidence,
                metrics.api_reliability,
                metrics.retraining_success_rate,
                overall_score
            ))
            
            # Store component scores
            for name, score in self.component_scores.items():
                conn.execute("""
                    INSERT INTO component_scores 
                    (timestamp, component_name, raw_value, normalized_score, weight, weighted_contribution)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    metrics.timestamp.isoformat(),
                    score.name,
                    score.raw_value,
                    score.normalized_score,
                    score.weight,
                    score.weighted_contribution
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Database storage error: {e}")

    def _trim_performance_history(self, max_entries: int = 1000):
        """Trim performance history to prevent memory issues"""
        if len(self.performance_history) > max_entries:
            self.performance_history = self.performance_history[-max_entries:]

    async def generate_reports(self) -> Dict[str, Any]:
        """Generate comprehensive performance reports"""
        try:
            timestamp = datetime.now()
            
            # Generate daily report
            daily_report = await self._generate_daily_report()
            
            # Generate trend analysis
            trend_analysis = await self._generate_trend_analysis()
            
            # Generate component analysis
            component_analysis = await self._generate_component_analysis()
            
            # Save reports
            await self._save_reports({
                "daily_report": daily_report,
                "trend_analysis": trend_analysis,
                "component_analysis": component_analysis,
                "timestamp": timestamp.isoformat()
            })
            
            self.logger.info("Reports generated successfully")
            
            return {
                "status": "generated",
                "timestamp": timestamp.isoformat(),
                "reports": ["daily", "trend", "component"]
            }
            
        except Exception as e:
            self.logger.error(f"Report generation error: {e}")
            return {"status": "error", "error": str(e)}

    async def _generate_daily_report(self) -> Dict[str, Any]:
        """Generate daily performance report"""
        if not self.performance_history:
            return {"status": "no_data"}
        
        latest_metrics = self.performance_history[-1]
        
        return {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "overall_score": self.latest_score,
            "trading_summary": {
                "total_trades": latest_metrics.total_trades,
                "win_rate": latest_metrics.win_rate,
                "profit_loss_ratio": latest_metrics.profit_loss_ratio,
                "sharpe_ratio": latest_metrics.sharpe_ratio,
                "max_drawdown": latest_metrics.max_drawdown
            },
            "model_performance": {
                "prediction_accuracy": latest_metrics.prediction_accuracy,
                "avg_confidence": latest_metrics.avg_confidence,
                "api_reliability": latest_metrics.api_reliability,
                "retraining_success_rate": latest_metrics.retraining_success_rate
            },
            "component_scores": {
                name: score.normalized_score 
                for name, score in self.component_scores.items()
            }
        }

    async def _generate_trend_analysis(self) -> Dict[str, Any]:
        """Generate trend analysis from historical data"""
        if len(self.performance_history) < 2:
            return {"status": "insufficient_data"}
        
        # Calculate trends over different periods
        trends = {}
        
        # Recent trend (last 24 hours of data points)
        recent_data = self.performance_history[-24:] if len(self.performance_history) >= 24 else self.performance_history
        
        if len(recent_data) >= 2:
            win_rates = [m.win_rate for m in recent_data]
            sharpe_ratios = [m.sharpe_ratio for m in recent_data]
            
            trends["win_rate_trend"] = "improving" if win_rates[-1] > win_rates[0] else "declining"
            trends["sharpe_trend"] = "improving" if sharpe_ratios[-1] > sharpe_ratios[0] else "declining"
        
        return trends

    async def _generate_component_analysis(self) -> Dict[str, Any]:
        """Generate component performance analysis"""
        analysis = {}
        
        for name, score in self.component_scores.items():
            threshold_key = f"{name}_threshold" if name != "drawdown_control" else "drawdown_threshold"
            
            analysis[name] = {
                "current_score": score.normalized_score,
                "weight": score.weight,
                "contribution": score.weighted_contribution,
                "status": "good" if score.normalized_score >= 70 else "needs_improvement"
            }
        
        return analysis

    async def _save_reports(self, reports: Dict[str, Any]):
        """Save reports to files"""
        self.reports_path.mkdir(exist_ok=True)
        
        # Save daily report
        daily_dir = self.reports_path / "daily"
        daily_dir.mkdir(exist_ok=True)
        
        daily_file = daily_dir / f"daily_report_{datetime.now().strftime('%Y%m%d')}.json"
        with open(daily_file, 'w') as f:
            json.dump(reports["daily_report"], f, indent=2)
        
        # Save trend analysis
        trend_file = self.reports_path / f"trend_analysis_{datetime.now().strftime('%Y%m%d')}.json"
        with open(trend_file, 'w') as f:
            json.dump(reports["trend_analysis"], f, indent=2)

    async def run_final_assessment(self) -> Dict[str, Any]:
        """Run final live trading readiness assessment"""
        self.logger.info("🎯 Starting Final Live Trading Readiness Assessment")
        
        try:
            # Update scores one final time
            score_update = await self.update_scores(force_update=True)
            
            if score_update.get("status") != "updated":
                return {"status": "failed", "error": "Could not update scores"}
            
            overall_score = score_update["overall_score"]
            metrics = score_update["metrics"]
            thresholds_met = score_update["thresholds_met"]
            
            # Determine approval status
            approval_status = self._determine_approval_status(overall_score, thresholds_met)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(thresholds_met)
            
            # Create final assessment report
            final_assessment = {
                "assessment_timestamp": datetime.now().isoformat(),
                "live_trading_readiness_score": overall_score,
                "approval_status": approval_status,
                "performance_metrics": metrics,
                "component_scores": {
                    name: asdict(score) for name, score in self.component_scores.items()
                },
                "threshold_checks": thresholds_met,
                "recommendations": recommendations,
                "next_steps": self._get_next_steps(approval_status),
                "scoring_methodology": {
                    "weights": self.scoring_weights,
                    "thresholds": self.min_thresholds
                }
            }
            
            # Save final assessment
            await self._save_final_assessment(final_assessment)
            
            # Log results
            self._log_final_assessment(overall_score, approval_status)
            
            return final_assessment
            
        except Exception as e:
            self.logger.error(f"Final assessment error: {e}")
            return {"status": "failed", "error": str(e)}

    def _determine_approval_status(self, overall_score: float, thresholds_met: Dict[str, bool]) -> str:
        """Determine final approval status"""
        # Check if score meets minimum requirement
        score_approved = overall_score >= self.min_thresholds['live_trading_score']
        
        # Check critical thresholds
        critical_thresholds = ['win_rate_threshold', 'prediction_threshold', 'api_threshold']
        critical_met = all(thresholds_met.get(thresh, False) for thresh in critical_thresholds)
        
        if score_approved and critical_met:
            return "APPROVED_FOR_LIVE_TRADING"
        elif overall_score >= 75.0:
            return "CONDITIONAL_APPROVAL"
        else:
            return "NOT_APPROVED"

    def _generate_recommendations(self, thresholds_met: Dict[str, bool]) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        for threshold, met in thresholds_met.items():
            if not met:
                if threshold == 'win_rate_threshold':
                    recommendations.append("Improve win rate: Consider adjusting entry/exit strategies")
                elif threshold == 'sharpe_threshold':
                    recommendations.append("Enhance risk-adjusted returns: Review position sizing")
                elif threshold == 'prediction_threshold':
                    recommendations.append("Boost prediction accuracy: Retrain models with more data")
                elif threshold == 'drawdown_threshold':
                    recommendations.append("Strengthen drawdown control: Implement stricter stop-loss")
                elif threshold == 'api_threshold':
                    recommendations.append("Improve API reliability: Review connection handling")
                elif threshold == 'retraining_threshold':
                    recommendations.append("Enhance retraining pipeline: Debug model updates")
        
        if not recommendations:
            recommendations.append("System performance is excellent - ready for live trading")
        
        return recommendations

    def _get_next_steps(self, approval_status: str) -> List[str]:
        """Get next steps based on approval status"""
        if approval_status == "APPROVED_FOR_LIVE_TRADING":
            return [
                "✅ System approved for live trading deployment",
                "Configure live trading API credentials",
                "Set initial live trading position sizes",
                "Activate continuous monitoring for live environment"
            ]
        elif approval_status == "CONDITIONAL_APPROVAL":
            return [
                "⚠️ Address specific threshold failures before live deployment",
                "Consider extended testing period with improvements",
                "Re-run assessment after improvements"
            ]
        else:
            return [
                "❌ System requires significant improvements before live trading",
                "Extend testing period",
                "Implement recommended improvements",
                "Re-assess after substantial improvements"
            ]

    async def _save_final_assessment(self, assessment: Dict[str, Any]):
        """Save final assessment to file and database"""
        # Save to file
        final_dir = self.reports_path / "final"
        final_dir.mkdir(exist_ok=True)
        
        final_file = final_dir / "final_assessment.json"
        with open(final_file, 'w') as f:
            json.dump(assessment, f, indent=2)
        
        # Save to database
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("""
                INSERT INTO assessments (timestamp, assessment_type, overall_score, approval_status, report_data)
                VALUES (?, ?, ?, ?, ?)
            """, (
                assessment["assessment_timestamp"],
                "final_assessment",
                assessment["live_trading_readiness_score"],
                assessment["approval_status"],
                json.dumps(assessment)
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            self.logger.error(f"Assessment database storage error: {e}")

    def _log_final_assessment(self, score: float, status: str):
        """Log final assessment results"""
        self.logger.info("=" * 60)
        self.logger.info("🎯 FINAL LIVE TRADING READINESS ASSESSMENT")
        self.logger.info("=" * 60)
        self.logger.info(f"Final Score: {score}/100")
        self.logger.info(f"Status: {status}")
        
        if status == "APPROVED_FOR_LIVE_TRADING":
            self.logger.info(" SYSTEM APPROVED FOR LIVE TRADING DEPLOYMENT!")
        elif status == "CONDITIONAL_APPROVAL":
            self.logger.warning("⚠️ Conditional approval - address issues before live deployment")
        else:
            self.logger.warning("❌ System not ready for live trading - improvements required")
        
        self.logger.info("=" * 60)

    def get_current_score(self) -> Optional[float]:
        """Get current overall score"""
        return self.latest_score

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        if not self.performance_history:
            return {"status": "no_data"}
        
        latest = self.performance_history[-1]
        
        return {
            "current_score": self.latest_score,
            "latest_metrics": asdict(latest),
            "component_scores": {
                name: score.normalized_score 
                for name, score in self.component_scores.items()
            },
            "history_count": len(self.performance_history)
        }
