#!/usr/bin/env python3
"""
TradeMasterX 2.0 - Phase 10 Direct Runner (Simplified)
Direct execution of Phase 10 learning loop without complex dependencies
"""

import asyncio
import logging
import sys
import os
from pathlib import Path
from datetime import datetime

# Add current directory to path
current_dir = Path(__file__).parent.absolute()
sys.path.append(str(current_dir))

# Import our simplified controller
from phase_10_direct_controller import Phase10LearningController

def setup_logging():
    """Setup logging for Phase 10"""
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / f"phase_10_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger("Phase10Runner")

async def run_phase_10():
    """Run Phase 10 learning loop"""
    logger = setup_logging()
    
    logger.info("🎯 TradeMasterX 2.0 - Phase 10: Mainnet Demo Learning Loop (Direct)")
    logger.info("=" * 80)
    logger.info("🛡️ DEMO MODE ONLY - NO REAL MONEY TRADING")
    logger.info("🌐 Using simulated trading with virtual funds")
    logger.info("⚡ 30-second trading cycles")
    logger.info("🔄 12-hour model retraining intervals")
    logger.info("📊 Weekly performance reports")
    logger.info("=" * 80)
    
    # Load simplified configuration
    config = {
        'learning': {
            'trade_frequency': 30,  # 30 seconds
            'retrain_interval': 43200,  # 12 hours (in seconds)
            'weekly_report': True
        },
        'safety': {
            'confidence_threshold': 0.80,
            'min_return_threshold': 0.15,
            'max_position_size': 1000
        },
        'trading_mode': {
            'DEMO_MODE': True,
            'LIVE_MODE': False,
            'mainnet_demo': True
        }
    }
    
    logger.info(f"📋 Configuration:")
    logger.info(f"   DEMO_MODE: {config['trading_mode']['DEMO_MODE']}")
    logger.info(f"   LIVE_MODE: {config['trading_mode']['LIVE_MODE']}")
    logger.info(f"   Mainnet Demo: {config['trading_mode']['mainnet_demo']}")
    logger.info(f"   Trade Frequency: {config['learning']['trade_frequency']}s")
    logger.info(f"   Retrain Interval: {config['learning']['retrain_interval']}s ({config['learning']['retrain_interval']/3600:.1f}h)")
    
    # Safety checks
    if not config['trading_mode']['DEMO_MODE']:
        logger.error("❌ CRITICAL: DEMO_MODE is not enabled! Aborting for safety.")
        return False
        
    if config['trading_mode']['LIVE_MODE']:
        logger.error("❌ CRITICAL: LIVE_MODE is enabled! Aborting for safety.")
        return False
    
    logger.info("✅ Safety checks passed - proceeding with demo mode")
    logger.info("")
    
    try:
        # Initialize Phase 10 learning controller
        learning_controller = Phase10LearningController(config)
        
        logger.info(" Starting Phase 10 learning loop...")
        logger.info("Press Ctrl+C to stop gracefully")
        logger.info("")
        
        # Start the learning phase
        await learning_controller.start_learning_phase()
        
        logger.info("✅ Phase 10 learning loop completed successfully")
        return True
        
    except KeyboardInterrupt:
        logger.info("🛑 Manual shutdown requested")
        return True
        
    except Exception as e:
        logger.error(f"❌ Phase 10 failed: {e}")
        return False

def main():
    """Main entry point"""
    try:
        # Run the async Phase 10 function
        success = asyncio.run(run_phase_10())
        
        if success:
            print("\n🎉 Phase 10 completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Phase 10 failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Manual shutdown")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
