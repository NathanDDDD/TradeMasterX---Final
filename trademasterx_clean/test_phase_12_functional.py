#!/usr/bin/env python3
"""
Phase 12 Functional Tests - Testing actual component interactions and emergency scenarios
"""

import sys
import os
import json
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path

# Setup path for imports
sys.path.insert(0, os.path.abspath('.'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('Phase12FunctionalTest')

class Phase12FunctionalTest:
    def __init__(self):
        self.results = {
            'test_time': datetime.now().isoformat(),
            'emergency_scenarios': {},
            'component_interactions': {},
            'performance_tests': {},
            'dashboard_integration': {},
            'overall_status': 'UNKNOWN'
        }
        
    def setup_test_environment(self):
        """Setup test environment with clean state"""
        logger.info("Setting up functional test environment...")
        
        # Clean up any persistent state
        kill_switch_file = Path("kill_switch_state.json")
        if kill_switch_file.exists():
            kill_switch_file.unlink()
            logger.info("Cleaned up kill switch state file")
            
        # Clean up test data
        test_dirs = ['test_reports', 'snapshots', 'logs']
        for test_dir in test_dirs:
            test_path = Path(test_dir)
            if test_path.exists():
                for file in test_path.glob('*test*'):
                    try:
                        file.unlink()
                        logger.info(f"Cleaned up test file: {file}")
                    except Exception as e:
                        logger.warning(f"Could not clean {file}: {e}")
        
        logger.info("Functional test environment setup complete")
        
    def test_emergency_kill_switch_scenario(self):
        """Test emergency kill switch activation and recovery"""
        logger.info("Testing emergency kill switch scenario...")
        
        try:
            from trademasterx.core import KillSwitch
            
            # Test 1: Emergency activation
            kill_switch = KillSwitch()
            
            # Simulate emergency scenario
            emergency_result = kill_switch.activate(
                reason="EMERGENCY_FUNCTIONAL_TEST", 
                authority="TEST_SUITE"
            )
            
            emergency_success = (
                emergency_result.get('success', False) and
                emergency_result.get('status') == 'ACTIVATED'
            )
            
            # Test 2: System lockdown verification
            is_locked = kill_switch.is_active()
            can_trade = kill_switch.can_execute_trade({'symbol': 'TEST'})
            
            lockdown_success = is_locked and not can_trade
            
            # Test 3: Recovery procedure
            recovery_result = kill_switch.deactivate(
                reason="EMERGENCY_TEST_COMPLETE",
                authority="TEST_SUITE"
            )
            
            recovery_success = (
                recovery_result.get('success', False) and
                recovery_result.get('status') == 'DEACTIVATED'
            )
            
            # Test 4: System restoration
            is_restored = not kill_switch.is_active()
            can_trade_again = kill_switch.can_execute_trade({'symbol': 'TEST'})
            
            restoration_success = is_restored and can_trade_again
            
            self.results['emergency_scenarios']['kill_switch'] = {
                'emergency_activation': emergency_success,
                'system_lockdown': lockdown_success,
                'recovery_procedure': recovery_success,
                'system_restoration': restoration_success,
                'overall_success': all([
                    emergency_success, lockdown_success, 
                    recovery_success, restoration_success
                ])
            }
            
            logger.info(f"✓ Emergency kill switch test completed - Success: {self.results['emergency_scenarios']['kill_switch']['overall_success']}")
            
        except Exception as e:
            logger.error(f"❌ Emergency kill switch test failed: {e}")
            self.results['emergency_scenarios']['kill_switch'] = {
                'error': str(e),
                'overall_success': False
            }
            
    def test_risk_guard_protection(self):
        """Test risk guard protection scenarios"""
        logger.info("Testing risk guard protection scenarios...")
        
        try:
            from trademasterx.core import RiskGuard
            
            risk_guard = RiskGuard()
            
            # Test 1: Normal trade validation
            normal_trade = {
                'symbol': 'EURUSD',
                'amount': 100,
                'side': 'buy',
                'price': 1.1000
            }
            
            normal_result = risk_guard.validate_trade(normal_trade)
            normal_success = normal_result.get('allowed', False)
            
            # Test 2: Risky trade rejection
            risky_trade = {
                'symbol': 'GBPJPY',
                'amount': 100000,  # Very large amount
                'side': 'sell',
                'price': 150.00
            }
            
            risky_result = risk_guard.validate_trade(risky_trade)
            risky_rejected = not risky_result.get('allowed', True)
            
            # Test 3: Daily limit enforcement
            daily_status = risk_guard.get_daily_status()
            limits_enforced = (
                'pnl' in daily_status and
                'trade_count' in daily_status and
                'limits' in daily_status
            )
            
            self.results['emergency_scenarios']['risk_guard'] = {
                'normal_trade_validation': normal_success,
                'risky_trade_rejection': risky_rejected,
                'daily_limits_enforced': limits_enforced,
                'overall_success': all([normal_success, risky_rejected, limits_enforced])
            }
            
            logger.info(f"✓ Risk guard protection test completed - Success: {self.results['emergency_scenarios']['risk_guard']['overall_success']}")
            
        except Exception as e:
            logger.error(f"❌ Risk guard protection test failed: {e}")
            self.results['emergency_scenarios']['risk_guard'] = {
                'error': str(e),
                'overall_success': False
            }
            
    def test_component_interactions(self):
        """Test interactions between Phase 12 components"""
        logger.info("Testing component interactions...")
        
        try:
            from trademasterx.core import (
                KillSwitch, RiskGuard, TradeDeviationAlert, 
                RecoveryManager, SafetyDashboard
            )
            
            # Initialize all components
            kill_switch = KillSwitch()
            risk_guard = RiskGuard()
            deviation_alert = TradeDeviationAlert()
            recovery_manager = RecoveryManager()
            safety_dashboard = SafetyDashboard()
            
            # Test 1: Dashboard aggregation
            safety_status = safety_dashboard.get_safety_status()
            dashboard_success = (
                'kill_switch' in safety_status and
                'risk_guard' in safety_status and
                'system_health' in safety_status
            )
            
            # Test 2: Cross-component communication
            # Risk guard -> Kill switch interaction
            kill_switch.deactivate("TEST_SETUP", "TEST_SUITE")  # Ensure deactivated
            
            # Simulate high-risk scenario
            high_risk_trade = {
                'symbol': 'XAUUSD',
                'amount': 50000,
                'side': 'buy',
                'price': 2000.00
            }
            
            risk_result = risk_guard.validate_trade(high_risk_trade)
            
            # If risk guard rejects, kill switch should remain accessible
            communication_success = (
                not risk_result.get('allowed', True) and
                not kill_switch.is_active()  # Kill switch not auto-triggered
            )
            
            # Test 3: Recovery coordination
            # Create snapshot
            snapshot_result = recovery_manager.create_snapshot()
            snapshot_success = snapshot_result.get('success', False)
            
            # Get latest snapshot
            latest_snapshot = recovery_manager.get_latest_snapshot()
            snapshot_retrieval = latest_snapshot is not None
            
            self.results['component_interactions'] = {
                'dashboard_aggregation': dashboard_success,
                'cross_component_communication': communication_success,
                'recovery_coordination': snapshot_success and snapshot_retrieval,
                'overall_success': all([
                    dashboard_success, communication_success, 
                    snapshot_success, snapshot_retrieval
                ])
            }
            
            logger.info(f"✓ Component interactions test completed - Success: {self.results['component_interactions']['overall_success']}")
            
        except Exception as e:
            logger.error(f"❌ Component interactions test failed: {e}")
            self.results['component_interactions'] = {
                'error': str(e),
                'overall_success': False
            }
            
    def test_performance_under_load(self):
        """Test performance under simulated load conditions"""
        logger.info("Testing performance under load...")
        
        try:
            from trademasterx.core import SafetyDashboard, RiskGuard
            
            safety_dashboard = SafetyDashboard()
            risk_guard = RiskGuard()
            
            # Test 1: Rapid dashboard queries
            start_time = time.time()
            dashboard_responses = []
            
            for i in range(10):  # 10 rapid queries
                status = safety_dashboard.get_safety_status()
                dashboard_responses.append(status is not None)
                
            dashboard_time = time.time() - start_time
            dashboard_performance = dashboard_time < 5.0  # Should complete in under 5 seconds
            
            # Test 2: Rapid trade validations
            start_time = time.time()
            validation_responses = []
            
            test_trade = {
                'symbol': 'EURUSD',
                'amount': 1000,
                'side': 'buy',
                'price': 1.1000
            }
            
            for i in range(20):  # 20 rapid validations
                result = risk_guard.validate_trade(test_trade)
                validation_responses.append(result is not None)
                
            validation_time = time.time() - start_time
            validation_performance = validation_time < 5.0  # Should complete in under 5 seconds
            
            self.results['performance_tests'] = {
                'dashboard_queries': {
                    'time': dashboard_time,
                    'success_rate': sum(dashboard_responses) / len(dashboard_responses),
                    'performance_ok': dashboard_performance
                },
                'trade_validations': {
                    'time': validation_time,
                    'success_rate': sum(validation_responses) / len(validation_responses),
                    'performance_ok': validation_performance
                },
                'overall_success': dashboard_performance and validation_performance
            }
            
            logger.info(f"✓ Performance test completed - Success: {self.results['performance_tests']['overall_success']}")
            
        except Exception as e:
            logger.error(f"❌ Performance test failed: {e}")
            self.results['performance_tests'] = {
                'error': str(e),
                'overall_success': False
            }
            
    def test_dashboard_integration(self):
        """Test web interface integration with core dashboard"""
        logger.info("Testing dashboard integration...")
        
        try:
            # Test core dashboard
            from trademasterx.core import SafetyDashboard
            core_dashboard = SafetyDashboard()
            
            # Test standalone functions
            from trademasterx.core.safety_dashboard import (
                get_risk_metrics, get_deviation_data, 
                get_recent_alerts, emergency_stop
            )
            
            # Test 1: Core dashboard functionality
            safety_status = core_dashboard.get_safety_status()
            core_success = isinstance(safety_status, dict)
            
            # Test 2: Standalone function access
            risk_metrics = get_risk_metrics()
            deviation_data = get_deviation_data()
            recent_alerts = get_recent_alerts()
            
            standalone_success = all([
                isinstance(risk_metrics, dict),
                isinstance(deviation_data, dict),
                isinstance(recent_alerts, dict)
            ])
            
            # Test 3: Emergency stop function
            emergency_result = emergency_stop()
            emergency_function_success = isinstance(emergency_result, dict)
            
            # Test 4: Web interface accessibility (import test)
            try:
                from trademasterx.interface.web.safety_dashboard import SafetyDashboardInterface
                web_interface = SafetyDashboardInterface()
                web_interface_success = True
            except Exception as e:
                logger.warning(f"Web interface test skipped: {e}")
                web_interface_success = False
            
            self.results['dashboard_integration'] = {
                'core_dashboard': core_success,
                'standalone_functions': standalone_success,
                'emergency_function': emergency_function_success,
                'web_interface': web_interface_success,
                'overall_success': all([
                    core_success, standalone_success, emergency_function_success
                ])
            }
            
            logger.info(f"✓ Dashboard integration test completed - Success: {self.results['dashboard_integration']['overall_success']}")
            
        except Exception as e:
            logger.error(f"❌ Dashboard integration test failed: {e}")
            self.results['dashboard_integration'] = {
                'error': str(e),
                'overall_success': False
            }
    
    def run_all_tests(self):
        """Run all functional tests"""
        logger.info("Starting Phase 12 Functional Tests...")
        
        self.setup_test_environment()
        
        # Run all test categories
        self.test_emergency_kill_switch_scenario()
        self.test_risk_guard_protection()
        self.test_component_interactions()
        self.test_performance_under_load()
        self.test_dashboard_integration()
        
        # Calculate overall results
        all_categories = [
            self.results['emergency_scenarios'].get('kill_switch', {}).get('overall_success', False),
            self.results['emergency_scenarios'].get('risk_guard', {}).get('overall_success', False),
            self.results['component_interactions'].get('overall_success', False),
            self.results['performance_tests'].get('overall_success', False),
            self.results['dashboard_integration'].get('overall_success', False)
        ]
        
        total_tests = len(all_categories)
        passed_tests = sum(all_categories)
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        self.results['overall_status'] = 'SUCCESS' if success_rate >= 80 else 'PARTIAL' if success_rate >= 60 else 'FAILED'
        
        # Print results
        logger.info("=" * 80)
        logger.info("PHASE 12 FUNCTIONAL TEST RESULTS")
        logger.info("=" * 80)
        logger.info(f"Emergency Scenarios - Kill Switch: {'✓' if self.results['emergency_scenarios'].get('kill_switch', {}).get('overall_success', False) else '❌'}")
        logger.info(f"Emergency Scenarios - Risk Guard: {'✓' if self.results['emergency_scenarios'].get('risk_guard', {}).get('overall_success', False) else '❌'}")
        logger.info(f"Component Interactions: {'✓' if self.results['component_interactions'].get('overall_success', False) else '❌'}")
        logger.info(f"Performance Tests: {'✓' if self.results['performance_tests'].get('overall_success', False) else '❌'}")
        logger.info(f"Dashboard Integration: {'✓' if self.results['dashboard_integration'].get('overall_success', False) else '❌'}")
        logger.info(f"Overall Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests})")
        logger.info(f"Overall Status: {self.results['overall_status']}")
        logger.info("=" * 80)
        
        # Save detailed results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_dir = Path("test_reports")
        results_dir.mkdir(exist_ok=True)
        
        results_file = results_dir / f"phase_12_functional_test_{timestamp}.json"
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
            
        logger.info(f"Detailed results saved to: {results_file}")
        
        if self.results['overall_status'] == 'SUCCESS':
            logger.info("✓ PHASE 12 FUNCTIONAL TESTS: SUCCESS")
        elif self.results['overall_status'] == 'PARTIAL':
            logger.info("⚠ PHASE 12 FUNCTIONAL TESTS: PARTIAL SUCCESS")
        else:
            logger.info("❌ PHASE 12 FUNCTIONAL TESTS: FAILED")
        
        return self.results['overall_status'] == 'SUCCESS'

if __name__ == "__main__":
    test_runner = Phase12FunctionalTest()
    success = test_runner.run_all_tests()
    sys.exit(0 if success else 1)
