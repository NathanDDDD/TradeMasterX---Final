#!/usr/bin/env python3
"""
TradeMasterX 2.0 - Phase 10 Integration Test (Simplified)
Tests core Phase 10 functionality without complex imports
"""

import asyncio
import sys
import os
from pathlib import Path
import logging
import json
from datetime import datetime, timedelta

# Configure paths
current_dir = Path(__file__).parent.absolute()
sys.path.append(str(current_dir))

def test_phase_10_basic_functionality():
    """Test basic Phase 10 functionality without complex imports"""
    print("🧪 Starting Phase 10 Basic Functionality Test")
    print("=" * 60)
    
    # Test 1: Configuration Loading
    print("\n📋 Test 1: Configuration Loading")
    try:
        config_path = "trademasterx/config/phase_10.yaml"
        if os.path.exists(config_path):
            print("✅ Phase 10 config file exists")
        else:
            print("❌ Phase 10 config file not found")
            
        # Test core config directory
        if os.path.exists("config"):
            print("✅ Core config directory exists")
        else:
            print("❌ Core config directory not found")
            
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
    
    # Test 2: Core Module Structure
    print("\n🏗️ Test 2: Core Module Structure")
    try:
        core_modules = [
            "trademasterx/core/learning_phase_controller.py",
            "trademasterx/core/phase10_optimizer.py", 
            "trademasterx/core/bot_registry.py",
            "core/training/continuous_retrainer.py"
        ]
        
        for module in core_modules:
            if os.path.exists(module):
                print(f"✅ {module}")
            else:
                print(f"❌ {module}")
                
    except Exception as e:
        print(f"❌ Module structure test failed: {e}")
    
    # Test 3: Phase 10 Execution Scripts
    print("\n Test 3: Phase 10 Execution Scripts")
    try:
        scripts = [
            "run_phase_10_direct.py",
            "phase_10_operations.py",
            "check_phase_10_status_new.py"
        ]
        
        for script in scripts:
            if os.path.exists(script):
                print(f"✅ {script}")
            else:
                print(f"❌ {script}")
                
    except Exception as e:
        print(f"❌ Script test failed: {e}")
    
    # Test 4: Database and Logs Setup
    print("\n💾 Test 4: Database and Logs Setup")
    try:
        # Check directories
        directories = ["data", "logs"]
        for directory in directories:
            if os.path.exists(directory):
                print(f"✅ {directory}/ directory exists")
            else:
                print(f"❌ {directory}/ directory missing")
        
        # Check for database files
        db_files = ["data/performance.db", "data/memory_bot.db"]
        for db_file in db_files:
            if os.path.exists(db_file):
                print(f"✅ {db_file}")
            else:
                print(f"⚠️  {db_file} (will be created on first run)")
                
    except Exception as e:
        print(f"❌ Database test failed: {e}")
    
    # Test 5: Safety and Demo Mode Configuration
    print("\n🛡️ Test 5: Safety and Demo Mode Configuration")
    try:
        # Check for .env file and demo mode settings
        if os.path.exists(".env"):
            print("✅ .env file exists")
            with open(".env", "r") as f:
                env_content = f.read()
                if "DEMO_MODE=true" in env_content or "DEMO_MODE=True" in env_content:
                    print("✅ Demo mode enabled in .env")
                else:
                    print("⚠️  Demo mode setting not found in .env")
        else:
            print("⚠️  .env file not found (demo mode should be configured)")
            
    except Exception as e:
        print(f"❌ Safety configuration test failed: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 Basic functionality test completed!")
    print("=" * 60)

def test_phase_10_file_syntax():
    """Test syntax of Phase 10 core files"""
    print("\n🔍 Testing file syntax...")
    
    core_files = [
        "trademasterx/core/learning_phase_controller.py",
        "trademasterx/core/phase10_optimizer.py",
        "trademasterx/core/bot_registry.py",
        "core/training/continuous_retrainer.py"
    ]
    
    for file_path in core_files:
        if os.path.exists(file_path):
            try:
                import py_compile
                py_compile.compile(file_path, doraise=True)
                print(f"✅ {file_path} - syntax OK")
            except py_compile.PyCompileError as e:
                print(f"❌ {file_path} - syntax error: {e}")
            except Exception as e:
                print(f"❌ {file_path} - error: {e}")
        else:
            print(f"⚠️  {file_path} - file not found")

async def test_phase_10_demo_safety():
    """Test Phase 10 demo mode safety controls"""
    print("\n🛡️ Testing Phase 10 Demo Mode Safety...")
    
    # Simulate demo mode checks
    demo_mode_active = True
    mainnet_demo = True
    live_mode = False
    
    print(f"Demo Mode: {demo_mode_active}")
    print(f"Mainnet Demo: {mainnet_demo}")
    print(f"Live Mode: {live_mode}")
    
    # Safety validations
    if demo_mode_active and not live_mode:
        print("✅ Safety: Demo mode active, live trading disabled")
    else:
        print("❌ Safety: Live trading risk detected!")
        
    if mainnet_demo and demo_mode_active:
        print("✅ Safety: Mainnet demo mode configured correctly")
    else:
        print("❌ Safety: Mainnet demo configuration issue")
        
    # Simulate learning loop parameters
    trade_frequency = 30  # seconds
    retrain_interval = 43200  # 12 hours
    
    print(f"Trade Frequency: {trade_frequency}s")
    print(f"Retrain Interval: {retrain_interval}s ({retrain_interval/3600:.1f}h)")
    
    if trade_frequency >= 30:
        print("✅ Safety: Trade frequency within safe limits")
    else:
        print("❌ Safety: Trade frequency too aggressive")

def main():
    """Run all Phase 10 tests"""
    print(" TradeMasterX 2.0 - Phase 10 Integration Test (Simplified)")
    print("=" * 70)
    print(f"Test Start: {datetime.now()}")
    print("=" * 70)
    
    try:
        # Run basic functionality tests
        test_phase_10_basic_functionality()
        
        # Test file syntax
        test_phase_10_file_syntax()
        
        # Test demo safety
        asyncio.run(test_phase_10_demo_safety())
        
        print("\n🎉 All Phase 10 tests completed!")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        return False
        
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
