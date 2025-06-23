#!/usr/bin/env python3
"""
TradeMasterX 2.0 - Phase 14: Observer Agent
Monitors trade inputs/outputs every 30s and logs performance metrics
"""

import asyncio
import json
import csv
import os
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np

class ObserverAgent:
    """Monitors trading activity and logs performance metrics"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger("ObserverAgent")
        
        # File paths
        self.logs_dir = Path("logs")
        self.reports_dir = Path("reports")
        self.observer_log_file = self.logs_dir / "observer_log.csv"
        self.anomaly_log_file = self.reports_dir / "anomaly_log.json"
        
        # Ensure directories exist
        self.logs_dir.mkdir(exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)
        
        # Monitoring state
        self.monitoring = False
        self.trade_buffer = []
        self.anomalies = []
        
        # Performance tracking
        self.last_check_time = datetime.now()
        self.observation_interval = 30  # seconds
          # Initialize CSV headers if file doesn't exist
        self._initialize_observer_log()
        
    def _initialize_observer_log(self):
        """Initialize observer log CSV with headers"""
        if not self.observer_log_file.exists():
            headers = [
                'timestamp', 'symbol', 'signal', 'confidence', 
                'expected_return', 'actual_return', 'success',
                'deviation', 'bot_name', 'strategy'
            ]
            with open(self.observer_log_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                
    async def start_monitoring(self):
        """Start continuous trade monitoring"""
        self.monitoring = True
        self.logger.info("🔍 Observer Agent started - monitoring trades every 30s")
        
        while self.monitoring:
            try:
                await self._observe_trades()
                await asyncio.sleep(self.observation_interval)
            except Exception as e:
                self.logger.error(f"Observer monitoring error: {e}")
                await asyncio.sleep(5)  # Brief pause before retry
                
    def stop_monitoring(self):
        """Stop trade monitoring"""
        self.monitoring = False
        self.logger.info("🛑 Observer Agent monitoring stopped")
        
    async def _observe_trades(self):
        """Observe recent trades and log metrics"""
        try:
            # Check for new trade data
            trade_data = await self._collect_recent_trades()
            
            if not trade_data:
                self.logger.debug("No new trades to observe")
                return
                
            self.logger.info(f"📊 Observing {len(trade_data)} new trades")
            
            for trade in trade_data:
                # Calculate metrics
                metrics = self._calculate_trade_metrics(trade)
                
                # Log to CSV
                self._log_trade_observation(metrics)
                
                # Check for anomalies
                if self._is_anomaly(metrics):
                    self._log_anomaly(metrics)
                    
        except Exception as e:
            self.logger.error(f"Trade observation failed: {e}")
            
    async def _collect_recent_trades(self) -> List[Dict[str, Any]]:
        """Collect recent trade data from various sources"""
        trades = []
        
        try:
            # Check for trade logs
            data_dir = Path("data/performance")
            if data_dir.exists():
                trade_files = list(data_dir.glob("trades_*.csv"))
                if trade_files:
                    recent_file = max(trade_files, key=lambda p: p.stat().st_mtime)
                    df = pd.read_csv(recent_file)
                    
                    # Filter trades since last check
                    if 'timestamp' in df.columns:
                        df['timestamp'] = pd.to_datetime(df['timestamp'])
                        recent_trades = df[df['timestamp'] > self.last_check_time]
                        trades.extend(recent_trades.to_dict('records'))
                        
            # Update last check time
            self.last_check_time = datetime.now()
            
        except Exception as e:
            self.logger.warning(f"Could not collect trade data: {e}")
            
        return trades
        
    def _calculate_trade_metrics(self, trade: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate performance metrics for a trade"""
        metrics = {
            'timestamp': trade.get('timestamp', datetime.now().isoformat()),
            'symbol': trade.get('symbol', 'UNKNOWN'),
            'signal': trade.get('signal', 'unknown'),
            'confidence': float(trade.get('confidence', 0)),
            'expected_return': float(trade.get('expected_return', 0)),
            'actual_return': float(trade.get('actual_return', 0)),
            'bot_name': trade.get('bot_name', 'unknown'),
            'strategy': trade.get('strategy', 'unknown')
        }
        
        # Calculate success/failure
        metrics['success'] = metrics['actual_return'] > 0
        
        # Calculate deviation from expected
        if metrics['expected_return'] != 0:
            metrics['deviation'] = abs(metrics['actual_return'] - metrics['expected_return']) / abs(metrics['expected_return'])
        else:
            metrics['deviation'] = abs(metrics['actual_return'])
            
        return metrics
        
    def _log_trade_observation(self, metrics: Dict[str, Any]):
        """Log trade observation to CSV"""
        try:
            with open(self.observer_log_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    metrics['timestamp'], metrics['symbol'], metrics['signal'],
                    metrics['confidence'], metrics['expected_return'], 
                    metrics['actual_return'], metrics['success'],
                    metrics['deviation'], metrics['bot_name'], metrics['strategy']
                ])
        except Exception as e:
            self.logger.error(f"Failed to log observation: {e}")
            
    def _is_anomaly(self, metrics: Dict[str, Any]) -> bool:
        """Determine if trade is an anomaly"""
        # Loss > 20%
        if metrics['actual_return'] < -0.20:
            return True
            
        # Confidence error > 25%
        if metrics['deviation'] > 0.25:
            return True
            
        # Check against historical statistics
        return self._check_statistical_anomaly(metrics)
        
    def _check_statistical_anomaly(self, metrics: Dict[str, Any]) -> bool:
        """Check if trade is >3 standard deviations from average"""
        try:
            # Load recent observations
            if not self.observer_log_file.exists():
                return False
                
            df = pd.read_csv(self.observer_log_file)
            if len(df) < 10:  # Need sufficient data
                return False
                
            # Calculate statistics for actual returns
            returns = df['actual_return'].astype(float)
            mean_return = returns.mean()
            std_return = returns.std()
            
            if std_return == 0:
                return False
                
            # Check if current return is >3 std deviations
            z_score = abs(metrics['actual_return'] - mean_return) / std_return
            return z_score > 3.0
            
        except Exception as e:
            self.logger.warning(f"Statistical anomaly check failed: {e}")
            return False
            
    def _log_anomaly(self, metrics: Dict[str, Any]):
        """Log anomaly to JSON file"""
        try:
            anomaly_record = {
                'timestamp': datetime.now().isoformat(),
                'trade_metrics': metrics,
                'anomaly_type': self._classify_anomaly(metrics),
                'severity': self._assess_severity(metrics)
            }
            
            # Load existing anomalies
            anomalies = []
            if self.anomaly_log_file.exists():
                with open(self.anomaly_log_file, 'r') as f:
                    anomalies = json.load(f)
                    
            # Add new anomaly
            anomalies.append(anomaly_record)
            
            # Keep only last 1000 anomalies
            if len(anomalies) > 1000:
                anomalies = anomalies[-1000:]
                
            # Save back to file
            with open(self.anomaly_log_file, 'w') as f:
                json.dump(anomalies, f, indent=2)
                
            self.logger.warning(f"🚨 Anomaly detected: {anomaly_record['anomaly_type']} - {metrics['symbol']}")
            
        except Exception as e:
            self.logger.error(f"Failed to log anomaly: {e}")
            
    def _classify_anomaly(self, metrics: Dict[str, Any]) -> str:
        """Classify the type of anomaly"""
        if metrics['actual_return'] < -0.20:
            return "LARGE_LOSS"
        elif metrics['deviation'] > 0.25:
            return "CONFIDENCE_ERROR"
        else:
            return "STATISTICAL_OUTLIER"
            
    def _assess_severity(self, metrics: Dict[str, Any]) -> str:
        """Assess anomaly severity"""
        if metrics['actual_return'] < -0.30:
            return "CRITICAL"
        elif metrics['actual_return'] < -0.20 or metrics['deviation'] > 0.50:
            return "HIGH"
        elif metrics['deviation'] > 0.25:
            return "MEDIUM"
        else:
            return "LOW"
            
    def get_observation_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get summary of observations from last N hours"""
        try:
            if not self.observer_log_file.exists():
                return {"error": "No observation data available"}
                
            df = pd.read_csv(self.observer_log_file)
            
            # Filter to last N hours
            cutoff_time = datetime.now() - timedelta(hours=hours)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            recent_df = df[df['timestamp'] > cutoff_time]
            
            if len(recent_df) == 0:
                return {"message": f"No observations in last {hours} hours"}
                
            summary = {
                'total_trades': len(recent_df),
                'successful_trades': len(recent_df[recent_df['success'] == True]),
                'win_rate': len(recent_df[recent_df['success'] == True]) / len(recent_df),
                'avg_return': recent_df['actual_return'].mean(),
                'avg_confidence': recent_df['confidence'].mean(),
                'avg_deviation': recent_df['deviation'].mean(),
                'unique_symbols': recent_df['symbol'].nunique(),
                'unique_bots': recent_df['bot_name'].nunique(),
                'observation_period_hours': hours
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Failed to generate observation summary: {e}")
            return {"error": str(e)}
            
    def get_anomaly_rate(self, hours: int = 24) -> float:
        """Get anomaly rate for last N hours"""
        try:
            if not self.anomaly_log_file.exists():
                return 0.0
                
            with open(self.anomaly_log_file, 'r') as f:
                anomalies = json.load(f)
                
            # Filter to last N hours
            cutoff_time = datetime.now() - timedelta(hours=hours)
            recent_anomalies = [
                a for a in anomalies 
                if datetime.fromisoformat(a['timestamp']) > cutoff_time
            ]
            
            # Get total trades in same period
            summary = self.get_observation_summary(hours)
            total_trades = summary.get('total_trades', 0)
            
            if total_trades == 0:
                return 0.0
                
            return len(recent_anomalies) / total_trades
            
        except Exception as e:
            self.logger.error(f"Failed to calculate anomaly rate: {e}")
            return 0.0


# Demo functions for testing
async def demo_observer_agent():
    """Demo the observer agent functionality"""
    config = {"demo_mode": True}
    observer = ObserverAgent(config)
    
    print("🔍 TradeMasterX Phase 14: Observer Agent Demo")
    print("=" * 50)
    
    # Create some demo trade data
    demo_trades = [
        {
            'timestamp': datetime.now().isoformat(),
            'symbol': 'BTCUSDT',
            'signal': 'buy',
            'confidence': 0.85,
            'expected_return': 0.02,
            'actual_return': 0.018,
            'bot_name': 'AnalyticsBot',
            'strategy': 'momentum'
        },
        {
            'timestamp': datetime.now().isoformat(),
            'symbol': 'ETHUSDT',
            'signal': 'sell',
            'confidence': 0.75,
            'expected_return': 0.015,
            'actual_return': -0.25,  # Anomaly - large loss
            'bot_name': 'StrategyBot',
            'strategy': 'reversal'
        }
    ]
    
    # Process demo trades
    for trade in demo_trades:
        metrics = observer._calculate_trade_metrics(trade)
        observer._log_trade_observation(metrics)
        
        if observer._is_anomaly(metrics):
            observer._log_anomaly(metrics)
            
    # Generate summary
    summary = observer.get_observation_summary(24)
    print(f"📊 Observation Summary:")
    for key, value in summary.items():
        print(f"   {key}: {value}")
        
    anomaly_rate = observer.get_anomaly_rate(24)
    print(f"🚨 Anomaly Rate: {anomaly_rate:.2%}")
    
    print("\n✅ Observer Agent demo completed")


if __name__ == "__main__":
    asyncio.run(demo_observer_agent())
