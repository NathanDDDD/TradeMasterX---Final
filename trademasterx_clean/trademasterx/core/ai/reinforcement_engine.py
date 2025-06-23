#!/usr/bin/env python3
"""
TradeMasterX 2.0 - Phase 14: Reinforcement Engine
Tracks performance per strategy/bot and adjusts weights dynamically
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np

class ReinforcementEngine:
    """Dynamic strategy and bot weight optimization engine"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger("ReinforcementEngine")
        
        # File paths
        self.weights_file = Path("strategy_weights.json")
        self.performance_history_file = Path("data/strategy_performance_history.json")
        
        # Strategy/bot weights (initialized with equal weights)
        self.strategy_weights = {}
        self.bot_weights = {}
        
        # Performance tracking
        self.performance_history = {}
        
        # Reinforcement parameters
        self.learning_rate = 0.1
        self.decay_factor = 0.95
        self.min_weight = 0.1
        self.max_weight = 2.0
        self.performance_window = 100  # Number of trades to consider
        
        # Load existing weights and history
        self._load_weights()
        self._load_performance_history()
        
    def _load_weights(self):
        """Load strategy and bot weights from file"""
        try:
            if self.weights_file.exists():
                with open(self.weights_file, 'r') as f:
                    data = json.load(f)
                    self.strategy_weights = data.get('strategies', {})
                    self.bot_weights = data.get('bots', {})
                    
                self.logger.info(f"📊 Loaded weights for {len(self.strategy_weights)} strategies, {len(self.bot_weights)} bots")
            else:
                self.logger.info("🆕 No existing weights found, starting fresh")
                
        except Exception as e:
            self.logger.error(f"Failed to load weights: {e}")
            
    def _save_weights(self):
        """Save strategy and bot weights to file"""
        try:
            weights_data = {
                'timestamp': datetime.now().isoformat(),
                'strategies': self.strategy_weights,
                'bots': self.bot_weights,
                'metadata': {
                    'learning_rate': self.learning_rate,
                    'decay_factor': self.decay_factor,
                    'performance_window': self.performance_window
                }
            }
            
            with open(self.weights_file, 'w') as f:
                json.dump(weights_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save weights: {e}")
            
    def _load_performance_history(self):
        """Load performance history from file"""
        try:
            if self.performance_history_file.exists():
                with open(self.performance_history_file, 'r') as f:
                    self.performance_history = json.load(f)
            else:
                self.performance_history = {}
                
        except Exception as e:
            self.logger.error(f"Failed to load performance history: {e}")
            self.performance_history = {}
            
    def _save_performance_history(self):
        """Save performance history to file"""
        try:
            # Ensure directory exists
            self.performance_history_file.parent.mkdir(exist_ok=True)
            
            with open(self.performance_history_file, 'w') as f:
                json.dump(self.performance_history, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save performance history: {e}")
            
    def record_trade_performance(self, trade_data: Dict[str, Any]):
        """Record trade performance for strategy/bot reinforcement"""
        try:
            strategy = trade_data.get('strategy', 'unknown')
            bot_name = trade_data.get('bot_name', 'unknown')
            actual_return = float(trade_data.get('actual_return', 0))
            confidence = float(trade_data.get('confidence', 0))
            timestamp = trade_data.get('timestamp', datetime.now().isoformat())
            
            # Initialize if not exists
            if strategy not in self.performance_history:
                self.performance_history[strategy] = []
            if bot_name not in self.performance_history:
                self.performance_history[bot_name] = []
                
            # Record performance
            performance_record = {
                'timestamp': timestamp,
                'return': actual_return,
                'confidence': confidence,
                'success': actual_return > 0
            }
            
            self.performance_history[strategy].append(performance_record)
            self.performance_history[bot_name].append(performance_record)
            
            # Trim history to performance window
            if len(self.performance_history[strategy]) > self.performance_window:
                self.performance_history[strategy] = self.performance_history[strategy][-self.performance_window:]
            if len(self.performance_history[bot_name]) > self.performance_window:
                self.performance_history[bot_name] = self.performance_history[bot_name][-self.performance_window:]
                
            # Update weights based on performance
            self._update_weights(strategy, bot_name, actual_return)
            
            self.logger.debug(f"📈 Recorded performance: {strategy}/{bot_name} -> {actual_return:.4f}")
            
        except Exception as e:
            self.logger.error(f"Failed to record trade performance: {e}")
            
    def _update_weights(self, strategy: str, bot_name: str, performance: float):
        """Update weights based on performance"""
        try:
            # Initialize weights if not exist
            if strategy not in self.strategy_weights:
                self.strategy_weights[strategy] = 1.0
            if bot_name not in self.bot_weights:
                self.bot_weights[bot_name] = 1.0
                
            # Calculate performance impact
            performance_impact = self._calculate_performance_impact(performance)
            
            # Update strategy weight
            old_strategy_weight = self.strategy_weights[strategy]
            self.strategy_weights[strategy] = self._apply_weight_update(
                old_strategy_weight, performance_impact
            )
            
            # Update bot weight
            old_bot_weight = self.bot_weights[bot_name]
            self.bot_weights[bot_name] = self._apply_weight_update(
                old_bot_weight, performance_impact
            )
            
            # Log significant weight changes
            strategy_change = abs(self.strategy_weights[strategy] - old_strategy_weight)
            bot_change = abs(self.bot_weights[bot_name] - old_bot_weight)
            
            if strategy_change > 0.1 or bot_change > 0.1:
                self.logger.info(f"⚖️ Weight update - {strategy}: {old_strategy_weight:.3f} -> {self.strategy_weights[strategy]:.3f}")
                self.logger.info(f"⚖️ Weight update - {bot_name}: {old_bot_weight:.3f} -> {self.bot_weights[bot_name]:.3f}")
                
            # Save updated weights
            self._save_weights()
            
        except Exception as e:
            self.logger.error(f"Failed to update weights: {e}")
            
    def _calculate_performance_impact(self, performance: float) -> float:
        """Calculate impact factor from performance (-1 to 1)"""
        # Normalize performance to impact scale
        # Positive returns increase weights, negative decrease them
        
        if performance > 0:
            # Positive performance: logarithmic scaling for diminishing returns
            impact = min(np.log(1 + performance * 10) / 10, 1.0)
        else:
            # Negative performance: more aggressive penalty
            impact = max(-np.log(1 + abs(performance) * 20) / 5, -1.0)
            
        return impact
        
    def _apply_weight_update(self, current_weight: float, performance_impact: float) -> float:
        """Apply weight update with learning rate and constraints"""
        # Calculate weight change
        weight_change = self.learning_rate * performance_impact
        
        # Apply decay to prevent extreme weights
        decayed_weight = current_weight * self.decay_factor
        
        # Update weight
        new_weight = decayed_weight + weight_change
        
        # Apply constraints
        new_weight = max(self.min_weight, min(self.max_weight, new_weight))
        
        return new_weight
        
    def get_strategy_performance(self) -> Dict[str, Any]:
        """Get comprehensive strategy performance metrics"""
        performance_metrics = {
            'strategies': {},
            'bots': {},
            'summary': {
                'total_strategies': len(self.strategy_weights),
                'total_bots': len(self.bot_weights),
                'avg_strategy_weight': np.mean(list(self.strategy_weights.values())) if self.strategy_weights else 0,
                'avg_bot_weight': np.mean(list(self.bot_weights.values())) if self.bot_weights else 0
            }
        }
        
        try:
            # Strategy metrics
            for strategy, weight in self.strategy_weights.items():
                if strategy in self.performance_history:
                    history = self.performance_history[strategy]
                    metrics = self._calculate_performance_metrics(history)
                    metrics['current_weight'] = weight
                    performance_metrics['strategies'][strategy] = metrics
                    
            # Bot metrics
            for bot, weight in self.bot_weights.items():
                if bot in self.performance_history:
                    history = self.performance_history[bot]
                    metrics = self._calculate_performance_metrics(history)
                    metrics['current_weight'] = weight
                    performance_metrics['bots'][bot] = metrics
                    
        except Exception as e:
            self.logger.error(f"Failed to get strategy performance: {e}")
            
        return performance_metrics
        
    def _calculate_performance_metrics(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate performance metrics from history"""
        if not history:
            return {
                'total_trades': 0,
                'win_rate': 0,
                'avg_return': 0,
                'total_return': 0,
                'sharpe_ratio': 0
            }
            
        returns = [trade['return'] for trade in history]
        successes = [trade['success'] for trade in history]
        
        metrics = {
            'total_trades': len(history),
            'win_rate': sum(successes) / len(successes),
            'avg_return': np.mean(returns),
            'total_return': sum(returns),
            'volatility': np.std(returns),
            'sharpe_ratio': np.mean(returns) / np.std(returns) if np.std(returns) > 0 else 0,
            'max_return': max(returns),
            'min_return': min(returns)
        }
        
        return metrics
        
    def identify_top_performers(self, metric: str = 'sharpe_ratio', top_n: int = 5) -> Dict[str, List[Dict[str, Any]]]:
        """Identify top performing strategies and bots"""
        performance = self.get_strategy_performance()
        
        top_performers = {
            'strategies': [],
            'bots': []
        }
        
        try:
            # Sort strategies by metric
            strategy_items = [
                {'name': name, **metrics} 
                for name, metrics in performance['strategies'].items()
                if metrics['total_trades'] >= 5  # Minimum trade threshold
            ]
            strategy_items.sort(key=lambda x: x.get(metric, 0), reverse=True)
            top_performers['strategies'] = strategy_items[:top_n]
            
            # Sort bots by metric
            bot_items = [
                {'name': name, **metrics} 
                for name, metrics in performance['bots'].items()
                if metrics['total_trades'] >= 5  # Minimum trade threshold
            ]
            bot_items.sort(key=lambda x: x.get(metric, 0), reverse=True)
            top_performers['bots'] = bot_items[:top_n]
            
        except Exception as e:
            self.logger.error(f"Failed to identify top performers: {e}")
            
        return top_performers
        
    def identify_underperformers(self, threshold: float = -0.1) -> Dict[str, List[str]]:
        """Identify underperforming strategies and bots"""
        performance = self.get_strategy_performance()
        
        underperformers = {
            'strategies': [],
            'bots': []
        }
        
        try:
            # Check strategies
            for name, metrics in performance['strategies'].items():
                if (metrics['total_trades'] >= 10 and 
                    metrics['avg_return'] < threshold):
                    underperformers['strategies'].append(name)
                    
            # Check bots
            for name, metrics in performance['bots'].items():
                if (metrics['total_trades'] >= 10 and 
                    metrics['avg_return'] < threshold):
                    underperformers['bots'].append(name)
                    
        except Exception as e:
            self.logger.error(f"Failed to identify underperformers: {e}")
            
        return underperformers
        
    def adjust_allocation(self, entity_type: str, name: str, new_weight: float):
        """Manually adjust allocation weight"""
        try:
            new_weight = max(self.min_weight, min(self.max_weight, new_weight))
            
            if entity_type == 'strategy':
                old_weight = self.strategy_weights.get(name, 1.0)
                self.strategy_weights[name] = new_weight
                self.logger.info(f"⚖️ Manual strategy weight adjustment: {name} {old_weight:.3f} -> {new_weight:.3f}")
                
            elif entity_type == 'bot':
                old_weight = self.bot_weights.get(name, 1.0)
                self.bot_weights[name] = new_weight
                self.logger.info(f"⚖️ Manual bot weight adjustment: {name} {old_weight:.3f} -> {new_weight:.3f}")
                
            self._save_weights()
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to adjust allocation: {e}")
            return False
            
    def reset_weights(self):
        """Reset all weights to default (1.0)"""
        try:
            for strategy in self.strategy_weights:
                self.strategy_weights[strategy] = 1.0
            for bot in self.bot_weights:
                self.bot_weights[bot] = 1.0
                
            self._save_weights()
            self.logger.info("🔄 All weights reset to default values")
            
        except Exception as e:
            self.logger.error(f"Failed to reset weights: {e}")


# Demo function
def demo_reinforcement_engine():
    """Demo the reinforcement engine functionality"""
    config = {"demo_mode": True}
    engine = ReinforcementEngine(config)
    
    print("⚖️ TradeMasterX Phase 14: Reinforcement Engine Demo")
    print("=" * 50)
    
    # Simulate some trade performances
    demo_trades = [
        {'strategy': 'momentum', 'bot_name': 'AnalyticsBot', 'actual_return': 0.025, 'confidence': 0.8},
        {'strategy': 'momentum', 'bot_name': 'AnalyticsBot', 'actual_return': 0.015, 'confidence': 0.75},
        {'strategy': 'reversal', 'bot_name': 'StrategyBot', 'actual_return': -0.02, 'confidence': 0.6},
        {'strategy': 'momentum', 'bot_name': 'AnalyticsBot', 'actual_return': 0.03, 'confidence': 0.85},
        {'strategy': 'reversal', 'bot_name': 'StrategyBot', 'actual_return': -0.015, 'confidence': 0.55}
    ]
    
    # Record performances
    for trade in demo_trades:
        engine.record_trade_performance(trade)
        
    # Get performance metrics
    performance = engine.get_strategy_performance()
    print("📊 Strategy Performance:")
    for strategy, metrics in performance['strategies'].items():
        print(f"   {strategy}: Weight={metrics['current_weight']:.3f}, "
              f"Win Rate={metrics['win_rate']:.2%}, "
              f"Avg Return={metrics['avg_return']:.4f}")
              
    print("\n📊 Bot Performance:")
    for bot, metrics in performance['bots'].items():
        print(f"   {bot}: Weight={metrics['current_weight']:.3f}, "
              f"Win Rate={metrics['win_rate']:.2%}, "
              f"Avg Return={metrics['avg_return']:.4f}")
              
    # Identify top performers
    top_performers = engine.identify_top_performers()
    print(f"\n🏆 Top Performing Strategy: {top_performers['strategies'][0]['name'] if top_performers['strategies'] else 'None'}")
    print(f"🏆 Top Performing Bot: {top_performers['bots'][0]['name'] if top_performers['bots'] else 'None'}")
    
    # Check for underperformers
    underperformers = engine.identify_underperformers()
    if underperformers['strategies'] or underperformers['bots']:
        print(f"⚠️ Underperformers found: {underperformers}")
    else:
        print("✅ No significant underperformers detected")
        
    print("\n✅ Reinforcement Engine demo completed")


if __name__ == "__main__":
    demo_reinforcement_engine()
