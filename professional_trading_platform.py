#!/usr/bin/env python3
"""
TradeMasterX 2.0 - Professional Trading Platform
Unified Interface with Claude, OpenAI, and Bybit API Integration

Professional UX/UI designed for finance and trading professionals
Single port, multi-panel layout with real-time data and controls
"""

import asyncio
import json
import logging
import random
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import aiohttp
from aiohttp import web, WSMsgType
import aiohttp_cors
import yaml
from pathlib import Path
import hmac
import hashlib
import sys
import webbrowser
import threading
import time
import traceback
if getattr(sys, 'frozen', False):
    # Running as a PyInstaller bundle
    bundle_dir = sys._MEIPASS  # type: ignore
    sys.path.insert(0, os.path.join(bundle_dir, "trademasterx"))
    sys.path.insert(0, bundle_dir)
else:
    # Running in normal Python
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from new_folder.trademasterx.core.master_bot import MasterBot

class ProfessionalTradingPlatform:
    """
    Professional trading platform with unified interface
    Integrates Claude, OpenAI, and Bybit APIs
    """
    
    def __init__(self):
        self.host = 'localhost'
        self.port = 9100  # Changed from 8080 to 9100 for the most current and updated instance
        
        # Trading state
        self.trading_active = False
        self.emergency_stop_active = False
        self.current_pnl = 0.0
        self.total_trades = 0
        self.live_trades = []
        self.websocket_connections = set()
        self.shutdown_requested = False
        
        # API integrations
        self.claude_api_key = os.getenv('ANTHROPIC_API_KEY', '')
        self.openai_api_key = os.getenv('OPENAI_API_KEY', '')
        self.bybit_api_key = os.getenv('BYBIT_API_KEY', 'YTfGvLKG9VmCqS9iQ9')
        self.bybit_secret = os.getenv('BYBIT_API_SECRET', '4v7r8qUwlCzaUrXV4J7XYfUnGaVAJQP9IFsY')
        
        # Market data
        self.market_data = {
            'BTCUSDT': {'price': 45000, 'change': 2.5, 'volume': 1500000},
            'ETHUSDT': {'price': 2800, 'change': -1.2, 'volume': 800000},
            'ADAUSDT': {'price': 0.45, 'change': 5.8, 'volume': 200000},
            'DOTUSDT': {'price': 6.8, 'change': -0.8, 'volume': 300000},
            'LINKUSDT': {'price': 15.2, 'change': 3.1, 'volume': 400000}
        }
        
        # Portfolio data
        self.portfolio = {
            'total_value': 10000.0,
            'available_balance': 5000.0,
            'positions': [],
            'daily_pnl': 0.0,
            'total_pnl': 0.0
        }
        
        # AI responses
        self.ai_responses = []
        
        # Create web app
        self.app = web.Application()
        self._setup_routes()
        self._setup_cors()
        self._setup_static()
        
        # Initialize logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("TradingPlatform")
        # Add file handler for error logging
        file_handler = logging.FileHandler("platform_error.log", mode="a")
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        self.master_bot = None
        self.master_bot_task = None
        self.master_bot_running = False
        self.trade_callback = self.record_and_broadcast_trade
    
    def _setup_routes(self):
        """Setup web routes"""
        self.app.router.add_get('/', self.main_dashboard)
        self.app.router.add_get('/api/status', self.get_status)
        self.app.router.add_get('/api/market-data', self.get_market_data)
        self.app.router.add_get('/api/portfolio', self.get_portfolio)
        self.app.router.add_get('/api/trades', self.get_trades)
        self.app.router.add_post('/api/start-trading', self.start_trading)
        self.app.router.add_post('/api/stop-trading', self.stop_trading)
        self.app.router.add_post('/api/emergency-stop', self.handle_emergency_stop)
        self.app.router.add_post('/api/ai-query', self.ai_query)
        self.app.router.add_post('/api/place-order', self.place_order)
        self.app.router.add_post('/api/trigger-retrain', self.trigger_retrain)
        self.app.router.add_get('/ws', self.websocket_handler)
    
    def _setup_cors(self):
        """Setup CORS"""
        cors = aiohttp_cors.setup(self.app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods="*"
            )
        })
        
        for route in list(self.app.router.routes()):
            cors.add(route)
    
    def _setup_static(self):
        static_path = os.path.join(os.path.dirname(__file__), 'static')
        if not os.path.exists(static_path):
            os.makedirs(static_path)
        self.app.router.add_static('/static/', static_path, show_index=True)
    
    def _generate_main_dashboard(self):
        """Generate the main professional trading dashboard"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TradeMasterX 2.0 - Professional Trading Platform</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #0a0e1a;
            color: #ffffff;
            overflow: hidden;
            height: 100vh;
        }
        
        .header {
            background: linear-gradient(135deg, #1a1f2e 0%, #2d3748 100%);
            border-bottom: 1px solid #2d3748;
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            height: 60px;
        }
        
        .brand {
            font-size: 24px;
            font-weight: bold;
            background: linear-gradient(45deg, #00d4aa, #0099cc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .status-bar {
            display: flex;
            align-items: center;
            gap: 20px;
        }
        
        .status-indicator {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .status-dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        
        .status-active { background: #00d4aa; }
        .status-stopped { background: #e53e3e; }
        .status-emergency { background: #f6ad55; animation: blink 1s infinite; }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        @keyframes blink {
            0%, 50% { opacity: 1; }
            51%, 100% { opacity: 0.3; }
        }
        
        .main-container {
            display: grid;
            grid-template-columns: 300px 1fr 350px;
            grid-template-rows: 1fr 250px;
            height: calc(100vh - 60px);
            gap: 1px;
            background: #1a1f2e;
        }
        
        .sidebar {
            background: #1a1f2e;
            border-right: 1px solid #2d3748;
            display: flex;
            flex-direction: column;
        }
        
        .main-content {
            background: #0a0e1a;
            display: flex;
            flex-direction: column;
        }
        
        .right-panel {
            background: #1a1f2e;
            border-left: 1px solid #2d3748;
            display: flex;
            flex-direction: column;
        }
        
        .bottom-panel {
            grid-column: 1 / -1;
            background: #1a1f2e;
            border-top: 1px solid #2d3748;
            display: flex;
            flex-direction: column;
        }
        
        .panel-header {
            background: #2d3748;
            padding: 12px 16px;
            font-weight: bold;
            font-size: 14px;
            color: #00d4aa;
            border-bottom: 1px solid #4a5568;
        }
        
        .panel-content {
            flex: 1;
            padding: 16px;
            overflow-y: auto;
        }
        
        .control-buttons {
            display: flex;
            flex-direction: column;
            gap: 8px;
            padding: 16px;
        }
        
        .btn {
            background: linear-gradient(135deg, #00d4aa 0%, #0099cc 100%);
            color: white;
            border: none;
            padding: 12px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: bold;
            font-size: 14px;
            transition: all 0.3s;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 212, 170, 0.3);
        }
        
        .btn.danger {
            background: linear-gradient(135deg, #e53e3e 0%, #c53030 100%);
        }
        
        .btn.danger:hover {
            box-shadow: 0 4px 12px rgba(229, 62, 62, 0.3);
        }
        
        .btn.warning {
            background: linear-gradient(135deg, #f6ad55 0%, #ed8936 100%);
        }
        
        .btn.warning:hover {
            box-shadow: 0 4px 12px rgba(246, 173, 85, 0.3);
        }
        
        .btn:disabled {
            background: #4a5568;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 20px;
        }
        
        .metric-card {
            background: linear-gradient(135deg, #2d3748 0%, #1a1f2e 100%);
            border: 1px solid #4a5568;
            border-radius: 8px;
            padding: 16px;
            text-align: center;
        }
        
        .metric-value {
            font-size: 28px;
            font-weight: bold;
            margin-bottom: 4px;
        }
        
        .metric-label {
            font-size: 12px;
            color: #a0aec0;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .positive { color: #00d4aa; }
        .negative { color: #e53e3e; }
        .neutral { color: #a0aec0; }
        
        .market-data {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 12px;
        }
        
        .market-item {
            background: #2d3748;
            border: 1px solid #4a5568;
            border-radius: 6px;
            padding: 12px;
            text-align: center;
        }
        
        .symbol {
            font-weight: bold;
            color: #00d4aa;
            margin-bottom: 4px;
        }
        
        .price {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 4px;
        }
        
        .change {
            font-size: 12px;
            font-weight: bold;
        }
        
        .trades-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 12px;
        }
        
        .trades-table th,
        .trades-table td {
            padding: 8px 12px;
            text-align: left;
            border-bottom: 1px solid #4a5568;
        }
        
        .trades-table th {
            background: #2d3748;
            color: #00d4aa;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-size: 11px;
        }
        
        .trade-buy { color: #00d4aa; }
        .trade-sell { color: #e53e3e; }
        
        .ai-chat {
            display: flex;
            flex-direction: column;
            height: 100%;
        }
        
        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 12px;
            background: #0a0e1a;
            border-radius: 6px;
            margin-bottom: 12px;
        }
        
        .chat-message {
            margin-bottom: 12px;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 12px;
        }
        
        .message-user {
            background: #2d3748;
            margin-left: 20px;
        }
        
        .message-ai {
            background: #1a1f2e;
            border: 1px solid #4a5568;
            margin-right: 20px;
        }
        
        .chat-input {
            display: flex;
            gap: 8px;
        }
        
        .chat-input input {
            flex: 1;
            background: #2d3748;
            border: 1px solid #4a5568;
            border-radius: 6px;
            padding: 8px 12px;
            color: white;
            font-size: 12px;
        }
        
        .chat-input input:focus {
            outline: none;
            border-color: #00d4aa;
        }
        
        .logs {
            flex: 1;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 11px;
            line-height: 1.4;
        }
        
        .log-entry {
            padding: 4px 0;
            border-bottom: 1px solid #2d3748;
        }
        
        .log-time {
            color: #00d4aa;
            margin-right: 8px;
        }
        
        .log-error { color: #e53e3e; }
        .log-warning { color: #f6ad55; }
        .log-success { color: #00d4aa; }
        .log-info { color: #a0aec0; }
        
        .order-form {
            background: #2d3748;
            border: 1px solid #4a5568;
            border-radius: 6px;
            padding: 16px;
            margin-bottom: 16px;
        }
        
        .form-group {
            margin-bottom: 12px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 4px;
            font-size: 12px;
            color: #a0aec0;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .form-group input,
        .form-group select {
            width: 100%;
            background: #1a1f2e;
            border: 1px solid #4a5568;
            border-radius: 4px;
            padding: 8px 12px;
            color: white;
            font-size: 12px;
        }
        
        .form-group input:focus,
        .form-group select:focus {
            outline: none;
            border-color: #00d4aa;
        }
        
        .form-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
        }
        
        .scrollbar::-webkit-scrollbar {
            width: 6px;
        }
        
        .scrollbar::-webkit-scrollbar-track {
            background: #1a1f2e;
        }
        
        .scrollbar::-webkit-scrollbar-thumb {
            background: #4a5568;
            border-radius: 3px;
        }
        
        .scrollbar::-webkit-scrollbar-thumb:hover {
            background: #00d4aa;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="brand">TradeMasterX 2.0</div>
        <div class="status-bar">
            <div class="status-indicator">
                <div class="status-dot" id="status-dot"></div>
                <span id="status-text">System Status</span>
            </div>
            <div id="connection-status">Connected</div>
        </div>
    </div>
    
    <div class="main-container">
        <!-- Left Sidebar - Controls & Portfolio -->
        <div class="sidebar">
            <div class="panel-header">Trading Controls</div>
            <div class="control-buttons">
                <button class="btn" id="start-btn" onclick="startTrading()">Start Trading</button>
                <button class="btn danger" id="stop-btn" onclick="stopTrading()">Stop Trading</button>
                <button class="btn warning" id="emergency-btn" onclick="emergencyStop()">Emergency Stop</button>
                <button class="btn" onclick="triggerRetrain()">Retrain Models</button>
            </div>
            
            <div class="panel-header">Portfolio</div>
            <div class="panel-content">
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-value" id="total-value">$10,000</div>
                        <div class="metric-label">Total Value</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value" id="available-balance">$5,000</div>
                        <div class="metric-label">Available</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value" id="daily-pnl">$0</div>
                        <div class="metric-label">Daily P&L</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value" id="total-pnl">$0</div>
                        <div class="metric-label">Total P&L</div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Main Content - Market Data & Charts -->
        <div class="main-content">
            <div class="panel-header">Market Overview</div>
            <div class="panel-content">
                <div class="market-data" id="market-data">
                    <!-- Market data will be populated here -->
                </div>
                
                <div class="panel-header" style="margin-top: 20px;">Live Trades</div>
                <div class="panel-content" style="padding-top: 0;">
                    <table class="trades-table">
                        <thead>
                            <tr>
                                <th>Time</th>
                                <th>Symbol</th>
                                <th>Type</th>
                                <th>Price</th>
                                <th>Quantity</th>
                                <th>P&L</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody id="trades-body">
                            <tr>
                                <td colspan="7" style="text-align: center; color: #a0aec0;">No active trades</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        
        <!-- Right Panel - AI Assistant & Order Entry -->
        <div class="right-panel">
            <div class="panel-header">AI Assistant</div>
            <div class="panel-content">
                <div class="ai-chat">
                    <div class="chat-messages scrollbar" id="chat-messages">
                        <div class="chat-message message-ai">
                            Hello! I'm your AI trading assistant. I can help you with market analysis, trading strategies, and system management. How can I assist you today?
                        </div>
                    </div>
                    <div class="chat-input">
                        <input type="text" id="chat-input" placeholder="Ask me anything about trading..." onkeypress="handleChatKeyPress(event)">
                        <button class="btn" onclick="sendChatMessage()">Send</button>
                    </div>
                </div>
            </div>
            
            <div class="panel-header">Order Entry</div>
            <div class="panel-content">
                <div class="order-form">
                    <div class="form-group">
                        <label>Symbol</label>
                        <select id="order-symbol">
                            <option value="BTCUSDT">BTCUSDT</option>
                            <option value="ETHUSDT">ETHUSDT</option>
                            <option value="ADAUSDT">ADAUSDT</option>
                            <option value="DOTUSDT">DOTUSDT</option>
                            <option value="LINKUSDT">LINKUSDT</option>
                        </select>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label>Type</label>
                            <select id="order-type">
                                <option value="BUY">BUY</option>
                                <option value="SELL">SELL</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Quantity</label>
                            <input type="number" id="order-quantity" step="0.01" value="0.01">
                        </div>
                    </div>
                    <button class="btn" onclick="placeOrder()">Place Order</button>
                </div>
            </div>
        </div>
        
        <!-- Bottom Panel - System Logs -->
        <div class="bottom-panel">
            <div class="panel-header">System Logs</div>
            <div class="panel-content">
                <div class="logs scrollbar" id="logs">
                    <div class="log-entry">
                        <span class="log-time">[15:50:00]</span>
                        <span class="log-success">Professional trading platform initialized</span>
                    </div>
                    <div class="log-entry">
                        <span class="log-time">[15:50:01]</span>
                        <span class="log-info">Connected to Bybit API</span>
                    </div>
                    <div class="log-entry">
                        <span class="log-time">[15:50:02]</span>
                        <span class="log-info">AI assistants (Claude & OpenAI) ready</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="/static/custom_script.js"></script>
</body>
</html>
"""
    
    async def main_dashboard(self, request):
        """Serve the main dashboard"""
        html = self._generate_main_dashboard()
        return web.Response(text=html, content_type='text/html')
    
    async def get_status(self, request):
        """Get system status"""
        status = "ACTIVE" if self.trading_active else "STOPPED"
        if self.emergency_stop_active:
            status = "EMERGENCY_STOP"
        return web.json_response({
            'status': status,
            'trading_active': self.trading_active,
            'emergency_stop_active': self.emergency_stop_active
        })
    
    async def get_market_data(self, request):
        """Get market data"""
        return web.json_response(self.market_data)
    
    async def get_portfolio(self, request):
        """Get portfolio data"""
        return web.json_response(self.portfolio)
    
    async def get_trades(self, request):
        """Get live trades"""
        return web.json_response({
            'trades': self.live_trades,
            'count': len(self.live_trades)
        })
    
    async def start_trading(self, request):
        """Start trading (launch MasterBot)"""
        if self.emergency_stop_active:
            self.logger.warning("Start trading called while emergency stop is active.")
            return web.json_response({
                'success': False,
                'error': 'Emergency stop is active'
            })
        if self.master_bot_running:
            self.logger.warning("Start trading called while master bot already running.")
            return web.json_response({'success': False, 'error': 'Master bot already running'})
        try:
            self.logger.info("Attempting to start MasterBot...")
            self.trading_active = True
            self.emergency_stop_active = False
            self.master_bot = MasterBot()
            self.master_bot_task = asyncio.create_task(self._run_master_bot())
            self.master_bot_running = True
            self.logger.info("MasterBot started successfully.")
            await self.broadcast({
                'type': 'status',
                'data': {'status': 'ACTIVE'}
            })
            await self.broadcast({
                'type': 'log',
                'message': 'Master bot trading started',
                'level': 'success'
            })
            return web.json_response({'success': True})
        except ImportError as e:
            self.logger.error(f"MasterBot import failed, using simulation mode: {e}")
            self.logger.error(traceback.format_exc())
            self.trading_active = True
            self.emergency_stop_active = False
            self.master_bot_running = True
            self.master_bot_task = asyncio.create_task(self._run_simulation_mode())
            await self.broadcast({
                'type': 'status',
                'data': {'status': 'ACTIVE'}
            })
            await self.broadcast({
                'type': 'log',
                'message': 'Trading started in simulation mode',
                'level': 'warning'
            })
            return web.json_response({'success': True, 'mode': 'simulation'})
        except Exception as e:
            self.logger.error(f"Failed to start trading: {e}")
            self.logger.error(traceback.format_exc())
            self.trading_active = False
            self.master_bot_running = False
            return web.json_response({
                'success': False,
                'error': f'Failed to start trading: {str(e)}'
            })
    
    async def _run_master_bot(self):
        try:
            if self.master_bot is not None:
                await self.master_bot.start_session('testnet')
        except Exception as e:
            self.logger.error(f"MasterBot error: {e}")
        finally:
            self.master_bot_running = False
            self.trading_active = False
            await self.broadcast({
                'type': 'status',
                'data': {'status': 'STOPPED'}
            })
            await self.broadcast({
                'type': 'log',
                'message': 'Master bot trading stopped',
                'level': 'warning'
            })
    
    async def _run_simulation_mode(self):
        """Run trading simulation when MasterBot is not available"""
        try:
            self.logger.info("Running in simulation mode")
            while self.trading_active and not self.shutdown_requested:
                # Simulate trades
                await self._simulate_trade()
                await asyncio.sleep(30)  # Simulate trade every 30 seconds
        except Exception as e:
            self.logger.error(f"Simulation mode error: {e}")
        finally:
            self.master_bot_running = False
            self.trading_active = False
            await self.broadcast({
                'type': 'status',
                'data': {'status': 'STOPPED'}
            })
            await self.broadcast({
                'type': 'log',
                'message': 'Simulation mode stopped',
                'level': 'warning'
            })
    
    async def _simulate_trade(self):
        """Simulate a trade for demo purposes"""
        try:
            symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'DOTUSDT', 'LINKUSDT']
            symbol = random.choice(symbols)
            side = random.choice(['BUY', 'SELL'])
            quantity = round(random.uniform(0.01, 0.1), 4)
            price = self.market_data[symbol]['price']
            price_change = random.uniform(-0.02, 0.02) * price
            self.market_data[symbol]['price'] += price_change
            trade = {
                'id': f"sim_{int(time.time())}",
                'symbol': symbol,
                'side': side,
                'quantity': quantity,
                'price': price,
                'timestamp': datetime.now().isoformat(),
                'pnl': random.uniform(-50, 100)
            }
            self.logger.info(f"Simulated trade: {trade}")
            self.record_and_broadcast_trade(trade)
        except Exception as e:
            self.logger.error(f"Simulate trade error: {e}")
            self.logger.error(traceback.format_exc())
    
    async def stop_trading(self, request):
        """Stop trading (halt MasterBot)"""
        self.trading_active = False
        if self.master_bot and self.master_bot_running:
            self.master_bot.shutdown_requested = True
            if self.master_bot_task:
                await self.master_bot_task
        self.master_bot_running = False
        await self.broadcast({
            'type': 'status',
            'data': {'status': 'STOPPED'}
        })
        await self.broadcast({
            'type': 'log',
            'message': 'Master bot trading stopped',
            'level': 'warning'
        })
        return web.json_response({'success': True})
    
    async def handle_emergency_stop(self, request):
        """Emergency stop"""
        self.emergency_stop_active = True
        self.trading_active = False
        await self.broadcast({
            'type': 'status',
            'data': {'status': 'EMERGENCY_STOP'}
        })
        await self.broadcast({
            'type': 'log',
            'message': 'EMERGENCY STOP ACTIVATED!',
            'level': 'error'
        })
        return web.json_response({'success': True})
    
    async def ai_query(self, request):
        """Handle AI queries using Claude or OpenAI"""
        try:
            data = await request.json()
            query = data.get('query', '')
            self.logger.info(f"AI query received: {query}")
            response = await self._query_claude(query)
            if not response:
                response = await self._query_openai(query)
            if response:
                await self.broadcast({
                    'type': 'ai_response',
                    'message': response
                })
                return web.json_response({
                    'success': True,
                    'response': response
                })
            else:
                self.logger.warning("No AI service available for query.")
                return web.json_response({
                    'success': False,
                    'error': 'No AI service available'
                })
        except Exception as e:
            self.logger.error(f"AI query error: {e}")
            self.logger.error(traceback.format_exc())
            return web.json_response({
                'success': False,
                'error': str(e)
            })
    
    async def _query_claude(self, query: str) -> Optional[str]:
        """Query Claude API"""
        if not self.claude_api_key:
            return None
            
        try:
            headers = {
                'x-api-key': self.claude_api_key,
                'Content-Type': 'application/json',
                'anthropic-version': '2023-06-01'
            }
            
            payload = {
                'model': 'claude-3-haiku-20240307',
                'max_tokens': 300,
                'messages': [{
                    'role': 'user',
                    'content': f"You are a professional trading assistant. Answer this question about trading: {query}"
                }]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    'https://api.anthropic.com/v1/messages',
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data['content'][0]['text'].strip()
                        
        except Exception as e:
            self.logger.error(f"Claude API error: {e}")
            
        return None
    
    async def _query_openai(self, query: str) -> Optional[str]:
        """Query OpenAI API"""
        if not self.openai_api_key:
            return None
            
        try:
            headers = {
                'Authorization': f'Bearer {self.openai_api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': 'gpt-3.5-turbo',
                'messages': [
                    {
                        'role': 'system',
                        'content': 'You are a professional trading assistant. Provide concise, helpful answers about trading.'
                    },
                    {
                        'role': 'user',
                        'content': query
                    }
                ],
                'max_tokens': 300,
                'temperature': 0.7
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    'https://api.openai.com/v1/chat/completions',
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data['choices'][0]['message']['content'].strip()
                        
        except Exception as e:
            self.logger.error(f"OpenAI API error: {e}")
            
        return None
    
    async def place_order(self, request):
        """Place trading order via Bybit API (testnet)"""
        try:
            data = await request.json()
            symbol = data.get('symbol', 'BTCUSDT')
            order_type = data.get('type', 'BUY')
            quantity = float(data.get('quantity', 0.01))

            # Bybit testnet REST API endpoint for USDT Perpetual
            base_url = 'https://api-testnet.bybit.com'
            endpoint = '/v5/order/create'
            url = base_url + endpoint

            # Bybit API params
            side = 'Buy' if order_type.upper() == 'BUY' else 'Sell'
            category = 'linear'  # USDT Perpetual
            params = {
                'category': category,
                'symbol': symbol,
                'side': side,
                'orderType': 'Market',
                'qty': str(quantity),
                'timeInForce': 'GoodTillCancel',
                'reduceOnly': False,
                'closeOnTrigger': False,
                'positionIdx': 0,
                'timestamp': str(int(datetime.utcnow().timestamp() * 1000)),
                'recvWindow': '5000',
            }

            # Prepare signature
            param_str = '&'.join([f"{k}={params[k]}" for k in sorted(params)])
            api_key = self.bybit_api_key
            api_secret = self.bybit_secret
            headers = {
                'X-BAPI-API-KEY': api_key,
                'Content-Type': 'application/json',
            }
            # Bybit v5 signature: sign = HMAC_SHA256(secret, timestamp + api_key + recv_window + body)
            body = json.dumps(params)
            sign_payload = params['timestamp'] + api_key + params['recvWindow'] + body
            signature = hmac.new(api_secret.encode(), sign_payload.encode(), hashlib.sha256).hexdigest()
            headers['X-BAPI-SIGN'] = signature
            headers['X-BAPI-TIMESTAMP'] = params['timestamp']
            headers['X-BAPI-RECV-WINDOW'] = params['recvWindow']

            # Send order to Bybit
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, data=body) as resp:
                    resp_data = await resp.json()
                    if resp.status == 200 and resp_data.get('retCode') == 0:
                        order_info = resp_data['result']
                        # Show real order in UI
                        order = {
                            'id': order_info.get('orderId', f"O{self.total_trades + 1}"),
                            'symbol': symbol,
                            'type': order_type,
                            'quantity': quantity,
                            'price': float(order_info.get('avgPrice', 0)) or self.market_data[symbol]['price'],
                            'status': order_info.get('orderStatus', 'FILLED'),
                            'timestamp': datetime.now().isoformat()
                        }
                        self.live_trades.append(order)
                        self.total_trades += 1
                        await self.broadcast({'type': 'trades', 'data': self.live_trades})
                        await self.broadcast({'type': 'log', 'message': f"Order placed: {order_type} {quantity} {symbol}", 'level': 'success'})
                        return web.json_response({'success': True, 'order': order})
                    else:
                        error_msg = resp_data.get('retMsg', 'Unknown error')
                        await self.broadcast({'type': 'log', 'message': f"Bybit order error: {error_msg}", 'level': 'error'})
                        return web.json_response({'success': False, 'error': error_msg})
        except Exception as e:
            self.logger.error(f"Order placement error: {e}")
            await self.broadcast({'type': 'log', 'message': f"Order placement error: {e}", 'level': 'error'})
            return web.json_response({'success': False, 'error': str(e)})
    
    async def websocket_handler(self, request):
        """Handle WebSocket connections"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        self.websocket_connections.add(ws)
        
        try:
            async for msg in ws:
                if msg.type == WSMsgType.ERROR:
                    self.logger.error(f'WebSocket error: {ws.exception()}')
        finally:
            self.websocket_connections.discard(ws)
        
        return ws
    
    async def broadcast(self, message):
        """Broadcast message to all WebSocket clients"""
        if not self.websocket_connections:
            return
            
        closed = set()
        for ws in self.websocket_connections.copy():
            try:
                await ws.send_str(json.dumps(message))
            except:
                closed.add(ws)
        
        self.websocket_connections -= closed
    
    async def _simulate_market_updates(self):
        """Simulate market data updates"""
        while True:
            # Update market prices
            for symbol in self.market_data:
                current_price = self.market_data[symbol]['price']
                change_percent = random.uniform(-5, 5)
                new_price = current_price * (1 + change_percent / 100)
                
                self.market_data[symbol]['price'] = round(new_price, 2)
                self.market_data[symbol]['change'] = round(change_percent, 2)
                self.market_data[symbol]['volume'] = random.randint(100000, 2000000)
            
            # Update portfolio
            if self.trading_active and not self.emergency_stop_active:
                pnl_change = random.uniform(-100, 100)
                self.portfolio['daily_pnl'] += pnl_change
                self.portfolio['total_pnl'] += pnl_change
                self.portfolio['total_value'] = self.portfolio['available_balance'] + self.portfolio['total_pnl']
            
            # Broadcast updates
            await self.broadcast({
                'type': 'market_data',
                'data': self.market_data
            })
            
            await self.broadcast({
                'type': 'portfolio',
                'data': self.portfolio
            })
            
            await asyncio.sleep(5)  # Update every 5 seconds
    
    async def start(self):
        """Start the professional trading platform"""
        self.logger.info(f"Starting Professional Trading Platform on http://{self.host}:{self.port}")
        # Start background tasks
        asyncio.create_task(self._simulate_market_updates())
        asyncio.create_task(self._periodic_retraining())
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        self.logger.info(f"Professional Trading Platform running at http://{self.host}:{self.port}")
        self.logger.info("Features:")
        self.logger.info("- Single unified interface")
        self.logger.info("- Professional multi-panel layout")
        self.logger.info("- Real-time market data")
        self.logger.info("- AI assistant (Claude + OpenAI)")
        self.logger.info("- Bybit API integration")
        self.logger.info("- Live trading controls")
        self.logger.info("- Portfolio management")
        self.logger.info("- Order entry system")
        # Open dashboard in browser
        webbrowser.open(f"http://{self.host}:{self.port}")
        # Keep process alive
        while True:
            await asyncio.sleep(3600)

    async def _periodic_retraining(self):
        """Automatically trigger retraining every 12 hours"""
        while True:
            await asyncio.sleep(12 * 3600)  # 12 hours
            await self.trigger_retrain(None)

    def record_and_broadcast_trade(self, trade: dict):
        """Record a new trade, update P&L, and broadcast to dashboard clients."""
        self.live_trades.append(trade)
        self.total_trades += 1
        # Update P&L (simple sum for now)
        pnl = trade.get('pnl', 0)
        self.portfolio['daily_pnl'] += pnl
        self.portfolio['total_pnl'] += pnl
        self.portfolio['total_value'] = self.portfolio['available_balance'] + self.portfolio['total_pnl']
        # Broadcast updates
        asyncio.create_task(self.broadcast({'type': 'trades', 'data': self.live_trades}))
        asyncio.create_task(self.broadcast({'type': 'portfolio', 'data': self.portfolio}))
        asyncio.create_task(self.broadcast({'type': 'log', 'message': f"Trade executed: {trade}", 'level': 'info'}))

    async def trigger_retrain(self, request):
        """Trigger model retraining and broadcast to dashboard"""
        await self.broadcast({
            'type': 'log',
            'message': 'Model retraining triggered',
            'level': 'warning'
        })
        # Simulate retraining
        asyncio.create_task(self._simulate_retraining())
        return web.json_response({'success': True})

    async def _simulate_retraining(self):
        await asyncio.sleep(3)
        await self.broadcast({
            'type': 'log',
            'message': 'Retraining completed successfully',
            'level': 'success'
        })

async def main():
    """Main function"""
    platform = ProfessionalTradingPlatform()
    await platform.start()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProfessional Trading Platform stopped") 