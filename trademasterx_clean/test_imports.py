#!/usr/bin/env python3
"""Test imports for master_bot.py"""

import sys
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent.absolute()
sys.path.append(str(current_dir))

def test_import(module_name, import_statement):
    try:
        exec(import_statement)
        print(f"✅ {module_name}: OK")
        return True
    except Exception as e:
        print(f"❌ {module_name}: {e}")
        return False

def main():
    print("Testing imports for master_bot.py...")
    print("=" * 50)
    
    # Test standard library imports
    test_import("asyncio", "import asyncio")
    test_import("json", "import json") 
    test_import("logging", "import logging")
    test_import("signal", "import signal")
    test_import("sys", "import sys")
    test_import("datetime", "from datetime import datetime, timedelta")
    test_import("pathlib", "from pathlib import Path")
    test_import("typing", "from typing import Dict, List, Optional, Any, Union")
    test_import("threading", "import threading")
    test_import("time", "import time")
    
    print("\nTesting TradeMasterX imports...")
    print("-" * 30)
    
    # Test TradeMasterX imports
    test_import("ConfigLoader", "from trademasterx.config.config_loader import ConfigLoader")
    test_import("BotRegistry", "from trademasterx.core.bot_registry import BotRegistry")
    test_import("ScoringEngine", "from trademasterx.core.scoring import ScoringEngine")
    test_import("SafetyController", "from trademasterx.core.safety_controller import SafetyController")
    test_import("LearningPhaseController", "from trademasterx.core.learning_phase_controller import LearningPhaseController")
    
    print("\nTesting direct file execution...")
    print("-" * 30)
    
    try:
        # Try to execute the file directly
        with open("trademasterx/core/master_bot.py", "r") as f:
            code = f.read()
        
        # Create a test environment
        test_globals = {}
        exec(code, test_globals)
        
        if 'MasterBot' in test_globals:
            print("✅ MasterBot class found in executed code")
        else:
            print("❌ MasterBot class not found in executed code")
            print("Available names:", [name for name in test_globals.keys() if not name.startswith('_')])
            
    except Exception as e:
        print(f"❌ File execution failed: {e}")

if __name__ == "__main__":
    main()
