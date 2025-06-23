#!/usr/bin/env python3
"""Simple test script to debug Phase 11 imports"""

import sys
import os
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

print("=== Phase 11 Import Test ===")
print(f"Python version: {sys.version}")
print(f"Current directory: {current_dir}")
print(f"Python path: {sys.path[:3]}")

# Check directory structure
print("\n=== Directory Structure ===")
trademasterx_dir = current_dir / "trademasterx"
print(f"trademasterx exists: {trademasterx_dir.exists()}")

if trademasterx_dir.exists():
    optimizers_dir = trademasterx_dir / "optimizers"
    print(f"optimizers exists: {optimizers_dir.exists()}")
    
    if optimizers_dir.exists():
        phase11_dir = optimizers_dir / "phase_11"
        print(f"phase_11 exists: {phase11_dir.exists()}")
        
        if phase11_dir.exists():
            print(f"phase_11 contents: {list(phase11_dir.glob('*.py'))}")

# Test imports step by step
print("\n=== Testing Imports ===")

try:
    print("1. Importing trademasterx...")
    import trademasterx
    print("   ✅ trademasterx imported")
except Exception as e:
    print(f"   ❌ trademasterx import failed: {e}")

try:
    print("2. Importing trademasterx.optimizers...")
    from trademasterx import optimizers
    print("   ✅ optimizers imported")
except Exception as e:
    print(f"   ❌ optimizers import failed: {e}")

try:
    print("3. Importing trademasterx.optimizers.phase_11...")
    from trademasterx.optimizers import phase_11
    print("   ✅ phase_11 imported")
except Exception as e:
    print(f"   ❌ phase_11 import failed: {e}")
    import traceback
    traceback.print_exc()

try:
    print("4. Importing Phase11Controller...")
    from trademasterx.optimizers.phase_11.phase_11_controller import Phase11Controller
    print("   ✅ Phase11Controller imported")
    
    # Test initialization
    print("5. Testing initialization...")
    controller = Phase11Controller(data_dir="test_data", logs_dir="test_logs")
    print("   ✅ Phase11Controller initialized")
    
    # Test basic functionality
    print("6. Testing system status...")
    status = controller.get_system_status()
    print(f"   ✅ System status: {status['is_running']}")
    
except Exception as e:
    print(f"   ❌ Phase11Controller import/init failed: {e}")
    import traceback
    traceback.print_exc()

print("\n=== Test Complete ===")
