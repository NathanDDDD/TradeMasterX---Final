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
            self.logger.error(f"❌ Error loading trade history: {e}")
            self.trade_history = []
            self.baseline_metrics = {}
            
    def analyze_trade(self, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a trade for deviations and trigger alerts if necessary
        
        Args:
            trade_data: Trade information including expected vs actual results
            
        Returns:
            Dict with analysis results and alert information
        """
        with self._lock:
            try:
                # Add trade to history
                self._add_trade_to_history(trade_data)
                
                # Calculate deviations
                deviations = self._calculate_deviations(trade_data)
                
                # Check for significant deviations
                alert_triggered = self._check_deviation_alerts(trade_data, deviations)
                
                # Update baseline metrics
                self._update_baseline_metrics()
                
                # Save updated data
                self._save_trade_data()
                
                # Create analysis result
                result = {
                    "trade_id": trade_data.get('trade_id'),
                    "timestamp": datetime.now().isoformat(),
                    "deviations": deviations,
                    "alert_triggered": alert_triggered,
                    "baseline_metrics": self.baseline_metrics.copy(),
                    "consecutive_deviations": self.consecutive_deviations
                }
                
                return result
                
            except Exception as e:
                self.logger.error(f"❌ Error analyzing trade: {e}")
                return {"error": str(e)}
                
    def _add_trade_to_history(self, trade_data: Dict[str, Any]):
        """Add trade to historical data"""
        try:
            trade_record = {
                "trade_id": trade_data.get('trade_id'),
                "timestamp": datetime.now().isoformat(),
                "symbol": trade_data.get('symbol'),
                "expected_return": trade_data.get('expected_return', 0.0),
                "actual_return": trade_data.get('actual_return', 0.0),
                "expected_confidence": trade_data.get('expected_confidence', 0.0),
                "actual_confidence": trade_data.get('actual_confidence', 0.0),
                "position_size": trade_data.get('position_size', 0.0),
                "execution_time_ms": trade_data.get('execution_time_ms', 0),
                "slippage": trade_data.get('slippage', 0.0),
                "fees": trade_data.get('fees', 0.0)
            }
            
            self.trade_history.append(trade_record)
            
            # Limit history size
            if len(self.trade_history) > 1000:
                self.trade_history = self.trade_history[-800:]  # Keep recent 800 trades
                
        except Exception as e:
            self.logger.error(f"❌ Error adding trade to history: {e}")
            
    def _calculate_deviations(self, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate various deviation metrics for the trade"""
        try:
            deviations = {}
            
            # Return deviation
            expected_return = trade_data.get('expected_return', 0.0)
            actual_return = trade_data.get('actual_return', 0.0)
            
            if expected_return != 0:
                return_deviation = abs(actual_return - expected_return) / abs(expected_return)
                deviations['return_deviation'] = return_deviation
            else:
                deviations['return_deviation'] = 0.0
                
            # Confidence deviation
            expected_confidence = trade_data.get('expected_confidence', 0.0)
            actual_confidence = trade_data.get('actual_confidence', 0.0)
            
            if expected_confidence != 0:
                confidence_deviation = abs(actual_confidence - expected_confidence) / expected_confidence
                deviations['confidence_deviation'] = confidence_deviation
            else:
                deviations['confidence_deviation'] = 0.0
                
            # Execution time deviation (vs baseline)
            execution_time = trade_data.get('execution_time_ms', 0)
            baseline_exec_time = self.baseline_metrics.get('avg_execution_time_ms', 100)
            
            if baseline_exec_time > 0:
                exec_time_deviation = abs(execution_time - baseline_exec_time) / baseline_exec_time
                deviations['execution_time_deviation'] = exec_time_deviation
            else:
                deviations['execution_time_deviation'] = 0.0
                
            # Slippage deviation
            slippage = trade_data.get('slippage', 0.0)
            baseline_slippage = self.baseline_metrics.get('avg_slippage', 0.001)
            
            if baseline_slippage > 0:
                slippage_deviation = abs(slippage - baseline_slippage) / baseline_slippage
                deviations['slippage_deviation'] = slippage_deviation
            else:
                deviations['slippage_deviation'] = 0.0
                
            # Overall deviation score
            deviations['overall_deviation'] = max(
                deviations['return_deviation'],
                deviations['confidence_deviation'],
                deviations['execution_time_deviation'],
                deviations['slippage_deviation']
            )
            
            return deviations
            
        except Exception as e:
            self.logger.error(f"❌ Error calculating deviations: {e}")
            return {}
            
    def _check_deviation_alerts(self, trade_data: Dict[str, Any], deviations: Dict[str, Any]) -> bool:
        """Check if deviations trigger alerts"""
        try:
            alert_triggered = False
            
            # Check if any deviation exceeds threshold
            significant_deviations = []
            
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
            self.logger.error(f"❌ Error checking deviation alerts: {e}")
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
            self.logger.error(f"❌ Error checking alert cooldown: {e}")
            return True
            
    def _log_deviation_alert(self, trade_data: Dict[str, Any], deviations: List[Dict[str, Any]]):
        """Log deviation alert to file"""
        try:
            alert_data = {
                "timestamp": datetime.now().isoformat(),
                "alert_type": "TRADE_DEVIATION",
                "trade_id": trade_data.get('trade_id'),
                "symbol": trade_data.get('symbol'),
                "deviations": deviations,
                "trade_data": trade_data,
                "consecutive_count": self.consecutive_deviations
            }
            
            # Log to main alert file
            with open(self.alert_log_file, 'a') as f:
                f.write(json.dumps(alert_data) + '\n')
                
            # Log to detailed analysis file
            with open(self.detailed_log_file, 'a') as f:
                f.write(f"[{datetime.now()}] DEVIATION ALERT: {trade_data.get('trade_id')}\n")
                f.write(f"Symbol: {trade_data.get('symbol')}\n")
                for dev in deviations:
                    f.write(f"  {dev['metric']}: {dev['deviation']:.1%} (threshold: {dev['threshold']:.1%})\n")
                f.write("\n")
                
            # Add to recent alerts
            self.recent_alerts.append(alert_data)
            
            # Limit recent alerts list
            if len(self.recent_alerts) > 50:
                self.recent_alerts = self.recent_alerts[-30:]
                
            self.logger.warning(f"DEVIATION ALERT: Trade {trade_data.get('trade_id')} - {len(deviations)} significant deviations")
            
        except Exception as e:
            self.logger.error(f"❌ Error logging deviation alert: {e}")
            
    def _trigger_consecutive_deviation_alert(self, trade_data: Dict[str, Any]):
        """Trigger alert for consecutive deviations"""
        try:
            consecutive_alert = {
                "timestamp": datetime.now().isoformat(),
                "alert_type": "CONSECUTIVE_DEVIATIONS",
                "trade_id": trade_data.get('trade_id'),
                "consecutive_count": self.consecutive_deviations,
                "threshold": self.consecutive_deviations_alert
            }
            
            # Log to alert file
            with open(self.alert_log_file, 'a') as f:
                f.write(json.dumps(consecutive_alert) + '\n')
            self.logger.critical(f"CONSECUTIVE DEVIATION ALERT: {self.consecutive_deviations} trades with significant deviations")
            self.logger.critical("Potential system issue or model degradation detected")
            
        except Exception as e:
            self.logger.error(f"❌ Error triggering consecutive deviation alert: {e}")
            
    def _calculate_baseline_metrics(self):
        """Calculate baseline metrics from historical data"""
        try:
            if len(self.trade_history) < self.min_trades_for_baseline:
                return
                
            # Filter recent trades for baseline
            cutoff_time = datetime.now() - timedelta(hours=self.lookback_hours)
            recent_trades = [
                trade for trade in self.trade_history
                if datetime.fromisoformat(trade['timestamp']) > cutoff_time
            ]
            
            if not recent_trades:
                return
                
            # Calculate metrics
            returns = [trade['actual_return'] for trade in recent_trades]
            confidences = [trade['actual_confidence'] for trade in recent_trades]
            exec_times = [trade['execution_time_ms'] for trade in recent_trades]
            slippages = [trade['slippage'] for trade in recent_trades]
            
            self.baseline_metrics = {
                "avg_return": statistics.mean(returns) if returns else 0.0,
                "std_return": statistics.stdev(returns) if len(returns) > 1 else 0.0,
                "avg_confidence": statistics.mean(confidences) if confidences else 0.0,
                "std_confidence": statistics.stdev(confidences) if len(confidences) > 1 else 0.0,
                "avg_execution_time_ms": statistics.mean(exec_times) if exec_times else 100,
                "std_execution_time_ms": statistics.stdev(exec_times) if len(exec_times) > 1 else 0.0,
                "avg_slippage": statistics.mean(slippages) if slippages else 0.001,
                "std_slippage": statistics.stdev(slippages) if len(slippages) > 1 else 0.0,
                "sample_size": len(recent_trades),
                "last_updated": datetime.now().isoformat()
            }
            
            self.logger.info(f"Baseline metrics updated with {len(recent_trades)} trades")
            
        except Exception as e:
            self.logger.error(f"❌ Error calculating baseline metrics: {e}")
            
    def _update_baseline_metrics(self):
        """Update baseline metrics with new trade data"""
        # Recalculate baseline periodically
        if len(self.trade_history) % 10 == 0:  # Every 10 trades
            self._calculate_baseline_metrics()
            
    def get_deviation_status(self) -> Dict[str, Any]:
        """Get current deviation monitoring status"""
        return {
            "system_active": True,
            "deviation_threshold": self.deviation_threshold,
            "trades_analyzed": len(self.trade_history),
            "consecutive_deviations": self.consecutive_deviations,
            "baseline_metrics": self.baseline_metrics.copy(),
            "recent_alerts_count": len(self.recent_alerts),
            "last_alert": self.recent_alerts[-1] if self.recent_alerts else None
        }
        
    def get_recent_alerts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent deviation alerts"""
        return self.recent_alerts[-limit:] if self.recent_alerts else []
        
    def _save_trade_data(self):
        """Save trade history and metrics to file"""
        try:
            data = {
                "trade_history": self.trade_history,
                "baseline_metrics": self.baseline_metrics,
                "last_updated": datetime.now().isoformat()
            }
            
            with open(self.trade_data_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"❌ Error saving trade data: {e}")


class DeviationAlertCLI:
    """
    Command-line interface for deviation alert system
    """
    
    def __init__(self):
        # Mock config for CLI
        config = {
            "deviation_alert": {
                "threshold": 0.30,
                "min_trades_baseline": 10,
                "lookback_hours": 24,
                "alert_cooldown_minutes": 30,
                "consecutive_deviations": 3
            }
        }
        self.deviation_alert = TradeDeviationAlert(config)
        
    def status(self):
        """Display deviation alert status"""
        status = self.deviation_alert.get_deviation_status()
        
        print("\nTRADE DEVIATION ALERT STATUS")
        print("=" * 50)
        print(f"System Active: {'YES' if status['system_active'] else 'NO'}")
        print(f"Deviation Threshold: {status['deviation_threshold']:.1%}")
        print(f"Trades Analyzed: {status['trades_analyzed']}")
        print(f"Consecutive Deviations: {status['consecutive_deviations']}")
        print(f"Recent Alerts: {status['recent_alerts_count']}")
        
        if status['baseline_metrics']:
            metrics = status['baseline_metrics']
            print(f"\nBaseline Metrics:")
            print(f"  Avg Return: {metrics.get('avg_return', 0):.2%}")
            print(f"  Avg Confidence: {metrics.get('avg_confidence', 0):.2%}")
            print(f"  Avg Execution Time: {metrics.get('avg_execution_time_ms', 0):.0f}ms")
            print(f"  Sample Size: {metrics.get('sample_size', 0)} trades")
            
        print("=" * 50)
        
    def recent_alerts(self, limit: int = 5):
        """Display recent alerts"""
        alerts = self.deviation_alert.get_recent_alerts(limit)
        
        print(f"\nRECENT DEVIATION ALERTS (Last {limit})")
        print("=" * 60)
        
        if not alerts:
            print("No recent alerts")
        else:
            for alert in alerts:
                print(f"[{alert['timestamp']}] {alert['alert_type']}")
                print(f"  Trade ID: {alert.get('trade_id', 'N/A')}")
                if 'deviations' in alert:
                    for dev in alert['deviations']:
                        print(f"    {dev['metric']}: {dev['deviation']:.1%}")
                print()
                
        print("=" * 60)


if __name__ == "__main__":
    import sys
    
    cli = DeviationAlertCLI()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python trade_deviation_alert.py status")
        print("  python trade_deviation_alert.py alerts [limit]")
        sys.exit(1)
        
    command = sys.argv[1]
    
    if command == "status":
        cli.status()
    elif command == "alerts":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        cli.recent_alerts(limit)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
