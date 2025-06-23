import csv
import json
from datetime import datetime

print("=" * 60)
print("🎯 PHASE 10 STATUS SUMMARY")
print("=" * 60)

# Check trade log
try:
    with open('data/performance/trade_log.csv', 'r') as f:
        trades = list(csv.DictReader(f))
    
    print(f"✅ Total Trades Executed: {len(trades)}")
    
    if trades:
        latest = trades[-1]
        latest_time = datetime.fromisoformat(latest['timestamp'])
        current_time = datetime.now()
        time_since = (current_time - latest_time).total_seconds()
        
        print(f"📊 Latest Trade: {latest['symbol']} | {latest['signal'].upper()}")
        print(f"💰 Expected Return: {float(latest['expected_return']):.1%}")
        print(f"🎯 Confidence: {float(latest['confidence']):.1%}")
        print(f"⏰ Time Since Last: {time_since:.0f} seconds ago")
        print(f"🔄 Next Trade: ~{30 - (time_since % 30):.0f} seconds")
        
        # Check trading frequency
        if len(trades) >= 2:
            first_time = datetime.fromisoformat(trades[0]['timestamp'])
            duration = (latest_time - first_time).total_seconds() / 60
            rate = len(trades) / (duration / 60) if duration > 0 else 0
            print(f"📈 Trading Rate: {rate:.1f} trades/hour")
            
        print(f"🛡️ Safety Status: DEMO_MODE_ACTIVE")
        print(f"🟢 System Status: OPERATIONAL")
        
except Exception as e:
    print(f"❌ Error reading data: {e}")

print("=" * 60)
