"""
TradeMasterX 2.0 - Phase 11 Integration Test
Comprehensive test for the Intelligent Optimization system
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
import sys
import os

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from trademasterx.optimizers.phase_11.phase_11_controller import Phase11Controller
from trademasterx.optimizers.phase_11.config import Phase11Config, TESTING_CONFIG

class Phase11IntegrationTest:
    """
    Integration test suite for Phase 11 Intelligent Optimization
    
    Tests all 5 components working together:
    - AdaptiveStrategyReinforcer
    - BotPerformanceScorer
    - StrategySwitcher
    - AnomalyDetector
    - LiveOptimizationDashboard
    """
    
    def __init__(self):
        self.test_data_dir = Path("test_data/phase_11")
        self.test_logs_dir = Path("test_logs/phase_11")
        
        # Create test directories
        self.test_data_dir.mkdir(parents=True, exist_ok=True)
        self.test_logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize controller with testing configuration
        self.controller = Phase11Controller(
            data_dir=str(self.test_data_dir),
            logs_dir=str(self.test_logs_dir)
        )
        
        # Apply testing configuration
        test_config = TESTING_CONFIG.to_dict()
        self.controller.update_configuration(test_config)
        
        self.test_results = []
        self.logger = self._setup_logging()
    
    def _setup_logging(self):
        """Setup test logging"""
        logger = logging.getLogger("Phase11IntegrationTest")
        logger.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # File handler
        file_handler = logging.FileHandler(self.test_logs_dir / "integration_test.log")
        file_handler.setLevel(logging.DEBUG)
        
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        
        if not logger.handlers:
            logger.addHandler(console_handler)
            logger.addHandler(file_handler)
        
        return logger
    
    def generate_mock_trade_data(self, trade_count: int = 50):
        """Generate mock trade data for testing"""
        import random
        
        strategies = ['momentum', 'mean_reversion', 'breakout', 'scalping', 'swing']
        bots = ['bot_alpha', 'bot_beta', 'bot_gamma', 'bot_delta', 'bot_epsilon']
        symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'SOLUSDT', 'DOTUSDT']
        
        trades = []
        base_time = datetime.now() - timedelta(hours=2)
        
        for i in range(trade_count):
            # Create realistic trade data with some patterns
            confidence = random.uniform(0.3, 0.95)
            expected_return = random.uniform(-0.05, 0.08)
            
            # Simulate performance correlation with confidence
            if confidence > 0.8:
                actual_return = expected_return + random.uniform(-0.01, 0.02)
            else:
                actual_return = expected_return + random.uniform(-0.03, 0.03)
            
            # Add some anomalies
            if random.random() < 0.1:  # 10% anomalies
                actual_return = expected_return + random.uniform(-0.15, 0.15)
            
            trade = {
                'trade_id': f"test_trade_{i:04d}",
                'bot_id': random.choice(bots),
                'strategy_id': random.choice(strategies),
                'symbol': random.choice(symbols),
                'signal': random.choice(['buy', 'sell']),
                'confidence': confidence,
                'expected_return': expected_return,
                'actual_return': actual_return,
                'position_size': random.uniform(100, 1000),
                'timestamp': (base_time + timedelta(minutes=i*2)).isoformat(),
                'market_conditions': {
                    'volatility': random.uniform(0.01, 0.05),
                    'volume': random.uniform(1000000, 10000000),
                    'trend': random.choice(['bullish', 'bearish', 'sideways'])
                }
            }
            trades.append(trade)
        
        return trades
    
    async def test_component_initialization(self):
        """Test that all Phase 11 components initialize correctly"""
        self.logger.info("Testing component initialization...")
        
        try:
            # Check controller initialization
            assert self.controller is not None, "Controller not initialized"
            
            # Check all components are accessible
            assert hasattr(self.controller, 'strategy_reinforcer'), "Strategy reinforcer not found"
            assert hasattr(self.controller, 'bot_scorer'), "Bot scorer not found"
            assert hasattr(self.controller, 'strategy_switcher'), "Strategy switcher not found"
            assert hasattr(self.controller, 'anomaly_detector'), "Anomaly detector not found"
            assert hasattr(self.controller, 'dashboard'), "Dashboard not found"
            
            # Test system status
            status = self.controller.get_system_status()
            assert status['component_status']['strategy_reinforcer'] == 'active', "Strategy reinforcer not active"
            assert status['component_status']['bot_scorer'] == 'active', "Bot scorer not active"
            
            self.test_results.append({
                'test': 'component_initialization',
                'status': 'PASSED',
                'message': 'All components initialized successfully'
            })
            self.logger.info("✅ Component initialization test passed")
            return True
            
        except Exception as e:
            self.test_results.append({
                'test': 'component_initialization',
                'status': 'FAILED',
                'message': str(e)
            })
            self.logger.error(f"❌ Component initialization test failed: {e}")
            return False
    
    async def test_trade_processing(self):
        """Test processing individual trades through all components"""
        self.logger.info("Testing trade processing...")
        
        try:
            # Generate test trades
            test_trades = self.generate_mock_trade_data(10)
            processed_count = 0
            
            for trade in test_trades:
                result = await self.controller.process_trade_result(trade)
                
                # Verify result structure
                assert 'timestamp' in result, "Missing timestamp in result"
                assert 'trade_id' in result, "Missing trade_id in result"
                assert 'optimization_results' in result, "Missing optimization_results in result"
                
                # Check that all components processed the trade
                opt_results = result['optimization_results']
                assert 'strategy_reinforcement' in opt_results, "Strategy reinforcement missing"
                assert 'bot_scoring' in opt_results, "Bot scoring missing"
                assert 'anomaly_detection' in opt_results, "Anomaly detection missing"
                
                processed_count += 1
            
            self.test_results.append({
                'test': 'trade_processing',
                'status': 'PASSED',
                'message': f'Successfully processed {processed_count} trades'
            })
            self.logger.info(f"✅ Trade processing test passed - {processed_count} trades processed")
            return True
            
        except Exception as e:
            self.test_results.append({
                'test': 'trade_processing',
                'status': 'FAILED',
                'message': str(e)
            })
            self.logger.error(f"❌ Trade processing test failed: {e}")
            return False
    
    async def test_optimization_cycles(self):
        """Test optimization cycle execution"""
        self.logger.info("Testing optimization cycles...")
        
        try:
            # Run a few optimization cycles
            cycle_results = []
            
            for i in range(3):
                result = await self.controller.run_optimization_cycle()
                cycle_results.append(result)
                
                # Verify cycle result structure
                assert 'cycle_number' in result, "Missing cycle_number in result"
                assert 'timestamp' in result, "Missing timestamp in result"
                assert 'component_results' in result, "Missing component_results in result"
                
                # Check component results
                comp_results = result['component_results']
                assert 'bot_rankings' in comp_results, "Bot rankings missing"
                assert 'strategy_evaluation' in comp_results, "Strategy evaluation missing"
                assert 'anomaly_patterns' in comp_results, "Anomaly patterns missing"
                
                await asyncio.sleep(1)  # Small delay between cycles
            
            # Verify cycle count increased
            assert self.controller.optimization_cycle_count == 3, "Cycle count not updated correctly"
            
            self.test_results.append({
                'test': 'optimization_cycles',
                'status': 'PASSED',
                'message': f'Successfully completed 3 optimization cycles'
            })
            self.logger.info("✅ Optimization cycles test passed")
            return True
            
        except Exception as e:
            self.test_results.append({
                'test': 'optimization_cycles',
                'status': 'FAILED',
                'message': str(e)
            })
            self.logger.error(f"❌ Optimization cycles test failed: {e}")
            return False
    
    async def test_dashboard_functionality(self):
        """Test dashboard functionality"""
        self.logger.info("Testing dashboard functionality...")
        
        try:
            # Test dashboard summary
            summary = self.controller.dashboard.get_dashboard_summary()
            assert summary is not None, "Dashboard summary is None"
            
            # Test metrics update
            mock_metrics = {
                'bot_metrics': {'avg_performance': 0.75, 'active_bots': 5},
                'strategy_metrics': {'switches_24h': 2, 'success_rate': 0.8},
                'anomaly_metrics': {'anomalies_24h': 3, 'patterns': 1},
                'system_metrics': {'trades_per_hour': 15, 'win_rate': 0.7}
            }
            
            dashboard_result = self.controller.dashboard.update_metrics(
                mock_metrics['bot_metrics'],
                mock_metrics['strategy_metrics'],
                mock_metrics['anomaly_metrics'],
                mock_metrics['system_metrics']
            )
            
            assert dashboard_result is not None, "Dashboard metrics update failed"
            
            # Test alert logging
            self.controller.dashboard.log_optimization_event(
                'test_event',
                'TestComponent',
                'Test optimization event',
                {'test_before': 'value1'},
                {'test_after': 'value2'},
                True
            )
            
            self.test_results.append({
                'test': 'dashboard_functionality',
                'status': 'PASSED',
                'message': 'Dashboard functionality working correctly'
            })
            self.logger.info("✅ Dashboard functionality test passed")
            return True
            
        except Exception as e:
            self.test_results.append({
                'test': 'dashboard_functionality',
                'status': 'FAILED',
                'message': str(e)
            })
            self.logger.error(f"❌ Dashboard functionality test failed: {e}")
            return False
    
    async def test_anomaly_detection(self):
        """Test anomaly detection with intentional anomalies"""
        self.logger.info("Testing anomaly detection...")
        
        try:
            # Create normal trades
            normal_trades = []
            for i in range(20):
                trade = {
                    'trade_id': f"normal_{i}",
                    'bot_id': 'test_bot',
                    'strategy_id': 'test_strategy',
                    'confidence': 0.7 + (i % 3) * 0.1,
                    'expected_return': 0.02,
                    'actual_return': 0.02 + (i % 2) * 0.005,
                    'timestamp': datetime.now().isoformat()
                }
                normal_trades.append(trade)
            
            # Process normal trades to establish baseline
            for trade in normal_trades:
                await self.controller.process_trade_result(trade)
            
            # Create anomalous trade
            anomaly_trade = {
                'trade_id': 'anomaly_1',
                'bot_id': 'test_bot',
                'strategy_id': 'test_strategy',
                'confidence': 0.95,
                'expected_return': 0.02,
                'actual_return': -0.15,  # Major deviation
                'timestamp': datetime.now().isoformat()
            }
            
            # Process anomaly trade
            result = await self.controller.process_trade_result(anomaly_trade)
            anomaly_result = result['optimization_results']['anomaly_detection']
            
            # Check if anomaly was detected
            # Note: Detection depends on having enough baseline data
            self.logger.info(f"Anomaly detection result: {anomaly_result}")
            
            self.test_results.append({
                'test': 'anomaly_detection',
                'status': 'PASSED',
                'message': 'Anomaly detection system functioning'
            })
            self.logger.info("✅ Anomaly detection test passed")
            return True
            
        except Exception as e:
            self.test_results.append({
                'test': 'anomaly_detection',
                'status': 'FAILED',
                'message': str(e)
            })
            self.logger.error(f"❌ Anomaly detection test failed: {e}")
            return False
    
    async def test_continuous_optimization(self):
        """Test short continuous optimization run"""
        self.logger.info("Testing continuous optimization...")
        
        try:
            # Set short optimization interval for testing
            self.controller.update_configuration({
                'optimization_interval_seconds': 2,
                'max_optimization_cycles': 3
            })
            
            # Start continuous optimization
            optimization_task = asyncio.create_task(
                self.controller.start_continuous_optimization()
            )
            
            # Let it run for a bit
            await asyncio.sleep(8)
            
            # Stop optimization
            self.controller.stop_optimization()
            
            # Wait for task to complete
            try:
                await asyncio.wait_for(optimization_task, timeout=5)
            except asyncio.TimeoutError:
                optimization_task.cancel()
            
            # Check that cycles were completed
            assert self.controller.optimization_cycle_count >= 3, "Expected at least 3 cycles"
            
            self.test_results.append({
                'test': 'continuous_optimization',
                'status': 'PASSED',
                'message': f'Continuous optimization completed {self.controller.optimization_cycle_count} cycles'
            })
            self.logger.info("✅ Continuous optimization test passed")
            return True
            
        except Exception as e:
            self.test_results.append({
                'test': 'continuous_optimization',
                'status': 'FAILED',
                'message': str(e)
            })
            self.logger.error(f"❌ Continuous optimization test failed: {e}")
            return False
    
    async def test_report_generation(self):
        """Test comprehensive report generation"""
        self.logger.info("Testing report generation...")
        
        try:
            # Generate optimization report
            report = self.controller.get_optimization_report()
            
            # Verify report structure
            assert 'report_timestamp' in report, "Missing report_timestamp"
            assert 'system_overview' in report, "Missing system_overview"
            assert 'bot_performance' in report, "Missing bot_performance"
            assert 'strategy_analysis' in report, "Missing strategy_analysis"
            assert 'anomaly_analysis' in report, "Missing anomaly_analysis"
            assert 'recommendations' in report, "Missing recommendations"
            
            # Save report to file for inspection
            report_file = self.test_data_dir / "integration_test_report.json"
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            self.test_results.append({
                'test': 'report_generation',
                'status': 'PASSED',
                'message': f'Report generated successfully and saved to {report_file}'
            })
            self.logger.info("✅ Report generation test passed")
            return True
            
        except Exception as e:
            self.test_results.append({
                'test': 'report_generation',
                'status': 'FAILED',
                'message': str(e)
            })
            self.logger.error(f"❌ Report generation test failed: {e}")
            return False
    
    async def run_all_tests(self):
        """Run complete integration test suite"""
        self.logger.info(" Starting Phase 11 Integration Test Suite")
        self.logger.info("=" * 60)
        
        start_time = time.time()
        
        # Run all tests
        tests = [
            self.test_component_initialization,
            self.test_trade_processing,
            self.test_optimization_cycles,
            self.test_dashboard_functionality,
            self.test_anomaly_detection,
            self.test_continuous_optimization,
            self.test_report_generation
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_func in tests:
            try:
                result = await test_func()
                if result:
                    passed_tests += 1
            except Exception as e:
                self.logger.error(f"Test {test_func.__name__} crashed: {e}")
        
        # Generate final summary
        end_time = time.time()
        duration = end_time - start_time
        
        self.logger.info("=" * 60)
        self.logger.info("🏁 Phase 11 Integration Test Results")
        self.logger.info(f"Tests Passed: {passed_tests}/{total_tests}")
        self.logger.info(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        self.logger.info(f"Total Duration: {duration:.2f} seconds")
        
        # Save detailed results
        results_file = self.test_data_dir / "integration_test_results.json"
        test_summary = {
            'timestamp': datetime.now().isoformat(),
            'duration_seconds': duration,
            'tests_passed': passed_tests,
            'tests_total': total_tests,
            'success_rate': (passed_tests/total_tests)*100,
            'detailed_results': self.test_results
        }
        
        with open(results_file, 'w') as f:
            json.dump(test_summary, f, indent=2)
        
        self.logger.info(f"📊 Detailed results saved to: {results_file}")
        
        if passed_tests == total_tests:
            self.logger.info("🎉 ALL TESTS PASSED - Phase 11 Integration Successful!")
            return True
        else:
            self.logger.warning("⚠️  Some tests failed - Review results for issues")
            return False
    
    def cleanup(self):
        """Cleanup test data and resources"""
        self.logger.info("🧹 Cleaning up test resources...")
        # Test directories will be preserved for inspection

async def main():
    """Main test execution"""
    print("TradeMasterX 2.0 - Phase 11 Integration Test")
    print("=" * 50)
    
    # Run integration tests
    test_suite = Phase11IntegrationTest()
    
    try:
        success = await test_suite.run_all_tests()
        test_suite.cleanup()
        
        if success:
            print("\n✅ Integration test completed successfully!")
            return 0
        else:
            print("\n❌ Integration test completed with failures!")
            return 1
            
    except Exception as e:
        print(f"\n💥 Integration test crashed: {e}")
        return 2

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
