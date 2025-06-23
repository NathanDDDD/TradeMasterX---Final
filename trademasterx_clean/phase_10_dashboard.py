#!/usr/bin/env python3
"""
TradeMasterX 2.0 - Phase 10 Monitor Dashboard
"""

import os
import time
import subprocess
from datetime import datetime

def display_header():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("=" * 80)
    print("🎯 TradeMasterX 2.0 - PHASE 10 MONITOR DASHBOARD")
    print("=" * 80)
    print(f"⏱️ Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

def monitor_phase_10():
    # Run continuously until interrupted
    try:
        while True:
            display_header()
            
            # Run status check
            print("📊 Running Status Check...")
            subprocess.run(['python', 'check_phase_10_status.py'], check=False)
            
            print("\n" + "=" * 80)
            print("🔄 Refreshing in 30 seconds (Ctrl+C to exit)")
            print("=" * 80)
            
            # Wait before refreshing
            time.sleep(30)
    except KeyboardInterrupt:
        print("\n🛑 Monitor stopped by user")

def start_phase_10():
    display_header()
    print(" Starting Phase 10: Mainnet Demo Learning Loop")
    
    # Run in a separate process so we can monitor it
    process = subprocess.Popen(['python', 'run_phase_10_direct.py'], 
                              stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE,
                              text=True)
    
    print("⏳ Waiting for startup (10 seconds)...")
    time.sleep(10)
    
    # Check if process is still running
    if process.poll() is None:
        print("✅ Phase 10 started successfully (running in background)")
        return True
    else:
        stdout, stderr = process.communicate()
        print(f"❌ Phase 10 failed to start: {stderr}")
        print(f"Output: {stdout}")
        return False

if __name__ == "__main__":
    print("TradeMasterX 2.0 - Phase 10 Control Panel")
    print("1. Start Phase 10 Learning Loop")
    print("2. Monitor Phase 10 Status")
    print("3. Exit")
    
    choice = input("Enter your choice (1-3): ")
    
    if choice == '1':
        success = start_phase_10()
        if success:
            # Automatically start monitoring if Phase 10 started successfully
            print("🖥️ Starting monitor...")
            time.sleep(2)
            monitor_phase_10()
    elif choice == '2':
        monitor_phase_10()
    else:
        print("👋 Goodbye!")
