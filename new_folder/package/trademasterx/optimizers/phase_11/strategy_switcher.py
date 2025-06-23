"""
TradeMasterX 2.0 - Phase 11: Strategy Switcher
Monitors strategy ROI over last 50 trades and auto-switches underperforming strategies
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


@dataclass
class StrategyMetrics:
    """Strategy performance metrics"""
    strategy_name: str
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_return: float
    average_return: float
    roi_50_trades: float  # ROI over last 50 trades
    sharpe_ratio: float
    max_drawdown: float
    confidence_avg: float
    last_active: str
    status: str  # 'active', 'paused', 'retired'
    performance_grade: str  # 'A', 'B', 'C', 'D', 'F'


@dataclass
class StrategyConfiguration:
    """Strategy configuration profile"""
    strategy_name: str
    config_version: str
    parameters: Dict[str, Any]
    created_at: str
    last_used: str
    performance_score: float
    is_backup: bool


@dataclass
class SwitchingEvent:
    """Strategy switching event record"""
    timestamp: str
    from_strategy: str
    to_strategy: str
    trigger_reason: str
    roi_threshold: float
    actual_roi: float
    trades_analyzed: int


class StrategySwitcher:
    """
    Monitors strategy ROI over last 50 trades and automatically switches 
    underperforming strategies to better alternatives.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize StrategySwitcher"""
        self.config = config or {}
        self.logger = self._setup_logging()
        
        # File paths
        self.data_dir = Path(self.config.get('data_dir', 'reports'))
        self.config_dir = Path(self.config.get('config_dir', 'configs/strategy_profiles'))
        self.data_dir.mkdir(exist_ok=True)
        self.config_dir.mkdir(exist_ok=True, parents=True)
        
        self.metrics_file = self.data_dir / 'strategy_metrics.json'
        self.switch_history_file = self.data_dir / 'strategy_switch_history.json' 
        self.active_config_file = self.data_dir / 'active_strategy_config.json'
        
        # Switching thresholds
        self.thresholds = {
            'min_trades_for_switch': 50,
            'poor_roi_threshold': 0.05,  # 5% ROI minimum
            'excellent_roi_threshold': 0.15,  # 15% ROI excellent
            'min_win_rate': 0.45,
            'max_drawdown_limit': 0.20,
            'switch_cooldown_hours': 6,  # Minimum time between switches
            'backup_strategy_threshold': 0.08  # ROI for backup strategies
        }
        
        # Strategy tracking
        self.strategy_metrics: Dict[str, StrategyMetrics] = {}
        self.strategy_configs: Dict[str, StrategyConfiguration] = {}
        self.trade_history: Dict[str, deque] = {}  # Last 50 trades per strategy
        self.switch_history: List[SwitchingEvent] = []
        self.current_strategy: Optional[str] = None
        self.last_switch_time: Optional[datetime] = None
        
        # Load existing data
        self._load_existing_data()
        self._load_strategy_configurations()
        
        self.logger.info("StrategySwitcher initialized successfully")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for StrategySwitcher"""
        logger = logging.getLogger("StrategySwitcher")
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
        """Load existing strategy performance data"""
        try:
            # Load strategy metrics
            if self.metrics_file.exists():
                with open(self.metrics_file, 'r') as f:
                    metrics_data = json.load(f)
                    for strategy_name, data in metrics_data.items():
                        self.strategy_metrics[strategy_name] = StrategyMetrics(**data)
                self.logger.info(f"Loaded metrics for {len(self.strategy_metrics)} strategies")
            
            # Load switch history
            if self.switch_history_file.exists():
                with open(self.switch_history_file, 'r') as f:
                    switch_data = json.load(f)
                    self.switch_history = [SwitchingEvent(**event) for event in switch_data]
                self.logger.info(f"Loaded {len(self.switch_history)} switch events")
            
            # Load current active strategy
            if self.active_config_file.exists():
                with open(self.active_config_file, 'r') as f:
                    active_data = json.load(f)
                    self.current_strategy = active_data.get('current_strategy')
                    if 'last_switch_time' in active_data:
                        self.last_switch_time = datetime.fromisoformat(active_data['last_switch_time'])
                self.logger.info(f"Current active strategy: {self.current_strategy}")
                
        except Exception as e:
            self.logger.error(f"Error loading existing data: {e}")
    
    def _load_strategy_configurations(self):
        """Load available strategy configurations"""
        try:
            # Look for strategy configuration files
            config_files = list(self.config_dir.glob('*.json'))
            
            for config_file in config_files:
                try:
                    with open(config_file, 'r') as f:
                        config_data = json.load(f)
                        
                    if 'strategy_name' in config_data:
                        strategy_config = StrategyConfiguration(**config_data)
                        self.strategy_configs[strategy_config.strategy_name] = strategy_config
                        
                except Exception as e:
                    self.logger.error(f"Error loading config {config_file}: {e}")
            
            # Create default configurations if none exist
            if not self.strategy_configs:
                self._create_default_configurations()
            
            self.logger.info(f"Loaded {len(self.strategy_configs)} strategy configurations")
            
        except Exception as e:
            self.logger.error(f"Error loading strategy configurations: {e}")
    
    def _create_default_configurations(self):
        """Create default strategy configurations"""
        default_strategies = [
            {
                'strategy_name': 'conservative_trend',
                'parameters': {
                    'risk_tolerance': 'low',
                    'trend_strength_threshold': 0.7,
                    'stop_loss': 0.02,
                    'take_profit': 0.04,
                    'position_size': 0.02
                }
            },
            {
                'strategy_name': 'aggressive_momentum', 
                'parameters': {
                    'risk_tolerance': 'high',
                    'momentum_threshold': 0.6,
                    'stop_loss': 0.03,
                    'take_profit': 0.08,
                    'position_size': 0.05
                }
            },
            {
                'strategy_name': 'balanced_multi_signal',
                'parameters': {
                    'risk_tolerance': 'medium',
                    'signal_weight_technical': 0.4,
                    'signal_weight_fundamental': 0.3,
                    'signal_weight_sentiment': 0.3,
                    'stop_loss': 0.025,
                    'take_profit': 0.06,
                    'position_size': 0.03
                }
            }
        ]
        
        for strategy_def in default_strategies:
            strategy_config = StrategyConfiguration(
                strategy_name=strategy_def['strategy_name'],
                config_version='1.0',
                parameters=strategy_def['parameters'],
                created_at=datetime.now().isoformat(),
                last_used=datetime.now().isoformat(),
                performance_score=0.5,
                is_backup=False
            )
            
            self.strategy_configs[strategy_config.strategy_name] = strategy_config
            
            # Save configuration file
            config_path = self.config_dir / f"{strategy_config.strategy_name}.json"
            with open(config_path, 'w') as f:
                json.dump(asdict(strategy_config), f, indent=2)
        
        self.logger.info("Created default strategy configurations")
    
    def _save_data(self):
        """Save all strategy performance data"""
        try:
            # Save strategy metrics
            metrics_data = {
                strategy_name: asdict(metrics) 
                for strategy_name, metrics in self.strategy_metrics.items()
            }
            with open(self.metrics_file, 'w') as f:
                json.dump(metrics_data, f, indent=2)
            
            # Save switch history
            switch_data = [asdict(event) for event in self.switch_history]
            with open(self.switch_history_file, 'w') as f:
                json.dump(switch_data, f, indent=2)
            
            # Save active configuration
            active_data = {
                'current_strategy': self.current_strategy,
                'last_switch_time': self.last_switch_time.isoformat() if self.last_switch_time else None,
                'updated_at': datetime.now().isoformat()
            }
            with open(self.active_config_file, 'w') as f:
                json.dump(active_data, f, indent=2)
                
            self.logger.debug("Strategy data saved successfully")
            
        except Exception as e:
            self.logger.error(f"Error saving data: {e}")
    
    def record_trade_result(self, strategy_name: str, trade_data: Dict[str, Any]):
        """Record trade result for strategy performance tracking"""
        try:
            # Initialize strategy tracking if needed
            if strategy_name not in self.strategy_metrics:
                self._initialize_strategy_tracking(strategy_name)
            
            metrics = self.strategy_metrics[strategy_name]
            
            # Extract trade data
            trade_return = trade_data.get('return', 0)
            confidence = trade_data.get('confidence', 0.5)
            is_profitable = trade_return > 0
            
            # Update trade counters
            metrics.total_trades += 1
            if is_profitable:
                metrics.winning_trades += 1
            else:
                metrics.losing_trades += 1
            
            # Update win rate
            metrics.win_rate = metrics.winning_trades / metrics.total_trades
            
            # Update returns
            metrics.total_return += trade_return
            metrics.average_return = metrics.total_return / metrics.total_trades
            
            # Update confidence average
            total_confidence = metrics.confidence_avg * (metrics.total_trades - 1)
            metrics.confidence_avg = (total_confidence + confidence) / metrics.total_trades
            
            # Add to trade history (keep last 50)
            if strategy_name not in self.trade_history:
                self.trade_history[strategy_name] = deque(maxlen=50)
            
            trade_record = {
                'timestamp': datetime.now().isoformat(),
                'return': trade_return,
                'confidence': confidence,
                'is_profitable': is_profitable
            }
            self.trade_history[strategy_name].append(trade_record)
            
            # Calculate ROI over last 50 trades
            metrics.roi_50_trades = self._calculate_roi_last_50(strategy_name)
            
            # Update performance grade
            metrics.performance_grade = self._calculate_performance_grade(metrics)
            
            # Update last active time
            metrics.last_active = datetime.now().isoformat()
            
            # Check if strategy switch is needed
            if strategy_name == self.current_strategy:
                self._evaluate_strategy_switch()
            
            self.logger.debug(f"Recorded trade for {strategy_name}: "
                            f"Return={trade_return:.4f}, ROI_50={metrics.roi_50_trades:.4f}")
            
        except Exception as e:
            self.logger.error(f"Error recording trade for {strategy_name}: {e}")
    
    def _initialize_strategy_tracking(self, strategy_name: str):
        """Initialize tracking for a new strategy"""
        self.strategy_metrics[strategy_name] = StrategyMetrics(
            strategy_name=strategy_name,
            total_trades=0,
            winning_trades=0,
            losing_trades=0,
            win_rate=0.0,
            total_return=0.0,
            average_return=0.0,
            roi_50_trades=0.0,
            sharpe_ratio=0.0,
            max_drawdown=0.0,
            confidence_avg=0.5,
            last_active=datetime.now().isoformat(),
            status='active',
            performance_grade='C'
        )
        
        self.trade_history[strategy_name] = deque(maxlen=50)
        
        self.logger.info(f"Initialized tracking for strategy {strategy_name}")
    
    def _calculate_roi_last_50(self, strategy_name: str) -> float:
        """Calculate ROI over last 50 trades"""
        try:
            if strategy_name not in self.trade_history:
                return 0.0
            
            trades = list(self.trade_history[strategy_name])
            if not trades:
                return 0.0
            
            total_return = sum(trade['return'] for trade in trades)
            roi = total_return / len(trades) if trades else 0.0
            
            return roi
            
        except Exception as e:
            self.logger.error(f"Error calculating ROI for {strategy_name}: {e}")
            return 0.0
    
    def _calculate_performance_grade(self, metrics: StrategyMetrics) -> str:
        """Calculate performance grade A-F for strategy"""
        try:
            if metrics.total_trades < 10:
                return 'C'  # Default for new strategies
            
            # Scoring criteria
            roi_score = min(100, (metrics.roi_50_trades / self.thresholds['excellent_roi_threshold']) * 100)
            win_rate_score = (metrics.win_rate - 0.3) / 0.4 * 100  # Scale 30-70% to 0-100
            
            # Combined score
            combined_score = (roi_score * 0.6 + win_rate_score * 0.4)
            
            if combined_score >= 85:
                return 'A'
            elif combined_score >= 70:
                return 'B'
            elif combined_score >= 55:
                return 'C'
            elif combined_score >= 40:
                return 'D'
            else:
                return 'F'
                
        except Exception as e:
            self.logger.error(f"Error calculating grade: {e}")
            return 'C'
    
    def _evaluate_strategy_switch(self):
        """Evaluate if current strategy should be switched"""
        try:
            if not self.current_strategy:
                return
            
            current_metrics = self.strategy_metrics.get(self.current_strategy)
            if not current_metrics:
                return
            
            # Check if we have enough trades to evaluate
            if current_metrics.total_trades < self.thresholds['min_trades_for_switch']:
                return
            
            # Check cooldown period
            if self.last_switch_time:
                hours_since_switch = (datetime.now() - self.last_switch_time).total_seconds() / 3600
                if hours_since_switch < self.thresholds['switch_cooldown_hours']:
                    return
            
            # Determine if switch is needed
            should_switch = False
            switch_reason = ""
            
            # ROI-based switching
            if current_metrics.roi_50_trades < self.thresholds['poor_roi_threshold']:
                should_switch = True
                switch_reason = f"Poor ROI: {current_metrics.roi_50_trades:.4f} < {self.thresholds['poor_roi_threshold']}"
            
            # Win rate-based switching
            elif current_metrics.win_rate < self.thresholds['min_win_rate']:
                should_switch = True
                switch_reason = f"Low win rate: {current_metrics.win_rate:.4f} < {self.thresholds['min_win_rate']}"
            
            # Performance grade-based switching
            elif current_metrics.performance_grade in ['D', 'F']:
                should_switch = True
                switch_reason = f"Poor performance grade: {current_metrics.performance_grade}"
            
            if should_switch:
                best_alternative = self._find_best_alternative_strategy()
                if best_alternative and best_alternative != self.current_strategy:
                    self._execute_strategy_switch(best_alternative, switch_reason, current_metrics)
                else:
                    self.logger.warning(f"Switch needed for {self.current_strategy} but no better alternative found")
            
        except Exception as e:
            self.logger.error(f"Error evaluating strategy switch: {e}")
    
    def _find_best_alternative_strategy(self) -> Optional[str]:
        """Find the best alternative strategy to switch to"""
        try:
            # Get strategies with sufficient performance data
            candidates = []
            
            for strategy_name, metrics in self.strategy_metrics.items():
                if (strategy_name != self.current_strategy and 
                    metrics.total_trades >= 20 and  # Minimum trades for consideration
                    metrics.status == 'active'):
                    
                    candidates.append((strategy_name, metrics))
            
            # If no historical candidates, try backup strategies
            if not candidates:
                for strategy_name, config in self.strategy_configs.items():
                    if (strategy_name != self.current_strategy and 
                        config.is_backup and 
                        config.performance_score >= self.thresholds['backup_strategy_threshold']):
                        
                        # Create minimal metrics for backup strategy
                        if strategy_name not in self.strategy_metrics:
                            self._initialize_strategy_tracking(strategy_name)
                        
                        candidates.append((strategy_name, self.strategy_metrics[strategy_name]))
            
            if not candidates:
                return None
            
            # Sort by ROI over last 50 trades, then by win rate
            candidates.sort(key=lambda x: (x[1].roi_50_trades, x[1].win_rate), reverse=True)
            
            best_strategy = candidates[0][0]
            self.logger.info(f"Best alternative strategy found: {best_strategy}")
            return best_strategy
            
        except Exception as e:
            self.logger.error(f"Error finding alternative strategy: {e}")
            return None
    
    def _execute_strategy_switch(self, new_strategy: str, reason: str, 
                                current_metrics: StrategyMetrics):
        """Execute strategy switch"""
        try:
            old_strategy = self.current_strategy
            
            # Create switch event record
            switch_event = SwitchingEvent(
                timestamp=datetime.now().isoformat(),
                from_strategy=old_strategy,
                to_strategy=new_strategy,
                trigger_reason=reason,
                roi_threshold=self.thresholds['poor_roi_threshold'],
                actual_roi=current_metrics.roi_50_trades,
                trades_analyzed=current_metrics.total_trades
            )
            
            # Update current strategy
            self.current_strategy = new_strategy
            self.last_switch_time = datetime.now()
            
            # Update strategy statuses
            if old_strategy in self.strategy_metrics:
                self.strategy_metrics[old_strategy].status = 'paused'
            
            if new_strategy in self.strategy_metrics:
                self.strategy_metrics[new_strategy].status = 'active'
                self.strategy_metrics[new_strategy].last_active = datetime.now().isoformat()
            
            # Record switch event
            self.switch_history.append(switch_event)
            
            # Update strategy config last used time
            if new_strategy in self.strategy_configs:
                self.strategy_configs[new_strategy].last_used = datetime.now().isoformat()
            
            # Save data
            self._save_data()
            
            self.logger.warning(f"STRATEGY SWITCH EXECUTED: {old_strategy} → {new_strategy}")
            self.logger.warning(f"Switch reason: {reason}")
            self.logger.info(f"New strategy {new_strategy} is now active")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error executing strategy switch: {e}")
            return False
    
    def force_strategy_switch(self, new_strategy: str, reason: str = "Manual override") -> bool:
        """Manually force a strategy switch"""
        try:
            if new_strategy not in self.strategy_configs:
                self.logger.error(f"Strategy {new_strategy} not found in configurations")
                return False
            
            old_strategy = self.current_strategy
            current_metrics = self.strategy_metrics.get(old_strategy) if old_strategy else None
            
            if not current_metrics:
                # Create minimal metrics for the switch record
                current_metrics = StrategyMetrics(
                    strategy_name=old_strategy or "unknown",
                    total_trades=0, winning_trades=0, losing_trades=0,
                    win_rate=0.0, total_return=0.0, average_return=0.0,
                    roi_50_trades=0.0, sharpe_ratio=0.0, max_drawdown=0.0,
                    confidence_avg=0.5, last_active=datetime.now().isoformat(),
                    status='inactive', performance_grade='C'
                )
            
            return self._execute_strategy_switch(new_strategy, reason, current_metrics)
            
        except Exception as e:
            self.logger.error(f"Error in forced strategy switch: {e}")
            return False
    
    def get_strategy_rankings(self) -> List[Tuple[str, StrategyMetrics]]:
        """Get strategies ranked by performance"""
        try:
            # Filter strategies with sufficient data
            qualified_strategies = [
                (name, metrics) for name, metrics in self.strategy_metrics.items()
                if metrics.total_trades >= 10
            ]
            
            # Sort by ROI, then win rate
            qualified_strategies.sort(
                key=lambda x: (x[1].roi_50_trades, x[1].win_rate), 
                reverse=True
            )
            
            return qualified_strategies
            
        except Exception as e:
            self.logger.error(f"Error getting strategy rankings: {e}")
            return []
    
    def generate_switching_report(self) -> Dict[str, Any]:
        """Generate comprehensive strategy switching report"""
        try:
            rankings = self.get_strategy_rankings()
            
            report = {
                'timestamp': datetime.now().isoformat(),
                'current_strategy': self.current_strategy,
                'total_strategies': len(self.strategy_metrics),
                'total_switches': len(self.switch_history),
                'last_switch': self.switch_history[-1].timestamp if self.switch_history else None,
                'strategy_rankings': [
                    {
                        'rank': i + 1,
                        'strategy_name': name,
                        'roi_50_trades': metrics.roi_50_trades,
                        'win_rate': metrics.win_rate,
                        'total_trades': metrics.total_trades,
                        'performance_grade': metrics.performance_grade,
                        'status': metrics.status
                    }
                    for i, (name, metrics) in enumerate(rankings)
                ],
                'recent_switches': [
                    asdict(event) for event in self.switch_history[-5:]
                ],
                'strategy_performance': {
                    name: asdict(metrics) 
                    for name, metrics in self.strategy_metrics.items()
                },
                'switching_statistics': {
                    'avg_time_between_switches': self._calculate_avg_switch_interval(),
                    'most_switched_from': self._get_most_switched_from_strategy(),
                    'most_switched_to': self._get_most_switched_to_strategy(),
                    'switch_success_rate': self._calculate_switch_success_rate()
                },
                'recommendations': self._generate_switching_recommendations()
            }
            
            self.logger.info("Generated comprehensive switching report")
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating switching report: {e}")
            return {}
    
    def _calculate_avg_switch_interval(self) -> float:
        """Calculate average time between switches in hours"""
        try:
            if len(self.switch_history) < 2:
                return 0.0
            
            intervals = []
            for i in range(1, len(self.switch_history)):
                prev_time = datetime.fromisoformat(self.switch_history[i-1].timestamp)
                curr_time = datetime.fromisoformat(self.switch_history[i].timestamp)
                interval_hours = (curr_time - prev_time).total_seconds() / 3600
                intervals.append(interval_hours)
            
            return sum(intervals) / len(intervals)
            
        except Exception as e:
            self.logger.error(f"Error calculating switch interval: {e}")
            return 0.0
    
    def _get_most_switched_from_strategy(self) -> str:
        """Get strategy that was switched away from most often"""
        try:
            from_counts = {}
            for event in self.switch_history:
                from_counts[event.from_strategy] = from_counts.get(event.from_strategy, 0) + 1
            
            if not from_counts:
                return "None"
            
            return max(from_counts, key=from_counts.get)
            
        except Exception as e:
            self.logger.error(f"Error getting most switched from strategy: {e}")
            return "None"
    
    def _get_most_switched_to_strategy(self) -> str:
        """Get strategy that was switched to most often"""
        try:
            to_counts = {}
            for event in self.switch_history:
                to_counts[event.to_strategy] = to_counts.get(event.to_strategy, 0) + 1
            
            if not to_counts:
                return "None"
            
            return max(to_counts, key=to_counts.get)
            
        except Exception as e:
            self.logger.error(f"Error getting most switched to strategy: {e}")
            return "None"
    
    def _calculate_switch_success_rate(self) -> float:
        """Calculate how often switches result in improved performance"""
        try:
            if len(self.switch_history) < 2:
                return 0.0
            
            successful_switches = 0
            
            for i, event in enumerate(self.switch_history[:-1]):  # Exclude last switch
                # Check if performance improved after switch
                to_strategy = event.to_strategy
                
                # Look for trades after this switch
                switch_time = datetime.fromisoformat(event.timestamp)
                
                if to_strategy in self.trade_history:
                    trades_after_switch = [
                        trade for trade in self.trade_history[to_strategy]
                        if datetime.fromisoformat(trade['timestamp']) > switch_time
                    ]
                    
                    if len(trades_after_switch) >= 10:  # Need enough data
                        avg_return_after = sum(t['return'] for t in trades_after_switch[-10:]) / 10
                        if avg_return_after > event.actual_roi:
                            successful_switches += 1
            
            return successful_switches / (len(self.switch_history) - 1) if len(self.switch_history) > 1 else 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating switch success rate: {e}")
            return 0.0
    
    def _generate_switching_recommendations(self) -> List[str]:
        """Generate recommendations for strategy switching optimization"""
        recommendations = []
        
        try:
            # Analyze current strategy performance
            if self.current_strategy and self.current_strategy in self.strategy_metrics:
                current_metrics = self.strategy_metrics[self.current_strategy]
                
                if current_metrics.roi_50_trades < self.thresholds['poor_roi_threshold']:
                    recommendations.append(f"Current strategy ROI ({current_metrics.roi_50_trades:.3f}) below threshold - consider switch")
                
                if current_metrics.performance_grade in ['D', 'F']:
                    recommendations.append(f"Current strategy has poor grade ({current_metrics.performance_grade}) - review parameters")
            
            # Analyze switching patterns
            if len(self.switch_history) > 5:
                switch_success_rate = self._calculate_switch_success_rate()
                if switch_success_rate < 0.5:
                    recommendations.append("Low switch success rate - review switching criteria")
                
                avg_interval = self._calculate_avg_switch_interval()
                if avg_interval < 3:
                    recommendations.append("Frequent switching detected - may need longer evaluation periods")
            
            # Strategy diversity recommendations
            active_strategies = [name for name, metrics in self.strategy_metrics.items() 
                               if metrics.status == 'active']
            if len(active_strategies) < 3:
                recommendations.append("Consider activating more backup strategies for better diversity")
            
            # Performance analysis
            rankings = self.get_strategy_rankings()
            if rankings and len(rankings) > 1:
                top_strategy_roi = rankings[0][1].roi_50_trades
                if top_strategy_roi > self.thresholds['excellent_roi_threshold']:
                    recommendations.append(f"Strategy {rankings[0][0]} shows excellent performance - consider primary allocation")
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")
            return ["Error generating recommendations - manual review needed"]
    
    async def start_continuous_monitoring(self, interval_seconds: int = 300):
        """Start continuous strategy monitoring and switching"""
        self.logger.info("Starting continuous strategy monitoring")
        
        while True:
            try:
                # Evaluate current strategy
                if self.current_strategy:
                    self._evaluate_strategy_switch()
                
                # Save current state
                self._save_data()
                
                # Log status
                if self.current_strategy and self.current_strategy in self.strategy_metrics:
                    metrics = self.strategy_metrics[self.current_strategy]
                    self.logger.info(f"Monitoring: {self.current_strategy} - "
                                   f"ROI: {metrics.roi_50_trades:.4f}, "
                                   f"Grade: {metrics.performance_grade}")
                
                await asyncio.sleep(interval_seconds)
                
            except Exception as e:
                self.logger.error(f"Error in continuous monitoring: {e}")
                await asyncio.sleep(interval_seconds)


# Example usage and testing
if __name__ == "__main__":
    # Initialize switcher
    switcher = StrategySwitcher()
    
    # Set initial strategy
    if not switcher.current_strategy:
        switcher.force_strategy_switch('balanced_multi_signal', 'Initial setup')
    
    # Simulate some trade results
    test_trades = [
        {'return': 0.02, 'confidence': 0.8},
        {'return': -0.01, 'confidence': 0.6},
        {'return': 0.015, 'confidence': 0.75},
        {'return': -0.005, 'confidence': 0.5},
        {'return': 0.03, 'confidence': 0.9}
    ]
    
    for trade in test_trades:
        switcher.record_trade_result('balanced_multi_signal', trade)
    
    # Generate report
    report = switcher.generate_switching_report()
    print(json.dumps(report, indent=2))
