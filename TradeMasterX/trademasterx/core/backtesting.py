import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from trademasterx.utils.logger import get_logger
from trademasterx.utils.mini_log import log_event

class Backtester:
    """Backtesting engine for trading strategy simulation."""
    
    def __init__(self):
        self.logger = get_logger("Backtester")
        self.results = {}
    
    def run_backtest(self, strategy, data, initial_capital=10000):
        """Run a backtest simulation."""
        self.logger.info(f"Starting backtest with ${initial_capital} initial capital")
        log_event(f"Backtest started with ${initial_capital} initial capital")
        
        try:
            # Initialize portfolio
            portfolio = {
                'cash': initial_capital,
                'position': 0,
                'trades': [],
                'equity_curve': []
            }
            
            prices = data.get('price', [])
            if len(prices) < 10:
                return {"error": "Insufficient data for backtesting"}
            
            # Simulate trading
            for i in range(10, len(prices)):
                current_price = prices[i]
                signal = strategy.generate_signal(prices[:i+1])
                
                if signal == 'buy' and portfolio['cash'] > 0:
                    # Buy signal
                    shares = portfolio['cash'] / current_price
                    portfolio['position'] += shares
                    portfolio['cash'] = 0
                    portfolio['trades'].append({
                        'date': i,
                        'action': 'buy',
                        'price': current_price,
                        'shares': shares
                    })
                
                elif signal == 'sell' and portfolio['position'] > 0:
                    # Sell signal
                    portfolio['cash'] = portfolio['position'] * current_price
                    portfolio['trades'].append({
                        'date': i,
                        'action': 'sell',
                        'price': current_price,
                        'shares': portfolio['position']
                    })
                    portfolio['position'] = 0
                
                # Calculate current equity
                current_equity = portfolio['cash'] + (portfolio['position'] * current_price)
                portfolio['equity_curve'].append(current_equity)
            
            # Calculate final results
            final_equity = portfolio['equity_curve'][-1] if portfolio['equity_curve'] else initial_capital
            total_return = ((final_equity - initial_capital) / initial_capital) * 100
            
            self.results = {
                'initial_capital': initial_capital,
                'final_equity': round(final_equity, 2),
                'total_return': round(total_return, 2),
                'total_trades': len(portfolio['trades']),
                'max_equity': max(portfolio['equity_curve']) if portfolio['equity_curve'] else initial_capital,
                'min_equity': min(portfolio['equity_curve']) if portfolio['equity_curve'] else initial_capital,
                'trades': portfolio['trades']
            }
            
            self.logger.info(f"Backtest completed. Total return: {total_return:.2f}%")
            log_event(f"Backtest completed. Total return: {total_return:.2f}%")
            
            return self.results
            
        except Exception as e:
            self.logger.error(f"Backtest error: {e}")
            return {"error": str(e)}
    
    def get_results(self):
        """Get the latest backtest results."""
        return self.results

class SimpleStrategy:
    """Simple moving average crossover strategy for demonstration."""
    
    def __init__(self, short_window=5, long_window=10):
        self.short_window = short_window
        self.long_window = long_window
    
    def generate_signal(self, prices):
        """Generate buy/sell signals based on moving average crossover."""
        if len(prices) < self.long_window:
            return 'hold'
        
        prices_series = pd.Series(prices)
        short_ma = prices_series.rolling(window=self.short_window).mean().iloc[-1]
        long_ma = prices_series.rolling(window=self.long_window).mean().iloc[-1]
        
        if short_ma > long_ma:
            return 'buy'
        elif short_ma < long_ma:
            return 'sell'
        else:
            return 'hold' 