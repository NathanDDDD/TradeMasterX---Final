#!/usr/bin/env python3
"""
TradeMasterX 2.0 - Phase 11 Complete Integration Test
Tests all Phase 11 components and their integration
"""

import asyncio
import json
import sys
import time
from datetime import datetime
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test if all Phase 11 components can be imported"""
    print("=" * 60)
    print("PHASE 11 IMPORT TEST")
    print("=" * 60)
    
    try:
        from trademasterx.optimizers.phase_11 import (
            AdaptiveStrategyReinforcer,
            BotPerformanceScorer,
            StrategySwitcher,
            AnomalyDetector,
            LiveOptimizationDashboard,
            Phase11Controller
        )
        print("✅ All Phase 11 components imported successfully!")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_individual_components():
    """Test each Phase 11 component individually"""
    print("\n" + "=" * 60)
    print("INDIVIDUAL COMPONENT TESTS")
    print("=" * 60)
    
    try:
        from trademasterx.optimizers.phase_11 import (
            AdaptiveStrategyReinforcer,
            BotPerformanceScorer,
            StrategySwitcher,
            AnomalyDetector,
            LiveOptimizationDashboard
        )
        
        # Test data directories
        data_dir = "test_reports"
        logs_dir = "test_logs"
        Path(data_dir).mkdir(exist_ok=True)
        Path(logs_dir).mkdir(exist_ok=True)
        
        results = {}
        
        # Test AdaptiveStrategyReinforcer
        try:
            reinforcer = AdaptiveStrategyReinforcer(data_dir)
            print("✅ AdaptiveStrategyReinforcer initialized")
            
            # Test trade analysis
            test_trade = {
                'strategy_id': 'test_strategy',
                'expected_return': 0.02,
                'actual_return': 0.015,
                'confidence': 0.8,
                'timestamp': datetime.now().isoformat()
            }
            result = reinforcer.analyze_trade_outcome(test_trade)
            print(f"   📊 Trade analysis result: {result.get('status', 'unknown')}")
            results['strategy_reinforcer'] = 'pass'
        except Exception as e:
            print(f"❌ AdaptiveStrategyReinforcer error: {e}")
            results['strategy_reinforcer'] = 'fail'
        
        # Test BotPerformanceScorer
        try:
            scorer = BotPerformanceScorer(data_dir)
            print("✅ BotPerformanceScorer initialized")
            
            # Test scoring
            score_result = scorer.score_prediction('test_bot', 0.8, 0.02, 0.015, datetime.now().isoformat())
            print(f"   📊 Scoring result: {score_result.get('score', 'unknown')}")
            results['bot_scorer'] = 'pass'
        except Exception as e:
            print(f"❌ BotPerformanceScorer error: {e}")
            results['bot_scorer'] = 'fail'
        
        # Test StrategySwitcher
        try:
            switcher = StrategySwitcher(data_dir)
            print("✅ StrategySwitcher initialized")
            
            # Test evaluation
            eval_result = switcher.evaluate_current_strategy('test_strategy', 0.015)
            print(f"   📊 Strategy evaluation: {eval_result.get('recommendation', 'none')}")
            results['strategy_switcher'] = 'pass'
        except Exception as e:
            print(f"❌ StrategySwitcher error: {e}")
            results['strategy_switcher'] = 'fail'
        
        # Test AnomalyDetector
        try:
            detector = AnomalyDetector(logs_dir)
            print("✅ AnomalyDetector initialized")
            
            # Test anomaly detection
            test_trade_anomaly = {
                'actual_return': 0.05,  # High return might be anomaly
                'confidence': 0.9,
                'position_size': 1000
            }
            anomaly_result = detector.detect_trade_anomaly(test_trade_anomaly)
            print(f"   📊 Anomaly detection: {anomaly_result.get('is_anomaly', False)}")
            results['anomaly_detector'] = 'pass'
        except Exception as e:
            print(f"❌ AnomalyDetector error: {e}")
            results['anomaly_detector'] = 'fail'
        
        # Test LiveOptimizationDashboard
        try:
            dashboard = LiveOptimizationDashboard(data_dir, logs_dir)
            print("✅ LiveOptimizationDashboard initialized")
            
            # Test dashboard summary
            summary = dashboard.get_dashboard_summary()
            print(f"   📊 Dashboard summary generated: {len(summary)} sections")
            results['dashboard'] = 'pass'
        except Exception as e:
            print(f"❌ LiveOptimizationDashboard error: {e}")
            results['dashboard'] = 'fail'
        
        return results
        
    except Exception as e:
        print(f"❌ Component test setup error: {e}")
        return {}

async def test_phase11_controller():
    """Test the main Phase 11 controller"""
    print("\n" + "=" * 60)
    print("PHASE 11 CONTROLLER TEST")
    print("=" * 60)
    
    try:
        from trademasterx.optimizers.phase_11 import Phase11Controller
        
        # Initialize controller
        controller = Phase11Controller("test_reports", "test_logs")
        print("✅ Phase11Controller initialized")
        
        # Test configuration
        controller.update_configuration({
            'optimization_interval_seconds': 60,
            'enable_dashboard': True
        })
        print("✅ Configuration updated")
        
        # Test trade processing
        test_trade = {
            'trade_id': 'test_001',
            'bot_id': 'test_bot',
            'strategy_id': 'test_strategy',
            'symbol': 'BTC/USD',
            'signal': 'buy',
            'confidence': 0.75,
            'expected_return': 0.02,
            'actual_return': 0.018,
            'position_size': 1000,
            'timestamp': datetime.now().isoformat()
        }
        
        print("🔄 Processing test trade...")
        trade_result = await controller.process_trade_result(test_trade)
        print(f"✅ Trade processed: {trade_result.get('trade_id')}")
        
        # Test optimization cycle
        print("🔄 Running optimization cycle...")
        cycle_result = await controller.run_optimization_cycle()
        print(f"✅ Optimization cycle completed: #{cycle_result.get('cycle_number')}")
        
        # Test system status
        status = controller.get_system_status()
        print(f"✅ System status retrieved: {status.get('optimization_cycles_completed')} cycles")
        
        # Test optimization report
        report = controller.get_optimization_report()
        print(f"✅ Optimization report generated: {report.get('report_timestamp')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Phase11Controller test error: {e}")
        return False

def test_integration_with_mock_phase10():
    """Test integration with a mock Phase 10 system"""
    print("\n" + "=" * 60)
    print("PHASE 10 INTEGRATION TEST")
    print("=" * 60)
    
    try:
        from trademasterx.optimizers.phase_11 import Phase11Controller
        
        # Mock Phase 10 optimizer
        class MockPhase10Optimizer:
            def get_system_metrics(self):
                return {
                    'total_trades': 100,
                    'win_rate': 0.68,
                    'avg_return': 0.025,
                    'active_bots': 5
                }
            
            def get_recent_trades(self, limit=10):
                trades = []
                for i in range(limit):
                    trades.append({
                        'trade_id': f'trade_{i}',
                        'bot_id': f'bot_{i % 3}',
                        'strategy_id': f'strategy_{i % 2}',
                        'expected_return': 0.02,
                        'actual_return': 0.015 + (i * 0.001),
                        'confidence': 0.7 + (i * 0.01),
                        'timestamp': datetime.now().isoformat()
                    })
                return trades
        
        controller = Phase11Controller("test_reports", "test_logs")
        mock_phase10 = MockPhase10Optimizer()
        
        print("🔄 Testing Phase 10 integration...")
        
        # Test the integration method
        integration_result = asyncio.run(controller.integrate_with_phase10(mock_phase10))
        
        if integration_result.get('integration_status') == 'success':
            print("✅ Phase 10 integration successful")
            print(f"   📊 Processed {len(mock_phase10.get_recent_trades())} trades")
            print(f"   📊 Generated {len(integration_result.get('recommendations', {}))} recommendation categories")
            return True
        else:
            print(f"❌ Phase 10 integration failed: {integration_result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Integration test error: {e}")
        return False

def generate_test_report(results):
    """Generate a comprehensive test report"""
    print("\n" + "=" * 60)
    print("PHASE 11 TEST REPORT")
    print("=" * 60)
    
    total_tests = 0
    passed_tests = 0
    
    # Component tests
    if results.get('components'):
        print("\n🧩 Component Tests:")
        for component, status in results['components'].items():
            total_tests += 1
            if status == 'pass':
                passed_tests += 1
                print(f"   ✅ {component}: PASS")
            else:
                print(f"   ❌ {component}: FAIL")
    
    # Controller tests
    if results.get('controller'):
        total_tests += 1
        if results['controller']:
            passed_tests += 1
            print(f"\n🎛️  Controller Test: ✅ PASS")
        else:
            print(f"\n🎛️  Controller Test: ❌ FAIL")
    
    # Integration tests
    if results.get('integration'):
        total_tests += 1
        if results['integration']:
            passed_tests += 1
            print(f"\n🔗 Integration Test: ✅ PASS")
        else:
            print(f"\n🔗 Integration Test: ❌ FAIL")
    
    # Summary
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    print(f"\n" + "=" * 40)
    print(f"SUMMARY: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)")
    print(f"=" * 40)
    
    if success_rate >= 80:
        print("🎉 Phase 11 is ready for production!")
    elif success_rate >= 60:
        print("⚠️  Phase 11 has some issues but is mostly functional")
    else:
        print("🚨 Phase 11 needs significant fixes before deployment")
    
    return success_rate

async def main():
    """Run all Phase 11 tests"""
    print(" TradeMasterX 2.0 - Phase 11 Complete Test Suite")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {}
    
    # Test imports
    imports_ok = test_imports()
    if not imports_ok:
        print("❌ Cannot proceed without successful imports")
        return
    
    # Test individual components
    results['components'] = test_individual_components()
    
    # Test controller
    results['controller'] = await test_phase11_controller()
    
    # Test integration
    results['integration'] = test_integration_with_mock_phase10()
    
    # Generate report
    success_rate = generate_test_report(results)
    
    print(f"\n⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return success_rate >= 80

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")
        sys.exit(1)
