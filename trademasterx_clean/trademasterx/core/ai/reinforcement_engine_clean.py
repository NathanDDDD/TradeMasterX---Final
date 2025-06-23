#!/usr/bin/env python3
"""
TradeMasterX 2.0 - Phase 14: Reinforcement Engine (Clean Implementation)
Tracks performance per strategy/bot and adjusts weights dynamically
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import numpy as np

class ReinforcementEngine:
    """Reinforcement learning engine for strategy optimization"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger("ReinforcementEngine")
        
        # Performance tracking
        self.strategy_performance = {}
        self.bot_performance = {}
        self.weight_adjustments = {}
        
        # Learning parameters
        self.learning_rate = 0.01
        self.min_weight = 0.1
        self.max_weight = 2.0
        
        # File paths
        self.data_dir = Path("data")
        self.reports_dir = Path("reports")
        self.performance_file = self.data_dir / "performance_tracking.json"
        self.weights_file = self.data_dir / "strategy_weights.json"
        
        # Ensure directories exist
        self.data_dir.mkdir(exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)
        
        # Load existing data
        self._load_performance_data()
        self._load_weights()
        
    def _load_performance_data(self):
        """Load existing performance data"""
        try:
            if self.performance_file.exists():
                with open(self.performance_file, 'r') as f:
                    data = json.load(f)
                    self.strategy_performance = data.get('strategies', {})
                    self.bot_performance = data.get('bots', {})
        except Exception as e:
            self.logger.error(f"Failed to load performance data: {e}")
            
    def _load_weights(self):
        """Load existing weights"""
        try:
            if self.weights_file.exists():
                with open(self.weights_file, 'r') as f:
                    self.weight_adjustments = json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load weights: {e}")
            
    def record_trade_performance(self, trade_data: Dict[str, Any]):
        """Record performance for a trade"""
        try:
            strategy = trade_data.get('strategy', 'unknown')
            bot_name = trade_data.get('bot_name', 'unknown')
            actual_return = trade_data.get('actual_return', 0)
            expected_return = trade_data.get('expected_return', 0)
            
            # Update strategy performance
            if strategy not in self.strategy_performance:
                self.strategy_performance[strategy] = {
                    'total_trades': 0,
                    'total_return': 0,
                    'wins': 0,
                    'losses': 0,
                    'recent_performance': []
                }
                
            self.strategy_performance[strategy]['total_trades'] += 1
            self.strategy_performance[strategy]['total_return'] += actual_return
            
            if actual_return > 0:
                self.strategy_performance[strategy]['wins'] += 1
            else:
                self.strategy_performance[strategy]['losses'] += 1
                
            # Keep recent performance (last 100 trades)
            self.strategy_performance[strategy]['recent_performance'].append({
                'timestamp': datetime.now().isoformat(),
                'return': actual_return,
                'expected': expected_return
            })
            
            if len(self.strategy_performance[strategy]['recent_performance']) > 100:
                self.strategy_performance[strategy]['recent_performance'] = \
                    self.strategy_performance[strategy]['recent_performance'][-100:]
                    
            # Update bot performance
            if bot_name not in self.bot_performance:
                self.bot_performance[bot_name] = {
                    'total_trades': 0,
                    'total_return': 0,
                    'wins': 0,
                    'losses': 0
                }
                
            self.bot_performance[bot_name]['total_trades'] += 1
            self.bot_performance[bot_name]['total_return'] += actual_return
            
            if actual_return > 0:
                self.bot_performance[bot_name]['wins'] += 1
            else:
                self.bot_performance[bot_name]['losses'] += 1
                
            # Adjust weights based on performance
            self._adjust_weights(strategy, actual_return, expected_return)
            
            # Save updated data
            self._save_performance_data()
            self._save_weights()
            
        except Exception as e:
            self.logger.error(f"Failed to record trade performance: {e}")
            
    def _adjust_weights(self, strategy: str, actual_return: float, expected_return: float):
        """Adjust strategy weights based on performance"""
        try:
            if strategy not in self.weight_adjustments:
                self.weight_adjustments[strategy] = 1.0
                
            # Calculate performance ratio
            performance_ratio = actual_return / max(abs(expected_return), 0.001)
            
            # Adjust weight based on performance
            if performance_ratio > 1.1:  # Outperformed by 10%
                adjustment = self.learning_rate * 0.1
            elif performance_ratio < 0.9:  # Underperformed by 10%
                adjustment = -self.learning_rate * 0.1
            else:
                adjustment = 0
                
            # Apply adjustment
            new_weight = self.weight_adjustments[strategy] + adjustment
            self.weight_adjustments[strategy] = max(self.min_weight, min(self.max_weight, new_weight))
            
        except Exception as e:
            self.logger.error(f"Failed to adjust weights: {e}")
            
    def get_strategy_performance(self) -> Dict[str, Any]:
        """Get comprehensive strategy performance data"""
        summary = {
            'strategies': {},
            'bots': {},
            'summary': {
                'total_strategies': len(self.strategy_performance),
                'total_bots': len(self.bot_performance),
                'total_trades': sum(s.get('total_trades', 0) for s in self.strategy_performance.values()),
                'overall_return': sum(s.get('total_return', 0) for s in self.strategy_performance.values())
            }
        }
        
        # Process strategy data
        for strategy, data in self.strategy_performance.items():
            total_trades = data.get('total_trades', 0)
            if total_trades > 0:
                win_rate = data.get('wins', 0) / total_trades
                avg_return = data.get('total_return', 0) / total_trades
                
                summary['strategies'][strategy] = {
                    'total_trades': total_trades,
                    'win_rate': win_rate,
                    'avg_return': avg_return,
                    'total_return': data.get('total_return', 0),
                    'current_weight': self.weight_adjustments.get(strategy, 1.0)
                }
                
        # Process bot data
        for bot, data in self.bot_performance.items():
            total_trades = data.get('total_trades', 0)
            if total_trades > 0:
                win_rate = data.get('wins', 0) / total_trades
                avg_return = data.get('total_return', 0) / total_trades
                
                summary['bots'][bot] = {
                    'total_trades': total_trades,
                    'win_rate': win_rate,
                    'avg_return': avg_return,
                    'total_return': data.get('total_return', 0)
                }
                
        return summary
        
    def get_strategy_weight(self, strategy: str) -> float:
        """Get current weight for a strategy"""
        return self.weight_adjustments.get(strategy, 1.0)
        
    def reset_weights(self):
        """Reset all strategy weights to default"""
        self.weight_adjustments = {}
        self._save_weights()
        self.logger.info("🔄 All strategy weights reset to default")
        
    def _save_performance_data(self):
        """Save performance data to file"""
        try:
            data = {
                'strategies': self.strategy_performance,
                'bots': self.bot_performance,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.performance_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save performance data: {e}")
            
    def _save_weights(self):
        """Save weights to file"""
        try:
            data = {
                'weights': self.weight_adjustments,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.weights_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save weights: {e}")


# Demo function
async def demo_reinforcement_engine():
    """Demo the reinforcement engine functionality"""
    config = {"demo_mode": True}
    engine = ReinforcementEngine(config)
    
    print("⚖️ TradeMasterX Phase 14: Reinforcement Engine Demo")
    print("=" * 50)
    
    # Simulate some trades
    demo_trades = [
        {'strategy': 'momentum', 'bot_name': 'MomentumBot', 'actual_return': 0.02, 'expected_return': 0.015},
        {'strategy': 'reversal', 'bot_name': 'ReversalBot', 'actual_return': -0.01, 'expected_return': 0.01},
        {'strategy': 'momentum', 'bot_name': 'MomentumBot', 'actual_return': 0.025, 'expected_return': 0.02},
    ]
    
    for trade in demo_trades:
        engine.record_trade_performance(trade)
        
    # Show performance summary
    performance = engine.get_strategy_performance()
    print(f"Strategies tracked: {len(performance['strategies'])}")
    print(f"Bots tracked: {len(performance['bots'])}")
    
    print("✅ Reinforcement Engine demo completed")


if __name__ == "__main__":
    import asyncio
    asyncio.run(demo_reinforcement_engine())
