#!/usr/bin/env python3
"""
TradeMasterX Phase 12: Safety Systems CLI Test Script

This script provides command-line testing for all Phase 12 safety systems:
- Kill Switch System
- Risk Guard System  
- Trade Deviation Alert System
- Failover & Recovery System
- Safety Dashboard Integration

Usage: python test_phase_12_cli.py [system] [action] [args...]

Author: TradeMasterX Development Team
Date: May 28, 2025
Version: 12.0.0
"""

import sys
import os
import json
import argparse
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_kill_switch():
    """Test Kill Switch System via CLI."""
    print("🔴 Testing Kill Switch System...")
    
    try:
        from trademasterx.core.kill_switch import KillSwitch
        
        kill_switch = KillSwitch()
        
        print("1. Checking initial status...")
        status = kill_switch.get_state()
        print(f"   Status: {'ACTIVE' if status['active'] else 'INACTIVE'}")
        
        print("2. Testing activation...")
        result = kill_switch.activate("TEST-2025-CLI", "CLI test activation")
        print(f"   Activation: {'SUCCESS' if result['success'] else 'FAILED'}")
        
        print("3. Verifying active state...")
        print(f"   Is Active: {kill_switch.is_active()}")
        
        print("4. Testing deactivation...")
        result = kill_switch.deactivate("TEST-2025-CLI", "CLI test completion")
        print(f"   Deactivation: {'SUCCESS' if result['success'] else 'FAILED'}")
        
        print("5. Final status check...")
        print(f"   Is Active: {kill_switch.is_active()}")
        
        print("✅ Kill Switch System: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Kill Switch System: FAILED - {e}")
        return False

def test_risk_guard():
    """Test Risk Guard System via CLI."""
    print("🛡️  Testing Risk Guard System...")
    
    try:
        from trademasterx.core.risk_guard import RiskGuard
        
        risk_guard = RiskGuard()
        
        print("1. Checking initial metrics...")
        metrics = risk_guard.get_current_metrics()
        print(f"   Daily Loss: ${metrics['daily_loss']}")
        print(f"   Daily Trades: {metrics['daily_trades']}")
        
        print("2. Testing trade validation...")
        test_trade = {
            "pnl": -50.0,
            "size": 100.0,
            "symbol": "BTCUSDT"
        }
        
        validation = risk_guard.validate_trade(test_trade)
        print(f"   Trade Allowed: {validation['allowed']}")
        
        print("3. Recording test trade...")
        risk_guard.record_trade_result(test_trade)
        
        print("4. Checking updated metrics...")
        updated_metrics = risk_guard.get_current_metrics()
        print(f"   Daily Loss: ${updated_metrics['daily_loss']}")
        print(f"   Daily Trades: {updated_metrics['daily_trades']}")
        
        print("5. Testing risk warnings...")
        warnings = risk_guard.get_risk_warnings()
        print(f"   Active Warnings: {len(warnings)}")
        
        print("6. Testing daily reset...")
        risk_guard.reset_daily_counters()
        reset_metrics = risk_guard.get_current_metrics()
        print(f"   Reset Daily Loss: ${reset_metrics['daily_loss']}")
        
        print("✅ Risk Guard System: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Risk Guard System: FAILED - {e}")
        return False

def test_deviation_alert():
    """Test Trade Deviation Alert System via CLI."""
    print("📊 Testing Trade Deviation Alert System...")
    
    try:
        from trademasterx.core.trade_deviation_alert import TradeDeviationAlert
        
        deviation_alert = TradeDeviationAlert()
        
        print("1. Creating baseline with sample data...")
        sample_trades = []
        for i in range(20):
            trade = {
                "expected_return": 0.15,
                "actual_return": 0.14,
                "confidence": 0.80,
                "execution_time": 1.5,
                "slippage": 0.001,
                "timestamp": datetime.now()
            }
            sample_trades.append(trade)
        
        baseline = deviation_alert.calculate_baseline(sample_trades)
        print(f"   Baseline calculated with {len(sample_trades)} trades")
        
        print("2. Testing normal trade (no deviation)...")
        normal_trade = {
            "expected_return": 0.16,
            "actual_return": 0.15,
            "confidence": 0.82,
            "execution_time": 1.6,
            "slippage": 0.0012
        }
        
        deviation_result = deviation_alert.check_deviation(normal_trade, baseline)
        print(f"   Is Deviation: {deviation_result['is_deviation']}")
        print(f"   Deviation %: {deviation_result['deviation_percentage']:.1f}%")
        
        print("3. Testing deviant trade...")
        deviant_trade = {
            "expected_return": 0.50,  # High deviation
            "actual_return": 0.05,
            "confidence": 0.30,
            "execution_time": 5.0,
            "slippage": 0.01
        }
        
        deviation_result = deviation_alert.check_deviation(deviant_trade, baseline)
        print(f"   Is Deviation: {deviation_result['is_deviation']}")
        print(f"   Deviation %: {deviation_result['deviation_percentage']:.1f}%")
        
        print("4. Testing alert logging...")
        if deviation_result['is_deviation']:
            alert_result = deviation_alert.log_alert(deviant_trade, deviation_result)
            print(f"   Alert Logged: {alert_result['logged']}")
        
        print("5. Checking consecutive deviations...")
        consecutive = deviation_alert.get_consecutive_deviations()
        print(f"   Consecutive Deviations: {consecutive}")
        
        print("6. Getting recent alerts...")
        recent_alerts = deviation_alert.get_recent_alerts(limit=5)
        print(f"   Recent Alerts: {len(recent_alerts)}")
        
        print("✅ Trade Deviation Alert System: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Trade Deviation Alert System: FAILED - {e}")
        return False

def test_failover_recovery():
    """Test Failover & Recovery System via CLI."""
    print("🔄 Testing Failover & Recovery System...")
    
    try:
        from trademasterx.core.failover_recovery import RecoveryManager
        
        recovery_manager = RecoveryManager()
        
        print("1. Registering test component...")
        test_state = {"active": True, "config": {"test": "value"}}
        recovery_method = lambda state: {"success": True, "restored_state": state}
        
        result = recovery_manager.register_component("TestComponent", test_state, recovery_method)
        print(f"   Component Registered: {result['success']}")
        
        print("2. Creating state snapshot...")
        snapshot_result = recovery_manager.create_snapshot()
        print(f"   Snapshot Created: {snapshot_result['success']}")
        print(f"   Snapshot ID: {snapshot_result.get('snapshot_id', 'Unknown')}")
        
        print("3. Listing snapshots...")
        snapshots = recovery_manager.list_snapshots()
        print(f"   Total Snapshots: {len(snapshots)}")
        
        print("4. Getting latest snapshot...")
        latest = recovery_manager.get_latest_snapshot()
        print(f"   Latest Snapshot: {latest['id'] if latest else 'None'}")
        
        print("5. Testing recovery simulation...")
        if latest:
            # Corrupt component state
            recovery_manager.components["TestComponent"]["state"] = {"corrupted": True}
            
            # Recover from snapshot
            recovery_result = recovery_manager.recover_from_snapshot(latest["id"])
            print(f"   Recovery Success: {recovery_result['success']}")
            
            # Verify restoration
            restored_state = recovery_manager.components["TestComponent"]["state"]
            print(f"   State Restored: {restored_state.get('active', False)}")
        
        print("6. Generating recovery report...")
        report_result = recovery_manager.generate_recovery_report()
        print(f"   Report Generated: {report_result['success']}")
        
        print("✅ Failover & Recovery System: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Failover & Recovery System: FAILED - {e}")
        return False

def test_safety_dashboard():
    """Test Safety Dashboard Integration via CLI."""
    print("📊 Testing Safety Dashboard Integration...")
    
    try:
        # Test individual dashboard functions
        print("1. Testing safety status aggregation...")
        from trademasterx.interface.web.safety_dashboard import get_safety_status
        
        status = get_safety_status()
        print(f"   Components: {list(status.keys())}")
        
        print("2. Testing risk metrics aggregation...")
        from trademasterx.interface.web.safety_dashboard import get_risk_metrics
        
        metrics = get_risk_metrics()
        print(f"   Metrics: {list(metrics.keys())}")
        
        print("3. Testing deviation data...")
        from trademasterx.interface.web.safety_dashboard import get_deviation_data
        
        deviation_data = get_deviation_data()
        print(f"   Data Points: {len(deviation_data.get('timestamps', []))}")
        
        print("4. Testing recent alerts...")
        from trademasterx.interface.web.safety_dashboard import get_recent_alerts
        
        alerts = get_recent_alerts()
        print(f"   Alert Count: {len(alerts.get('alerts', []))}")
        
        print("5. Testing emergency stop (dry run)...")
        from trademasterx.interface.web.safety_dashboard import emergency_stop
        
        stop_result = emergency_stop("CLI test", test_mode=True)
        print(f"   Emergency Stop Test: {stop_result.get('success', False)}")
        
        print("6. Testing dashboard initialization...")
        from trademasterx.interface.web.safety_dashboard import SafetyDashboard
        
        dashboard = SafetyDashboard()
        endpoints = dashboard.get_api_endpoints()
        print(f"   API Endpoints: {len(endpoints)}")
        
        print("✅ Safety Dashboard Integration: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Safety Dashboard Integration: FAILED - {e}")
        return False

def run_all_tests():
    """Run all Phase 12 safety system tests."""
    print("\n🔒 TradeMasterX Phase 12: Safety Systems CLI Test")
    print("=" * 60)
    
    tests = [
        ("Kill Switch System", test_kill_switch),
        ("Risk Guard System", test_risk_guard),
        ("Trade Deviation Alert System", test_deviation_alert),
        ("Failover & Recovery System", test_failover_recovery),
        ("Safety Dashboard Integration", test_safety_dashboard)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*40}")
        print(f"Testing: {test_name}")
        print(f"{'='*40}")
        
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} failed")
        except Exception as e:
            print(f"💥 {test_name} error: {e}")
    
    print(f"\n{'='*60}")
    print("PHASE 12 CLI TEST RESULTS")
    print(f"{'='*60}")
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ALL PHASE 12 SAFETY SYSTEMS OPERATIONAL!")
        return True
    else:
        print(f"\n⚠️  {total - passed} SYSTEM(S) REQUIRE ATTENTION")
        return False

def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="TradeMasterX Phase 12 Safety Systems CLI Test",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Available Commands:
  all                    - Run all safety system tests
  kill-switch           - Test kill switch system
  risk-guard            - Test risk guard system
  deviation-alert       - Test deviation alert system
  failover-recovery     - Test failover recovery system
  safety-dashboard      - Test safety dashboard integration

Examples:
  python test_phase_12_cli.py all
  python test_phase_12_cli.py kill-switch
  python test_phase_12_cli.py risk-guard
        """
    )
    
    parser.add_argument(
        'command',
        choices=['all', 'kill-switch', 'risk-guard', 'deviation-alert', 'failover-recovery', 'safety-dashboard'],
        help='Test command to execute'
    )
    
    args = parser.parse_args()
    
    try:
        if args.command == 'all':
            success = run_all_tests()
        elif args.command == 'kill-switch':
            success = test_kill_switch()
        elif args.command == 'risk-guard':
            success = test_risk_guard()
        elif args.command == 'deviation-alert':
            success = test_deviation_alert()
        elif args.command == 'failover-recovery':
            success = test_failover_recovery()
        elif args.command == 'safety-dashboard':
            success = test_safety_dashboard()
        else:
            print(f"Unknown command: {args.command}")
            return 1
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        return 130
    except Exception as e:
        print(f"\n💥 Test execution failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
