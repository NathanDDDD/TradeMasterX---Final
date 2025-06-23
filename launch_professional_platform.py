#!/usr/bin/env python3
"""
TradeMasterX 2.0 - Professional Trading Platform Launcher
Simple launcher script for the unified trading interface
"""

import asyncio
import sys
import os
from professional_trading_platform import ProfessionalTradingPlatform

async def main():
    """Launch the professional trading platform"""
    print("🚀 TradeMasterX 2.0 - Professional Trading Platform")
    print("=" * 60)
    print("Starting unified trading interface...")
    print()
    
    try:
        platform = ProfessionalTradingPlatform()
        await platform.start()
    except KeyboardInterrupt:
        print("\n🛑 Professional Trading Platform stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting platform: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 