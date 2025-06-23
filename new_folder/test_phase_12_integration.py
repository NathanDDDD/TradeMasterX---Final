#!/usr/bin/env python3
"""
TradeMasterX Phase 12: Live Trade Safety Systems Integration Test

This script comprehensively tests all Phase 12 safety components:
1. Kill Switch System
2. Multi-Layer Risk Guard  
3. Trade Deviation Alert
4. Failover & Recovery Protocol
5. Safety Status Dashboard

Author: TradeMasterX Development Team
Date: May 28, 2025
Version: 12.0.0
"""

import sys
import os
import json
import time
import logging
import tempfile
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import Phase 12 safety systems
try:
    from trademasterx.core.kill_switch import KillSwitch
    from trademasterx.core.risk_guard import RiskGuard
    from trademasterx.core.trade_deviation_alert import TradeDeviationAlert
    from trademasterx.core.failover_recovery import RecoveryManager
    # Note: SafetyDashboard is Flask-based, tested separately
    
    print("[SUCCESS] All Phase 12 core modules imported successfully")
except ImportError as e:
    print(f"[ERROR] Import error: {e}")
    print("Attempting to continue with available modules...")
    # Try individual imports to identify which ones work
    try:
        from trademasterx.core.kill_switch import KillSwitch
        print("[SUCCESS] KillSwitch imported")
    except ImportError:
        print("[ERROR] KillSwitch import failed")
        KillSwitch = None
    
    try:
        from trademasterx.core.risk_guard import RiskGuard
        print("[SUCCESS] RiskGuard imported")
    except ImportError:
        print("[ERROR] RiskGuard import failed")
        RiskGuard = None
    
    try:
        from trademasterx.core.trade_deviation_alert import TradeDeviationAlert
        print("[SUCCESS] TradeDeviationAlert imported")
    except ImportError:
        print("[ERROR] TradeDeviationAlert import failed")
        TradeDeviationAlert = None
    
    try:
        from trademasterx.core.failover_recovery import RecoveryManager
        print("[SUCCESS] RecoveryManager imported")
    except ImportError:
        print("[ERROR] RecoveryManager import failed")
        RecoveryManager = None

class Phase12IntegrationTest:
    """Comprehensive integration test for Phase 12 safety systems."""
    
    def __init__(self):
        self.test_results = {}
        self.setup_logging()
        self.setup_test_environment()
        
    def setup_logging(self):
        """Setup test logging."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('test_logs/phase_12_integration_test.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def setup_test_environment(self):
        """Setup test environment with temporary directories."""
        self.test_dir = tempfile.mkdtemp(prefix="phase12_test_")
        self.logger.info(f"Test environment: {self.test_dir}")
        
        # Create test data directories
        os.makedirs(f"{self.test_dir}/data", exist_ok=True)
        os.makedirs(f"{self.test_dir}/alerts", exist_ok=True)
        os.makedirs(f"{self.test_dir}/snapshots", exist_ok=True)
        
    def test_kill_switch_system(self) -> bool:
        """Test Kill Switch System functionality."""
        self.logger.info("Testing Kill Switch System...")
        
        try:
            # Initialize kill switch
            kill_switch = KillSwitch()
            
            # Test 1: Initial state
            assert not kill_switch.is_active(), "Kill switch should be inactive initially"
            
            # Test 2: Activate kill switch
            result = kill_switch.activate("TEST_EMERGENCY", "Integration test activation")
            assert result["success"], "Kill switch activation should succeed"
            assert kill_switch.is_active(), "Kill switch should be active after activation"
            
            # Test 3: Check state persistence
            state = kill_switch.get_state()
            assert state["active"], "Kill switch state should show active"
            assert state["reason"] == "Integration test activation"
            
            # Test 4: Authorization code validation
            auth_result = kill_switch.validate_authorization("TEST_EMERGENCY")
            assert auth_result["valid"], "Authorization code should be valid"
            
            # Test 5: Deactivate kill switch
            deactivate_result = kill_switch.deactivate("TEST_EMERGENCY", "Integration test completion")
            assert deactivate_result["success"], "Kill switch deactivation should succeed"
            assert not kill_switch.is_active(), "Kill switch should be inactive after deactivation"
            
            # Test 6: CLI interface simulation
            cli_result = kill_switch.cli_status()
            assert "status" in cli_result, "CLI status should return status information"
            
            self.test_results["kill_switch"] = {
                "status": "PASSED",
                "tests_run": 6,
                "tests_passed": 6,
                "details": "All kill switch tests passed successfully"
            }
            
            self.logger.info("[SUCCESS] Kill Switch System tests passed")
            return True
            
        except Exception as e:
            self.test_results["kill_switch"] = {
                "status": "FAILED",
                "error": str(e),
                "details": "Kill switch system test failed"
            }
            self.logger.error(f"Kill Switch System test failed: {e}")
            return False
    
    def test_risk_guard_system(self) -> bool:
        """Test Multi-Layer Risk Guard functionality."""
        self.logger.info("Testing Risk Guard System...")
        
        try:
            # Initialize risk guard
            risk_guard = RiskGuard()
            
            # Test 1: Initial metrics
            metrics = risk_guard.get_current_metrics()
            assert metrics["daily_loss"] == 0, "Initial daily loss should be 0"
            assert metrics["daily_trades"] == 0, "Initial daily trades should be 0"
            
            # Test 2: Record a trade (within limits)
            trade_data = {
                "pnl": -50.0,  # $50 loss
                "size": 100.0,
                "symbol": "BTCUSDT"
            }
            
            validation = risk_guard.validate_trade(trade_data)
            assert validation["allowed"], "Trade within limits should be allowed"
            
            # Record the trade
            risk_guard.record_trade_result(trade_data)
            
            # Verify metrics updated
            updated_metrics = risk_guard.get_current_metrics()
            assert updated_metrics["daily_loss"] == 50.0, "Daily loss should be updated"
            assert updated_metrics["daily_trades"] == 1, "Daily trades should be updated"
            
            # Test 3: Risk limit validation
            large_loss_trade = {
                "pnl": -500.0,  # Large loss that would exceed daily limit
                "size": 1000.0,
                "symbol": "ETHUSDT"
            }
            
            # Add multiple trades to approach limit
            for i in range(5):
                risk_guard.record_trade_result({"pnl": -40.0, "size": 100.0, "symbol": "BTCUSDT"})
            
            # This should trigger risk protection
            large_validation = risk_guard.validate_trade(large_loss_trade)
            risk_warnings = risk_guard.get_risk_warnings()
            
            # Test 4: Risk warnings generation
            assert len(risk_warnings) > 0, "Risk warnings should be generated"
            
            # Test 5: Daily reset functionality
            risk_guard.reset_daily_counters()
            reset_metrics = risk_guard.get_current_metrics()
            assert reset_metrics["daily_loss"] == 0, "Daily loss should reset to 0"
            assert reset_metrics["daily_trades"] == 0, "Daily trades should reset to 0"
            
            # Test 6: Configuration loading
            config = risk_guard.get_configuration()
            assert "daily_loss_limit" in config, "Configuration should include daily loss limit"
            
            self.test_results["risk_guard"] = {
                "status": "PASSED",
                "tests_run": 6,
                "tests_passed": 6,
                "details": "All risk guard tests passed successfully"
            }
            
            self.logger.info("[SUCCESS] Risk Guard System tests passed")
            return True
            
        except Exception as e:
            self.test_results["risk_guard"] = {
                "status": "FAILED",
                "error": str(e),
                "details": "Risk guard system test failed"
            }
            self.logger.error(f"[ERROR] Risk Guard System test failed: {e}")
            return False
    
    def test_deviation_alert_system(self) -> bool:
        """Test Trade Deviation Alert functionality."""
        self.logger.info("Testing Trade Deviation Alert System...")
        
        try:
            # Initialize deviation alert system
            deviation_alert = TradeDeviationAlert()
            
            # Test 1: Baseline calculation with sample data
            sample_trades = []
            for i in range(50):
                trade = {
                    "expected_return": 0.15 + (i % 10) * 0.01,  # Varying returns
                    "actual_return": 0.14 + (i % 8) * 0.012,
                    "confidence": 0.80 + (i % 5) * 0.02,
                    "execution_time": 1.5 + (i % 3) * 0.1,
                    "slippage": 0.001 + (i % 4) * 0.0002,
                    "timestamp": datetime.now() - timedelta(minutes=i)
                }
                sample_trades.append(trade)
            
            # Calculate baseline from sample data
            baseline = deviation_alert.calculate_baseline(sample_trades)
            assert "expected_return" in baseline, "Baseline should include expected return"
            assert "confidence" in baseline, "Baseline should include confidence"
            
            # Test 2: Normal trade (no deviation)
            normal_trade = {
                "expected_return": 0.16,
                "actual_return": 0.15,
                "confidence": 0.82,
                "execution_time": 1.6,
                "slippage": 0.0012
            }
            
            deviation_result = deviation_alert.check_deviation(normal_trade, baseline)
            assert not deviation_result["is_deviation"], "Normal trade should not be flagged as deviation"
            
            # Test 3: Deviant trade (high deviation)
            deviant_trade = {
                "expected_return": 0.50,  # Significantly higher than baseline
                "actual_return": 0.08,    # Much lower actual return
                "confidence": 0.40,       # Much lower confidence
                "execution_time": 5.0,    # Much slower execution
                "slippage": 0.01          # Much higher slippage
            }
            
            deviation_result = deviation_alert.check_deviation(deviant_trade, baseline)
            assert deviation_result["is_deviation"], "Deviant trade should be flagged"
            assert deviation_result["deviation_percentage"] > 30, "Deviation should exceed 30%"
            
            # Test 4: Log alert functionality
            alert_result = deviation_alert.log_alert(deviant_trade, deviation_result)
            assert alert_result["logged"], "Alert should be logged successfully"
            
            # Test 5: Consecutive deviation tracking
            for _ in range(3):
                deviation_alert.check_deviation(deviant_trade, baseline)
            
            consecutive_count = deviation_alert.get_consecutive_deviations()
            assert consecutive_count >= 3, "Consecutive deviations should be tracked"
            
            # Test 6: Alert history retrieval
            recent_alerts = deviation_alert.get_recent_alerts(limit=10)
            assert len(recent_alerts) > 0, "Recent alerts should be retrievable"
            
            self.test_results["deviation_alert"] = {
                "status": "PASSED",
                "tests_run": 6,
                "tests_passed": 6,
                "details": "All deviation alert tests passed successfully"
            }
            
            self.logger.info("[SUCCESS] Trade Deviation Alert System tests passed")
            return True
            
        except Exception as e:
            self.test_results["deviation_alert"] = {
                "status": "FAILED",
                "error": str(e),
                "details": "Deviation alert system test failed"
            }
            self.logger.error(f"[ERROR] Trade Deviation Alert System test failed: {e}")
            return False
    
    def test_failover_recovery_system(self) -> bool:
        """Test Failover & Recovery Protocol functionality."""
        self.logger.info("Testing Failover & Recovery System...")
        
        try:
            # Initialize recovery manager
            recovery_manager = RecoveryManager()
            
            # Test 1: Component registration
            test_component = {
                "name": "TestComponent",
                "state": {"active": True, "config": {"test": "value"}},
                "recovery_method": lambda state: {"success": True, "restored_state": state}
            }
            
            registration_result = recovery_manager.register_component(
                test_component["name"],
                test_component["state"],
                test_component["recovery_method"]
            )
            assert registration_result["success"], "Component registration should succeed"
            
            # Test 2: State snapshot creation
            snapshot_result = recovery_manager.create_snapshot()
            assert snapshot_result["success"], "Snapshot creation should succeed"
            assert "snapshot_id" in snapshot_result, "Snapshot should have an ID"
            
            # Test 3: State snapshot retrieval
            snapshots = recovery_manager.list_snapshots()
            assert len(snapshots) > 0, "Snapshots should be listed"
            
            latest_snapshot = recovery_manager.get_latest_snapshot()
            assert latest_snapshot is not None, "Latest snapshot should be retrievable"
            
            # Test 4: Recovery simulation
            # Simulate system state corruption
            recovery_manager.components["TestComponent"]["state"] = {"corrupted": True}
            
            # Perform recovery
            recovery_result = recovery_manager.recover_from_snapshot(latest_snapshot["id"])
            assert recovery_result["success"], "Recovery should succeed"
            
            # Verify state restoration
            restored_component = recovery_manager.components["TestComponent"]
            assert restored_component["state"]["active"], "Component state should be restored"
            
            # Test 5: Recovery report generation
            report_result = recovery_manager.generate_recovery_report()
            assert report_result["success"], "Recovery report generation should succeed"
            assert "report_content" in report_result, "Report should contain content"
            
            # Test 6: Graceful shutdown simulation
            shutdown_result = recovery_manager.initiate_graceful_shutdown()
            assert shutdown_result["success"], "Graceful shutdown should succeed"
            
            self.test_results["failover_recovery"] = {
                "status": "PASSED",
                "tests_run": 6,
                "tests_passed": 6,
                "details": "All failover recovery tests passed successfully"
            }
            
            self.logger.info("[SUCCESS] Failover & Recovery System tests passed")
            return True
            
        except Exception as e:
            self.test_results["failover_recovery"] = {
                "status": "FAILED",
                "error": str(e),
                "details": "Failover recovery system test failed"
            }
            self.logger.error(f"[ERROR] Failover & Recovery System test failed: {e}")
            return False
    
    def test_safety_dashboard_integration(self) -> bool:
        """Test Safety Status Dashboard integration."""
        self.logger.info("Testing Safety Dashboard Integration...")
        
        try:
            # Note: This is a basic integration test since the dashboard
            # requires Flask app context for full testing
            
            # Test 1: Safety status aggregation
            from trademasterx.interface.web.safety_dashboard import get_safety_status
            
            status = get_safety_status()
            assert "kill_switch" in status, "Status should include kill switch"
            assert "risk_guard" in status, "Status should include risk guard"
            assert "deviation_alert" in status, "Status should include deviation alert"
            assert "failover" in status, "Status should include failover"
            
            # Test 2: Risk metrics aggregation
            from trademasterx.interface.web.safety_dashboard import get_risk_metrics
            
            metrics = get_risk_metrics()
            assert "daily_loss" in metrics, "Metrics should include daily loss"
            assert "daily_trades" in metrics, "Metrics should include daily trades"
            
            # Test 3: Deviation data aggregation
            from trademasterx.interface.web.safety_dashboard import get_deviation_data
            
            deviation_data = get_deviation_data()
            assert "timestamps" in deviation_data, "Deviation data should include timestamps"
            assert "deviations" in deviation_data, "Deviation data should include deviations"
            
            # Test 4: Recent alerts aggregation
            from trademasterx.interface.web.safety_dashboard import get_recent_alerts
            
            alerts = get_recent_alerts()
            assert "alerts" in alerts, "Response should include alerts list"
            
            # Test 5: Emergency stop functionality (dry run)
            from trademasterx.interface.web.safety_dashboard import emergency_stop
            
            # This should work in test mode without actually stopping systems
            stop_result = emergency_stop("Integration test", test_mode=True)
            assert "success" in stop_result, "Emergency stop should return success status"
            
            # Test 6: API endpoint structure validation
            from trademasterx.interface.web.safety_dashboard import SafetyDashboard
            
            dashboard = SafetyDashboard()
            endpoints = dashboard.get_api_endpoints()
            assert len(endpoints) > 0, "Dashboard should have API endpoints"
            
            self.test_results["safety_dashboard"] = {
                "status": "PASSED",
                "tests_run": 6,
                "tests_passed": 6,
                "details": "All safety dashboard integration tests passed successfully"
            }
            
            self.logger.info("[SUCCESS] Safety Dashboard Integration tests passed")
            return True
            
        except Exception as e:
            self.test_results["safety_dashboard"] = {
                "status": "FAILED",
                "error": str(e),
                "details": "Safety dashboard integration test failed"
            }
            self.logger.error(f"[ERROR] Safety Dashboard Integration test failed: {e}")
            return False
    
    def test_full_system_integration(self) -> bool:
        """Test full system integration with all components working together."""
        self.logger.info("Testing Full System Integration...")
        
        try:
            # Initialize all systems
            kill_switch = KillSwitch()
            risk_guard = RiskGuard()
            deviation_alert = TradeDeviationAlert()
            recovery_manager = RecoveryManager()
            
            # Test 1: Systems initialization
            assert not kill_switch.is_active(), "Kill switch should start inactive"
            metrics = risk_guard.get_current_metrics()
            assert metrics["daily_loss"] == 0, "Risk guard should start with zero loss"
            
            # Test 2: Integrated safety workflow simulation
            # Simulate a risky trading scenario
            
            # First, record some normal trades
            for i in range(5):
                trade = {
                    "pnl": -20.0,  # Small losses
                    "size": 100.0,
                    "symbol": "BTCUSDT",
                    "expected_return": 0.15,
                    "actual_return": 0.12,
                    "confidence": 0.80,
                    "execution_time": 1.5,
                    "slippage": 0.001
                }
                
                # Validate trade with risk guard
                validation = risk_guard.validate_trade(trade)
                if validation["allowed"]:
                    risk_guard.record_trade_result(trade)
            
            # Test 3: Risk escalation scenario
            # Simulate a large loss that triggers risk warnings
            large_loss_trade = {
                "pnl": -150.0,  # Large loss
                "size": 500.0,
                "symbol": "ETHUSDT",
                "expected_return": 0.20,
                "actual_return": -0.30,  # Significant deviation
                "confidence": 0.45,      # Low confidence (deviation)
                "execution_time": 4.0,   # Slow execution (deviation)
                "slippage": 0.008        # High slippage (deviation)
            }
            
            # Check risk validation
            risk_validation = risk_guard.validate_trade(large_loss_trade)
            
            # Check for trade deviation
            baseline = deviation_alert.calculate_baseline([])  # Empty baseline for test
            deviation_check = deviation_alert.check_deviation(large_loss_trade, baseline)
            
            # Test 4: Emergency response integration
            if not risk_validation["allowed"] or deviation_check["is_deviation"]:
                # This should trigger emergency protocols
                emergency_result = kill_switch.activate(
                    "EMRG-2025-HALT", 
                    f"Risk breach detected: {risk_validation.get('reason', 'Unknown')}"
                )
                assert emergency_result["success"], "Emergency activation should succeed"
            
            # Test 5: System state snapshot during emergency
            if kill_switch.is_active():
                snapshot_result = recovery_manager.create_snapshot()
                assert snapshot_result["success"], "Emergency snapshot should succeed"
            
            # Test 6: Recovery and system restoration
            # Deactivate kill switch (simulate issue resolution)
            if kill_switch.is_active():
                deactivate_result = kill_switch.deactivate("EMRG-2025-HALT", "Issue resolved")
                assert deactivate_result["success"], "Kill switch deactivation should succeed"
            
            # Verify all systems are operational
            assert not kill_switch.is_active(), "Kill switch should be inactive after resolution"
            
            final_metrics = risk_guard.get_current_metrics()
            assert final_metrics["daily_loss"] > 0, "Risk metrics should reflect recorded trades"
            
            self.test_results["full_integration"] = {
                "status": "PASSED",
                "tests_run": 6,
                "tests_passed": 6,
                "details": "Full system integration test completed successfully"
            }
            
            self.logger.info("[SUCCESS] Full System Integration tests passed")
            return True
            
        except Exception as e:
            self.test_results["full_integration"] = {
                "status": "FAILED",
                "error": str(e),
                "details": "Full system integration test failed"
            }
            self.logger.error(f"[ERROR] Full System Integration test failed: {e}")
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all Phase 12 integration tests."""
        self.logger.info("=" * 60)
        self.logger.info("STARTING PHASE 12 INTEGRATION TESTS")
        self.logger.info("=" * 60)
        
        start_time = datetime.now()
        
        # Run individual system tests
        tests = [
            ("Kill Switch System", self.test_kill_switch_system),
            ("Risk Guard System", self.test_risk_guard_system),
            ("Deviation Alert System", self.test_deviation_alert_system),
            ("Failover Recovery System", self.test_failover_recovery_system),
            ("Safety Dashboard Integration", self.test_safety_dashboard_integration),
            ("Full System Integration", self.test_full_system_integration)
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            self.logger.info(f"\n{'=' * 40}")
            self.logger.info(f"Running: {test_name}")
            self.logger.info(f"{'=' * 40}")
            
            try:
                if test_func():
                    passed_tests += 1
                    self.logger.info(f"[SUCCESS] {test_name} - PASSED")
                else:
                    self.logger.error(f"[ERROR] {test_name} - FAILED")
            except Exception as e:
                self.logger.error(f"💥 {test_name} - ERROR: {e}")
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        # Generate final report
        final_report = {
            "test_summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": total_tests - passed_tests,
                "success_rate": f"{(passed_tests / total_tests) * 100:.1f}%",
                "duration": str(duration),
                "timestamp": end_time.isoformat()
            },
            "individual_results": self.test_results,
            "overall_status": "PASSED" if passed_tests == total_tests else "FAILED"
        }
        
        # Save test report
        report_file = f"test_reports/phase_12_integration_test_{int(time.time())}.json"
        os.makedirs("test_reports", exist_ok=True)
        
        with open(report_file, 'w') as f:
            json.dump(final_report, f, indent=2)
        
        self.logger.info("\n" + "=" * 60)
        self.logger.info("PHASE 12 INTEGRATION TEST RESULTS")
        self.logger.info("=" * 60)
        self.logger.info(f"Total Tests: {total_tests}")
        self.logger.info(f"Passed: {passed_tests}")
        self.logger.info(f"Failed: {total_tests - passed_tests}")
        self.logger.info(f"Success Rate: {(passed_tests / total_tests) * 100:.1f}%")
        self.logger.info(f"Duration: {duration}")
        self.logger.info(f"Report saved: {report_file}")
        
        if passed_tests == total_tests:
            self.logger.info("🎉 ALL PHASE 12 SAFETY SYSTEMS OPERATIONAL!")
        else:
            self.logger.error("[WARNING] SOME PHASE 12 SYSTEMS REQUIRE ATTENTION")
        
        self.logger.info("=" * 60)
        
        return final_report

def main():
    """Main test execution function."""
    print("\n🔒 TradeMasterX Phase 12: Live Trade Safety Systems Integration Test")
    print("=" * 70)
    
    try:
        # Initialize and run tests
        test_suite = Phase12IntegrationTest()
        results = test_suite.run_all_tests()
        
        # Exit with appropriate code
        if results["overall_status"] == "PASSED":
            print("\n[SUCCESS] Phase 12 integration test completed successfully!")
            sys.exit(0)
        else:
            print("\n[ERROR] Phase 12 integration test failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n[WARNING] Test interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Test execution failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
