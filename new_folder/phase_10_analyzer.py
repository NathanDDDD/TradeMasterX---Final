#!/usr/bin/env python3
"""
TradeMasterX 2.0 - Phase 10 Bot Performance Analyzer
Track and analyze bot performance during the learning loop
"""

import asyncio
import sys
import os
import json
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import logging

# Add the trademasterx package to the path
current_dir = Path(__file__).parent.absolute()
sys.path.append(str(current_dir))

from trademasterx.config.config_loader import ConfigLoader
from trademasterx.core.phase10_optimizer import Phase10Optimizer

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/phase_10_learning.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("Phase10Analyzer")

async def analyze_bot_performance():
    """Analyze bot performance from logs and CSV data"""
    logger.info("=" * 80)
    logger.info("🔍 PHASE 10: BOT PERFORMANCE ANALYSIS")
    logger.info("=" * 80)
      # Load configuration
    config_loader = ConfigLoader()
    system_config = config_loader.load_system_config("trademasterx/config/system.yaml")
    
    # Load Phase 10 specific configuration
    try:
        phase10_config = config_loader.load_yaml_config("trademasterx/config/phase_10.yaml")
        # Merge configurations with phase10 taking precedence
        config = {**system_config, **phase10_config}
        logger.info("✅ Loaded Phase 10 specific configuration")
    except Exception as e:
        logger.warning(f"⚠️ Could not load Phase 10 config: {e}")
        logger.warning("⚠️ Using system configuration instead")
        config = system_config
    
    # Initialize optimizer
    optimizer = Phase10Optimizer(config)
    
    # Check for trade data
    data_dir = Path("data/performance")
    if not data_dir.exists():
        logger.error("❌ No performance data directory found")
        return False
    
    # Look for trade log files
    trade_files = list(data_dir.glob("trades_*.csv"))
    if not trade_files:
        logger.error("❌ No trade logs found")
        return False
    
    # Process the most recent trade file
    recent_trade_file = max(trade_files, key=lambda p: p.stat().st_mtime)
    logger.info(f"📊 Processing trade data from: {recent_trade_file}")
    
    # Read trade data
    try:
        trades_df = pd.read_csv(recent_trade_file)
        logger.info(f"📈 Found {len(trades_df)} trades to analyze")
        
        # Process each trade
        for _, trade in trades_df.iterrows():
            trade_data = {
                'timestamp': trade.get('timestamp', datetime.now().isoformat()),
                'symbol': trade.get('symbol', 'BTCUSDT'),
                'signal': trade.get('signal', 'buy'),
                'price': trade.get('price', 0),
                'actual_return': trade.get('actual_return', 0),
                'confidence': trade.get('confidence', 0)
            }
            
            # Record in optimizer
            optimizer.record_trade_outcome(trade_data)
            
        # Update metrics
        metrics = optimizer.update_bot_metrics()
        logger.info(f"✅ Updated performance metrics for {len(metrics['trade_accuracy'])} bots")
        
        # Generate report
        report = optimizer.generate_bot_report()
        logger.info(f"📋 Generated performance report")
        logger.info(f"   Win Rate: {report['system']['win_rate']:.2%}")
        logger.info(f"   Avg Return: {report['system']['avg_system_return']:.4%}")
        logger.info(f"   Total Trades: {report['system']['total_trades']}")
        
        if report['system']['best_performing_bot']:
            logger.info(f"   Best Bot: {report['system']['best_performing_bot']}")
        
        # Find underperforming bots
        underperforming = optimizer.identify_underperforming_bots()
        if underperforming:
            logger.warning(f"⚠️ Identified {len(underperforming)} underperforming bots: {', '.join(underperforming)}")
        else:
            logger.info("✅ All bots performing within acceptable parameters")
        
        # Export top configurations
        top_configs = optimizer.export_top_configurations()
        if top_configs:
            logger.info(f"💾 Exported top configurations to configs/live_candidates.yaml")
        
        # Print system readiness
        logger.info(f"🚦 System Readiness Score: {report['system']['readiness_score']}%")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Analysis failed: {e}")
        return False

async def monitor_trade_data():
    """Continuously monitor trade data and update analysis"""
    logger.info("🔄 Starting continuous trade monitoring")
    
    check_interval = 300  # 5 minutes
    
    try:
        while True:
            success = await analyze_bot_performance()
            
            if success:
                logger.info(f"✅ Analysis complete - next check in {check_interval//60} minutes")
            else:
                logger.warning(f"⚠️ Analysis failed - will retry in {check_interval//60} minutes")
                
            await asyncio.sleep(check_interval)
    
    except KeyboardInterrupt:
        logger.info("🛑 Monitoring stopped by user")
    except Exception as e:
        logger.error(f"❌ Monitoring error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--monitor":
        # Run continuous monitoring
        asyncio.run(monitor_trade_data())
    else:
        # Run a single analysis
        asyncio.run(analyze_bot_performance())
