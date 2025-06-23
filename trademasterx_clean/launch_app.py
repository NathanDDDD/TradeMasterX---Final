#!/usr/bin/env python3
"""
TradeMasterX 2.0 - Simple Application Launcher
Starts the main application with proper error handling
"""

import sys
import os
import asyncio
from pathlib import Path

def check_environment():
    """Check if the environment is properly set up"""
    print("Checking environment...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("ERROR: Python 3.8+ required")
        return False
    
    # Check required directories
    required_dirs = ['logs', 'data', 'reports']
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"Created directory: {dir_name}")
    
    # Check configuration
    config_file = Path("trademasterx/config/system.yaml")
    if not config_file.exists():
        print("ERROR: Configuration file not found")
        return False
    
    print("Environment check passed")
    return True

def import_main_app():
    """Import the main application"""
    try:
        from main_app import TradeMasterXApp
        return TradeMasterXApp
    except ImportError as e:
        print(f"ERROR: Failed to import main app: {e}")
        return None

async def run_application():
    """Run the main application"""
    print("Starting TradeMasterX 2.0...")
    
    # Check environment
    if not check_environment():
        return False
    
    # Import main app
    TradeMasterXApp = import_main_app()
    if not TradeMasterXApp:
        return False
    
    try:
        # Create and run the application
        app = TradeMasterXApp()
        await app.run()
        return True
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
        return True
    except Exception as e:
        print(f"ERROR: Application failed to start: {e}")
        return False

def main():
    """Main launcher function"""
    print("TradeMasterX 2.0 Launcher")
    print("=" * 30)
    
    try:
        # Run the application
        success = asyncio.run(run_application())
        
        if success:
            print("Application completed successfully")
            return 0
        else:
            print("Application failed to start")
            return 1
            
    except Exception as e:
        print(f"Launcher error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 