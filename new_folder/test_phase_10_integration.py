#!/usr/bin/env python3
"""
TradeMasterX 2.0 - Phase 10 Integration Test
Tests the complete Phase 10 learning loop functionality
"""

import asyncio
import sys
import os
from pathlib import Path
import logging
import json
from datetime import datetime, timedelta
import unittest
from unittest.mock import Mock, patch

# Configure paths
current_dir = Path(__file__).parent.absolute()
sys.path.append(str(current_dir))

# Test imports
from trademasterx.config.config_loader import ConfigLoader
from trademasterx.core.safety_controller import SafetyController
from trademasterx.core.bot_registry import BotRegistry
from trademasterx.core.learning_phase_controller import LearningPhaseController
from trademasterx.core.phase10_optimizer import Phase10Optimizer
from core.training.continuous_retrainer import ContinuousRetrainer

class TestPhase10Integration(unittest.TestCase):
    """Integration tests for Phase 10 learning loop"""
    
    def setUp(self):
        """Setup test environment"""
        self.test_config = {
            'learning': {
                'trade_frequency': 5,  # Faster for testing
                'retrain_interval': 30,  # 30 seconds for testing
                'weekly_report': True,
                'top_bot_threshold': 0.7
            },
            'safety': {
                'confidence_threshold': 0.80,
                'min_return_threshold': 0.15,
                'max_position_size': 1000,
                'demo_mode': True,
                'mainnet_demo': True
            },
            'trading_mode': {
                'DEMO_MODE': True,
                'LIVE_MODE': False,
                'mainnet_demo': True
            }
        }
        
        # Setup logging for tests
        logging.basicConfig(level=logging.INFO)
        
    def test_phase10_optimizer_initialization(self):
        """Test Phase10Optimizer initialization"""
        optimizer = Phase10Optimizer(self.test_config)
        
        self.assertIsNotNone(optimizer)
        self.assertEqual(optimizer.config, self.test_config)
        self.assertIsInstance(optimizer.bot_scores, dict)
        self.assertIsInstance(optimizer.prediction_history, dict)
        
    def test_phase10_optimizer_prediction_recording(self):
        """Test prediction recording and scoring"""
        optimizer = Phase10Optimizer(self.test_config)
        
        # Test prediction recording
        prediction = {
            'signal': 'buy',
            'confidence': 0.85,
            'expected_return': 0.18,
            'symbol': 'BTCUSDT'
        }
        market_data = {'volatility': 0.15, 'trend': 'bullish'}
        
        optimizer.record_prediction('test_bot', prediction, market_data)
        
        self.assertIn('test_bot', optimizer.prediction_history)
        self.assertEqual(len(optimizer.prediction_history['test_bot']), 1)
        
    def test_phase10_optimizer_trade_outcome_scoring(self):
        """Test trade outcome recording and prediction scoring"""
        optimizer = Phase10Optimizer(self.test_config)
        
        # Record a prediction first
        prediction = {
            'signal': 'buy',
            'confidence': 0.85,
            'expected_return': 0.18,
            'symbol': 'BTCUSDT'
        }
        market_data = {'volatility': 0.15, 'trend': 'bullish'}
        optimizer.record_prediction('test_bot', prediction, market_data)
        
        # Record trade outcome
        trade_outcome = {
            'symbol': 'BTCUSDT',
            'signal': 'buy',
            'actual_return': 0.20,
            'timestamp': datetime.now().isoformat()
        }
        
        optimizer.record_trade_outcome(trade_outcome)
        
        # Check if prediction was scored
        pred = optimizer.prediction_history['test_bot'][0]
        self.assertTrue(pred['scored'])
        self.assertIsNotNone(pred['outcome'])
        self.assertTrue(pred['outcome']['was_correct'])
        
    def test_continuous_retrainer(self):
        """Test continuous retrainer functionality"""
        retrainer = ContinuousRetrainer("test_models/", "test_data/")
        
        # Test basic initialization
        self.assertIsNotNone(retrainer)
        self.assertEqual(retrainer.current_model_version, "v1.0.0")
        
        # Test retraining data structure
        retraining_data = {
            'predictions': [
                {'signal': 'buy', 'confidence': 0.85},
                {'signal': 'sell', 'confidence': 0.78}
            ],
            'outcomes': [
                {'was_correct': True, 'actual_return': 0.15},
                {'was_correct': True, 'actual_return': 0.12}
            ]
        }
        
        # Test async retraining
        async def test_retrain():
            result = await retrainer.retrain_models(retraining_data)
            return result
            
        result = asyncio.run(test_retrain())
        self.assertTrue(result)
        self.assertNotEqual(retrainer.current_model_version, "v1.0.0")
        
    def test_learning_phase_controller_initialization(self):
        """Test LearningPhaseController initialization with bot registry"""
        bot_registry = BotRegistry(self.test_config)
        controller = LearningPhaseController(self.test_config, bot_registry)
        
        self.assertIsNotNone(controller)
        self.assertEqual(controller.bot_registry, bot_registry)
        self.assertIsNotNone(controller.phase10_optimizer)
        self.assertIsNotNone(controller.safety_controller)
        
    def test_safety_controller_validation(self):
        """Test safety controller validates demo mode"""
        safety = SafetyController(self.test_config)
        
        # Should validate demo trading requests
        self.assertTrue(safety.validate_trading_request("DEMO_TRADE", 500))
        self.assertTrue(safety.validate_trading_request("START_LEARNING_PHASE"))
        
    def test_bot_registry_integration(self):
        """Test bot registry integration"""
        registry = BotRegistry(self.test_config)
        
        # Test basic functionality
        self.assertEqual(registry.get_bot_count(), 0)
        self.assertIsInstance(registry.get_bot_status(), dict)

class TestPhase10MockRun(unittest.TestCase):
    """Mock run tests for Phase 10 components"""
    
    def setUp(self):
        """Setup mock test environment"""
        self.test_config = {
            'learning': {
                'trade_frequency': 1,  # Very fast for testing
                'retrain_interval': 5,  # 5 seconds for testing
                'weekly_report': True
            },
            'safety': {
                'confidence_threshold': 0.80,
                'min_return_threshold': 0.15,
                'demo_mode': True,
                'mainnet_demo': True
            },
            'trading_mode': {
                'DEMO_MODE': True,
                'LIVE_MODE': False,
                'mainnet_demo': True
            }
        }
        
    async def test_learning_loop_cycle(self):
        """Test a single learning loop cycle"""
        bot_registry = Mock()
        bot_registry.execute_all_cycles = Mock(return_value={
            'strategy_bot': {'signal': 'buy', 'confidence': 0.85, 'expected_return': 0.18}
        })
        
        controller = LearningPhaseController(self.test_config, bot_registry)
        
        # Test market analysis
        market_analysis = await controller._analyze_market()
        self.assertIsInstance(market_analysis, dict)
        self.assertIn('timestamp', market_analysis)
        
        # Test bot predictions
        predictions = await controller._get_bot_predictions()
        self.assertIsInstance(predictions, dict)
        self.assertIn('strategy_bot', predictions)
        
        # Test trade evaluation
        trade_decision = await controller._evaluate_trade_opportunity(market_analysis, predictions)
        self.assertIsInstance(trade_decision, dict)
        
    def test_phase10_metrics_calculation(self):
        """Test Phase10Optimizer metrics calculation"""
        optimizer = Phase10Optimizer(self.test_config)
        
        # Add some mock bot scores
        optimizer.bot_scores = {
            'test_bot': {
                'total_predictions': 10,
                'correct_predictions': 7,
                'total_return': 1.5,
                'returns': [0.1, 0.2, -0.05, 0.15, 0.08, 0.12, -0.02, 0.18, 0.09, 0.14],
                'confidences': [0.8, 0.9, 0.7, 0.85, 0.75, 0.88, 0.72, 0.91, 0.79, 0.86],
                'signals': ['buy'] * 10
            }
        }
        
        # Test metrics calculation
        metrics = optimizer.update_bot_metrics()
        
        self.assertIn('trade_accuracy', metrics)
        self.assertIn('test_bot', metrics['trade_accuracy'])
        self.assertEqual(metrics['trade_accuracy']['test_bot'], 0.7)  # 7/10
        
    def test_report_generation(self):
        """Test report generation"""
        optimizer = Phase10Optimizer(self.test_config)
        
        # Add mock data
        optimizer.bot_scores = {
            'test_bot': {
                'total_predictions': 5,
                'correct_predictions': 4,
                'total_return': 0.8,
                'returns': [0.1, 0.2, 0.15, 0.18, 0.17],
                'confidences': [0.8, 0.9, 0.85, 0.88, 0.86],
                'signals': ['buy'] * 5
            }
        }
        
        # Test report generation
        report = optimizer.generate_bot_report()
        
        self.assertIsInstance(report, dict)
        self.assertIn('timestamp', report)
        self.assertIn('bots', report)
        self.assertIn('system', report)
        self.assertIn('test_bot', report['bots'])

def run_integration_tests():
    """Run all integration tests"""
    print("🧪 TradeMasterX 2.0 - Phase 10 Integration Tests")
    print("=" * 60)
    
    # Create test directories
    Path("test_models").mkdir(exist_ok=True)
    Path("test_data").mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)
    
    # Run unit tests
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPhase10Integration)
    runner = unittest.TextTestRunner(verbosity=2)
    result1 = runner.run(suite)
    
    # Run mock tests
    suite2 = unittest.TestLoader().loadTestsFromTestCase(TestPhase10MockRun)
    result2 = runner.run(suite2)
    
    # Summary
    total_tests = result1.testsRun + result2.testsRun
    total_failures = len(result1.failures) + len(result2.failures)
    total_errors = len(result1.errors) + len(result2.errors)
    
    print("=" * 60)
    print(f"📊 Test Summary:")
    print(f"   Total Tests: {total_tests}")
    print(f"   Failures: {total_failures}")
    print(f"   Errors: {total_errors}")
    
    if total_failures == 0 and total_errors == 0:
        print("✅ All tests passed!")
        return True
    else:
        print("❌ Some tests failed!")
        return False

if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)
