"""
TradeMasterX 2.0 - Quick Launch Script
Easy execution of the complete 7-day training system
"""

import sys
import subprocess
import os
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import numpy
        import pandas
        import aiohttp
        import requests
        print("✅ Core dependencies found")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_configuration():
    """Check if configuration files exist"""
    config_file = Path("config/master_config.json")
    if not config_file.exists():
        print("❌ Configuration file not found: config/master_config.json")
        return False
    
    print("✅ Configuration files found")
    return True

def main():
    """Main launch function"""
    print(" TradeMasterX 2.0 - Launch Verification")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        return False
    
    # Check configuration
    if not check_configuration():
        return False
    
    print("=" * 60)
    print("🎯 Ready to launch 7-day Bybit Testnet Training!")
    print("=" * 60)
    print("\nIMPORTANT: Before starting, ensure:")
    print("1. ✅ Bybit testnet API credentials configured")
    print("2. ✅ Internet connection stable")
    print("3. ✅ System will run for 168 hours (7 days)")
    print("4. ✅ Sufficient disk space for logs and reports")
    
    response = input("\nStart 7-day training session? (y/N): ")
    if response.lower() in ['y', 'yes']:
        print("\n Launching TradeMasterX 2.0...")
        os.chdir("launch")
        subprocess.run([sys.executable, "testnet_controller.py"])
    else:
        print("Launch cancelled.")
    
    return True

if __name__ == "__main__":
    main()
