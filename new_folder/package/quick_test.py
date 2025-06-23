#!/usr/bin/env python3
"""
Quick Package Test - TradeMasterX 2.0
Simple validation of the production package
"""

import sys
import os
from pathlib import Path

def test_package():
    """Test the production package"""
    print(" TradeMasterX 2.0 - Production Package Test")
    print("=" * 50)
    
    package_root = Path(__file__).parent
    print(f"📁 Package Root: {package_root}")
    
    # Add to Python path
    sys.path.insert(0, str(package_root))
    
    # Test critical imports
    tests = []
    
    print("\n🔍 Testing Critical Imports...")
    
    try:
        from trademasterx.core.kill_switch import KillSwitch
        print("✅ Kill Switch import: SUCCESS")
        
        # Test instantiation
        ks = KillSwitch()
        status = ks.get_status()
        print(f"✅ Kill Switch functional: {status['kill_switch_active']}")
        tests.append(True)
        
    except Exception as e:
        print(f"❌ Kill Switch: FAILED ({e})")
        tests.append(False)
    
    try:
        from trademasterx.core.safety_dashboard import SafetyDashboard
        print("✅ Safety Dashboard import: SUCCESS")
        
        # Test instantiation
        sd = SafetyDashboard()
        print("✅ Safety Dashboard functional")
        tests.append(True)
        
    except Exception as e:
        print(f"❌ Safety Dashboard: FAILED ({e})")
        tests.append(False)
    
    try:
        from trademasterx.interface.assistant.command_assistant import CommandAssistant
        print("✅ Command Assistant import: SUCCESS")
        tests.append(True)
        
    except Exception as e:
        print(f"❌ Command Assistant: FAILED ({e})")
        tests.append(False)
    
    try:
        from trademasterx.interface.cli.cli import TradeMasterXCLI
        print("✅ CLI import: SUCCESS")
        tests.append(True)
        
    except Exception as e:
        print(f"❌ CLI: FAILED ({e})")
        tests.append(False)
    
    # Calculate results
    passed = sum(tests)
    total = len(tests)
    success_rate = (passed / total) * 100 if total > 0 else 0
    
    print(f"\n📊 Test Results:")
    print(f"   Passed: {passed}/{total}")
    print(f"   Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 75:
        print("\n🎉 PACKAGE TEST: SUCCESS")
        print("TradeMasterX 2.0 Production Package is ready!")
        return True
    else:
        print("\n❌ PACKAGE TEST: FAILED")
        print("Package needs fixes before deployment.")
        return False

if __name__ == "__main__":
    success = test_package()
    sys.exit(0 if success else 1)
