#!/usr/bin/env python3
"""
TradeMasterX 2.0 - Phase 14: Anomaly Auditor
Detects and analyzes trading anomalies for system optimization
"""

import json
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from scipy import stats

class AnomalyAuditor:
    """Advanced anomaly detection and audit system"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger("AnomalyAuditor")
        
        # Anomaly thresholds
        self.loss_threshold = -0.20  # 20% loss
        self.confidence_error_threshold = 0.25  # 25% confidence error
        self.statistical_threshold = 3.0  # 3 standard deviations
        
        # File paths
        self.reports_dir = Path("reports")
        self.audit_log_file = self.reports_dir / "audit_log.json"
        self.anomaly_patterns_file = self.reports_dir / "anomaly_patterns.json"
        
        # Ensure directories exist
        self.reports_dir.mkdir(exist_ok=True)
        
        # Anomaly tracking
        self.detected_anomalies = []
        self.anomaly_patterns = {}
        
        # Load existing data
        self._load_anomaly_patterns()
        
    def _load_anomaly_patterns(self):
        """Load previously identified anomaly patterns"""
        try:
            if self.anomaly_patterns_file.exists():
                with open(self.anomaly_patterns_file, 'r') as f:
                    self.anomaly_patterns = json.load(f)
                self.logger.info(f"📋 Loaded {len(self.anomaly_patterns)} anomaly patterns")
            else:
                self.anomaly_patterns = {}
                
        except Exception as e:
            self.logger.error(f"Failed to load anomaly patterns: {e}")
            self.anomaly_patterns = {}
            
    def _save_anomaly_patterns(self):
        """Save anomaly patterns to file"""
        try:
            with open(self.anomaly_patterns_file, 'w') as f:
                json.dump(self.anomaly_patterns, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save anomaly patterns: {e}")
            
    def audit_trade(self, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive audit of a single trade"""
        audit_result = {
            'trade_id': trade_data.get('trade_id', f"trade_{datetime.now().timestamp()}"),
            'timestamp': datetime.now().isoformat(),
            'trade_data': trade_data,
            'anomalies_detected': [],
            'severity': 'NORMAL',
            'audit_score': 0.0,
            'recommendations': []
        }
        
        try:
            # Extract key metrics
            actual_return = float(trade_data.get('actual_return', 0))
            expected_return = float(trade_data.get('expected_return', 0))
            confidence = float(trade_data.get('confidence', 0))
            symbol = trade_data.get('symbol', 'UNKNOWN')
            strategy = trade_data.get('strategy', 'unknown')
            bot_name = trade_data.get('bot_name', 'unknown')
            
            # 1. Large Loss Detection
            if actual_return <= self.loss_threshold:
                anomaly = {
                    'type': 'LARGE_LOSS',
                    'severity': 'HIGH' if actual_return <= -0.30 else 'MEDIUM',
                    'description': f"Large loss detected: {actual_return:.2%}",
                    'value': actual_return,
                    'threshold': self.loss_threshold
                }
                audit_result['anomalies_detected'].append(anomaly)
                
            # 2. Confidence Error Detection
            if expected_return != 0:
                confidence_error = abs(actual_return - expected_return) / abs(expected_return)
                if confidence_error >= self.confidence_error_threshold:
                    anomaly = {
                        'type': 'CONFIDENCE_ERROR',
                        'severity': 'HIGH' if confidence_error >= 0.50 else 'MEDIUM',
                        'description': f"High confidence error: {confidence_error:.2%}",
                        'value': confidence_error,
                        'threshold': self.confidence_error_threshold,
                        'expected': expected_return,
                        'actual': actual_return
                    }
                    audit_result['anomalies_detected'].append(anomaly)
                    
            # 3. Statistical Outlier Detection
            statistical_anomaly = self._detect_statistical_anomaly(trade_data)
            if statistical_anomaly:
                audit_result['anomalies_detected'].append(statistical_anomaly)
                
            # 4. Pattern-based Anomaly Detection
            pattern_anomaly = self._detect_pattern_anomaly(trade_data)
            if pattern_anomaly:
                audit_result['anomalies_detected'].append(pattern_anomaly)
                
            # 5. Contextual Anomaly Detection
            contextual_anomalies = self._detect_contextual_anomalies(trade_data)
            audit_result['anomalies_detected'].extend(contextual_anomalies)
            
            # Calculate overall severity and audit score
            audit_result['severity'] = self._calculate_overall_severity(audit_result['anomalies_detected'])
            audit_result['audit_score'] = self._calculate_audit_score(audit_result['anomalies_detected'])
            
            # Generate recommendations
            audit_result['recommendations'] = self._generate_recommendations(audit_result['anomalies_detected'], trade_data)
            
            # Log significant anomalies
            if audit_result['anomalies_detected']:
                self._log_audit_result(audit_result)
                self.logger.warning(f"🚨 Anomalies detected in trade {audit_result['trade_id']}: {len(audit_result['anomalies_detected'])} issues")
                
        except Exception as e:
            self.logger.error(f"Trade audit failed: {e}")
            audit_result['error'] = str(e)
            
        return audit_result
        
    def _detect_statistical_anomaly(self, trade_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Detect statistical outliers using Z-score analysis"""
        try:
            # Load historical data for comparison
            historical_data = self._get_historical_data()
            if len(historical_data) < 30:  # Need sufficient data
                return None
                
            actual_return = float(trade_data.get('actual_return', 0))
            
            # Calculate Z-score
            mean_return = np.mean(historical_data)
            std_return = np.std(historical_data)
            
            if std_return == 0:
                return None
                
            z_score = abs(actual_return - mean_return) / std_return
            
            if z_score >= self.statistical_threshold:
                return {
                    'type': 'STATISTICAL_OUTLIER',
                    'severity': 'HIGH' if z_score >= 4.0 else 'MEDIUM',
                    'description': f"Statistical outlier detected: {z_score:.2f} standard deviations",
                    'value': z_score,
                    'threshold': self.statistical_threshold,
                    'mean': mean_return,
                    'std': std_return
                }
                
        except Exception as e:
            self.logger.error(f"Statistical anomaly detection failed: {e}")
            
        return None
        
    def _detect_pattern_anomaly(self, trade_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Detect anomalies based on learned patterns"""
        try:
            symbol = trade_data.get('symbol', 'UNKNOWN')
            strategy = trade_data.get('strategy', 'unknown')
            actual_return = float(trade_data.get('actual_return', 0))
            
            # Check against known patterns
            pattern_key = f"{symbol}_{strategy}"
            if pattern_key in self.anomaly_patterns:
                pattern = self.anomaly_patterns[pattern_key]
                
                # Check if current trade fits known bad patterns
                if (actual_return <= pattern.get('worst_return', 0) * 0.8 or
                    actual_return >= pattern.get('best_return', 0) * 1.2):
                    
                    return {
                        'type': 'PATTERN_ANOMALY',
                        'severity': 'MEDIUM',
                        'description': f"Trade deviates from learned pattern for {pattern_key}",
                        'pattern_reference': pattern_key,
                        'historical_range': [pattern.get('worst_return', 0), pattern.get('best_return', 0)]
                    }
                    
        except Exception as e:
            self.logger.error(f"Pattern anomaly detection failed: {e}")
            
        return None
        
    def _detect_contextual_anomalies(self, trade_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect contextual anomalies based on trading conditions"""
        anomalies = []
        
        try:
            confidence = float(trade_data.get('confidence', 0))
            actual_return = float(trade_data.get('actual_return', 0))
            
            # High confidence but poor performance
            if confidence >= 0.8 and actual_return <= -0.05:
                anomalies.append({
                    'type': 'HIGH_CONFIDENCE_LOSS',
                    'severity': 'MEDIUM',
                    'description': f"High confidence ({confidence:.2%}) but negative return ({actual_return:.2%})",
                    'confidence': confidence,
                    'return': actual_return
                })
                
            # Low confidence but good performance (might indicate model underconfidence)
            if confidence <= 0.5 and actual_return >= 0.02:
                anomalies.append({
                    'type': 'LOW_CONFIDENCE_WIN',
                    'severity': 'LOW',
                    'description': f"Low confidence ({confidence:.2%}) but positive return ({actual_return:.2%})",
                    'confidence': confidence,
                    'return': actual_return
                })
                
            # Extreme confidence values
            if confidence >= 0.95 or confidence <= 0.05:
                anomalies.append({
                    'type': 'EXTREME_CONFIDENCE',
                    'severity': 'LOW',
                    'description': f"Extreme confidence value: {confidence:.2%}",
                    'confidence': confidence
                })
                
        except Exception as e:
            self.logger.error(f"Contextual anomaly detection failed: {e}")
            
        return anomalies
        
    def _get_historical_data(self) -> List[float]:
        """Get historical return data for statistical analysis"""
        try:
            # Try to load from observer log
            observer_log_file = Path("logs/observer_log.csv")
            if observer_log_file.exists():
                df = pd.read_csv(observer_log_file)
                if 'actual_return' in df.columns:
                    return df['actual_return'].astype(float).tolist()
                    
            # Fallback to trade files
            data_dir = Path("data/performance")
            if data_dir.exists():
                trade_files = list(data_dir.glob("trades_*.csv"))
                if trade_files:
                    recent_file = max(trade_files, key=lambda p: p.stat().st_mtime)
                    df = pd.read_csv(recent_file)
                    if 'actual_return' in df.columns:
                        return df['actual_return'].astype(float).tolist()
                        
        except Exception as e:
            self.logger.error(f"Failed to get historical data: {e}")
            
        return []
        
    def _calculate_overall_severity(self, anomalies: List[Dict[str, Any]]) -> str:
        """Calculate overall severity from detected anomalies"""
        if not anomalies:
            return 'NORMAL'
            
        severity_scores = {
            'LOW': 1,
            'MEDIUM': 2,
            'HIGH': 3,
            'CRITICAL': 4
        }
        
        max_score = max(severity_scores.get(a.get('severity', 'LOW'), 1) for a in anomalies)
        total_score = sum(severity_scores.get(a.get('severity', 'LOW'), 1) for a in anomalies)
        
        if max_score >= 4 or total_score >= 8:
            return 'CRITICAL'
        elif max_score >= 3 or total_score >= 5:
            return 'HIGH'
        elif max_score >= 2 or total_score >= 3:
            return 'MEDIUM'
        else:
            return 'LOW'
            
    def _calculate_audit_score(self, anomalies: List[Dict[str, Any]]) -> float:
        """Calculate numerical audit score (0-100, lower is better)"""
        if not anomalies:
            return 0.0
            
        severity_weights = {
            'LOW': 10,
            'MEDIUM': 25,
            'HIGH': 50,
            'CRITICAL': 100
        }
        
        total_score = sum(severity_weights.get(a.get('severity', 'LOW'), 10) for a in anomalies)
        return min(100.0, total_score)
        
    def _generate_recommendations(self, anomalies: List[Dict[str, Any]], trade_data: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations based on detected anomalies"""
        recommendations = []
        
        anomaly_types = [a.get('type') for a in anomalies]
        
        if 'LARGE_LOSS' in anomaly_types:
            recommendations.append("Review position sizing and risk management parameters")
            recommendations.append("Analyze market conditions during trade execution")
            
        if 'CONFIDENCE_ERROR' in anomaly_types:
            recommendations.append("Recalibrate model confidence calculations")
            recommendations.append("Consider retraining with recent market data")
            
        if 'STATISTICAL_OUTLIER' in anomaly_types:
            recommendations.append("Investigate unusual market conditions")
            recommendations.append("Review data quality and preprocessing")
            
        if 'HIGH_CONFIDENCE_LOSS' in anomaly_types:
            recommendations.append("Examine model overconfidence issues")
            recommendations.append("Implement confidence threshold adjustments")
            
        if 'PATTERN_ANOMALY' in anomaly_types:
            recommendations.append("Update strategy parameters for current market regime")
            recommendations.append("Consider adaptive strategy allocation")
            
        # Strategy-specific recommendations
        strategy = trade_data.get('strategy', 'unknown')
        if strategy == 'momentum' and 'LARGE_LOSS' in anomaly_types:
            recommendations.append("Review momentum indicators for false signals")
        elif strategy == 'reversal' and 'CONFIDENCE_ERROR' in anomaly_types:
            recommendations.append("Validate reversal detection algorithms")
            
        return list(set(recommendations))  # Remove duplicates
        
    def _log_audit_result(self, audit_result: Dict[str, Any]):
        """Log audit result to persistent storage"""
        try:
            # Load existing audit log
            audit_log = []
            if self.audit_log_file.exists():
                with open(self.audit_log_file, 'r') as f:
                    audit_log = json.load(f)
                    
            # Add new result
            audit_log.append(audit_result)
            
            # Keep only last 10,000 entries
            if len(audit_log) > 10000:
                audit_log = audit_log[-10000:]
                
            # Save back to file
            with open(self.audit_log_file, 'w') as f:
                json.dump(audit_log, f, indent=2)
                
            # Update patterns
            self._update_anomaly_patterns(audit_result['trade_data'])
            
        except Exception as e:
            self.logger.error(f"Failed to log audit result: {e}")
            
    def _update_anomaly_patterns(self, trade_data: Dict[str, Any]):
        """Update learned anomaly patterns"""
        try:
            symbol = trade_data.get('symbol', 'UNKNOWN')
            strategy = trade_data.get('strategy', 'unknown')
            actual_return = float(trade_data.get('actual_return', 0))
            
            pattern_key = f"{symbol}_{strategy}"
            
            if pattern_key not in self.anomaly_patterns:
                self.anomaly_patterns[pattern_key] = {
                    'count': 0,
                    'best_return': actual_return,
                    'worst_return': actual_return,
                    'avg_return': actual_return,
                    'last_updated': datetime.now().isoformat()
                }
            else:
                pattern = self.anomaly_patterns[pattern_key]
                pattern['count'] += 1
                pattern['best_return'] = max(pattern['best_return'], actual_return)
                pattern['worst_return'] = min(pattern['worst_return'], actual_return)
                pattern['avg_return'] = (pattern['avg_return'] * (pattern['count'] - 1) + actual_return) / pattern['count']
                pattern['last_updated'] = datetime.now().isoformat()
                
            self._save_anomaly_patterns()
            
        except Exception as e:
            self.logger.error(f"Failed to update anomaly patterns: {e}")
            
    def get_audit_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get audit summary for specified time period"""
        try:
            if not self.audit_log_file.exists():
                return {"error": "No audit data available"}
                
            with open(self.audit_log_file, 'r') as f:
                audit_log = json.load(f)
                
            # Filter to specified time period
            cutoff_time = datetime.now() - timedelta(hours=hours)
            recent_audits = [
                audit for audit in audit_log
                if datetime.fromisoformat(audit['timestamp']) > cutoff_time
            ]
            
            if not recent_audits:
                return {"message": f"No audits in last {hours} hours"}
                
            # Calculate summary statistics
            total_audits = len(recent_audits)
            anomaly_count = sum(len(audit['anomalies_detected']) for audit in recent_audits)
            
            severity_counts = {
                'NORMAL': 0, 'LOW': 0, 'MEDIUM': 0, 'HIGH': 0, 'CRITICAL': 0
            }
            
            anomaly_type_counts = {}
            
            for audit in recent_audits:
                severity_counts[audit['severity']] += 1
                
                for anomaly in audit['anomalies_detected']:
                    anomaly_type = anomaly.get('type', 'UNKNOWN')
                    anomaly_type_counts[anomaly_type] = anomaly_type_counts.get(anomaly_type, 0) + 1
                    
            summary = {
                'period_hours': hours,
                'total_audits': total_audits,
                'total_anomalies': anomaly_count,
                'anomaly_rate': anomaly_count / total_audits if total_audits > 0 else 0,
                'severity_distribution': severity_counts,
                'anomaly_types': anomaly_type_counts,
                'avg_audit_score': sum(audit['audit_score'] for audit in recent_audits) / total_audits,
                'critical_issues': len([a for a in recent_audits if a['severity'] == 'CRITICAL'])
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Failed to generate audit summary: {e}")
            return {"error": str(e)}
            
    def generate_anomaly_report(self) -> Dict[str, Any]:
        """Generate comprehensive anomaly analysis report"""
        summary_24h = self.get_audit_summary(24)
        summary_7d = self.get_audit_summary(168)  # 7 days
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary_24h': summary_24h,
            'summary_7d': summary_7d,
            'patterns': self.anomaly_patterns,
            'system_health': self._assess_anomaly_system_health(summary_24h)
        }
        
        return report
        
    def _assess_anomaly_system_health(self, summary: Dict[str, Any]) -> Dict[str, Any]:
        """Assess system health based on anomaly patterns"""
        health = {
            'status': 'HEALTHY',
            'concerns': [],
            'recommendations': []
        }
        
        if isinstance(summary, dict) and 'anomaly_rate' in summary:
            anomaly_rate = summary['anomaly_rate']
            
            if anomaly_rate > 0.2:  # 20% anomaly rate
                health['status'] = 'CRITICAL'
                health['concerns'].append(f"Very high anomaly rate: {anomaly_rate:.2%}")
            elif anomaly_rate > 0.1:  # 10% anomaly rate
                health['status'] = 'DEGRADED'
                health['concerns'].append(f"High anomaly rate: {anomaly_rate:.2%}")
                
            critical_issues = summary.get('critical_issues', 0)
            if critical_issues > 0:
                health['status'] = 'CRITICAL'
                health['concerns'].append(f"{critical_issues} critical issues detected")
                
            if health['status'] != 'HEALTHY':
                health['recommendations'].append("Consider triggering model retraining")
                health['recommendations'].append("Review recent market conditions")
                health['recommendations'].append("Analyze top anomaly patterns")
                
        return health


# Demo function
def demo_anomaly_auditor():
    """Demo the anomaly auditor functionality"""
    config = {"demo_mode": True}
    auditor = AnomalyAuditor(config)
    
    print("🚨 TradeMasterX Phase 14: Anomaly Auditor Demo")
    print("=" * 50)
    
    # Simulate various trade scenarios
    demo_trades = [
        {
            'symbol': 'BTCUSDT',
            'strategy': 'momentum',
            'bot_name': 'AnalyticsBot',
            'actual_return': 0.02,
            'expected_return': 0.018,
            'confidence': 0.8
        },
        {
            'symbol': 'ETHUSDT',
            'strategy': 'reversal',
            'bot_name': 'StrategyBot',
            'actual_return': -0.25,  # Large loss anomaly
            'expected_return': 0.01,
            'confidence': 0.9  # High confidence error
        },
        {
            'symbol': 'ADAUSDT',
            'strategy': 'momentum',
            'bot_name': 'AnalyticsBot',
            'actual_return': 0.05,
            'expected_return': 0.02,
            'confidence': 0.3  # Low confidence win
        }
    ]
    
    # Audit each trade
    for i, trade in enumerate(demo_trades, 1):
        print(f"\n🔍 Auditing Trade {i}: {trade['symbol']} - {trade['strategy']}")
        audit_result = auditor.audit_trade(trade)
        
        print(f"   Severity: {audit_result['severity']}")
        print(f"   Audit Score: {audit_result['audit_score']:.1f}")
        print(f"   Anomalies: {len(audit_result['anomalies_detected'])}")
        
        for anomaly in audit_result['anomalies_detected']:
            print(f"     - {anomaly['type']}: {anomaly['description']}")
            
        if audit_result['recommendations']:
            print(f"   Recommendations:")
            for rec in audit_result['recommendations'][:2]:  # Show first 2
                print(f"     • {rec}")
                
    # Generate summary
    summary = auditor.get_audit_summary(24)
    print(f"\n📊 Audit Summary (24h):")
    if 'error' not in summary:
        print(f"   Total Audits: {summary['total_audits']}")
        print(f"   Anomaly Rate: {summary['anomaly_rate']:.2%}")
        print(f"   Critical Issues: {summary['critical_issues']}")
        
    # Generate full report
    report = auditor.generate_anomaly_report()
    health = report['system_health']
    print(f"\n🏥 System Health: {health['status']}")
    if health['concerns']:
        print(f"   Concerns: {', '.join(health['concerns'])}")
        
    print("\n✅ Anomaly Auditor demo completed")


if __name__ == "__main__":
    demo_anomaly_auditor()
