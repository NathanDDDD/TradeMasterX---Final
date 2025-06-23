#!/usr/bin/env python3
"""
TradeMasterX 2.0 - Phase 10 Direct Runner
Direct execution of the learning phase controller
"""

import sys
import os
import asyncio
from pathlib import Path

# Configure paths
current_dir = Path(__file__).parent.absolute()
sys.path.append(str(current_dir))

# Direct imports to avoid package issues
from trademasterx.config.config_loader import ConfigLoader
from trademasterx.core.safety_controller import SafetyController
from trademasterx.core.bot_registry import BotRegistry
from trademasterx.core.learning_phase_controller import LearningPhaseController

async def run_phase_10():
    print("🎯 TradeMasterX 2.0 - Phase 10: Mainnet Demo Learning Loop (Direct Runner)")
    print("=" * 80)
    print("🛡️ DEMO MODE ONLY - NO REAL MONEY TRADING")
    print("🌐 Using Bybit mainnet API with demo account")
    print("⚡ 30-second trading cycles with virtual funds")
    print("🔄 12-hour model retraining intervals")
    print("📊 Weekly performance reports")
    print("=" * 80)
    
    # Load configuration
    config_path = os.path.join(current_dir, "trademasterx", "config", "system.yaml")
    config_loader = ConfigLoader()
    config = config_loader.load_system_config(config_path)
    
    # Safety checks
    demo_mode = config.get('trading_mode', {}).get('DEMO_MODE', True)
    live_mode = config.get('trading_mode', {}).get('LIVE_MODE', False)
    mainnet_demo = config.get('trading_mode', {}).get('mainnet_demo', False)
    
    print(f"📋 Configuration loaded:")
    print(f"   DEMO_MODE: {demo_mode}")
    print(f"   LIVE_MODE: {live_mode}")
    print(f"   Mainnet Demo: {mainnet_demo}")
    
    if not demo_mode:
        print("❌ CRITICAL: DEMO_MODE is not enabled! Aborting for safety.")
        return False
        
    if live_mode:
        print("❌ CRITICAL: LIVE_MODE is enabled! Aborting for safety.")
        return False
    
    if not mainnet_demo:
        print("❌ CRITICAL: mainnet_demo is not enabled! Required for Phase 10.")
        return False
    
    # Initialize components directly
    print("🛡️ Initializing safety controller...")
    safety_controller = SafetyController(config)
    
    print("🤖 Initializing bot registry...")
    bot_registry = BotRegistry(config)
    
    print("🧠 Initializing learning phase controller...")
    learning_controller = LearningPhaseController(config, bot_registry)
    
    # Validate before starting
    if not safety_controller.validate_trading_request("START_LEARNING_PHASE"):
        print("❌ Safety validation failed - cannot start learning phase")
        return False
    
    # Start the learning phase
    print(" Starting mainnet demo learning loop...")
    try:
        await bot_registry.initialize_all_bots()
        await learning_controller.start_learning_phase()
        return True
    except Exception as e:
        print(f"❌ Learning phase failed: {e}")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(run_phase_10())
        if success:
            print("✅ Phase 10 learning loop completed successfully!")
            sys.exit(0)
        else:
            print("❌ Phase 10 learning loop failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Manual shutdown requested...")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(2)
