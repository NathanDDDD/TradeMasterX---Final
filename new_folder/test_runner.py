#!/usr/bin/env python3
"""Simple test runner to debug phase_tester.py"""

import sys
import os
import traceback

def main():
    print("=" * 60)
    print("SIMPLE TEST RUNNER")
    print("=" * 60)
    
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    print(f"Python path: {sys.path[:3]}")
    
    try:
        print("\n🧪 Attempting to import phase_tester...")
        from phase_tester import PhaseTester
        print("✅ Successfully imported PhaseTester")
        
        print("\n🧪 Creating PhaseTester instance...")
        tester = PhaseTester()
        print("✅ Successfully created PhaseTester")
        
        print("\n🧪 Running tests...")
        success = tester.run_all_tests()
        print(f"\n✅ Tests completed. Success: {success}")
        
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        print(f"❌ Exception type: {type(e).__name__}")
        print("\n📋 Full traceback:")
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    result = main()
    sys.exit(0 if result else 1)
