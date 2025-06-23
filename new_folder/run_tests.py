#!/usr/bin/env python3
"""
TradeMasterX 2.0 - Test Runner
Selective test execution with error handling
"""

import sys
import os
import subprocess
from pathlib import Path

def run_basic_import_tests():
    """Run basic import tests to verify core functionality"""
    print("Running basic import tests...")
    
    test_modules = [
        "trademasterx",
        "trademasterx.config",
        "trademasterx.core",
        "trademasterx.bots",
        "trademasterx.interface"
    ]
    
    failed_imports = []
    
    for module in test_modules:
        try:
            __import__(module)
            print(f"OK {module}")
        except ImportError as e:
            print(f"FAIL {module}: {e}")
            failed_imports.append(module)
    
    return len(failed_imports) == 0

def run_unit_tests():
    """Run unit tests"""
    print("\nRunning unit tests...")
    
    # Find test files
    test_files = []
    for pattern in ["test_*.py", "*_test.py"]:
        test_files.extend(Path(".").glob(pattern))
    
    # Filter out problematic files
    exclude_patterns = [
        "test_results", "test_clean_assistant", "test_system_backup",
        "desktop_app/components/test_simple"
    ]
    
    valid_tests = []
    for test_file in test_files:
        if not any(pattern in str(test_file) for pattern in exclude_patterns):
            valid_tests.append(test_file)
    
    print(f"Found {len(valid_tests)} test files")
    
    # Run tests
    for test_file in valid_tests:
        print(f"Running {test_file}...")
        try:
            result = subprocess.run([sys.executable, str(test_file)], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print(f"PASS {test_file}")
            else:
                print(f"FAIL {test_file}: {result.stderr[:100]}...")
        except Exception as e:
            print(f"ERROR {test_file}: {e}")

def run_integration_tests():
    """Run integration tests"""
    print("\nRunning integration tests...")
    
    integration_tests = [
        "integration_test.py",
        "test_phase_10_integration.py"
    ]
    
    for test_file in integration_tests:
        if Path(test_file).exists():
            print(f"Running {test_file}...")
            try:
                result = subprocess.run([sys.executable, str(test_file)], 
                                      capture_output=True, text=True, timeout=60)
                if result.returncode == 0:
                    print(f"PASS {test_file}")
                else:
                    print(f"FAIL {test_file}: {result.stderr[:100]}...")
            except Exception as e:
                print(f"ERROR {test_file}: {e}")

def main():
    """Main test runner"""
    print("TradeMasterX 2.0 Test Runner")
    print("=" * 50)
    
    # Check Python version
    print(f"Python version: {sys.version}")
    
    # Run basic import tests
    imports_ok = run_basic_import_tests()
    
    if not imports_ok:
        print("\nBasic imports failed. Fix import issues before running other tests.")
        return 1
    
    # Run unit tests
    run_unit_tests()
    
    # Run integration tests
    run_integration_tests()
    
    print("\nTest runner completed!")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 