from trademasterx.core.masterbot import MasterBot
from trademasterx.core.config import Config
from trademasterx.core.memory import Memory
from trademasterx.utils.mini_log import log_event, get_last_events

def main():
    config = Config('TradeMasterX/config.yaml')
    memory = Memory('TradeMasterX/memory.json')
    log_event('Loaded config')
    print("Loaded config:", config.data)
    
    bot = MasterBot()
    log_event('MasterBot initialized with AI assistant and emergency control')
    
    # Test emergency control
    print("\n=== Emergency Control Test ===")
    status = bot.get_system_status()
    print("System status:", status)
    
    # Test emergency stop
    emergency_result = bot.emergency_stop()
    print("Emergency stop result:", emergency_result)
    
    # Test signal aggregation (should be blocked)
    sample_data = {
        'price': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113],
        'volume': [200, 210, 220, 230, 240, 250, 260, 270, 280, 290, 300, 310, 320, 330],
        'news': ['Market is bullish today', 'Record high reached'],
        'sentiment': ['positive', 'bullish rally'],
    }
    log_event('Sample data prepared')
    
    # This should be blocked by emergency stop
    results = bot.aggregate_signals(sample_data)
    print("Signals (should be blocked):", results)
    
    # Reset emergency stop
    reset_result = bot.reset_emergency_stop()
    print("Reset result:", reset_result)
    
    # Now signals should work
    results = bot.aggregate_signals(sample_data)
    log_event('Signals aggregated')
    print("\n=== Analyzer Results ===")
    for name, result in results.items():
        print(f"{name}: {result}")
        memory.log_signal({name: result})
        log_event(f'Logged signal: {name}: {result}')
    
    # Test AI assistant
    print("\n=== AI Assistant Test ===")
    ai_advice = bot.get_ai_advice(sample_data, "What's the best strategy for this market data?")
    print("AI Advice:", ai_advice)
    log_event(f'AI advice requested: {ai_advice[:50]}...')
    
    print("\nSignals logged to memory.")
    log_event('Signals logged to memory')
    
    print("\n=== Last 10 Log Events ===")
    for line in get_last_events(10):
        print(line.strip())

if __name__ == "__main__":
    main() 