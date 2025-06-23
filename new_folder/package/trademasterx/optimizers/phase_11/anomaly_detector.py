"""
TradeMasterX 2.0 - Phase 11: Anomaly Detector
Identifies outlier trades with >25% deviation and logs anomalies
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
from collections import deque
from scipy import stats
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)


@dataclass
class AnomalyRecord:
    """Individual anomaly record"""
    anomaly_id: str
    timestamp: str
    anomaly_type: str  # 'return_outlier', 'confidence_mismatch', 'volume_spike', 'timing_anomaly'
    severity: str  # 'low', 'medium', 'high', 'critical'
    trade_data: Dict[str, Any]
    expected_value: float
    actual_value: float
    deviation_percentage: float
    z_score: float
    description: str
    bot_id: Optional[str]
    strategy_name: Optional[str]
    resolved: bool
    resolution_notes: Optional[str]


@dataclass
class AnomalyPattern:
    """Detected anomaly pattern"""
    pattern_id: str
    pattern_type: str
    frequency: int
    first_occurrence: str
    last_occurrence: str
    affected_bots: List[str]
    severity_distribution: Dict[str, int]
    description: str
    potential_causes: List[str]
    recommended_actions: List[str]


@dataclass
class AnomalyStatistics:
    """Anomaly detection statistics"""
    total_anomalies: int
    anomalies_by_type: Dict[str, int]
    anomalies_by_severity: Dict[str, int]
    average_deviation: float
    false_positive_rate: float
    detection_accuracy: float
    last_updated: str


class AnomalyDetector:
    """
    Identifies outlier trades and suspicious patterns using statistical analysis.
    Detects anomalies in returns, confidence calibration, trading volumes, and timing.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize AnomalyDetector"""
        self.config = config or {}
        self.logger = self._setup_logging()
        
        # File paths
        self.data_dir = Path(self.config.get('data_dir', 'logs'))
        self.data_dir.mkdir(exist_ok=True)
        
        self.anomalies_file = self.data_dir / 'anomalies.json'
        self.patterns_file = self.data_dir / 'anomaly_patterns.json'
        self.statistics_file = self.data_dir / 'anomaly_statistics.json'
        
        # Detection thresholds
        self.thresholds = {
            'return_deviation_pct': 25.0,  # 25% deviation threshold
            'z_score_threshold': 2.5,      # Statistical outlier threshold
            'confidence_mismatch_threshold': 0.3,  # 30% confidence vs outcome mismatch
            'volume_spike_multiplier': 3.0,  # 3x normal volume
            'timing_anomaly_seconds': 300,   # 5 minutes unusual timing
            'min_samples_for_detection': 20, # Minimum data points for baseline
            'pattern_frequency_threshold': 5  # Min occurrences for pattern detection
        }
        
        # Data storage
        self.anomalies: List[AnomalyRecord] = []
        self.patterns: Dict[str, AnomalyPattern] = {}
        self.statistics: AnomalyStatistics = self._init_statistics()
        
        # Historical data for baseline calculation
        self.trade_history: deque = deque(maxlen=1000)  # Last 1000 trades
        self.return_baseline: Dict[str, float] = {}  # Mean/std for returns
        self.confidence_baseline: Dict[str, float] = {}
        self.volume_baseline: Dict[str, float] = {}
        self.timing_baseline: Dict[str, float] = {}
        
        # Load existing data
        self._load_existing_data()
        
        self.logger.info("AnomalyDetector initialized successfully")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for AnomalyDetector"""
        logger = logging.getLogger("AnomalyDetector")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _init_statistics(self) -> AnomalyStatistics:
        """Initialize anomaly statistics"""
        return AnomalyStatistics(
            total_anomalies=0,
            anomalies_by_type={},
            anomalies_by_severity={},
            average_deviation=0.0,
            false_positive_rate=0.0,
            detection_accuracy=0.0,
            last_updated=datetime.now().isoformat()
        )
    
    def _load_existing_data(self):
        """Load existing anomaly data"""
        try:
            # Load anomalies
            if self.anomalies_file.exists():
                with open(self.anomalies_file, 'r') as f:
                    anomaly_data = json.load(f)
                    self.anomalies = [AnomalyRecord(**record) for record in anomaly_data]
                self.logger.info(f"Loaded {len(self.anomalies)} anomaly records")
            
            # Load patterns
            if self.patterns_file.exists():
                with open(self.patterns_file, 'r') as f:
                    pattern_data = json.load(f)
                    self.patterns = {
                        pattern_id: AnomalyPattern(**data) 
                        for pattern_id, data in pattern_data.items()
                    }
                self.logger.info(f"Loaded {len(self.patterns)} anomaly patterns")
            
            # Load statistics
            if self.statistics_file.exists():
                with open(self.statistics_file, 'r') as f:
                    stats_data = json.load(f)
                    self.statistics = AnomalyStatistics(**stats_data)
                self.logger.info("Loaded anomaly statistics")
                
        except Exception as e:
            self.logger.error(f"Error loading existing data: {e}")
    
    def _save_data(self):
        """Save all anomaly data"""
        try:
            # Save anomalies
            anomaly_data = [asdict(record) for record in self.anomalies]
            with open(self.anomalies_file, 'w') as f:
                json.dump(anomaly_data, f, indent=2)
            
            # Save patterns
            pattern_data = {
                pattern_id: asdict(pattern) 
                for pattern_id, pattern in self.patterns.items()
            }
            with open(self.patterns_file, 'w') as f:
                json.dump(pattern_data, f, indent=2)
            
            # Save statistics
            with open(self.statistics_file, 'w') as f:
                json.dump(asdict(self.statistics), f, indent=2)
                
            self.logger.debug("Anomaly data saved successfully")
            
        except Exception as e:
            self.logger.error(f"Error saving data: {e}")
    
    def analyze_trade(self, trade_data: Dict[str, Any], bot_id: Optional[str] = None, 
                     strategy_name: Optional[str] = None) -> List[AnomalyRecord]:
        """Analyze a trade for anomalies"""
        try:
            anomalies_found = []
            
            # Add trade to history for baseline calculation
            trade_record = {
                'timestamp': trade_data.get('timestamp', datetime.now().isoformat()),
                'return': trade_data.get('return', 0),
                'confidence': trade_data.get('confidence', 0.5),
                'volume': trade_data.get('volume', 0),
                'bot_id': bot_id,
                'strategy_name': strategy_name
            }
            self.trade_history.append(trade_record)
            
            # Update baselines
            self._update_baselines()
            
            # Skip detection if insufficient data
            if len(self.trade_history) < self.thresholds['min_samples_for_detection']:
                return anomalies_found
            
            # Detect different types of anomalies
            anomalies_found.extend(self._detect_return_anomalies(trade_data, bot_id, strategy_name))
            anomalies_found.extend(self._detect_confidence_anomalies(trade_data, bot_id, strategy_name))
            anomalies_found.extend(self._detect_volume_anomalies(trade_data, bot_id, strategy_name))
            anomalies_found.extend(self._detect_timing_anomalies(trade_data, bot_id, strategy_name))
            
            # Record found anomalies
            for anomaly in anomalies_found:
                self._record_anomaly(anomaly)
            
            if anomalies_found:
                self.logger.warning(f"Detected {len(anomalies_found)} anomalies in trade")
                for anomaly in anomalies_found:
                    self.logger.warning(f"  {anomaly.anomaly_type}: {anomaly.description}")
            
            return anomalies_found
            
        except Exception as e:
            self.logger.error(f"Error analyzing trade for anomalies: {e}")
            return []
    
    def _update_baselines(self):
        """Update statistical baselines from historical data"""
        try:
            if len(self.trade_history) < 5:
                return
            
            # Convert to arrays for calculation
            returns = [trade['return'] for trade in self.trade_history]
            confidences = [trade['confidence'] for trade in self.trade_history]
            volumes = [trade['volume'] for trade in self.trade_history if trade['volume'] > 0]
            
            # Calculate return statistics
            if returns:
                self.return_baseline = {
                    'mean': np.mean(returns),
                    'std': np.std(returns),
                    'median': np.median(returns),
                    'q25': np.percentile(returns, 25),
                    'q75': np.percentile(returns, 75)
                }
            
            # Calculate confidence statistics
            if confidences:
                self.confidence_baseline = {
                    'mean': np.mean(confidences),
                    'std': np.std(confidences),
                    'median': np.median(confidences)
                }
            
            # Calculate volume statistics
            if volumes:
                self.volume_baseline = {
                    'mean': np.mean(volumes),
                    'std': np.std(volumes),
                    'median': np.median(volumes)
                }
            
            # Calculate timing intervals
            timestamps = [datetime.fromisoformat(trade['timestamp']) for trade in self.trade_history]
            if len(timestamps) > 1:
                intervals = []
                for i in range(1, len(timestamps)):
                    interval = (timestamps[i] - timestamps[i-1]).total_seconds()
                    intervals.append(interval)
                
                if intervals:
                    self.timing_baseline = {
                        'mean': np.mean(intervals),
                        'std': np.std(intervals),
                        'median': np.median(intervals)
                    }
            
        except Exception as e:
            self.logger.error(f"Error updating baselines: {e}")
    
    def _detect_return_anomalies(self, trade_data: Dict[str, Any], bot_id: Optional[str], 
                                strategy_name: Optional[str]) -> List[AnomalyRecord]:
        """Detect anomalies in trade returns"""
        anomalies = []
        
        try:
            trade_return = trade_data.get('return', 0)
            
            if not self.return_baseline:
                return anomalies
            
            # Calculate z-score
            mean_return = self.return_baseline['mean']
            std_return = self.return_baseline['std']
            
            if std_return > 0:
                z_score = abs(trade_return - mean_return) / std_return
                
                if z_score > self.thresholds['z_score_threshold']:
                    # Calculate deviation percentage
                    if mean_return != 0:
                        deviation_pct = abs(trade_return - mean_return) / abs(mean_return) * 100
                    else:
                        deviation_pct = abs(trade_return) * 100
                    
                    if deviation_pct > self.thresholds['return_deviation_pct']:
                        severity = self._calculate_severity(deviation_pct, z_score)
                        
                        anomaly = AnomalyRecord(
                            anomaly_id=self._generate_anomaly_id(),
                            timestamp=datetime.now().isoformat(),
                            anomaly_type='return_outlier',
                            severity=severity,
                            trade_data=trade_data,
                            expected_value=mean_return,
                            actual_value=trade_return,
                            deviation_percentage=deviation_pct,
                            z_score=z_score,
                            description=f"Return {trade_return:.4f} deviates {deviation_pct:.1f}% from baseline {mean_return:.4f}",
                            bot_id=bot_id,
                            strategy_name=strategy_name,
                            resolved=False,
                            resolution_notes=None
                        )
                        
                        anomalies.append(anomaly)
            
        except Exception as e:
            self.logger.error(f"Error detecting return anomalies: {e}")
        
        return anomalies
    
    def _detect_confidence_anomalies(self, trade_data: Dict[str, Any], bot_id: Optional[str], 
                                   strategy_name: Optional[str]) -> List[AnomalyRecord]:
        """Detect confidence calibration anomalies"""
        anomalies = []
        
        try:
            confidence = trade_data.get('confidence', 0.5)
            trade_return = trade_data.get('return', 0)
            was_profitable = trade_return > 0
            
            # Check confidence vs outcome mismatch
            if confidence > 0.7 and trade_return < -0.02:  # High confidence, big loss
                deviation_pct = abs(confidence - 0.3) / 0.3 * 100  # Expected ~30% for losses
                
                if deviation_pct > self.thresholds['return_deviation_pct']:
                    z_score = 3.0  # High severity for confidence mismatches
                    
                    anomaly = AnomalyRecord(
                        anomaly_id=self._generate_anomaly_id(),
                        timestamp=datetime.now().isoformat(),
                        anomaly_type='confidence_mismatch',
                        severity='high',
                        trade_data=trade_data,
                        expected_value=0.3,  # Expected confidence for losing trades
                        actual_value=confidence,
                        deviation_percentage=deviation_pct,
                        z_score=z_score,
                        description=f"High confidence ({confidence:.3f}) with significant loss ({trade_return:.4f})",
                        bot_id=bot_id,
                        strategy_name=strategy_name,
                        resolved=False,
                        resolution_notes=None
                    )
                    
                    anomalies.append(anomaly)
            
            elif confidence < 0.3 and trade_return > 0.02:  # Low confidence, big win
                deviation_pct = abs(confidence - 0.7) / 0.7 * 100
                
                if deviation_pct > self.thresholds['return_deviation_pct']:
                    z_score = 2.0
                    
                    anomaly = AnomalyRecord(
                        anomaly_id=self._generate_anomaly_id(),
                        timestamp=datetime.now().isoformat(),
                        anomaly_type='confidence_mismatch',
                        severity='medium',
                        trade_data=trade_data,
                        expected_value=0.7,  # Expected confidence for winning trades
                        actual_value=confidence,
                        deviation_percentage=deviation_pct,
                        z_score=z_score,
                        description=f"Low confidence ({confidence:.3f}) with significant gain ({trade_return:.4f})",
                        bot_id=bot_id,
                        strategy_name=strategy_name,
                        resolved=False,
                        resolution_notes=None
                    )
                    
                    anomalies.append(anomaly)
            
        except Exception as e:
            self.logger.error(f"Error detecting confidence anomalies: {e}")
        
        return anomalies
    
    def _detect_volume_anomalies(self, trade_data: Dict[str, Any], bot_id: Optional[str], 
                                strategy_name: Optional[str]) -> List[AnomalyRecord]:
        """Detect trading volume anomalies"""
        anomalies = []
        
        try:
            volume = trade_data.get('volume', 0)
            
            if volume <= 0 or not self.volume_baseline:
                return anomalies
            
            baseline_volume = self.volume_baseline.get('mean', 0)
            
            if baseline_volume > 0:
                volume_ratio = volume / baseline_volume
                
                if volume_ratio > self.thresholds['volume_spike_multiplier']:
                    deviation_pct = (volume_ratio - 1) * 100
                    z_score = (volume - baseline_volume) / self.volume_baseline.get('std', 1)
                    
                    severity = 'high' if volume_ratio > 5 else 'medium'
                    
                    anomaly = AnomalyRecord(
                        anomaly_id=self._generate_anomaly_id(),
                        timestamp=datetime.now().isoformat(),
                        anomaly_type='volume_spike',
                        severity=severity,
                        trade_data=trade_data,
                        expected_value=baseline_volume,
                        actual_value=volume,
                        deviation_percentage=deviation_pct,
                        z_score=z_score,
                        description=f"Volume spike: {volume:.2f} is {volume_ratio:.1f}x baseline {baseline_volume:.2f}",
                        bot_id=bot_id,
                        strategy_name=strategy_name,
                        resolved=False,
                        resolution_notes=None
                    )
                    
                    anomalies.append(anomaly)
            
        except Exception as e:
            self.logger.error(f"Error detecting volume anomalies: {e}")
        
        return anomalies
    
    def _detect_timing_anomalies(self, trade_data: Dict[str, Any], bot_id: Optional[str], 
                               strategy_name: Optional[str]) -> List[AnomalyRecord]:
        """Detect timing anomalies in trade execution"""
        anomalies = []
        
        try:
            if len(self.trade_history) < 2 or not self.timing_baseline:
                return anomalies
            
            current_time = datetime.fromisoformat(trade_data.get('timestamp', datetime.now().isoformat()))
            last_trade_time = datetime.fromisoformat(self.trade_history[-2]['timestamp'])
            
            interval_seconds = (current_time - last_trade_time).total_seconds()
            expected_interval = self.timing_baseline.get('mean', 30)
            
            if abs(interval_seconds - expected_interval) > self.thresholds['timing_anomaly_seconds']:
                deviation_pct = abs(interval_seconds - expected_interval) / expected_interval * 100
                
                if deviation_pct > self.thresholds['return_deviation_pct']:
                    z_score = abs(interval_seconds - expected_interval) / self.timing_baseline.get('std', 1)
                    
                    severity = self._calculate_severity(deviation_pct, z_score)
                    
                    anomaly = AnomalyRecord(
                        anomaly_id=self._generate_anomaly_id(),
                        timestamp=datetime.now().isoformat(),
                        anomaly_type='timing_anomaly',
                        severity=severity,
                        trade_data=trade_data,
                        expected_value=expected_interval,
                        actual_value=interval_seconds,
                        deviation_percentage=deviation_pct,
                        z_score=z_score,
                        description=f"Unusual timing: {interval_seconds:.1f}s vs expected {expected_interval:.1f}s",
                        bot_id=bot_id,
                        strategy_name=strategy_name,
                        resolved=False,
                        resolution_notes=None
                    )
                    
                    anomalies.append(anomaly)
            
        except Exception as e:
            self.logger.error(f"Error detecting timing anomalies: {e}")
        
        return anomalies
    
    def _calculate_severity(self, deviation_pct: float, z_score: float) -> str:
        """Calculate anomaly severity based on deviation and z-score"""
        if deviation_pct > 100 or z_score > 4:
            return 'critical'
        elif deviation_pct > 75 or z_score > 3:
            return 'high'
        elif deviation_pct > 50 or z_score > 2.5:
            return 'medium'
        else:
            return 'low'
    
    def _generate_anomaly_id(self) -> str:
        """Generate unique anomaly ID"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        counter = len(self.anomalies) + 1
        return f"ANOM_{timestamp}_{counter:04d}"
    
    def _record_anomaly(self, anomaly: AnomalyRecord):
        """Record an anomaly and update statistics"""
        try:
            self.anomalies.append(anomaly)
            
            # Update statistics
            self.statistics.total_anomalies += 1
            self.statistics.anomalies_by_type[anomaly.anomaly_type] = \
                self.statistics.anomalies_by_type.get(anomaly.anomaly_type, 0) + 1
            self.statistics.anomalies_by_severity[anomaly.severity] = \
                self.statistics.anomalies_by_severity.get(anomaly.severity, 0) + 1
            
            # Update average deviation
            total_deviation = self.statistics.average_deviation * (self.statistics.total_anomalies - 1)
            self.statistics.average_deviation = (total_deviation + anomaly.deviation_percentage) / self.statistics.total_anomalies
            
            self.statistics.last_updated = datetime.now().isoformat()
            
            # Detect patterns
            self._detect_patterns()
            
            # Keep only recent anomalies (last 1000)
            if len(self.anomalies) > 1000:
                self.anomalies = self.anomalies[-1000:]
            
        except Exception as e:
            self.logger.error(f"Error recording anomaly: {e}")
    
    def _detect_patterns(self):
        """Detect patterns in anomaly occurrences"""
        try:
            # Group anomalies by type and bot
            recent_anomalies = [a for a in self.anomalies if 
                              (datetime.now() - datetime.fromisoformat(a.timestamp)).days <= 7]
            
            # Group by type and affected entities
            type_bot_groups = {}
            for anomaly in recent_anomalies:
                key = f"{anomaly.anomaly_type}_{anomaly.bot_id or 'unknown'}"
                if key not in type_bot_groups:
                    type_bot_groups[key] = []
                type_bot_groups[key].append(anomaly)
            
            # Identify patterns (repeated anomalies)
            for group_key, group_anomalies in type_bot_groups.items():
                if len(group_anomalies) >= self.thresholds['pattern_frequency_threshold']:
                    pattern_id = f"PATTERN_{group_key}_{datetime.now().strftime('%Y%m%d')}"
                    
                    if pattern_id not in self.patterns:
                        # Create new pattern
                        severity_counts = {}
                        for anomaly in group_anomalies:
                            severity_counts[anomaly.severity] = severity_counts.get(anomaly.severity, 0) + 1
                        
                        pattern = AnomalyPattern(
                            pattern_id=pattern_id,
                            pattern_type=group_anomalies[0].anomaly_type,
                            frequency=len(group_anomalies),
                            first_occurrence=min(a.timestamp for a in group_anomalies),
                            last_occurrence=max(a.timestamp for a in group_anomalies),
                            affected_bots=list(set(a.bot_id for a in group_anomalies if a.bot_id)),
                            severity_distribution=severity_counts,
                            description=f"Recurring {group_anomalies[0].anomaly_type} affecting {len(set(a.bot_id for a in group_anomalies if a.bot_id))} bots",
                            potential_causes=self._suggest_pattern_causes(group_anomalies[0].anomaly_type),
                            recommended_actions=self._suggest_pattern_actions(group_anomalies[0].anomaly_type)
                        )
                        
                        self.patterns[pattern_id] = pattern
                        self.logger.warning(f"New anomaly pattern detected: {pattern_id}")
            
        except Exception as e:
            self.logger.error(f"Error detecting patterns: {e}")
    
    def _suggest_pattern_causes(self, anomaly_type: str) -> List[str]:
        """Suggest potential causes for anomaly patterns"""
        causes = {
            'return_outlier': [
                'Market volatility spike',
                'News or event-driven price movement',
                'Strategy parameter misconfiguration',
                'Data feed anomaly',
                'Risk management failure'
            ],
            'confidence_mismatch': [
                'Model miscalibration',
                'Overconfident predictions',
                'Training data quality issues',
                'Feature engineering problems',
                'Market regime change'
            ],
            'volume_spike': [
                'Position sizing error',
                'Capital allocation misconfiguration',
                'Risk limit breach',
                'Manual intervention',
                'System error in order execution'
            ],
            'timing_anomaly': [
                'Network latency issues',
                'System performance degradation',
                'Market hours anomaly',
                'Exchange connectivity problems',
                'Rate limiting activation'
            ]
        }
        
        return causes.get(anomaly_type, ['Unknown pattern cause'])
    
    def _suggest_pattern_actions(self, anomaly_type: str) -> List[str]:
        """Suggest recommended actions for anomaly patterns"""
        actions = {
            'return_outlier': [
                'Review risk management parameters',
                'Validate data quality and sources',
                'Check strategy configuration',
                'Implement additional volatility filters',
                'Consider position size adjustments'
            ],
            'confidence_mismatch': [
                'Recalibrate prediction models',
                'Review training data quality',
                'Implement confidence thresholding',
                'Add model uncertainty quantification',
                'Update feature selection'
            ],
            'volume_spike': [
                'Review position sizing logic',
                'Implement volume limits',
                'Check capital allocation rules',
                'Validate order execution logic',
                'Add volume anomaly detection'
            ],
            'timing_anomaly': [
                'Monitor system performance',
                'Check network connectivity',
                'Review execution timing logic',
                'Implement timing validation',
                'Add latency monitoring'
            ]
        }
        
        return actions.get(anomaly_type, ['Manual investigation required'])
    
    def get_recent_anomalies(self, hours: int = 24) -> List[AnomalyRecord]:
        """Get anomalies from the last N hours"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            recent_anomalies = [
                anomaly for anomaly in self.anomalies
                if datetime.fromisoformat(anomaly.timestamp) > cutoff_time
            ]
            
            return recent_anomalies
            
        except Exception as e:
            self.logger.error(f"Error getting recent anomalies: {e}")
            return []
    
    def get_anomalies_by_severity(self, severity: str) -> List[AnomalyRecord]:
        """Get anomalies by severity level"""
        return [anomaly for anomaly in self.anomalies if anomaly.severity == severity]
    
    def get_anomalies_by_bot(self, bot_id: str) -> List[AnomalyRecord]:
        """Get anomalies for a specific bot"""
        return [anomaly for anomaly in self.anomalies if anomaly.bot_id == bot_id]
    
    def resolve_anomaly(self, anomaly_id: str, resolution_notes: str) -> bool:
        """Mark an anomaly as resolved"""
        try:
            for anomaly in self.anomalies:
                if anomaly.anomaly_id == anomaly_id:
                    anomaly.resolved = True
                    anomaly.resolution_notes = resolution_notes
                    self.logger.info(f"Resolved anomaly {anomaly_id}: {resolution_notes}")
                    return True
            
            self.logger.warning(f"Anomaly {anomaly_id} not found")
            return False
            
        except Exception as e:
            self.logger.error(f"Error resolving anomaly {anomaly_id}: {e}")
            return False
    
    def generate_anomaly_report(self) -> Dict[str, Any]:
        """Generate comprehensive anomaly report"""
        try:
            recent_anomalies = self.get_recent_anomalies(24)
            critical_anomalies = self.get_anomalies_by_severity('critical')
            
            report = {
                'timestamp': datetime.now().isoformat(),
                'summary': {
                    'total_anomalies': self.statistics.total_anomalies,
                    'recent_24h': len(recent_anomalies),
                    'critical_unresolved': len([a for a in critical_anomalies if not a.resolved]),
                    'average_deviation': self.statistics.average_deviation
                },
                'statistics': asdict(self.statistics),
                'recent_anomalies': [asdict(a) for a in recent_anomalies[-20:]],  # Last 20
                'critical_anomalies': [asdict(a) for a in critical_anomalies if not a.resolved],
                'patterns': {pid: asdict(pattern) for pid, pattern in self.patterns.items()},
                'anomaly_distribution': {
                    'by_type': self.statistics.anomalies_by_type,
                    'by_severity': self.statistics.anomalies_by_severity
                },
                'recommendations': self._generate_anomaly_recommendations(recent_anomalies)
            }
            
            self.logger.info("Generated comprehensive anomaly report")
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating anomaly report: {e}")
            return {}
    
    def _generate_anomaly_recommendations(self, recent_anomalies: List[AnomalyRecord]) -> List[str]:
        """Generate recommendations based on recent anomaly patterns"""
        recommendations = []
        
        try:
            if not recent_anomalies:
                recommendations.append("No recent anomalies detected - system operating normally")
                return recommendations
            
            # Analyze anomaly types
            type_counts = {}
            severity_counts = {}
            
            for anomaly in recent_anomalies:
                type_counts[anomaly.anomaly_type] = type_counts.get(anomaly.anomaly_type, 0) + 1
                severity_counts[anomaly.severity] = severity_counts.get(anomaly.severity, 0) + 1
            
            # High-level recommendations
            if severity_counts.get('critical', 0) > 0:
                recommendations.append(f"{severity_counts['critical']} critical anomalies detected - immediate attention required")
            
            if type_counts.get('return_outlier', 0) > 5:
                recommendations.append("Multiple return outliers detected - review risk management and market conditions")
            
            if type_counts.get('confidence_mismatch', 0) > 3:
                recommendations.append("Confidence calibration issues detected - review model performance")
            
            if type_counts.get('volume_spike', 0) > 2:
                recommendations.append("Volume anomalies detected - check position sizing and capital allocation")
            
            if type_counts.get('timing_anomaly', 0) > 3:
                recommendations.append("Timing anomalies detected - investigate system performance and connectivity")
            
            # Pattern-based recommendations
            if len(self.patterns) > 0:
                recommendations.append(f"{len(self.patterns)} anomaly patterns identified - review pattern analysis")
            
            # Bot-specific recommendations
            bot_anomalies = {}
            for anomaly in recent_anomalies:
                if anomaly.bot_id:
                    bot_anomalies[anomaly.bot_id] = bot_anomalies.get(anomaly.bot_id, 0) + 1
            
            problematic_bots = [bot_id for bot_id, count in bot_anomalies.items() if count > 3]
            if problematic_bots:
                recommendations.append(f"High anomaly rates for bots: {', '.join(problematic_bots)} - consider investigation")
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")
            return ["Error generating recommendations - manual review needed"]
    
    async def start_continuous_monitoring(self, interval_seconds: int = 60):
        """Start continuous anomaly monitoring"""
        self.logger.info("Starting continuous anomaly monitoring")
        
        while True:
            try:
                # Update patterns
                self._detect_patterns()
                
                # Save data
                self._save_data()
                
                # Log status
                recent_count = len(self.get_recent_anomalies(1))  # Last hour
                if recent_count > 0:
                    self.logger.info(f"Anomaly monitoring: {recent_count} anomalies in last hour")
                
                await asyncio.sleep(interval_seconds)
                
            except Exception as e:
                self.logger.error(f"Error in continuous monitoring: {e}")
                await asyncio.sleep(interval_seconds)


# Example usage and testing
if __name__ == "__main__":
    # Initialize detector
    detector = AnomalyDetector()
    
    # Simulate some normal trades to establish baseline
    normal_trades = [
        {'return': 0.01, 'confidence': 0.6, 'volume': 1000, 'timestamp': datetime.now().isoformat()},
        {'return': 0.015, 'confidence': 0.7, 'volume': 1100, 'timestamp': (datetime.now() + timedelta(seconds=30)).isoformat()},
        {'return': -0.005, 'confidence': 0.4, 'volume': 950, 'timestamp': (datetime.now() + timedelta(seconds=60)).isoformat()},
        {'return': 0.02, 'confidence': 0.8, 'volume': 1050, 'timestamp': (datetime.now() + timedelta(seconds=90)).isoformat()},
    ]
    
    for trade in normal_trades:
        detector.analyze_trade(trade, 'test_bot', 'test_strategy')
    
    # Simulate anomalous trades
    anomalous_trades = [
        {'return': 0.15, 'confidence': 0.6, 'volume': 1000, 'timestamp': (datetime.now() + timedelta(seconds=120)).isoformat()},  # Return outlier
        {'return': -0.08, 'confidence': 0.9, 'volume': 1000, 'timestamp': (datetime.now() + timedelta(seconds=150)).isoformat()},  # Confidence mismatch
        {'return': 0.01, 'confidence': 0.6, 'volume': 5000, 'timestamp': (datetime.now() + timedelta(seconds=180)).isoformat()},  # Volume spike
    ]
    
    for trade in anomalous_trades:
        anomalies = detector.analyze_trade(trade, 'test_bot', 'test_strategy')
        print(f"Trade anomalies detected: {len(anomalies)}")
    
    # Generate report
    report = detector.generate_anomaly_report()
    print(json.dumps(report, indent=2))
