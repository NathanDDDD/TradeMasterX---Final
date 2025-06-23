"""
Trade History Viewer Component
Displays and analyzes trade history data
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

class TradeHistoryViewer:
    """Trade history viewer and analytics"""
    
    def __init__(self, parent_dir: Path):
        self.parent_dir = parent_dir
        self.trade_log_file = parent_dir / "data" / "performance" / "trade_log.csv"
        self.data_dir = parent_dir / "data"
    
    def load_trade_data(self) -> Optional[pd.DataFrame]:
        """Load trade data from CSV file"""
        try:
            if self.trade_log_file.exists():
                df = pd.read_csv(self.trade_log_file)
                
                # Ensure required columns exist
                required_cols = ['timestamp', 'symbol', 'action', 'price', 'quantity']
                for col in required_cols:
                    if col not in df.columns:
                        st.warning(f"Missing column: {col}")
                        return self.generate_sample_data()
                
                # Parse timestamp
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                return df
            else:
                return self.generate_sample_data()
                
        except Exception as e:
            st.warning(f"Could not load trade data: {e}")
            return self.generate_sample_data()
    
    def generate_sample_data(self) -> pd.DataFrame:
        """Generate sample trade data for demonstration"""
        import random
        import numpy as np
        
        # Generate sample trades over the last 30 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        # Generate timestamps
        num_trades = 50
        timestamps = pd.date_range(start_date, end_date, periods=num_trades)
        
        # Sample symbols
        symbols = ['BTCUSD', 'ETHUSD', 'ADAUSD', 'SOLUSD', 'DOTUSD']
        
        trades = []
        current_price = 45000  # Starting BTC price
        
        for i, ts in enumerate(timestamps):
            # Random price movement
            price_change = random.uniform(-0.05, 0.05)
            current_price *= (1 + price_change)
            
            symbol = random.choice(symbols)
            action = random.choice(['BUY', 'SELL'])
            quantity = random.uniform(0.01, 0.5)
            confidence = random.uniform(0.6, 0.95)
            
            # Calculate return based on some logic
            if action == 'BUY':
                return_pct = random.uniform(-0.02, 0.04)  # Slight positive bias
            else:
                return_pct = random.uniform(-0.04, 0.02)  # Slight negative bias for sells
            
            trades.append({
                'timestamp': ts,
                'symbol': symbol,
                'action': action,
                'price': current_price * (1 + random.uniform(-0.1, 0.1)),
                'quantity': quantity,
                'confidence': confidence,
                'return_pct': return_pct,
                'strategy': random.choice(['momentum', 'mean_reversion', 'breakout']),
                'pnl': return_pct * current_price * quantity
            })
        
        return pd.DataFrame(trades)
    
    def calculate_metrics(self, df: pd.DataFrame) -> dict:
        """Calculate performance metrics from trade data"""
        if df.empty:
            return {}
        
        metrics = {}
        
        # Basic metrics
        metrics['total_trades'] = len(df)
        
        if 'return_pct' in df.columns:
            metrics['avg_return'] = df['return_pct'].mean()
            metrics['win_rate'] = (df['return_pct'] > 0).mean()
            metrics['best_trade'] = df['return_pct'].max()
            metrics['worst_trade'] = df['return_pct'].min()
            
            # Calculate cumulative return
            metrics['total_return'] = (1 + df['return_pct']).prod() - 1
            
            # Sharpe ratio approximation (assuming daily returns)
            if df['return_pct'].std() > 0:
                metrics['sharpe_ratio'] = df['return_pct'].mean() / df['return_pct'].std() * (252 ** 0.5)
            else:
                metrics['sharpe_ratio'] = 0
        
        if 'confidence' in df.columns:
            metrics['avg_confidence'] = df['confidence'].mean()
        
        if 'pnl' in df.columns:
            metrics['total_pnl'] = df['pnl'].sum()
            metrics['avg_pnl'] = df['pnl'].mean()
        
        return metrics
    
    def create_performance_chart(self, df: pd.DataFrame) -> go.Figure:
        """Create performance over time chart"""
        if df.empty or 'return_pct' not in df.columns:
            return go.Figure()
        
        # Calculate cumulative returns
        df_sorted = df.sort_values('timestamp')
        df_sorted['cumulative_return'] = (1 + df_sorted['return_pct']).cumprod() - 1
        
        fig = go.Figure()
        
        # Add cumulative return line
        fig.add_trace(go.Scatter(
            x=df_sorted['timestamp'],
            y=df_sorted['cumulative_return'] * 100,
            mode='lines',
            name='Cumulative Return (%)',
            line=dict(color='blue', width=2)
        ))
        
        fig.update_layout(
            title='Portfolio Performance Over Time',
            xaxis_title='Date',
            yaxis_title='Cumulative Return (%)',
            hovermode='x unified'
        )
        
        return fig
    
    def create_strategy_performance_chart(self, df: pd.DataFrame) -> go.Figure:
        """Create strategy performance comparison"""
        if df.empty or 'strategy' not in df.columns:
            return go.Figure()
        
        # Group by strategy and calculate metrics
        strategy_perf = df.groupby('strategy').agg({
            'return_pct': ['mean', 'count'],
            'confidence': 'mean'
        }).round(4)
        
        strategy_perf.columns = ['avg_return', 'trade_count', 'avg_confidence']
        strategy_perf = strategy_perf.reset_index()
        
        fig = px.bar(
            strategy_perf,
            x='strategy',
            y='avg_return',
            title='Average Return by Strategy',
            color='avg_confidence',
            color_continuous_scale='Viridis'
        )
        
        fig.update_layout(
            xaxis_title='Strategy',
            yaxis_title='Average Return (%)',
            yaxis=dict(tickformat='.2%')
        )
        
        return fig
    
    def get_trade_distribution(self, df: pd.DataFrame) -> go.Figure:
        """Create trade return distribution histogram"""
        if df.empty or 'return_pct' not in df.columns:
            return go.Figure()
        
        fig = px.histogram(
            df,
            x='return_pct',
            title='Trade Return Distribution',
            nbins=20,
            color_discrete_sequence=['lightblue']
        )
        
        fig.update_layout(
            xaxis_title='Return (%)',
            yaxis_title='Number of Trades',
            xaxis=dict(tickformat='.1%')
        )
        
        # Add vertical line at 0
        fig.add_vline(x=0, line_dash="dash", line_color="red")
        
        return fig
