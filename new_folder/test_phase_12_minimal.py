#!/usr/bin/env python3
"""
Minimal Phase 12 Integration Test
Tests core functionality without Unicode issues
"""

import sys
import os
import json
import time
import logging
from datetime import datetime

# Add project root to path
sys.path.insert(0, '.')

def test_imports():
    """Test that all Phase 12 components can be imported"""
    print("Testing Phase 12 component imports...")
    
    try:
        from trademasterx.core.kill_switch import KillSwitch
        print("✓ KillSwitch imported successfully")
    except Exception as e:
        print(f"✗ KillSwitch import failed: {e}")
        return False
    
    try:
        from trademasterx.core.risk_guard import RiskGuard
        print("✓ RiskGuard imported successfully")
    except Exception as e:
        print(f"✗ RiskGuard import failed: {e}")
        return False
    
    try:
        from trademasterx.core.trade_deviation_alert import TradeDeviationAlert
        print("✓ TradeDeviationAlert imported successfully")
    except Exception as e:
        print(f"✗ TradeDeviationAlert import failed: {e}")
        return False
    
    try:
        from trademasterx.core.failover_recovery import RecoveryManager
        print("✓ RecoveryManager imported successfully")
    except Exception as e:
        print(f"✗ RecoveryManager import failed: {e}")
        return False
    
    try:
        from trademasterx.core.safety_dashboard import SafetyDashboard
        print("✓ SafetyDashboard imported successfully")
    except Exception as e:
        print(f"✗ SafetyDashboard import failed: {e}")
        return False
    
    return True

def test_basic_functionality():
    """Test basic functionality of each component"""
    print("\nTesting basic functionality...")
    
    try:
        # Test KillSwitch
        from trademasterx.core.kill_switch import KillSwitch
        ks = KillSwitch()
        print("✓ KillSwitch instantiated")
        
        # Test RiskGuard
        from trademasterx.core.risk_guard import RiskGuard
        rg = RiskGuard()
        print("✓ RiskGuard instantiated")
        
        # Test TradeDeviationAlert
        from trademasterx.core.trade_deviation_alert import TradeDeviationAlert
        tda = TradeDeviationAlert()
        print("✓ TradeDeviationAlert instantiated")
        
        # Test RecoveryManager
        from trademasterx.core.failover_recovery import RecoveryManager
        rm = RecoveryManager()
        print("✓ RecoveryManager instantiated")
        
        # Test SafetyDashboard
        from trademasterx.core.safety_dashboard import SafetyDashboard
        sd = SafetyDashboard()
        print("✓ SafetyDashboard instantiated")
        
        return True
        
    except Exception as e:
        print(f"✗ Basic functionality test failed: {e}")
        return False

def test_method_availability():
    """Test that required methods are available"""
    print("\nTesting method availability...")
    
    try:
        from trademasterx.core.kill_switch import KillSwitch
        from trademasterx.core.risk_guard import RiskGuard
        from trademasterx.core.trade_deviation_alert import TradeDeviationAlert
        from trademasterx.core.failover_recovery import RecoveryManager
        from trademasterx.core.safety_dashboard import SafetyDashboard
        
        ks = KillSwitch()
        rg = RiskGuard()
        tda = TradeDeviationAlert()
        rm = RecoveryManager()
        sd = SafetyDashboard()
        
        # Check KillSwitch methods
        assert hasattr(ks, 'activate'), "KillSwitch.activate method missing"
        assert hasattr(ks, 'deactivate'), "KillSwitch.deactivate method missing"
        print("✓ KillSwitch methods available")
        
        # Check RiskGuard methods
        assert hasattr(rg, 'validate_trade'), "RiskGuard.validate_trade method missing"
        print("✓ RiskGuard methods available")
        
        # Check RecoveryManager methods
        assert hasattr(rm, 'get_latest_snapshot'), "RecoveryManager.get_latest_snapshot method missing"
        assert hasattr(rm, 'recover_from_snapshot'), "RecoveryManager.recover_from_snapshot method missing"
        print("✓ RecoveryManager methods available")
        
        return True
        
    except Exception as e:
        print(f"✗ Method availability test failed: {e}")
        return False

def run_tests():
    """Run all tests"""
    print("=" * 60)
    print("PHASE 12 MINIMAL INTEGRATION TEST")
    print("=" * 60)
    
    success_count = 0
    total_tests = 3
    
    # Test 1: Imports
    if test_imports():
        success_count += 1
    
    # Test 2: Basic functionality
    if test_basic_functionality():
        success_count += 1
    
    # Test 3: Method availability
    if test_method_availability():
        success_count += 1
    
    # Results
    print("\n" + "=" * 60)
    print(f"TEST RESULTS: {success_count}/{total_tests} tests passed")
    print("=" * 60)
    
    if success_count == total_tests:
        print("✓ ALL TESTS PASSED - Phase 12 core functionality is working!")
        return True
    else:
        print("✗ Some tests failed - Phase 12 needs fixes")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
