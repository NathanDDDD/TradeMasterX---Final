#!/usr/bin/env python3
"""
Simple import verification test for TradeMasterX 2.0
"""

import sys
import os

def test_core_imports():
    """Test core module imports"""
    print("Testing core imports...")
    
    try:
        import trademasterx
        print("OK: trademasterx")
    except ImportError as e:
        print(f"FAIL: trademasterx - {e}")
        return False
    
    try:
        from trademasterx.config import config_loader
        print("OK: trademasterx.config")
    except ImportError as e:
        print(f"FAIL: trademasterx.config - {e}")
    
    try:
        from trademasterx.core import bot_registry
        print("OK: trademasterx.core")
    except ImportError as e:
        print(f"FAIL: trademasterx.core - {e}")
    
    try:
        from trademasterx.bots import analytics
        print("OK: trademasterx.bots")
    except ImportError as e:
        print(f"FAIL: trademasterx.bots - {e}")
    
    try:
        from trademasterx.interface import assistant
        print("OK: trademasterx.interface")
    except ImportError as e:
        print(f"FAIL: trademasterx.interface - {e}")
    
    return True

def test_command_assistant_import():
    """Test command assistant import specifically"""
    print("\nTesting command assistant import...")
    
    try:
        from trademasterx.interface.assistant.command_assistant import CommandAssistant, NaturalLanguageParser
        print("OK: CommandAssistant and NaturalLanguageParser imported successfully")
        
        # Test instantiation
        parser = NaturalLanguageParser()
        print("OK: NaturalLanguageParser instantiated")
        
        assistant = CommandAssistant()
        print("OK: CommandAssistant instantiated")
        
        return True
    except ImportError as e:
        print(f"FAIL: Command assistant import - {e}")
        return False
    except Exception as e:
        print(f"FAIL: Command assistant instantiation - {e}")
        return False

def test_main_app_import():
    """Test main app import"""
    print("\nTesting main app import...")
    
    try:
        from main_app import TradeMasterXApp
        print("OK: TradeMasterXApp imported successfully")
        
        # Test instantiation
        app = TradeMasterXApp()
        print("OK: TradeMasterXApp instantiated")
        
        return True
    except ImportError as e:
        print(f"FAIL: Main app import - {e}")
        return False
    except Exception as e:
        print(f"FAIL: Main app instantiation - {e}")
        return False

def main():
    """Main test function"""
    print("TradeMasterX 2.0 Import Verification")
    print("=" * 40)
    
    success = True
    
    # Test core imports
    if not test_core_imports():
        success = False
    
    # Test command assistant
    if not test_command_assistant_import():
        success = False
    
    # Test main app
    if not test_main_app_import():
        success = False
    
    print("\n" + "=" * 40)
    if success:
        print("All imports successful!")
    else:
        print("Some imports failed.")
    
    return success

if __name__ == "__main__":
    main() 