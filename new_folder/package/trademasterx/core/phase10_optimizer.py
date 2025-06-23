"""
TradeMasterX 2.0 - Phase 10 Optimization Agent
Tracks bot performance, scores predictions, and improves models during the learning loop
"""

import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import json
import csv
import os
from typing import Dict, List, Any, Optional, Tuple

from ..config.config_loader import ConfigLoader

class Phase10Optimizer:
    """
    Phase 10 Optimization Agent - Tracks and improves bot performance during learning loop
    
    Responsibilities:
    - Score bot predictions against actual outcomes
    - Track performance metrics for each bot
    - Identify underperforming strategies
    - Generate optimization insights
    - Prepare retraining data
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the Phase 10 Optimizer"""
        self.config = config
        self.logger = self._setup_logging()
        
        # Initialize tracking structures
        self.bot_scores = {}
        self.prediction_history = {}
        self.trade_outcomes = []
        
        # Metrics to track
        self.metrics = {
            "trade_accuracy": {},
            "avg_return": {},
            "precision": {},
            "recall": {},
            "win_loss_ratio": {},
            "drawdown": {},
            "sharpe_ratio": {},
            "contribution_score": {}
        }
        
        # Create directories for reports and logs
        self.logs_dir = Path("logs")
        self.reports_dir = Path("reports")
        self.logs_dir.mkdir(exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)
        
        # File paths
        self.log_file = self.logs_dir / "phase_10_learning.log"
        self.performance_csv = self.reports_dir / "phase_10_bot_performance.csv"
        self.predictions_csv = self.reports_dir / "phase_10_predictions.csv"
        self.metrics_json = self.reports_dir / "phase_10_metrics.json"
        
        # Initialize files
        self._initialize_files()
        
        self.logger.info("Phase 10 Optimizer initialized successfully")
        
    def _setup_logging(self) -> logging.Logger:
        """Setup optimizer logging"""
        logger = logging.getLogger("Phase10Optimizer")
        logger.setLevel(logging.INFO)
        
        # Create file handler
        file_handler = logging.FileHandler("logs/phase_10_learning.log")
        
        # Create console handler
        console_handler = logging.StreamHandler()
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def _initialize_files(self):
        """Initialize log files and tracking CSVs"""
        # Initialize performance CSV
        if not self.performance_csv.exists():
            with open(self.performance_csv, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'bot_id', 'accuracy', 'win_rate', 
                    'avg_return', 'sharpe_ratio', 'drawdown', 
                    'contribution_score', 'confidence'
                ])
                
        # Initialize predictions CSV
        if not self.predictions_csv.exists():
            with open(self.predictions_csv, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'bot_id', 'prediction', 'confidence', 
                    'signal', 'expected_return', 'actual_return', 
                    'was_correct', 'market_conditions'
                ])
                
        # Initialize metrics JSON
        if not self.metrics_json.exists():
            with open(self.metrics_json, 'w') as f:
                json.dump(self.metrics, f, indent=2)
    
    def record_prediction(self, bot_id: str, prediction: Dict[str, Any], 
                          market_data: Dict[str, Any]) -> None:
        """Record a bot's prediction for later scoring"""
        timestamp = datetime.now().isoformat()
        
        if bot_id not in self.prediction_history:
            self.prediction_history[bot_id] = []
            
        prediction_record = {
            'timestamp': timestamp,
            'prediction': prediction,
            'market_data': market_data,
            'scored': False,
            'outcome': None
        }
        
        self.prediction_history[bot_id].append(prediction_record)
        
        # Log the prediction
        self.logger.info(f"Recorded prediction from {bot_id}: {prediction}")
    
    def record_trade_outcome(self, trade_data: Dict[str, Any]) -> None:
        """Record the outcome of a trade for scoring predictions"""
        self.trade_outcomes.append(trade_data)
        
        # Match trade with predictions and score them
        self._score_predictions_for_trade(trade_data)
        
        # Log the trade outcome
        self.logger.info(f"Trade outcome recorded: {trade_data}")
    
    def _score_predictions_for_trade(self, trade_data: Dict[str, Any]) -> None:
        """Score bot predictions against actual trade outcome"""
        trade_symbol = trade_data.get('symbol')
        trade_signal = trade_data.get('signal')
        trade_return = trade_data.get('actual_return', 0)
        trade_timestamp = trade_data.get('timestamp')
        
        if not trade_timestamp:
            trade_timestamp = datetime.now().isoformat()
            
        # Score each bot's predictions
        for bot_id, predictions in self.prediction_history.items():
            for pred in predictions:
                # Skip already scored predictions
                if pred['scored']:
                    continue
                    
                # Check if prediction is for this trade
                pred_symbol = pred['prediction'].get('symbol', trade_symbol)
                if pred_symbol != trade_symbol:
                    continue
                    
                # Get prediction details
                pred_signal = pred['prediction'].get('signal')
                confidence = pred['prediction'].get('confidence', 0.5)
                expected_return = pred['prediction'].get('expected_return', 0)
                
                # Score prediction
                was_correct = (pred_signal == trade_signal)
                pred['scored'] = True
                pred['outcome'] = {
                    'was_correct': was_correct,
                    'actual_return': trade_return,
                    'trade_timestamp': trade_timestamp
                }
                
                # Record to CSV for analysis
                with open(self.predictions_csv, 'a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        trade_timestamp, bot_id, json.dumps(pred['prediction']), 
                        confidence, pred_signal, expected_return, trade_return,
                        was_correct, json.dumps(pred['market_data'])
                    ])
                
                # Update bot scores
                if bot_id not in self.bot_scores:
                    self.bot_scores[bot_id] = {
                        'total_predictions': 0,
                        'correct_predictions': 0,
                        'total_return': 0,
                        'returns': [],
                        'confidences': [],
                        'signals': []
                    }
                
                scores = self.bot_scores[bot_id]
                scores['total_predictions'] += 1
                if was_correct:
                    scores['correct_predictions'] += 1
                
                scores['total_return'] += trade_return
                scores['returns'].append(trade_return)
                scores['confidences'].append(confidence)
                scores['signals'].append(pred_signal)
    
    def update_bot_metrics(self) -> Dict[str, Dict[str, float]]:
        """Calculate and update metrics for all bots"""
        for bot_id, scores in self.bot_scores.items():
            if scores['total_predictions'] == 0:
                continue
                
            # Calculate metrics
            accuracy = scores['correct_predictions'] / scores['total_predictions']
            avg_return = scores['total_return'] / scores['total_predictions']
            
            # Calculate Sharpe ratio if we have enough data
            returns = np.array(scores['returns'])
            if len(returns) > 1:
                sharpe = returns.mean() / returns.std() if returns.std() > 0 else 0
            else:
                sharpe = 0
                
            # Calculate max drawdown
            drawdown = 0
            if len(returns) > 1:
                cumulative = np.cumsum(returns)
                max_so_far = np.maximum.accumulate(cumulative)
                drawdowns = (max_so_far - cumulative) / (max_so_far + 1e-10)  # Avoid div by zero
                drawdown = np.max(drawdowns) if len(drawdowns) > 0 else 0
                
            # Calculate win/loss ratio
            wins = sum(1 for r in returns if r > 0)
            losses = sum(1 for r in returns if r <= 0)
            win_ratio = wins / losses if losses > 0 else wins
            
            # Calculate contribution score (custom metric)
            # Higher for bots with consistent, high-confidence, correct predictions
            confidences = np.array(scores['confidences'])
            correct_mask = np.array([1 if r > 0 else 0 for r in returns])
            if len(correct_mask) > 0 and len(confidences) > 0:
                contribution = np.mean(confidences * correct_mask) * (1 + avg_return)
            else:
                contribution = 0
                
            # Update metrics dictionary
            self.metrics["trade_accuracy"][bot_id] = accuracy
            self.metrics["avg_return"][bot_id] = avg_return
            self.metrics["sharpe_ratio"][bot_id] = sharpe
            self.metrics["drawdown"][bot_id] = drawdown
            self.metrics["win_loss_ratio"][bot_id] = win_ratio
            self.metrics["contribution_score"][bot_id] = contribution
            
            # Record to CSV
            with open(self.performance_csv, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    datetime.now().isoformat(), bot_id, accuracy, win_ratio, 
                    avg_return, sharpe, drawdown, contribution, 
                    np.mean(confidences) if len(confidences) > 0 else 0
                ])
            
            # Log the metrics update
            self.logger.info(f"Updated metrics for {bot_id}: "
                            f"Accuracy={accuracy:.2f}, "
                            f"Avg Return={avg_return:.4f}, "
                            f"Sharpe={sharpe:.2f}, "
                            f"Contribution={contribution:.2f}")
                
        # Save metrics to JSON
        with open(self.metrics_json, 'w') as f:
            # Convert numpy values to Python native types for JSON serialization
            metrics_json = {}
            for metric_name, bot_values in self.metrics.items():
                metrics_json[metric_name] = {
                    bot_id: float(value) for bot_id, value in bot_values.items()
                }
            
            json.dump(metrics_json, f, indent=2)
            
        return self.metrics
    
    def get_retraining_data(self) -> Dict[str, Any]:
        """Prepare data for model retraining based on performance"""
        # Collect high-confidence, correct predictions for retraining
        retraining_data = {
            'predictions': [],
            'outcomes': [],
            'market_data': [],
            'timestamps': []
        }
        
        # Identify top performing bots
        if self.metrics["contribution_score"]:
            top_bots = sorted(
                self.metrics["contribution_score"].items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:5]  # Top 5 bots
            
            top_bot_ids = [bot_id for bot_id, _ in top_bots]
            
            # Collect their successful predictions
            for bot_id in top_bot_ids:
                if bot_id not in self.prediction_history:
                    continue
                    
                for pred in self.prediction_history[bot_id]:
                    if not pred['scored'] or not pred['outcome']:
                        continue
                        
                    # Only use correct, high-confidence predictions
                    confidence = pred['prediction'].get('confidence', 0)
                    was_correct = pred['outcome']['was_correct']
                    
                    if was_correct and confidence >= 0.75:  # High confidence threshold
                        retraining_data['predictions'].append(pred['prediction'])
                        retraining_data['outcomes'].append(pred['outcome'])
                        retraining_data['market_data'].append(pred['market_data'])
                        retraining_data['timestamps'].append(pred['timestamp'])
        
        self.logger.info(f"Prepared retraining data with {len(retraining_data['predictions'])} high-quality samples")
        return retraining_data
    
    def generate_bot_report(self) -> Dict[str, Any]:
        """Generate a comprehensive report on bot performance"""
        # Update metrics first
        self.update_bot_metrics()
        
        # Create report structure
        report = {
            'timestamp': datetime.now().isoformat(),
            'period': '7d',
            'bots': {},
            'system': {
                'total_trades': len(self.trade_outcomes),
                'avg_system_return': 0,
                'win_rate': 0,
                'best_performing_bot': '',
                'worst_performing_bot': '',
                'optimization_recommendations': []
            }
        }
        
        # Calculate system-wide metrics
        if self.trade_outcomes:
            returns = [trade.get('actual_return', 0) for trade in self.trade_outcomes]
            wins = sum(1 for r in returns if r > 0)
            
            report['system']['avg_system_return'] = sum(returns) / len(returns)
            report['system']['win_rate'] = wins / len(returns)
        
        # Add per-bot statistics
        for bot_id, scores in self.bot_scores.items():
            if scores['total_predictions'] == 0:
                continue
                
            # Get metrics from the updated metrics dict
            accuracy = self.metrics["trade_accuracy"].get(bot_id, 0)
            avg_return = self.metrics["avg_return"].get(bot_id, 0)
            sharpe = self.metrics["sharpe_ratio"].get(bot_id, 0)
            drawdown = self.metrics["drawdown"].get(bot_id, 0)
            win_ratio = self.metrics["win_loss_ratio"].get(bot_id, 0)
            contribution = self.metrics["contribution_score"].get(bot_id, 0)
            
            report['bots'][bot_id] = {
                'accuracy': accuracy,
                'avg_return': avg_return,
                'sharpe_ratio': sharpe,
                'max_drawdown': drawdown,
                'win_loss_ratio': win_ratio,
                'contribution_score': contribution,
                'total_predictions': scores['total_predictions'],
                'recommendations': []
            }
            
            # Add bot-specific recommendations
            if accuracy < 0.5:
                report['bots'][bot_id]['recommendations'].append(
                    "Model accuracy below 50% - Consider retraining with more data"
                )
                
            if contribution < 0.2 and scores['total_predictions'] > 10:
                report['bots'][bot_id]['recommendations'].append(
                    "Low contribution score - Review bot utility in the system"
                )
                
            if drawdown > 0.3:
                report['bots'][bot_id]['recommendations'].append(
                    "High drawdown detected - Add risk management rules"
                )
                
        # Identify best and worst bots
        if self.metrics["contribution_score"]:
            contributions = self.metrics["contribution_score"].items()
            if contributions:
                best_bot = max(contributions, key=lambda x: x[1])[0]
                worst_bot = min(contributions, key=lambda x: x[1])[0]
                
                report['system']['best_performing_bot'] = best_bot
                report['system']['worst_performing_bot'] = worst_bot
        
        # Generate system-wide recommendations
        if report['system']['win_rate'] < 0.5:
            report['system']['optimization_recommendations'].append(
                "System win rate below 50% - Review overall strategy mix"
            )
            
        if report['system']['avg_system_return'] < 0:
            report['system']['optimization_recommendations'].append(
                "Negative average return - Consider more conservative position sizing"
            )
            
        # Calculate system readiness score
        readiness_factors = [
            min(1.0, report['system']['win_rate'] / 0.55),  # Target 55%+ win rate
            min(1.0, max(0, report['system']['avg_system_return'] / 0.002)),  # Target 0.2%+ return
        ]
        
        # Add bot factor (need at least 3 bots with contribution > 0.3)
        good_bots = sum(1 for bot_id, data in report['bots'].items() 
                      if data['contribution_score'] > 0.3)
        bot_factor = min(1.0, good_bots / 3)
        readiness_factors.append(bot_factor)
        
        # Calculate overall readiness (0-100%)
        if readiness_factors:
            report['system']['readiness_score'] = int(100 * sum(readiness_factors) / len(readiness_factors))
        else:
            report['system']['readiness_score'] = 0
            
        # Save report to file
        report_file = self.reports_dir / f"phase_10_report_{datetime.now().strftime('%Y%m%d')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        self.logger.info(f"Generated bot performance report: {report_file}")
        self.logger.info(f"System readiness score: {report['system']['readiness_score']}%")
        
        return report
    
    def identify_underperforming_bots(self) -> List[str]:
        """Identify bots that need improvement or replacement"""
        underperforming = []
        
        # Update metrics first
        self.update_bot_metrics()
        
        # Check each bot against thresholds
        for bot_id in self.bot_scores.keys():
            scores = self.bot_scores[bot_id]
            
            # Skip bots with too few predictions
            if scores['total_predictions'] < 10:
                continue
                
            # Get metrics
            accuracy = self.metrics["trade_accuracy"].get(bot_id, 0)
            avg_return = self.metrics["avg_return"].get(bot_id, 0)
            contribution = self.metrics["contribution_score"].get(bot_id, 0)
            
            # Check against thresholds
            if (accuracy < 0.45 or  # Below 45% accuracy
                avg_return < 0 or   # Negative returns
                contribution < 0.2): # Low contribution
                
                underperforming.append(bot_id)
                self.logger.warning(f"Bot {bot_id} identified as underperforming: "
                                  f"Accuracy={accuracy:.2f}, "
                                  f"Avg Return={avg_return:.4f}, "
                                  f"Contribution={contribution:.2f}")
                
        return underperforming
    
    def export_top_configurations(self) -> Dict[str, Any]:
        """Export configurations of top-performing bots"""
        if not self.metrics["contribution_score"]:
            return {}
            
        # Get top 3 bots by contribution score
        top_bots = sorted(
            self.metrics["contribution_score"].items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:3]
        
        # Format for export
        top_configs = {
            'timestamp': datetime.now().isoformat(),
            'top_performers': [
                {
                    'bot_id': bot_id,
                    'contribution_score': score,
                    'trade_accuracy': self.metrics["trade_accuracy"].get(bot_id, 0),
                    'avg_return': self.metrics["avg_return"].get(bot_id, 0)
                }
                for bot_id, score in top_bots
            ]
        }
        
        # Save to candidate file
        config_file = Path('configs') / 'live_candidates.yaml'
        
        # Simple YAML format
        with open(config_file, 'w') as f:
            f.write(f"# Top performing configurations from Phase 10\n")
            f.write(f"# Generated: {datetime.now().isoformat()}\n\n")
            
            f.write("top_performers:\n")
            for i, bot_data in enumerate(top_configs['top_performers']):
                f.write(f"  candidate_{i+1}:\n")
                f.write(f"    bot_id: {bot_data['bot_id']}\n")
                f.write(f"    contribution_score: {bot_data['contribution_score']:.4f}\n")
                f.write(f"    trade_accuracy: {bot_data['trade_accuracy']:.4f}\n")
                f.write(f"    avg_return: {bot_data['avg_return']:.4f}\n")
                f.write("\n")
                
        self.logger.info(f"Exported top configurations to {config_file}")
        return top_configs
