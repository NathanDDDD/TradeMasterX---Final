"""
TradeMasterX 2.0 - Live Trading Readiness Estimator
Phase 9B Task 5: Final 7-day assessment and live trading approval system
"""

import json
import logging
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import numpy as np
from dataclasses import dataclass

@dataclass
class PerformanceMetrics:
    win_rate: float
    total_trades: int
    profit_loss_ratio: float
    sharpe_ratio: float
    max_drawdown: float
    prediction_accuracy: float
    avg_confidence: float
    api_reliability: float
    retraining_success_rate: float

class LiveReadinessEstimator:
    """
    Final assessment system for 7-day testnet training completion.
    Generates LIVE_TRADING_READINESS_SCORE (0-100) for manual approval.
    """
    
    def __init__(self, data_path: str = "data", reports_path: str = "reports"):
        self.data_path = Path(data_path)
        self.reports_path = Path(reports_path)
        self.logger = self._setup_logging()
        
        # Scoring weights for different performance aspects
        self.scoring_weights = {
            'win_rate': 25,           # 25% weight
            'sharpe_ratio': 20,       # 20% weight  
            'prediction_accuracy': 20, # 20% weight
            'drawdown_control': 15,   # 15% weight
            'api_reliability': 10,    # 10% weight
            'retraining_success': 10  # 10% weight
        }
        
        # Minimum thresholds for live trading approval
        self.min_thresholds = {
            'win_rate': 0.55,         # 55% minimum win rate
            'sharpe_ratio': 1.0,      # Sharpe ratio >= 1.0
            'prediction_accuracy': 0.70, # 70% prediction accuracy
            'max_drawdown': 0.15,     # Max 15% drawdown
            'api_reliability': 0.95,  # 95% API success rate
            'retraining_success': 0.80 # 80% retraining success
        }

    def _setup_logging(self) -> logging.Logger:
        """Setup logging for readiness assessment"""
        logger = logging.getLogger("ReadinessEstimator")
        logger.setLevel(logging.INFO)
        
        # Create file handler
        log_file = self.reports_path / "final" / "readiness_assessment.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger

    def run_final_assessment(self) -> Dict:
        """
        Execute complete 7-day assessment and generate final readiness score.
        
        Returns:
            Dict: Complete assessment results with readiness score
        """
        self.logger.info("🎯 Starting Final Live Trading Readiness Assessment")
        
        try:
            # 1. Collect and aggregate all 7-day performance data
            performance_metrics = self._aggregate_performance_data()
            
            # 2. Calculate individual component scores
            component_scores = self._calculate_component_scores(performance_metrics)
            
            # 3. Calculate weighted final readiness score
            final_score = self._calculate_final_score(component_scores)
            
            # 4. Generate comprehensive assessment report
            assessment_report = self._generate_assessment_report(
                performance_metrics, component_scores, final_score
            )
            
            # 5. Save final evaluation to JSON
            self._save_final_evaluation(assessment_report)
            
            # 6. Log final decision
            self._log_final_decision(final_score, assessment_report)
            
            return assessment_report
            
        except Exception as e:
            self.logger.error(f"❌ Final assessment failed: {e}")
            return {
                "status": "FAILED",
                "readiness_score": 0,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _aggregate_performance_data(self) -> PerformanceMetrics:
        """Aggregate all performance data from 7-day testnet session"""
        self.logger.info("📊 Aggregating 7-day performance data...")
        
        # Connect to trade database
        db_path = self.data_path / "trades.db"
        if not db_path.exists():
            raise FileNotFoundError("Trade database not found")
        
        conn = sqlite3.connect(db_path)
        
        try:
            # Calculate trading performance metrics
            trade_metrics = self._calculate_trade_metrics(conn)
            
            # Calculate prediction accuracy metrics
            prediction_metrics = self._calculate_prediction_metrics(conn)
            
            # Calculate system reliability metrics
            system_metrics = self._calculate_system_metrics(conn)
            
            # Combine all metrics
            return PerformanceMetrics(
                win_rate=trade_metrics['win_rate'],
                total_trades=trade_metrics['total_trades'],
                profit_loss_ratio=trade_metrics['profit_loss_ratio'],
                sharpe_ratio=trade_metrics['sharpe_ratio'],
                max_drawdown=trade_metrics['max_drawdown'],
                prediction_accuracy=prediction_metrics['accuracy'],
                avg_confidence=prediction_metrics['avg_confidence'],
                api_reliability=system_metrics['api_reliability'],
                retraining_success_rate=system_metrics['retraining_success']
            )
            
        finally:
            conn.close()

    def _calculate_trade_metrics(self, conn: sqlite3.Connection) -> Dict:
        """Calculate trading performance metrics"""
        
        # Get all trades from 7-day session
        trades_query = """
        SELECT trade_result, pnl, entry_time 
        FROM trades 
        WHERE entry_time >= datetime('now', '-7 days')
        ORDER BY entry_time
        """
        
        trades = conn.execute(trades_query).fetchall()
        
        if not trades:
            return {
                'win_rate': 0.0, 'total_trades': 0, 'profit_loss_ratio': 0.0,
                'sharpe_ratio': 0.0, 'max_drawdown': 1.0
            }
        
        # Calculate basic metrics
        total_trades = len(trades)
        winning_trades = sum(1 for trade in trades if trade[0] == 'WIN')
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        # Calculate PnL metrics
        pnl_values = [trade[1] for trade in trades]
        total_pnl = sum(pnl_values)
        
        # Calculate profit/loss ratio
        profits = [pnl for pnl in pnl_values if pnl > 0]
        losses = [abs(pnl) for pnl in pnl_values if pnl < 0]
        
        avg_profit = np.mean(profits) if profits else 0
        avg_loss = np.mean(losses) if losses else 1
        profit_loss_ratio = avg_profit / avg_loss if avg_loss > 0 else 0
        
        # Calculate Sharpe ratio
        if len(pnl_values) > 1:
            returns_std = np.std(pnl_values)
            sharpe_ratio = (np.mean(pnl_values) / returns_std) if returns_std > 0 else 0
        else:
            sharpe_ratio = 0
        
        # Calculate maximum drawdown
        cumulative_pnl = np.cumsum(pnl_values)
        running_max = np.maximum.accumulate(cumulative_pnl)
        drawdowns = (running_max - cumulative_pnl) / np.where(running_max != 0, running_max, 1)
        max_drawdown = np.max(drawdowns) if len(drawdowns) > 0 else 0
        
        return {
            'win_rate': win_rate,
            'total_trades': total_trades,
            'profit_loss_ratio': profit_loss_ratio,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown
        }

    def _calculate_prediction_metrics(self, conn: sqlite3.Connection) -> Dict:
        """Calculate prediction accuracy metrics"""
        
        predictions_query = """
        SELECT prediction_correct, confidence 
        FROM predictions 
        WHERE timestamp >= datetime('now', '-7 days')
        """
        
        predictions = conn.execute(predictions_query).fetchall()
        
        if not predictions:
            return {'accuracy': 0.0, 'avg_confidence': 0.0}
        
        correct_predictions = sum(1 for pred in predictions if pred[0] == 1)
        accuracy = correct_predictions / len(predictions)
        
        confidences = [pred[1] for pred in predictions]
        avg_confidence = np.mean(confidences)
        
        return {
            'accuracy': accuracy,
            'avg_confidence': avg_confidence
        }

    def _calculate_system_metrics(self, conn: sqlite3.Connection) -> Dict:
        """Calculate system reliability metrics"""
        
        # API reliability
        api_query = """
        SELECT success FROM api_calls 
        WHERE timestamp >= datetime('now', '-7 days')
        """
        api_calls = conn.execute(api_query).fetchall()
        
        if api_calls:
            successful_calls = sum(1 for call in api_calls if call[0] == 1)
            api_reliability = successful_calls / len(api_calls)
        else:
            api_reliability = 0.0
        
        # Retraining success rate
        retraining_query = """
        SELECT status FROM retraining_sessions 
        WHERE start_time >= datetime('now', '-7 days')
        """
        retraining_sessions = conn.execute(retraining_query).fetchall()
        
        if retraining_sessions:
            successful_retrainings = sum(1 for session in retraining_sessions if session[0] == 'SUCCESS')
            retraining_success = successful_retrainings / len(retraining_sessions)
        else:
            retraining_success = 0.0
        
        return {
            'api_reliability': api_reliability,
            'retraining_success': retraining_success
        }

    def _calculate_component_scores(self, metrics: PerformanceMetrics) -> Dict[str, float]:
        """Calculate individual component scores (0-100)"""
        
        scores = {}
        
        # Win Rate Score (0-100)
        scores['win_rate'] = min(100, (metrics.win_rate / 0.8) * 100)  # 80% = perfect score
        
        # Sharpe Ratio Score (0-100)
        scores['sharpe_ratio'] = min(100, (metrics.sharpe_ratio / 2.0) * 100)  # Sharpe 2.0 = perfect
        
        # Prediction Accuracy Score (0-100)
        scores['prediction_accuracy'] = min(100, (metrics.prediction_accuracy / 0.9) * 100)  # 90% = perfect
        
        # Drawdown Control Score (0-100) - inverse scoring
        scores['drawdown_control'] = max(0, 100 - (metrics.max_drawdown * 500))  # 20% drawdown = 0 points
        
        # API Reliability Score (0-100)
        scores['api_reliability'] = metrics.api_reliability * 100
        
        # Retraining Success Score (0-100)
        scores['retraining_success'] = metrics.retraining_success_rate * 100
        
        return scores

    def _calculate_final_score(self, component_scores: Dict[str, float]) -> float:
        """Calculate weighted final readiness score"""
        
        final_score = 0.0
        
        for component, weight in self.scoring_weights.items():
            score = component_scores.get(component, 0.0)
            final_score += (score * weight) / 100
        
        return round(final_score, 1)

    def _generate_assessment_report(self, metrics: PerformanceMetrics, 
                                  component_scores: Dict[str, float], 
                                  final_score: float) -> Dict:
        """Generate comprehensive assessment report"""
        
        # Check if system meets minimum thresholds
        threshold_checks = self._check_minimum_thresholds(metrics)
        
        # Determine approval status
        approval_status = self._determine_approval_status(final_score, threshold_checks)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(metrics, component_scores)
        
        return {
            "assessment_timestamp": datetime.now().isoformat(),
            "session_duration_days": 7,
            "live_trading_readiness_score": final_score,
            "approval_status": approval_status,
            "performance_metrics": {
                "win_rate": round(metrics.win_rate, 3),
                "total_trades": metrics.total_trades,
                "profit_loss_ratio": round(metrics.profit_loss_ratio, 2),
                "sharpe_ratio": round(metrics.sharpe_ratio, 2),
                "max_drawdown": round(metrics.max_drawdown, 3),
                "prediction_accuracy": round(metrics.prediction_accuracy, 3),
                "avg_confidence": round(metrics.avg_confidence, 2),
                "api_reliability": round(metrics.api_reliability, 3),
                "retraining_success_rate": round(metrics.retraining_success_rate, 2)
            },
            "component_scores": {k: round(v, 1) for k, v in component_scores.items()},
            "threshold_checks": threshold_checks,
            "recommendations": recommendations,
            "next_steps": self._get_next_steps(approval_status),
            "scoring_methodology": {
                "weights": self.scoring_weights,
                "minimum_thresholds": self.min_thresholds
            }
        }

    def _check_minimum_thresholds(self, metrics: PerformanceMetrics) -> Dict[str, bool]:
        """Check if system meets minimum thresholds for live trading"""
        
        return {
            "win_rate_threshold": metrics.win_rate >= self.min_thresholds['win_rate'],
            "sharpe_threshold": metrics.sharpe_ratio >= self.min_thresholds['sharpe_ratio'],
            "prediction_threshold": metrics.prediction_accuracy >= self.min_thresholds['prediction_accuracy'],
            "drawdown_threshold": metrics.max_drawdown <= self.min_thresholds['max_drawdown'],
            "api_threshold": metrics.api_reliability >= self.min_thresholds['api_reliability'],
            "retraining_threshold": metrics.retraining_success_rate >= self.min_thresholds['retraining_success']
        }

    def _determine_approval_status(self, final_score: float, threshold_checks: Dict[str, bool]) -> str:
        """Determine final approval status"""
        
        # Check if score meets minimum requirement
        score_approved = final_score >= 90.0
        
        # Check if all critical thresholds are met
        critical_thresholds = ['win_rate_threshold', 'prediction_threshold', 'api_threshold']
        critical_met = all(threshold_checks[thresh] for thresh in critical_thresholds)
        
        if score_approved and critical_met:
            return "APPROVED_FOR_LIVE_TRADING"
        elif final_score >= 75.0:
            return "CONDITIONAL_APPROVAL"
        else:
            return "NOT_APPROVED"

    def _generate_recommendations(self, metrics: PerformanceMetrics, 
                                component_scores: Dict[str, float]) -> List[str]:
        """Generate improvement recommendations"""
        
        recommendations = []
        
        if component_scores['win_rate'] < 70:
            recommendations.append("Improve win rate: Consider adjusting entry/exit strategies or confidence thresholds")
        
        if component_scores['sharpe_ratio'] < 50:
            recommendations.append("Enhance risk-adjusted returns: Review position sizing and risk management")
        
        if component_scores['prediction_accuracy'] < 75:
            recommendations.append("Boost prediction accuracy: Retrain models with more data or feature engineering")
        
        if component_scores['drawdown_control'] < 60:
            recommendations.append("Strengthen drawdown control: Implement stricter stop-loss mechanisms")
        
        if component_scores['api_reliability'] < 95:
            recommendations.append("Improve API reliability: Review connection handling and error recovery")
        
        if component_scores['retraining_success'] < 80:
            recommendations.append("Enhance retraining pipeline: Debug model update processes")
        
        if not recommendations:
            recommendations.append("System performance is excellent - ready for live trading deployment")
        
        return recommendations

    def _get_next_steps(self, approval_status: str) -> List[str]:
        """Get next steps based on approval status"""
        
        if approval_status == "APPROVED_FOR_LIVE_TRADING":
            return [
                "✅ System approved for live trading deployment",
                "Configure live trading API credentials",
                "Set initial live trading position sizes",
                "Activate continuous monitoring for live environment",
                "Schedule weekly performance reviews"
            ]
        elif approval_status == "CONDITIONAL_APPROVAL":
            return [
                "⚠️ Address specific threshold failures before live deployment",
                "Consider extended testnet period with improvements",
                "Review and optimize underperforming components",
                "Re-run assessment after improvements"
            ]
        else:
            return [
                "❌ System requires significant improvements before live trading",
                "Extend testnet training period",
                "Implement recommended improvements",
                "Consider strategy overhaul if multiple components fail",
                "Re-assess after substantial improvements"
            ]

    def _save_final_evaluation(self, assessment_report: Dict) -> None:
        """Save final evaluation to JSON file"""
        
        final_report_path = self.reports_path / "final" / "final_testnet_evaluation.json"
        final_report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(final_report_path, 'w') as f:
            json.dump(assessment_report, f, indent=2)
        
        self.logger.info(f"📄 Final evaluation saved to: {final_report_path}")

    def _log_final_decision(self, final_score: float, assessment_report: Dict) -> None:
        """Log final assessment decision"""
        
        approval_status = assessment_report['approval_status']
        
        self.logger.info("=" * 60)
        self.logger.info("🎯 FINAL LIVE TRADING READINESS ASSESSMENT")
        self.logger.info("=" * 60)
        self.logger.info(f"Final Score: {final_score}/100")
        self.logger.info(f"Status: {approval_status}")
        
        if approval_status == "APPROVED_FOR_LIVE_TRADING":
            self.logger.info(" SYSTEM APPROVED FOR LIVE TRADING DEPLOYMENT!")
        elif approval_status == "CONDITIONAL_APPROVAL":
            self.logger.warning("⚠️ Conditional approval - address issues before live deployment")
        else:
            self.logger.warning("❌ System not ready for live trading - improvements required")
        
        self.logger.info("=" * 60)


def main():
    """Main function for manual assessment execution"""
    estimator = LiveReadinessEstimator()
    
    print("🎯 TradeMasterX 2.0 - Final Live Trading Readiness Assessment")
    print("=" * 60)
    
    # Run complete assessment
    results = estimator.run_final_assessment()
    
    # Display results
    if results.get('status') != 'FAILED':
        score = results['live_trading_readiness_score']
        status = results['approval_status']
        
        print(f"Final Readiness Score: {score}/100")
        print(f"Approval Status: {status}")
        
        if status == "APPROVED_FOR_LIVE_TRADING":
            print(" CONGRATULATIONS! System approved for live trading!")
        else:
            print("⚠️ System requires improvements before live deployment")
            
        print(f"\nDetailed report saved to: reports/final/final_testnet_evaluation.json")
    else:
        print(f"❌ Assessment failed: {results.get('error')}")


if __name__ == "__main__":
    main()
