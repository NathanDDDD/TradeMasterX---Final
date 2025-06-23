#!/usr/bin/env python3
"""
TradeMasterX Clean Launcher
Simple launcher for the cleaned project
"""

import sys
import os
import asyncio
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

async def main():
    """Main launcher function"""
    print("TradeMasterX Clean Project")
    print("=" * 30)
    
    # Check if main app exists
    if not (current_dir / "main_app_clean.py").exists():
        print("ERROR: main_app_clean.py not found!")
        return 1
    
    try:
        # Import the main app
        from main_app_clean import main as app_main
        
        # Run the async main function
        return await app_main()
    except ImportError as e:
        print(f"Import error: {e}")
        print("Try running: python main_app_clean.py")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 