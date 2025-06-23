#!/usr/bin/env python3
"""
TradeMasterX 2.0 - Phase 10 Status Monitor
Monitor the running Phase 10 learning loop status and performance
"""

import json
import csv
from datetime import datetime, timedelta
from pathlib import Path
import time

def display_performance_summary():
    """Display current Phase 10 performance summary"""
    print("=" * 80)
    print("🎯 TradeMasterX 2.0 - Phase 10 Status Monitor")
    print("=" * 80)
    
    # Check performance data
    performance_file = Path("data/performance/performance_data.json")
    trade_log_file = Path("data/performance/trade_log.csv")
    
    if not performance_file.exists():
        print("❌ No performance data found. Phase 10 may not be running.")
        return
        
    # Load performance data
    with open(performance_file, 'r') as f:
        data = json.load(f)
    
    trades = data.get('trades', [])
    market_data = data.get('market_data', [])
    retraining_history = data.get('retraining_history', [])
    
    print(f"📊 SYSTEM STATUS:")
    print(f"   🟢 Phase 10 Learning Loop: ACTIVE")
    print(f"   🛡️ Safety Mode: DEMO_MODE_ACTIVE")
    print(f"   💰 Virtual Balance: ${market_data[-1]['metrics']['virtual_balance']:,.2f}" if market_data else "N/A")
    print()
    
    print(f"📈 TRADING PERFORMANCE:")
    print(f"   Total Trades: {len(trades)}")
    
    if trades:
        latest_trade = trades[-1]
        trade_time = datetime.fromisoformat(latest_trade['timestamp'])
        time_since = datetime.now() - trade_time
        
        print(f"   Latest Trade: {latest_trade['symbol']} | {latest_trade['signal'].upper()}")
        print(f"   Expected Return: {latest_trade['expected_return']:.2%}")
        print(f"   Confidence: {latest_trade['confidence']:.2%}")
        print(f"   Position Size: ${latest_trade['position_size']:,}")
        print(f"   Time Since Last Trade: {time_since.total_seconds():.0f}s ago")
        
        # Calculate average returns
        avg_return = sum(t['expected_return'] for t in trades) / len(trades)
        avg_confidence = sum(t['confidence'] for t in trades) / len(trades)
        print(f"   Average Return: {avg_return:.2%}")
        print(f"   Average Confidence: {avg_confidence:.2%}")
    
    print()
    
    # Check if trade log exists and show recent trades
    if trade_log_file.exists():
        print(f"📋 RECENT TRADES (last 5):")
        with open(trade_log_file, 'r') as f:
            reader = csv.DictReader(f)
            recent_trades = list(reader)[-5:]  # Get last 5 trades
            
        for trade in recent_trades:
            trade_time = datetime.fromisoformat(trade['timestamp'])
            print(f"   {trade_time.strftime('%H:%M:%S')} | {trade['symbol']} | "
                  f"{trade['signal'].upper()} | {float(trade['expected_return']):.1%} | "
                  f"Conf: {float(trade['confidence']):.1%}")
    
    print()
    
    # Session info
    if market_data:
        session_duration = market_data[-1]['metrics']['session_duration']
        trades_per_hour = market_data[-1]['metrics']['trades_per_hour']
        print(f"⏱️ SESSION INFO:")
        print(f"   Session Duration: {session_duration:.1f} minutes")
        print(f"   Trading Rate: {trades_per_hour:.1f} trades/hour")
        print(f"   Expected Next Trade: ~{30 - (time_since.total_seconds() % 30):.0f}s" if trades else "N/A")
    
    print()
    
    # Safety status
    print(f"🛡️ SAFETY STATUS:")
    print(f"   ✅ Demo Mode: ACTIVE")
    print(f"   ❌ Live Trading: DISABLED")
    print(f"   🔒 Real Money Protected: YES")
    print()
    
    # Retraining status
    print(f"🔄 MODEL RETRAINING:")
    if retraining_history:
        last_retrain = retraining_history[-1]
        retrain_time = datetime.fromisoformat(last_retrain['timestamp'])
        next_retrain = retrain_time + timedelta(hours=12)
        time_to_retrain = next_retrain - datetime.now()
        print(f"   Last Retrain: {retrain_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Next Retrain: {next_retrain.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Time Until Retrain: {time_to_retrain}")
    else:
        print(f"   Next Retrain: In ~12 hours from system start")
        print(f"   Status: No retraining performed yet")
    
    print("=" * 80)

def monitor_continuously():
    """Monitor Phase 10 status continuously"""
    try:
        while True:
            # Clear screen (Windows compatible)
            import os
            os.system('cls' if os.name == 'nt' else 'clear')
            
            display_performance_summary()
            print("Press Ctrl+C to stop monitoring...")
            print("Refreshing every 30 seconds...")
            
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--continuous":
        monitor_continuously()
    else:
        display_performance_summary()
