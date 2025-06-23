#!/usr/bin/env python3
"""
TradeMasterX 2.0 - Phase 11: AdaptiveStrategyReinforcer
Analyzes trade results and reinforces high-performing strategies while penalizing poor performers.
"""

import yaml
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import statistics
import csv

class AdaptiveStrategyReinforcer:
    """
    Adaptive Strategy Reinforcement Engine
    
    Analyzes trade performance and automatically adjusts strategy weights:
    - Rewards strategies with ROI >= 15%
    - Penalizes strategies with drawdown or < 5% ROI
    - Updates adaptive_weights.yaml configuration
    """
    
    def __init__(self, config_path: str = "configs/adaptive_weights.yaml"):
        self.config_path = Path(config_path)
        self.logger = logging.getLogger("AdaptiveStrategyReinforcer")
        self.trade_log_path = Path("data/performance/trade_log.csv")
        
        # Performance thresholds
        self.reward_threshold = 0.15  # 15% ROI for rewards
        self.penalty_threshold = 0.05  # 5% ROI minimum
        self.max_drawdown_threshold = 0.10  # 10% max drawdown
        
        # Reinforcement parameters
        self.reward_multiplier = 1.20  # 20% weight increase for good strategies
        self.penalty_multiplier = 0.80  # 20% weight decrease for poor strategies
        self.min_weight = 0.10  # Minimum strategy weight
        self.max_weight = 2.00  # Maximum strategy weight
        
        # Initialize configuration
        self._initialize_config()
        
        self.logger.info("AdaptiveStrategyReinforcer initialized")
    
    def _initialize_config(self):
        """Initialize adaptive weights configuration file"""
        if not self.config_path.exists():
            # Create default configuration
            default_config = {
                'strategy_weights': {
                    'momentum_strategy': 1.0,
                    'mean_reversion_strategy': 1.0,
                    'breakout_strategy': 1.0,
                    'scalping_strategy': 1.0,
                    'trend_following_strategy': 1.0
                },
                'reinforcement_history': [],
                'last_update': None,
                'performance_metrics': {
                    'total_adjustments': 0,
                    'rewards_given': 0,
                    'penalties_applied': 0
                }
            }
            
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                yaml.dump(default_config, f, default_flow_style=False)
            
            self.logger.info(f"Created default adaptive weights config at {self.config_path}")
    
    def load_current_weights(self) -> Dict[str, Any]:
        """Load current adaptive weights configuration"""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.error(f"Error loading weights config: {e}")
            return {}
    
    def save_weights_config(self, config: Dict[str, Any]):
        """Save updated weights configuration"""
        try:
            config['last_update'] = datetime.now().isoformat()
            with open(self.config_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, indent=2)
            self.logger.info(f"Updated adaptive weights configuration")
        except Exception as e:
            self.logger.error(f"Error saving weights config: {e}")
    
    def analyze_trade_results(self, lookback_trades: int = 100) -> Dict[str, Dict[str, float]]:
        """
        Analyze recent trade results by strategy
        
        Args:
            lookback_trades: Number of recent trades to analyze
            
        Returns:
            Dictionary of strategy performance metrics
        """
        if not self.trade_log_path.exists():
            self.logger.warning("Trade log not found")
            return {}
        
        try:
            # Load recent trades
            with open(self.trade_log_path, 'r') as f:
                reader = csv.DictReader(f)
                trades = list(reader)[-lookback_trades:]  # Get last N trades
            
            if not trades:
                self.logger.warning("No trades found for analysis")
                return {}
            
            # Group trades by strategy (inferred from trade patterns)
            strategy_performance = {}
            
            for trade in trades:
                # Infer strategy from trade characteristics
                strategy = self._infer_strategy_from_trade(trade)
                
                if strategy not in strategy_performance:
                    strategy_performance[strategy] = {
                        'trades': [],
                        'total_roi': 0.0,
                        'win_count': 0,
                        'loss_count': 0,
                        'avg_roi': 0.0,
                        'win_rate': 0.0,
                        'max_drawdown': 0.0
                    }
                
                roi = float(trade.get('expected_return', 0))
                strategy_performance[strategy]['trades'].append(roi)
                strategy_performance[strategy]['total_roi'] += roi
                
                if roi > 0:
                    strategy_performance[strategy]['win_count'] += 1
                else:
                    strategy_performance[strategy]['loss_count'] += 1
            
            # Calculate performance metrics
            for strategy, data in strategy_performance.items():
                total_trades = len(data['trades'])
                if total_trades > 0:
                    data['avg_roi'] = data['total_roi'] / total_trades
                    data['win_rate'] = data['win_count'] / total_trades
                    
                    # Calculate maximum drawdown
                    if data['trades']:
                        cumulative_returns = []
                        running_total = 0
                        for roi in data['trades']:
                            running_total += roi
                            cumulative_returns.append(running_total)
                        
                        peak = cumulative_returns[0]
                        max_drawdown = 0
                        for return_val in cumulative_returns:
                            if return_val > peak:
                                peak = return_val
                            drawdown = (peak - return_val) / peak if peak != 0 else 0
                            max_drawdown = max(max_drawdown, drawdown)
                        
                        data['max_drawdown'] = max_drawdown
            
            self.logger.info(f"Analyzed {len(trades)} trades across {len(strategy_performance)} strategies")
            return strategy_performance
            
        except Exception as e:
            self.logger.error(f"Error analyzing trade results: {e}")
            return {}
    
    def _infer_strategy_from_trade(self, trade: Dict[str, str]) -> str:
        """
        Infer trading strategy from trade characteristics
        
        Args:
            trade: Trade data dictionary
            
        Returns:
            Inferred strategy name
        """
        # Simple strategy inference based on trade characteristics
        confidence = float(trade.get('confidence', 0))
        expected_return = float(trade.get('expected_return', 0))
        position_size = float(trade.get('position_size', 0))
        
        # Strategy classification logic
        if confidence >= 0.90 and expected_return >= 0.20:
            return 'breakout_strategy'
        elif confidence >= 0.80 and position_size <= 300:
            return 'scalping_strategy'
        elif expected_return >= 0.15:
            return 'momentum_strategy'
        elif expected_return < 0.10:
            return 'mean_reversion_strategy'
        else:
            return 'trend_following_strategy'
    
    def calculate_reinforcement_adjustments(self, strategy_performance: Dict[str, Dict[str, float]]) -> Dict[str, float]:
        """
        Calculate weight adjustments based on strategy performance
        
        Args:
            strategy_performance: Strategy performance metrics
            
        Returns:
            Dictionary of weight adjustments for each strategy
        """
        adjustments = {}
        
        for strategy, metrics in strategy_performance.items():
            avg_roi = metrics['avg_roi']
            max_drawdown = metrics['max_drawdown']
            win_rate = metrics['win_rate']
            
            # Determine adjustment type
            adjustment_factor = 1.0
            
            # Reward high-performing strategies
            if avg_roi >= self.reward_threshold and max_drawdown <= self.max_drawdown_threshold:
                adjustment_factor = self.reward_multiplier
                self.logger.info(f"Rewarding {strategy}: ROI={avg_roi:.2%}, Drawdown={max_drawdown:.2%}")
            
            # Penalize poor-performing strategies
            elif avg_roi < self.penalty_threshold or max_drawdown > self.max_drawdown_threshold:
                adjustment_factor = self.penalty_multiplier
                self.logger.info(f"Penalizing {strategy}: ROI={avg_roi:.2%}, Drawdown={max_drawdown:.2%}")
            
            # Additional boost for high win rate
            if win_rate >= 0.70:
                adjustment_factor *= 1.05  # 5% bonus for high win rate
            
            adjustments[strategy] = adjustment_factor
        
        return adjustments
    
    def apply_reinforcement_adjustments(self, adjustments: Dict[str, float]) -> bool:
        """
        Apply calculated adjustments to strategy weights
        
        Args:
            adjustments: Weight adjustment factors for each strategy
            
        Returns:
            True if adjustments were applied successfully
        """
        try:
            config = self.load_current_weights()
            if not config:
                return False
            
            strategy_weights = config.get('strategy_weights', {})
            history_entry = {
                'timestamp': datetime.now().isoformat(),
                'adjustments': {},
                'reason': 'performance_reinforcement'
            }
            
            rewards_given = 0
            penalties_applied = 0
            
            for strategy, adjustment_factor in adjustments.items():
                if strategy in strategy_weights:
                    old_weight = strategy_weights[strategy]
                    new_weight = old_weight * adjustment_factor
                    
                    # Clamp weights to valid range
                    new_weight = max(self.min_weight, min(self.max_weight, new_weight))
                    
                    strategy_weights[strategy] = new_weight
                    history_entry['adjustments'][strategy] = {
                        'old_weight': old_weight,
                        'new_weight': new_weight,
                        'adjustment_factor': adjustment_factor
                    }
                    
                    if adjustment_factor > 1.0:
                        rewards_given += 1
                    elif adjustment_factor < 1.0:
                        penalties_applied += 1
                    
                    self.logger.info(f"Adjusted {strategy}: {old_weight:.3f} -> {new_weight:.3f} (factor: {adjustment_factor:.3f})")
            
            # Update configuration
            config['strategy_weights'] = strategy_weights
            config['reinforcement_history'].append(history_entry)
            config['performance_metrics']['total_adjustments'] += len(adjustments)
            config['performance_metrics']['rewards_given'] += rewards_given
            config['performance_metrics']['penalties_applied'] += penalties_applied
            
            # Keep only last 100 history entries
            if len(config['reinforcement_history']) > 100:
                config['reinforcement_history'] = config['reinforcement_history'][-100:]
            
            self.save_weights_config(config)
            return True
            
        except Exception as e:
            self.logger.error(f"Error applying reinforcement adjustments: {e}")
            return False
    
    def run_reinforcement_cycle(self, lookback_trades: int = 100) -> Dict[str, Any]:
        """
        Execute complete reinforcement cycle
        
        Args:
            lookback_trades: Number of recent trades to analyze
            
        Returns:
            Reinforcement cycle results
        """
        self.logger.info(f"Starting reinforcement cycle with {lookback_trades} trades lookback")
        
        # Analyze recent performance
        strategy_performance = self.analyze_trade_results(lookback_trades)
        
        if not strategy_performance:
            self.logger.warning("No strategy performance data available")
            return {'success': False, 'reason': 'no_data'}
        
        # Calculate adjustments
        adjustments = self.calculate_reinforcement_adjustments(strategy_performance)
        
        if not adjustments:
            self.logger.info("No adjustments needed")
            return {'success': True, 'adjustments': 0}
        
        # Apply adjustments
        success = self.apply_reinforcement_adjustments(adjustments)
        
        result = {
            'success': success,
            'timestamp': datetime.now().isoformat(),
            'strategies_analyzed': len(strategy_performance),
            'adjustments_made': len(adjustments),
            'performance_summary': {
                strategy: {
                    'avg_roi': metrics['avg_roi'],
                    'win_rate': metrics['win_rate'],
                    'max_drawdown': metrics['max_drawdown']
                }
                for strategy, metrics in strategy_performance.items()
            },
            'weight_adjustments': adjustments
        }
        
        self.logger.info(f"Reinforcement cycle completed: {len(adjustments)} adjustments made")
        return result
    
    def get_current_strategy_weights(self) -> Dict[str, float]:
        """Get current strategy weights"""
        config = self.load_current_weights()
        return config.get('strategy_weights', {})
    
    def get_reinforcement_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent reinforcement history"""
        config = self.load_current_weights()
        history = config.get('reinforcement_history', [])
        return history[-limit:] if history else []
