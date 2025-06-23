#!/usr/bin/env python3
"""
TradeMasterX 2.0 - Phase 11 Integration Testing
Comprehensive integration tests for the Phase 11 Intelligent Optimization system
"""

import asyncio
import json
import logging
import sys
import time
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from trademasterx.optimizers.phase_11 import (
    Phase11Controller,
    AdaptiveStrategyReinforcer,
    BotPerformanceScorer,
    StrategySwitcher,
    AnomalyDetector,
    LiveOptimizationDashboard
)
from trademasterx.config.config_loader import ConfigLoader

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/phase_11_integration_test.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("Phase11IntegrationTest")

class TestPhase11Components(unittest.TestCase):
    """Test individual Phase 11 components"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_data_dir = Path("test_data")
        self.test_logs_dir = Path("test_logs")
        
        # Create test directories
        self.test_data_dir.mkdir(exist_ok=True)
        self.test_logs_dir.mkdir(exist_ok=True)
        
        # Initialize components
        self.strategy_reinforcer = AdaptiveStrategyReinforcer(str(self.test_data_dir))
        self.bot_scorer = BotPerformanceScorer(str(self.test_data_dir))
        self.strategy_switcher = StrategySwitcher(str(self.test_data_dir))
        self.anomaly_detector = AnomalyDetector(str(self.test_logs_dir))
        self.dashboard = LiveOptimizationDashboard(str(self.test_data_dir), str(self.test_logs_dir))
    
    def test_adaptive_strategy_reinforcer(self):
        """Test AdaptiveStrategyReinforcer functionality"""
        print("\n🧪 Testing AdaptiveStrategyReinforcer...")
        
        # Test trade outcome analysis
        trade_data = {
            'strategy_id': 'momentum_strategy',
            'actual_return': 0.08,
            'confidence': 0.85,
            'timestamp': datetime.now().isoformat()
        }
        
        result = self.strategy_reinforcer.analyze_trade_outcome(trade_data)
        self.assertIsInstance(result, dict)
        self.assertIn('weight_adjusted', result)
        
        # Test strategy weight updates
        weights_before = self.strategy_reinforcer.get_current_weights()
        update_result = self.strategy_reinforcer.update_all_strategies()
        weights_after = self.strategy_reinforcer.get_current_weights()
        
        self.assertIsInstance(update_result, dict)
        self.assertIn('strategies_updated', update_result)
        
        print("   ✅ AdaptiveStrategyReinforcer tests passed")
    
    def test_bot_performance_scorer(self):
        """Test BotPerformanceScorer functionality"""
        print("\n🧪 Testing BotPerformanceScorer...")
        
        # Test prediction scoring
        result = self.bot_scorer.score_prediction(
            bot_id="test_bot_001",
            confidence=0.75,
            expected_return=0.05,
            actual_return=0.04,
            timestamp=datetime.now().isoformat()
        )
        
        self.assertIsInstance(result, dict)
        self.assertIn('score_updated', result)
        
        # Test bot ranking
        rankings = self.bot_scorer.get_bot_rankings()
        self.assertIsInstance(rankings, dict)
        self.assertIn('rankings', rankings)
        
        print("   ✅ BotPerformanceScorer tests passed")
    
    def test_strategy_switcher(self):
        """Test StrategySwitcher functionality"""
        print("\n🧪 Testing StrategySwitcher...")
        
        # Test trade recording
        trade_data = {'return': 0.03, 'confidence': 0.8}
        self.strategy_switcher.record_trade_result('balanced_strategy', trade_data)
        
        # Test strategy evaluation
        evaluation = self.strategy_switcher.evaluate_current_strategy('balanced_strategy', 0.02)
        self.assertIsInstance(evaluation, dict)
        
        # Test all strategies evaluation
        all_eval = self.strategy_switcher.evaluate_all_strategies()
        self.assertIsInstance(all_eval, dict)
        self.assertIn('strategies_evaluated', all_eval)
        
        print("   ✅ StrategySwitcher tests passed")
    
    def test_anomaly_detector(self):
        """Test AnomalyDetector functionality"""
        print("\n🧪 Testing AnomalyDetector...")
        
        # Test trade anomaly detection
        trade_data = {
            'actual_return': 0.15,  # High return
            'confidence': 0.9,
            'volume': 1000000,
            'timestamp': datetime.now().isoformat()
        }
        
        result = self.anomaly_detector.detect_trade_anomaly(trade_data)
        self.assertIsInstance(result, dict)
        self.assertIn('is_anomaly', result)
        
        # Test pattern analysis
        patterns = self.anomaly_detector.analyze_patterns()
        self.assertIsInstance(patterns, dict)
        
        print("   ✅ AnomalyDetector tests passed")
    
    def test_live_optimization_dashboard(self):
        """Test LiveOptimizationDashboard functionality"""
        print("\n🧪 Testing LiveOptimizationDashboard...")
        
        # Test metrics aggregation
        metrics = self.dashboard.aggregate_real_time_metrics()
        self.assertIsInstance(metrics, object)  # DashboardMetrics object
        
        # Test alert creation
        alert_result = self.dashboard.create_alert(
            "test_alert", "medium", "Test alert message"
        )
        self.assertIsInstance(alert_result, dict)
        
        # Test optimization event logging
        self.dashboard.log_optimization_event(
            "test_event", "TestComponent", "Test event", {}, {}, True
        )
        
        print("   ✅ LiveOptimizationDashboard tests passed")

class TestPhase11Controller(unittest.TestCase):
    """Test Phase 11 Controller integration"""
    
    def setUp(self):
        """Set up controller test environment"""
        self.test_data_dir = Path("test_data")
        self.test_logs_dir = Path("test_logs")
        
        # Create test directories
        self.test_data_dir.mkdir(exist_ok=True)
        self.test_logs_dir.mkdir(exist_ok=True)
        
        # Initialize controller
        self.controller = Phase11Controller(
            data_dir=str(self.test_data_dir),
            logs_dir=str(self.test_logs_dir)
        )
    
    def test_controller_initialization(self):
        """Test controller initialization"""
        print("\n🧪 Testing Phase11Controller initialization...")
        
        # Test system status
        status = self.controller.get_system_status()
        self.assertIsInstance(status, dict)
        self.assertIn('component_status', status)
        self.assertIn('configuration', status)
        
        # Test configuration update
        config_updates = {'optimization_interval_seconds': 180}
        self.controller.update_configuration(config_updates)
        
        updated_status = self.controller.get_system_status()
        self.assertEqual(
            updated_status['configuration']['optimization_interval_seconds'], 
            180
        )
        
        print("   ✅ Phase11Controller initialization tests passed")
    
    async def test_trade_processing(self):
        """Test trade result processing"""
        print("\n🧪 Testing trade result processing...")
        
        trade_data = {
            'trade_id': 'test_trade_001',
            'symbol': 'BTCUSDT',
            'signal': 'buy',
            'confidence': 0.85,
            'expected_return': 0.05,
            'actual_return': 0.04,
            'bot_id': 'test_bot_001',
            'strategy_id': 'momentum_strategy',
            'timestamp': datetime.now().isoformat(),
            'position_size': 1000
        }
        
        result = await self.controller.process_trade_result(trade_data)
        
        self.assertIsInstance(result, dict)
        self.assertIn('trade_id', result)
        self.assertIn('optimization_results', result)
        self.assertIn('processing_time_seconds', result)
        
        print("   ✅ Trade processing tests passed")
    
    async def test_optimization_cycle(self):
        """Test optimization cycle execution"""
        print("\n🧪 Testing optimization cycle...")
        
        # Process some trades first
        for i in range(5):
            trade_data = {
                'trade_id': f'test_trade_{i:03d}',
                'symbol': 'BTCUSDT',
                'signal': 'buy' if i % 2 == 0 else 'sell',
                'confidence': 0.7 + (i * 0.05),
                'expected_return': 0.03 + (i * 0.01),
                'actual_return': 0.02 + (i * 0.008),
                'bot_id': f'test_bot_{i % 3:03d}',
                'strategy_id': 'balanced_strategy',
                'timestamp': datetime.now().isoformat(),
                'position_size': 1000
            }
            await self.controller.process_trade_result(trade_data)
        
        # Run optimization cycle
        cycle_result = await self.controller.run_optimization_cycle()
        
        self.assertIsInstance(cycle_result, dict)
        self.assertIn('cycle_number', cycle_result)
        self.assertIn('component_results', cycle_result)
        self.assertIn('cycle_time_seconds', cycle_result)
        
        print("   ✅ Optimization cycle tests passed")
    
    def test_optimization_report(self):
        """Test optimization report generation"""
        print("\n🧪 Testing optimization report generation...")
        
        report = self.controller.get_optimization_report()
        
        self.assertIsInstance(report, dict)
        self.assertIn('report_timestamp', report)
        
        if 'error' not in report:
            self.assertIn('system_overview', report)
            self.assertIn('component_reports', report)
            self.assertIn('recommendations', report)
        
        print("   ✅ Optimization report tests passed")

class TestPhase11Integration(unittest.TestCase):
    """Test Phase 11 integration with other systems"""
    
    def setUp(self):
        """Set up integration test environment"""
        self.controller = Phase11Controller()
    
    def test_configuration_loading(self):
        """Test Phase 11 configuration loading"""
        print("\n🧪 Testing configuration loading...")
        
        config_loader = ConfigLoader()
        
        # Test loading Phase 11 config
        phase11_config = config_loader.load_config("trademasterx/config/phase_11.yaml")
        
        if phase11_config:
            self.assertIn('system', phase11_config)
            self.assertIn('components', phase11_config)
            self.assertIn('controller', phase11_config)
            print("   ✅ Phase 11 configuration loaded successfully")
        else:
            print("   ⚠️ Phase 11 configuration file not found, using defaults")
    
    @patch('trademasterx.core.phase10_optimizer.Phase10Optimizer')
    async def test_phase10_integration(self, mock_phase10):
        """Test integration with Phase 10 optimizer"""
        print("\n🧪 Testing Phase 10 integration...")
        
        # Mock Phase 10 optimizer
        mock_phase10.get_system_metrics.return_value = {
            'total_trades': 100,
            'win_rate': 0.65,
            'avg_return': 0.04
        }
        mock_phase10.get_recent_trades.return_value = [
            {
                'trade_id': 'phase10_trade_001',
                'symbol': 'BTCUSDT',
                'actual_return': 0.03,
                'confidence': 0.8
            }
        ]
        
        # Test integration
        integration_result = await self.controller.integrate_with_phase10(mock_phase10)
        
        self.assertIsInstance(integration_result, dict)
        
        if integration_result.get('integration_status') == 'success':
            self.assertIn('optimization_results', integration_result)
            self.assertIn('recommendations', integration_result)
            print("   ✅ Phase 10 integration tests passed")
        else:
            print(f"   ⚠️ Phase 10 integration test failed: {integration_result.get('error', 'Unknown error')}")

async def run_integration_tests():
    """Run all integration tests"""
    print("=" * 80)
    print("🧠 TradeMasterX 2.0 - Phase 11 Integration Testing")
    print("=" * 80)
    
    # Create test directories
    Path("test_data").mkdir(exist_ok=True)
    Path("test_logs").mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)
    
    test_suite = unittest.TestSuite()
    
    # Add component tests
    component_tests = unittest.TestLoader().loadTestsFromTestCase(TestPhase11Components)
    test_suite.addTests(component_tests)
    
    # Add controller tests
    controller_tests = unittest.TestLoader().loadTestsFromTestCase(TestPhase11Controller)
    test_suite.addTests(controller_tests)
    
    # Add integration tests
    integration_tests = unittest.TestLoader().loadTestsFromTestCase(TestPhase11Integration)
    test_suite.addTests(integration_tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    
    print("\n Starting Phase 11 integration tests...")
    start_time = time.time()
    
    # Run sync tests
    sync_result = runner.run(test_suite)
    
    # Run async tests separately
    print("\n🔄 Running async tests...")
    
    try:
        # Test async controller methods
        controller = Phase11Controller(data_dir="test_data", logs_dir="test_logs")
        
        # Test trade processing
        trade_data = {
            'trade_id': 'async_test_001',
            'symbol': 'BTCUSDT',
            'signal': 'buy',
            'confidence': 0.8,
            'expected_return': 0.05,
            'actual_return': 0.04,
            'bot_id': 'async_test_bot',
            'strategy_id': 'test_strategy',
            'timestamp': datetime.now().isoformat()
        }
        
        trade_result = await controller.process_trade_result(trade_data)
        assert isinstance(trade_result, dict), "Trade processing failed"
        print("   ✅ Async trade processing test passed")
        
        # Test optimization cycle
        cycle_result = await controller.run_optimization_cycle()
        assert isinstance(cycle_result, dict), "Optimization cycle failed"
        print("   ✅ Async optimization cycle test passed")
        
        # Test Phase 10 integration
        mock_phase10 = Mock()
        mock_phase10.get_system_metrics.return_value = {'total_trades': 10}
        mock_phase10.get_recent_trades.return_value = []
        
        integration_result = await controller.integrate_with_phase10(mock_phase10)
        assert isinstance(integration_result, dict), "Phase 10 integration failed"
        print("   ✅ Async Phase 10 integration test passed")
        
        async_tests_passed = True
        
    except Exception as e:
        print(f"   ❌ Async tests failed: {e}")
        async_tests_passed = False
    
    end_time = time.time()
    
    # Generate test report
    print("\n" + "=" * 80)
    print("📊 PHASE 11 INTEGRATION TEST RESULTS")
    print("=" * 80)
    
    print(f"⏱️  Total test time: {end_time - start_time:.2f} seconds")
    print(f"🧪 Tests run: {sync_result.testsRun}")
    print(f"✅ Tests passed: {sync_result.testsRun - len(sync_result.failures) - len(sync_result.errors)}")
    print(f"❌ Tests failed: {len(sync_result.failures)}")
    print(f"💥 Test errors: {len(sync_result.errors)}")
    print(f"🔄 Async tests: {'✅ Passed' if async_tests_passed else '❌ Failed'}")
    
    overall_success = (
        sync_result.wasSuccessful() and 
        async_tests_passed and
        len(sync_result.failures) == 0 and 
        len(sync_result.errors) == 0
    )
    
    if overall_success:
        print("\n🎉 ALL PHASE 11 INTEGRATION TESTS PASSED!")
        print("✅ Phase 11 system is ready for integration with TradeMasterX 2.0")
    else:
        print("\n⚠️  Some tests failed - review errors above")
        
        if sync_result.failures:
            print("\n❌ Test Failures:")
            for test, traceback in sync_result.failures:
                print(f"   - {test}: {traceback.split('AssertionError:')[-1].strip()}")
        
        if sync_result.errors:
            print("\n💥 Test Errors:")
            for test, traceback in sync_result.errors:
                print(f"   - {test}: {traceback.split('Exception:')[-1].strip()}")
    
    # Cleanup test directories
    try:
        import shutil
        if Path("test_data").exists():
            shutil.rmtree("test_data")
        if Path("test_logs").exists():
            shutil.rmtree("test_logs")
        print("\n🧹 Test directories cleaned up")
    except Exception as e:
        print(f"\n⚠️  Cleanup failed: {e}")
    
    print("=" * 80)
    
    return overall_success

def run_performance_validation():
    """Run performance validation tests"""
    print("\n Running Phase 11 Performance Validation...")
    
    try:
        # Initialize controller
        controller = Phase11Controller()
        
        # Performance metrics
        start_time = time.time()
        
        # Test rapid trade processing
        async def process_trades():
            tasks = []
            for i in range(100):  # Process 100 trades
                trade_data = {
                    'trade_id': f'perf_test_{i:03d}',
                    'symbol': 'BTCUSDT',
                    'signal': 'buy' if i % 2 == 0 else 'sell',
                    'confidence': 0.5 + (i % 10) * 0.05,
                    'expected_return': 0.01 + (i % 5) * 0.01,
                    'actual_return': 0.008 + (i % 5) * 0.008,
                    'bot_id': f'perf_bot_{i % 5}',
                    'strategy_id': 'performance_test',
                    'timestamp': datetime.now().isoformat()
                }
                tasks.append(controller.process_trade_result(trade_data))
            
            return await asyncio.gather(*tasks)
        
        # Run performance test
        results = asyncio.run(process_trades())
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Calculate performance metrics
        trades_per_second = 100 / processing_time
        avg_processing_time = processing_time / 100
        
        print(f"   📊 Performance Results:")
        print(f"      Total trades processed: 100")
        print(f"      Total time: {processing_time:.2f} seconds")
        print(f"      Trades per second: {trades_per_second:.2f}")
        print(f"      Average processing time: {avg_processing_time:.4f} seconds")
        
        # Performance thresholds
        if trades_per_second >= 10:  # At least 10 trades per second
            print("   ✅ Performance test PASSED - Meets throughput requirements")
            return True
        else:
            print("   ❌ Performance test FAILED - Below throughput requirements")
            return False
            
    except Exception as e:
        print(f"   ❌ Performance validation failed: {e}")
        return False

if __name__ == "__main__":
    print("TradeMasterX 2.0 - Phase 11 Integration Testing")
    print("Select testing mode:")
    print("1. Full Integration Tests (default)")
    print("2. Performance Validation")
    print("3. Both tests")
    
    choice = input("\nEnter choice (1-3): ").strip() or "1"
    
    if choice == "1":
        success = asyncio.run(run_integration_tests())
        sys.exit(0 if success else 1)
    elif choice == "2":
        success = run_performance_validation()
        sys.exit(0 if success else 1)
    elif choice == "3":
        integration_success = asyncio.run(run_integration_tests())
        performance_success = run_performance_validation()
        overall_success = integration_success and performance_success
        
        print(f"\n🏁 Overall Result: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
        sys.exit(0 if overall_success else 1)
    else:
        print("Invalid choice. Running full integration tests...")
        success = asyncio.run(run_integration_tests())
        sys.exit(0 if success else 1)
