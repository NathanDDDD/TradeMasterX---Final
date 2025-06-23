"""
TradeMasterX 2.0 - Trade Deviation Alert System
Phase 12: Live Trade Safety, Failovers & Risk Mitigation Systems

Detects >30% deviation from expected results and logs trade anomalies.
"""

import json
import logging
import math
import statistics
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import csv


class TradeDeviationAlert:
    """
    Trade deviation detection and alert system
    """
    
    @staticmethod
    def _get_default_config() -> Dict[str, Any]:
        """Get default configuration for deviation alert"""
        return {
            'deviation_alert': {
                'threshold': 0.30,
                'min_trades_baseline': 10,
                'lookback_hours': 24,
                'alert_cooldown_minutes': 30,
                'consecutive_deviations': 3
            }
        }
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._get_default_config()
        self.logger = logging.getLogger("TradeDeviationAlert")
        
        # Deviation thresholds
        self.deviation_threshold = self.config.get('deviation_alert', {}).get('threshold', 0.30)  # 30%
        self.min_trades_for_baseline = self.config.get('deviation_alert', {}).get('min_trades_baseline', 10)
        self.lookback_hours = self.config.get('deviation_alert', {}).get('lookback_hours', 24)
        
        # Alert settings
        self.alert_cooldown_minutes = self.config.get('deviation_alert', {}).get('alert_cooldown_minutes', 30)
        self.consecutive_deviations_alert = self.config.get('deviation_alert', {}).get('consecutive_deviations', 3)
        
        # State tracking
        self.trade_history = []
        self.baseline_metrics = {}
        self.recent_alerts = []
        self.consecutive_deviations = 0
        self._lock = threading.Lock()
        
        # File paths
        self.alert_log_file = Path("alerts/trade_anomaly.log")
        self.trade_data_file = Path("data/safety/trade_deviations.json")
        self.detailed_log_file = Path("logs/deviation_analysis.log")
        
        # Ensure directories exist
        self.alert_log_file.parent.mkdir(parents=True, exist_ok=True)
        self.trade_data_file.parent.mkdir(parents=True, exist_ok=True)
        self.detailed_log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load historical data
        self._load_trade_history()
        self.logger.info("Trade Deviation Alert system initialized")
        self.logger.info(f"Deviation threshold: {self.deviation_threshold:.1%}")
        
    def _load_trade_history(self):
        """Load historical trade data for baseline calculation"""
        try:
            if self.trade_data_file.exists():
                with open(self.trade_data_file, 'r') as f:
                    data = json.load(f)
                    self.trade_history = data.get('trade_history', [])
                    self.baseline_metrics = data.get('baseline_metrics', {})
                    
                # Clean old data (keep only recent trades)
                cutoff_time = datetime.now() - timedelta(hours=self.lookback_hours * 2)
                self.trade_history = [
                    trade for trade in self.trade_history
                    if datetime.fromisoformat(trade['timestamp']) > cutoff_time
                ]
                
                self.logger.info(f"Loaded {len(self.trade_history)} historical trades")
                
                # Recalculate baseline if enough data
                if len(self.trade_history) >= self.min_trades_for_baseline:
                    self._calculate_baseline_metrics()
                    
        except Exception as e:
            self.logger.error(f"Error loading trade history: {e}")
            self.trade_history = []
            self.baseline_metrics = {}
            
    def analyze_trade(self, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a trade for deviation from baseline
        
        Args:
            trade_data: Current trade data
            
        Returns:
            Dict containing analysis results
        """
        with self._lock:
            try:
                # Add trade to history
                self.add_trade_to_history(trade_data)
                
                # Check if we have enough data for analysis
                if len(self.trade_history) < self.min_trades_for_baseline:
                    return {
                        "analysis_complete": False,
                        "reason": f"Insufficient data (need {self.min_trades_for_baseline}, have {len(self.trade_history)})",
                        "timestamp": datetime.now().isoformat()
                    }
                
                # Calculate deviations
                deviations = self._calculate_deviations(trade_data)
                
                # Check for deviation alerts
                alert_triggered = self._check_deviation_alerts(trade_data)
                
                analysis_result = {
                    "analysis_complete": True,
                    "deviations": deviations,
                    "alert_triggered": alert_triggered,
                    "consecutive_deviations": self.consecutive_deviations,
                    "baseline_metrics": self.baseline_metrics,
                    "timestamp": datetime.now().isoformat()
                }
                
                return analysis_result
                
            except Exception as e:
                self.logger.error(f"Error analyzing trade: {e}")
                return {"error": str(e), "timestamp": datetime.now().isoformat()}
    
    def add_trade_to_history(self, trade_data: Dict[str, Any]):
        """Add a trade to the historical data"""
        try:
            trade_entry = {
                "timestamp": datetime.now().isoformat(),
                "symbol": trade_data.get('symbol', 'UNKNOWN'),
                "action": trade_data.get('action', 'UNKNOWN'),
                "quantity": trade_data.get('quantity', 0),
                "price": trade_data.get('price', 0),
                "pnl": trade_data.get('pnl', 0),
                "win_rate": trade_data.get('win_rate', 0),
                "avg_win": trade_data.get('avg_win', 0),
                "avg_loss": trade_data.get('avg_loss', 0),
                "risk_reward": trade_data.get('risk_reward', 0)
            }
            
            self.trade_history.append(trade_entry)
            
            # Keep only recent trades
            cutoff_time = datetime.now() - timedelta(hours=self.lookback_hours)
            self.trade_history = [
                trade for trade in self.trade_history
                if datetime.fromisoformat(trade['timestamp']) > cutoff_time
            ]
            
            # Recalculate baseline if enough data
            if len(self.trade_history) >= self.min_trades_for_baseline:
                self._calculate_baseline_metrics()
                
            # Save data
            self._save_trade_data()
            
        except Exception as e:
            self.logger.error(f"Error adding trade to history: {e}")
    
    def _calculate_deviations(self, trade_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate deviations from baseline metrics"""
        try:
            if not self.baseline_metrics:
                return {}
            
            deviations = {}
            
            # Calculate win rate deviation
            current_win_rate = trade_data.get('win_rate', 0)
            baseline_win_rate = self.baseline_metrics.get('avg_win_rate', current_win_rate)
            if baseline_win_rate > 0:
                win_rate_deviation = abs(current_win_rate - baseline_win_rate) / baseline_win_rate
                deviations['win_rate'] = win_rate_deviation
            
            # Calculate PnL deviation
            current_pnl = trade_data.get('pnl', 0)
            baseline_pnl = self.baseline_metrics.get('avg_pnl', current_pnl)
            if baseline_pnl != 0:
                pnl_deviation = abs(current_pnl - baseline_pnl) / abs(baseline_pnl)
                deviations['pnl'] = pnl_deviation
            
            # Calculate risk-reward deviation
            current_rr = trade_data.get('risk_reward', 0)
            baseline_rr = self.baseline_metrics.get('avg_risk_reward', current_rr)
            if baseline_rr > 0:
                rr_deviation = abs(current_rr - baseline_rr) / baseline_rr
                deviations['risk_reward'] = rr_deviation
                
            return deviations
            
        except Exception as e:
            self.logger.error(f"Error calculating deviations: {e}")
            return {}
            
    def _check_deviation_alerts(self, trade_data: Dict[str, Any]) -> bool:
        """
        Check for deviation alerts based on trade data
        
        Args:
            trade_data: Current trade data
            
        Returns:
            bool: True if alert was triggered
        """
        try:
            alert_triggered = False
            
            # Calculate deviations
            deviations = self._calculate_deviations(trade_data)
            significant_deviations = []
            
            # Check for significant deviations
            for metric, deviation in deviations.items():
                if deviation > self.deviation_threshold:
                    significant_deviations.append({
                        "metric": metric,
                        "deviation": deviation,
                        "threshold": self.deviation_threshold
                    })
                    
            if significant_deviations:
                # Check alert cooldown
                if self._should_trigger_alert():
                    alert_triggered = True
                    self.consecutive_deviations += 1
                    
                    # Log to alert file
                    self._log_deviation_alert(trade_data, significant_deviations)
                    
                    # Check for consecutive deviation alerts
                    if self.consecutive_deviations >= self.consecutive_deviations_alert:
                        self._trigger_consecutive_deviation_alert(trade_data)
                        
                else:
                    self.logger.debug("Alert suppressed due to cooldown period")
            else:
                # Reset consecutive counter if no significant deviations
                self.consecutive_deviations = 0
                
            return alert_triggered
            
        except Exception as e:
            self.logger.error(f"Error checking deviation alerts: {e}")
            return False
            
    def _should_trigger_alert(self) -> bool:
        """Check if enough time has passed since last alert"""
        try:
            if not self.recent_alerts:
                return True
                
            last_alert_time = datetime.fromisoformat(self.recent_alerts[-1]['timestamp'])
            cooldown_period = timedelta(minutes=self.alert_cooldown_minutes)
            
            return datetime.now() - last_alert_time > cooldown_period
            
        except Exception as e:
            self.logger.error(f"Error checking alert cooldown: {e}")
            return True
            
    def _log_deviation_alert(self, trade_data: Dict[str, Any], deviations: List[Dict[str, Any]]):
        """Log deviation alert to file"""
        try:
            alert_data = {
                "timestamp": datetime.now().isoformat(),
                "trade_data": trade_data,
                "deviations": deviations,
                "consecutive_count": self.consecutive_deviations
            }
            
            # Add to recent alerts
            self.recent_alerts.append(alert_data)
            
            # Keep only recent alerts (last 50)
            self.recent_alerts = self.recent_alerts[-50:]
            
            # Log to file
            with open(self.alert_log_file, 'a', encoding='utf-8') as f:
                f.write(f"{json.dumps(alert_data)}\\n")
                
            self.logger.warning(f"DEVIATION ALERT: {len(deviations)} metrics exceeded threshold")
            
        except Exception as e:
            self.logger.error(f"Error logging deviation alert: {e}")
            
    def _trigger_consecutive_deviation_alert(self, trade_data: Dict[str, Any]):
        """Trigger high-priority alert for consecutive deviations"""
        try:
            alert_msg = f"CRITICAL: {self.consecutive_deviations} consecutive trade deviations detected!"
            
            # Log critical alert
            self.logger.critical(alert_msg)
            
            # Reset consecutive counter after triggering
            self.consecutive_deviations = 0
            
        except Exception as e:
            self.logger.error(f"Error triggering consecutive deviation alert: {e}")
    
    def calculate_baseline(self, trades: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate baseline metrics from provided trade data
        
        Args:
            trades: List of trade data dictionaries
            
        Returns:
            Dict containing calculated baseline metrics
        """
        try:
            if not trades:
                return {}
              # Extract metrics from trades
            win_rates = [trade.get('win_rate', 0) for trade in trades if trade.get('win_rate') is not None]
            pnls = [trade.get('pnl', 0) for trade in trades if trade.get('pnl') is not None]
            risk_rewards = [trade.get('risk_reward', 0) for trade in trades if trade.get('risk_reward') is not None]
            expected_returns = [trade.get('expected_return', 0) for trade in trades if trade.get('expected_return') is not None]
            
            baseline = {}
              # Calculate averages
            if win_rates:
                baseline['avg_win_rate'] = statistics.mean(win_rates)
                baseline['std_win_rate'] = statistics.stdev(win_rates) if len(win_rates) > 1 else 0
            
            if pnls:
                baseline['avg_pnl'] = statistics.mean(pnls)
                baseline['std_pnl'] = statistics.stdev(pnls) if len(pnls) > 1 else 0
            
            if risk_rewards:
                baseline['avg_risk_reward'] = statistics.mean(risk_rewards)
                baseline['std_risk_reward'] = statistics.stdev(risk_rewards) if len(risk_rewards) > 1 else 0              # Calculate expected return from either expected_return field or PnL data
            if expected_returns:
                baseline['expected_return'] = statistics.mean(expected_returns)
            elif pnls:
                baseline['expected_return'] = statistics.mean(pnls)
            
            # Calculate confidence metrics
            confidences = [trade.get('confidence', 0.7) for trade in trades if trade.get('confidence') is not None]
            if confidences:
                baseline['confidence'] = statistics.mean(confidences)
            else:
                baseline['confidence'] = 0.7  # Default confidence level
            
            baseline['trade_count'] = len(trades)
            baseline['calculated_at'] = datetime.now().isoformat()
            
            return baseline
            
        except Exception as e:
            self.logger.error(f"Error calculating baseline metrics: {e}")
            return {}
    
    def _calculate_baseline_metrics(self):
        """Calculate baseline metrics from current trade history"""
        self.baseline_metrics = self.calculate_baseline(self.trade_history)
        
    def _save_trade_data(self):
        """Save trade data and metrics to file"""
        try:
            data = {
                "trade_history": self.trade_history,
                "baseline_metrics": self.baseline_metrics,
                "saved_at": datetime.now().isoformat()
            }
            
            with open(self.trade_data_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Error saving trade data: {e}")
    
    def get_deviation_status(self) -> Dict[str, Any]:
        """Get current deviation monitoring status"""
        return {
            "active": True,
            "trade_count": len(self.trade_history),
            "baseline_established": bool(self.baseline_metrics),
            "consecutive_deviations": self.consecutive_deviations,
            "recent_alerts": len(self.recent_alerts),
            "threshold": self.deviation_threshold,
            "baseline_metrics": self.baseline_metrics,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_recent_alerts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent deviation alerts"""
        return self.recent_alerts[-limit:] if self.recent_alerts else []


def main():
    """CLI interface for deviation alert system"""
    import sys
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    deviation_alert = TradeDeviationAlert()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python trade_deviation_alert.py status")
        print("  python trade_deviation_alert.py alerts [limit]")
        sys.exit(1)
        
    command = sys.argv[1]
    
    if command == "status":
        status = deviation_alert.get_deviation_status()
        print("\\nTRADE DEVIATION ALERT STATUS")
        print("=" * 40)
        print(f"Active: {status['active']}")
        print(f"Trade Count: {status['trade_count']}")
        print(f"Baseline Established: {status['baseline_established']}")
        print(f"Consecutive Deviations: {status['consecutive_deviations']}")
        print(f"Recent Alerts: {status['recent_alerts']}")
        print(f"Threshold: {status['threshold']:.1%}")
        
        if status['baseline_metrics']:
            print("\\nBaseline Metrics:")
            for key, value in status['baseline_metrics'].items():
                if isinstance(value, float):
                    print(f"  {key}: {value:.4f}")
                else:
                    print(f"  {key}: {value}")
                    
    elif command == "alerts":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        alerts = deviation_alert.get_recent_alerts(limit)
        
        print(f"\\nRECENT DEVIATION ALERTS (Last {limit})")
        print("=" * 50)
        
        if not alerts:
            print("No recent alerts")
        else:
            for i, alert in enumerate(alerts, 1):
                print(f"\\n{i}. {alert['timestamp']}")
                print(f"   Consecutive: {alert['consecutive_count']}")
                print(f"   Deviations: {len(alert['deviations'])}")
                for dev in alert['deviations']:
                    print(f"     - {dev['metric']}: {dev['deviation']:.2%} (threshold: {dev['threshold']:.1%})")
                    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
