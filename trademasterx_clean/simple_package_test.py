#!/usr/bin/env python3
"""
Simple test to verify the TradeMasterX production package works correctly
"""

import sys
import os

# Add package to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'package'))

def test_package_structure():
    """Test that package structure exists"""
    package_dir = os.path.join(os.path.dirname(__file__), 'package')
    
    required_dirs = [
        'trademasterx',
        'trademasterx/core',
        'trademasterx/interface',
        'trademasterx/interface/cli',
        'trademasterx/interface/assistant'
    ]
    
    for dir_path in required_dirs:
        full_path = os.path.join(package_dir, dir_path)
        if os.path.exists(full_path):
            print(f"✅ {dir_path}")
        else:
            print(f"❌ {dir_path}")
            return False
    
    return True

def test_imports():
    """Test that core imports work"""
    try:
        # Test basic imports
        from trademasterx.core.kill_switch import KillSwitch
        print("✅ KillSwitch import successful")
        
        from trademasterx.core.safety_dashboard import SafetyDashboard
        print("✅ SafetyDashboard import successful")
        
        from trademasterx.interface.cli.cli import TradeMasterXCLI
        print("✅ CLI import successful")
        
        from trademasterx.interface.assistant.command_assistant import CommandAssistant
        print("✅ CommandAssistant import successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality"""
    try:
        from trademasterx.core.kill_switch import KillSwitch
        
        # Test kill switch creation
        ks = KillSwitch()
        status = ks.get_status()
        print(f"✅ Kill switch status: {status['kill_switch_active']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        return False

def main():
    """Run all tests"""
    print(" TradeMasterX 2.0 Production Package Test")
    print("=" * 50)
    
    tests = [
        ("Package Structure", test_package_structure),
        ("Core Imports", test_imports),
        ("Basic Functionality", test_basic_functionality)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Testing {test_name}...")
        if test_func():
            print(f"✅ {test_name} PASSED")
            passed += 1
        else:
            print(f"❌ {test_name} FAILED")
    
    print("\n" + "=" * 50)
    print(f"📊 TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - Package is ready for production!")
        return True
    else:
        print("⚠️  Some tests failed - package needs attention")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
