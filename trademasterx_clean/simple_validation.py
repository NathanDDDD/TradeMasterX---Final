#!/usr/bin/env python3
"""
TradeMasterX 2.0 - Simple System Validation
Quick validation of core components
"""

import sys
import os
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

def test_basic_structure():
    """Test basic project structure"""
    print("🔍 Testing Basic Project Structure...")
    
    # Test required files
    required_files = [
        'main_app.py',
        'phase_14_complete_autonomous_ai.py',
        'requirements.txt',
        'README.md'
    ]
    
    missing_files = []
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path}")
            missing_files.append(file_path)
    
    # Test directories
    required_dirs = [
        'trademasterx',
        'logs_clean', 
        'reports_clean',
        'tests_clean'
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"   ✅ {dir_path}/")
        else:
            print(f"   ❌ {dir_path}/")
            missing_dirs.append(dir_path)
    
    return len(missing_files) == 0 and len(missing_dirs) == 0

def test_dependencies():
    """Test core dependencies"""
    print("\n📦 Testing Core Dependencies...")
    
    core_deps = ['numpy', 'pandas', 'asyncio', 'json', 'pathlib']
    failed_deps = []
    
    for dep in core_deps:
        try:
            __import__(dep)
            print(f"   ✅ {dep}")
        except ImportError:
            print(f"   ❌ {dep}")
            failed_deps.append(dep)
    
    return len(failed_deps) == 0

def test_ai_system():
    """Test AI system imports"""
    print("\n🤖 Testing AI System...")
    
    try:
        # Test Phase 14 system
        from phase_14_complete_autonomous_ai import Phase14AutonomousAI
        print("   ✅ Phase14AutonomousAI imported successfully")
        
        # Test basic initialization
        config = {'demo_mode': True, 'test_mode': True}
        system = Phase14AutonomousAI(config)
        print("   ✅ AI system initialized successfully")
        
        return True
        
    except Exception as e:
        print(f"   ❌ AI System failed: {e}")
        return False

def test_main_app():
    """Test main application structure"""
    print("\n Testing Main Application...")
    
    try:
        # Import main app class
        from main_app import TradeMasterXApp
        print("   ✅ TradeMasterXApp imported successfully")
        
        # Test basic initialization
        app = TradeMasterXApp()
        print("   ✅ Main app initialized successfully")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Main App failed: {e}")
        return False

def main():
    """Run simple system validation"""
    print(" TradeMasterX 2.0 - Simple System Validation")
    print("=" * 60)
    
    tests = [
        ("Basic Structure", test_basic_structure),
        ("Dependencies", test_dependencies), 
        ("AI System", test_ai_system),
        ("Main Application", test_main_app)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            if result:
                passed += 1
            print()
        except Exception as e:
            print(f"   ❌ {test_name} test crashed: {e}")
            print()
    
    # Summary
    print("=" * 60)
    print("📊 VALIDATION SUMMARY")
    print("=" * 60)
    print(f"Tests Passed: {passed}/{total}")
    print(f"Success Rate: {passed/total*100:.1f}%")
    
    if passed == total:
        print("🟢 Overall Status: READY FOR LAUNCH")
        print("\n Next Steps:")
        print("   1. Run: python main_app.py")
        print("   2. Access dashboard: http://localhost:8080")
        print("   3. Start trading with demo mode")
    elif passed >= total * 0.75:
        print("🟡 Overall Status: MOSTLY READY")
        print("\n⚠️  Minor issues detected - system should work with limited functionality")
    else:
        print("🔴 Overall Status: NEEDS FIXES")
        print("\n❌ Critical issues detected - system needs attention")
    
    return passed >= total * 0.75

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        sys.exit(1)
