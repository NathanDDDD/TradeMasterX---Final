import time
from trademasterx.core.master_bot import MasterBot
from trademasterx.core.forms import PatternAnalyzer, IndicatorAnalyzer, SentimentAnalyzer, NewsAnalyzer, RLAgent, CopyTradingBot
from trademasterx.api.bybit_client import BybitClient
from trademasterx.config.config_loader import load_config
from trademasterx.utils.data_logger import DataLogger
from trademasterx.utils.retrainer import Retrainer

if __name__ == "__main__":
    config = load_config()
    logger = DataLogger()
    retrainer = Retrainer(logger)
    forms = [
        PatternAnalyzer(),
        IndicatorAnalyzer(),
        SentimentAnalyzer(),
        NewsAnalyzer(),
        RLAgent(),
        CopyTradingBot()
    ]
    bot = MasterBot(config, forms)
    bybit = BybitClient(config)

    while True:
        try:
            # Simulate getting market data and making a decision
            market_data = bybit.get_market_data('BTCUSDT')
            signals = bot.collect_signals(market_data)
            decision = bot.aggregate_signals(signals)
            print(f"Decision: {decision}")
            # Simulate trade execution and logging
            if decision['action'] in ['BUY', 'SELL']:
                entry_price = market_data['price']
                # Simulate exit after target profit (12-15%)
                target_profit = 0.13  # midpoint of 12-15%
                exit_price = entry_price * (1 + target_profit) if decision['action'] == 'BUY' else entry_price * (1 - target_profit)
                profit_loss = abs(exit_price - entry_price)
                duration = 60 * 60  # 1 hour in seconds (stub)
                bybit.place_order('BTCUSDT', decision['action'], 1)
                logger.log_trade('BTCUSDT', decision['action'], entry_price, exit_price, profit_loss, duration, signals)
                retrainer.record_trade()
            time.sleep(60)  # Wait 1 minute before next cycle
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(60) 