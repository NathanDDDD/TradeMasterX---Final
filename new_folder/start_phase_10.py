#!/usr/bin/env python3
"""
TradeMasterX 2.0 - Phase 10 Launcher
Start mainnet demo learning loop with safety controls
"""

import asyncio
import sys
from pathlib import Path

# Add the trademasterx package to the path
sys.path.insert(0, str(Path(__file__).parent))

from trademasterx.core.master_bot import MasterBot
from trademasterx.config.config_loader import ConfigLoader


async def start_phase_10():
    """Start Phase 10: Mainnet Demo Learning Loop"""
    
    print("🎯 TradeMasterX 2.0 - Phase 10: Mainnet Demo Learning Loop")
    print("=" * 80)
    print("🛡️ DEMO MODE ONLY - NO REAL MONEY TRADING")
    print("🌐 Using Bybit mainnet API with demo account")
    print("⚡ 30-second trading cycles with virtual funds")
    print("🔄 12-hour model retraining intervals")
    print("📊 Weekly performance reports")
    print("=" * 80)
    
    try:
        # Load system configuration
        config_loader = ConfigLoader()
        config = config_loader.load_system_config("trademasterx/config/system.yaml")
        
        print(f"📋 Configuration loaded:")
        print(f"   Environment: {config.get('system', {}).get('environment', 'unknown')}")
        print(f"   DEMO_MODE: {config.get('system', {}).get('trading_mode', {}).get('DEMO_MODE', 'unknown')}")
        print(f"   LIVE_MODE: {config.get('system', {}).get('trading_mode', {}).get('LIVE_MODE', 'unknown')}")
        print(f"   Mainnet Demo: {config.get('system', {}).get('trading_mode', {}).get('mainnet_demo', 'unknown')}")
        print("")
        
        # Verify safety settings
        if not config.get('system', {}).get('trading_mode', {}).get('DEMO_MODE', True):
            print("❌ CRITICAL: DEMO_MODE is not enabled! Aborting for safety.")
            return False
            
        if config.get('system', {}).get('trading_mode', {}).get('LIVE_MODE', False):
            print("❌ CRITICAL: LIVE_MODE is enabled! Aborting for safety.")
            return False
            
        print("✅ Safety checks passed - DEMO_MODE confirmed")
        print("")
        
        # Initialize MasterBot
        print("🤖 Initializing MasterBot...")
        master_bot = MasterBot(config.get('system', {}))
        
        # Start the learning phase
        print(" Starting mainnet demo learning loop...")
        success = await master_bot.start_learning_phase()
        
        if success:
            print("✅ Phase 10 learning loop completed successfully!")
            return True
        else:
            print("❌ Phase 10 learning loop failed!")
            return False
            
    except KeyboardInterrupt:
        print("\n🛑 Manual shutdown requested...")
        return True
        
    except Exception as e:
        print(f"❌ Phase 10 startup failed: {e}")
        return False


async def main():
    """Main entry point"""
    success = await start_phase_10()
    
    if success:
        print("\n🎉 Phase 10 session completed!")
    else:
        print("\n💥 Phase 10 session failed!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
