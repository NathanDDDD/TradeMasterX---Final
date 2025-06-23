#!/usr/bin/env python3
"""
TradeMasterX 2.0 - Phase 14: AI Dashboard
Web dashboard for monitoring AI system health and performance
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import aiohttp
from aiohttp import web, WSMsgType
import aiohttp_cors
import jinja2
import aiofiles

class AIDashboard:
    """Web dashboard for AI system monitoring"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger("AIDashboard")
        
        # Web server configuration
        self.host = config.get('dashboard_host', 'localhost')
        self.port = config.get('dashboard_port', 8080)
        
        # Component references
        self.observer_agent = None
        self.ai_orchestrator = None
        self.reinforcement_engine = None
        self.anomaly_auditor = None
        
        # WebSocket connections
        self.websocket_connections = set()
        
        # Data cache
        self.data_cache = {
            'last_update': None,
            'system_metrics': {},
            'anomaly_data': {},
            'performance_data': {}
        }
        
        # Create web app
        self.app = web.Application()
        self._setup_routes()
        self._setup_cors()
        
    def inject_components(self, observer=None, orchestrator=None, reinforcement=None, auditor=None):
        """Inject AI component dependencies"""
        if observer:
            self.observer_agent = observer
        if orchestrator:
            self.ai_orchestrator = orchestrator
        if reinforcement:
            self.reinforcement_engine = reinforcement
        if auditor:
            self.anomaly_auditor = auditor
            
    def _setup_routes(self):
        """Setup web routes"""
        # Static dashboard page
        self.app.router.add_get('/', self.dashboard_page)
        
        # API endpoints
        self.app.router.add_get('/api/system-status', self.get_system_status)
        self.app.router.add_get('/api/strategy-performance', self.get_strategy_performance)
        self.app.router.add_get('/api/anomaly-report', self.get_anomaly_report)
        self.app.router.add_get('/api/ai-health', self.get_ai_health)
        
        # WebSocket endpoint
        self.app.router.add_get('/ws', self.websocket_handler)
        
        # Control endpoints
        self.app.router.add_post('/api/trigger-retrain', self.trigger_retrain)
        self.app.router.add_post('/api/adjust-weights', self.adjust_weights)
        
    def _setup_cors(self):
        """Setup CORS for web dashboard"""
        cors = aiohttp_cors.setup(self.app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods="*"
            )
        })
        
        # Add CORS to all routes
        for route in list(self.app.router.routes()):
            cors.add(route)
            
    async def dashboard_page(self, request):
        """Serve the main dashboard HTML page"""
        html_content = self._generate_dashboard_html()
        return web.Response(text=html_content, content_type='text/html')
        
    def _generate_dashboard_html(self) -> str:
        """Generate the dashboard HTML content"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TradeMasterX AI Dashboard</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            min-height: 100vh;
        }
        
        .dashboard-header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .dashboard-card {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        
        .status-healthy { background: #4CAF50; }
        .status-degraded { background: #FF9800; }
        .status-critical { background: #F44336; }
        
        .metric-row {
            display: flex;
            justify-content: space-between;
            margin: 10px 0;
            padding: 8px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .metric-value {
            font-weight: bold;
        }
        
        .chart-container {
            height: 200px;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 5px;
            margin: 10px 0;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .controls {
            text-align: center;
            margin-top: 20px;
        }
        
        .btn {
            background: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            margin: 0 10px;
            transition: background 0.3s;
        }
        
        .btn:hover {
            background: #45a049;
        }
        
        .btn.danger {
            background: #F44336;
        }
        
        .btn.danger:hover {
            background: #da190b;
        }
        
        .log-container {
            max-height: 200px;
            overflow-y: auto;
            background: rgba(0, 0, 0, 0.3);
            padding: 10px;
            border-radius: 5px;
            font-family: monospace;
            font-size: 12px;
        }
        
        .anomaly-item {
            background: rgba(244, 67, 54, 0.2);
            padding: 8px;
            margin: 5px 0;
            border-radius: 5px;
            border-left: 3px solid #F44336;
        }
        
        .update-time {
            text-align: center;
            font-size: 12px;
            opacity: 0.7;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="dashboard-header">
        <h1>🤖 TradeMasterX AI Dashboard</h1>
        <p>Phase 14: Autonomous Intelligence Layer</p>
    </div>
    
    <div class="dashboard-grid">
        <!-- System Health Card -->
        <div class="dashboard-card">
            <h3>🏥 System Health</h3>
            <div id="system-health">
                <div class="metric-row">
                    <span>Overall Status:</span>
                    <span class="metric-value">
                        <span class="status-indicator status-healthy"></span>
                        <span id="health-status">Loading...</span>
                    </span>
                </div>
                <div class="metric-row">
                    <span>Anomaly Rate (24h):</span>
                    <span class="metric-value" id="anomaly-rate">-</span>
                </div>
                <div class="metric-row">
                    <span>Total Trades (24h):</span>
                    <span class="metric-value" id="total-trades">-</span>
                </div>
                <div class="metric-row">
                    <span>Win Rate (24h):</span>
                    <span class="metric-value" id="win-rate">-</span>
                </div>
            </div>
        </div>
        
        <!-- Strategy Performance Card -->
        <div class="dashboard-card">
            <h3>📈 Strategy Performance</h3>
            <div id="strategy-performance">
                <div class="chart-container">
                    <span>Strategy weight visualization would go here</span>
                </div>
                <div id="strategy-list">
                    <!-- Strategies will be populated here -->
                </div>
            </div>
        </div>
        
        <!-- Model Versions Card -->
        <div class="dashboard-card">
            <h3>🧠 Model Status</h3>
            <div id="model-status">
                <div class="metric-row">
                    <span>Last Retrain:</span>
                    <span class="metric-value" id="last-retrain">-</span>
                </div>
                <div class="metric-row">
                    <span>Performance Trend:</span>
                    <span class="metric-value" id="performance-trend">-</span>
                </div>
                <div class="metric-row">
                    <span>Active Models:</span>
                    <span class="metric-value" id="active-models">-</span>
                </div>
            </div>
        </div>
        
        <!-- Anomaly Detection Card -->
        <div class="dashboard-card">
            <h3>🚨 Anomaly Detection</h3>
            <div id="anomaly-detection">
                <div class="metric-row">
                    <span>Critical Issues:</span>
                    <span class="metric-value" id="critical-issues">-</span>
                </div>
                <div id="recent-anomalies">
                    <!-- Recent anomalies will be listed here -->
                </div>
            </div>
        </div>
        
        <!-- Real-time Metrics Card -->
        <div class="dashboard-card">
            <h3>⚡ Real-time Metrics</h3>
            <div id="realtime-metrics">
                <div class="metric-row">
                    <span>Observer Agent:</span>
                    <span class="metric-value" id="observer-status">-</span>
                </div>
                <div class="metric-row">
                    <span>AI Orchestrator:</span>
                    <span class="metric-value" id="orchestrator-status">-</span>
                </div>
                <div class="metric-row">
                    <span>Reinforcement Engine:</span>
                    <span class="metric-value" id="reinforcement-status">-</span>
                </div>
                <div class="metric-row">
                    <span>Anomaly Auditor:</span>
                    <span class="metric-value" id="auditor-status">-</span>
                </div>
            </div>
        </div>
        
        <!-- Activity Log Card -->
        <div class="dashboard-card">
            <h3>📋 Activity Log</h3>
            <div class="log-container" id="activity-log">
                <!-- Activity logs will be displayed here -->
            </div>
        </div>
    </div>
    
    <!-- Control Panel -->
    <div class="controls">
        <button class="btn" onclick="triggerRetrain()">🧠 Trigger Retrain</button>
        <button class="btn" onclick="refreshData()">🔄 Refresh Data</button>
        <button class="btn danger" onclick="exportReport()">📊 Export Report</button>
    </div>
    
    <div class="update-time">
        Last updated: <span id="last-update">-</span>
    </div>
    
    <script>
        let ws = null;
        
        // Initialize WebSocket connection
        function initWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws`;
            
            ws = new WebSocket(wsUrl);
            
            ws.onopen = function() {
                console.log('WebSocket connected');
                addToLog('🟢 Dashboard connected');
            };
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                updateDashboard(data);
            };
            
            ws.onclose = function() {
                console.log('WebSocket disconnected');
                addToLog('🔴 Dashboard disconnected');
                // Attempt reconnection after 5 seconds
                setTimeout(initWebSocket, 5000);
            };
            
            ws.onerror = function(error) {
                console.error('WebSocket error:', error);
                addToLog('❌ Connection error');
            };
        }
        
        // Update dashboard with new data
        function updateDashboard(data) {
            if (data.type === 'system_update') {
                updateSystemHealth(data.system_health);
                updateMetrics(data.metrics);
                document.getElementById('last-update').textContent = new Date().toLocaleTimeString();
            } else if (data.type === 'anomaly_alert') {
                addAnomalyAlert(data.anomaly);
            } else if (data.type === 'log_message') {
                addToLog(data.message);
            }
        }
        
        // Update system health display
        function updateSystemHealth(health) {
            const statusElement = document.getElementById('health-status');
            const indicator = statusElement.parentElement.querySelector('.status-indicator');
            
            statusElement.textContent = health.status;
            
            // Update indicator color
            indicator.className = 'status-indicator';
            if (health.status === 'HEALTHY') {
                indicator.classList.add('status-healthy');
            } else if (health.status === 'DEGRADED') {
                indicator.classList.add('status-degraded');
            } else {
                indicator.classList.add('status-critical');
            }
        }
        
        // Update metrics display
        function updateMetrics(metrics) {
            if (metrics.anomaly_rate !== undefined) {
                document.getElementById('anomaly-rate').textContent = (metrics.anomaly_rate * 100).toFixed(1) + '%';
            }
            if (metrics.total_trades !== undefined) {
                document.getElementById('total-trades').textContent = metrics.total_trades;
            }
            if (metrics.win_rate !== undefined) {
                document.getElementById('win-rate').textContent = (metrics.win_rate * 100).toFixed(1) + '%';
            }
        }
        
        // Add message to activity log
        function addToLog(message) {
            const logContainer = document.getElementById('activity-log');
            const timestamp = new Date().toLocaleTimeString();
            const logEntry = document.createElement('div');
            logEntry.textContent = `[${timestamp}] ${message}`;
            logContainer.appendChild(logEntry);
            
            // Keep only last 50 entries
            while (logContainer.children.length > 50) {
                logContainer.removeChild(logContainer.firstChild);
            }
            
            // Scroll to bottom
            logContainer.scrollTop = logContainer.scrollHeight;
        }
        
        // Control functions
        async function triggerRetrain() {
            try {
                const response = await fetch('/api/trigger-retrain', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({reason: 'Manual dashboard trigger'})
                });
                const result = await response.json();
                
                if (result.success) {
                    addToLog('🧠 Model retraining triggered successfully');
                } else {
                    addToLog('❌ Failed to trigger retraining: ' + result.error);
                }
            } catch (error) {
                addToLog('❌ Error triggering retrain: ' + error.message);
            }
        }
        
        async function refreshData() {
            try {
                const response = await fetch('/api/system-status');
                const data = await response.json();
                updateDashboard({type: 'system_update', ...data});
                addToLog('🔄 Data refreshed');
            } catch (error) {
                addToLog('❌ Failed to refresh data: ' + error.message);
            }
        }
        
        async function exportReport() {
            try {
                const response = await fetch('/api/anomaly-report');
                const report = await response.json();
                
                const blob = new Blob([JSON.stringify(report, null, 2)], {type: 'application/json'});
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `ai_report_${new Date().toISOString().split('T')[0]}.json`;
                a.click();
                URL.revokeObjectURL(url);
                
                addToLog('📊 Report exported successfully');
            } catch (error) {
                addToLog('❌ Failed to export report: ' + error.message);
            }
        }
        
        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {
            initWebSocket();
            refreshData();
            
            // Auto-refresh every 30 seconds
            setInterval(refreshData, 30000);
        });
    </script>
</body>
</html>
        """
        
    async def get_system_status(self, request):
        """Get current system status"""
        try:
            status = {
                'timestamp': datetime.now().isoformat(),
                'system_health': {'status': 'HEALTHY'},
                'metrics': {
                    'anomaly_rate': 0.05,
                    'total_trades': 150,
                    'win_rate': 0.67
                },
                'components': {
                    'observer_agent': 'ACTIVE' if self.observer_agent else 'INACTIVE',
                    'ai_orchestrator': 'ACTIVE' if self.ai_orchestrator else 'INACTIVE',
                    'reinforcement_engine': 'ACTIVE' if self.reinforcement_engine else 'INACTIVE',
                    'anomaly_auditor': 'ACTIVE' if self.anomaly_auditor else 'INACTIVE'
                }
            }
            
            # Get real data if components are available
            if self.ai_orchestrator:
                ai_health = self.ai_orchestrator.get_ai_health_report()
                if 'system_health' in ai_health:
                    status['system_health'] = ai_health['system_health']
                if 'system_metrics' in ai_health:
                    status['metrics'].update(ai_health['system_metrics'])
                    
            return web.json_response(status)
            
        except Exception as e:
            self.logger.error(f"Failed to get system status: {e}")
            return web.json_response({'error': str(e)}, status=500)
            
    async def get_strategy_performance(self, request):
        """Get strategy performance data"""
        try:
            if self.reinforcement_engine:
                performance = self.reinforcement_engine.get_strategy_performance()
                return web.json_response(performance)
            else:
                # Demo data
                demo_performance = {
                    'strategies': {
                        'momentum': {'current_weight': 1.2, 'win_rate': 0.68, 'avg_return': 0.025},
                        'reversal': {'current_weight': 0.8, 'win_rate': 0.55, 'avg_return': 0.010}
                    },
                    'bots': {
                        'AnalyticsBot': {'current_weight': 1.1, 'win_rate': 0.72, 'avg_return': 0.028},
                        'StrategyBot': {'current_weight': 0.9, 'win_rate': 0.58, 'avg_return': 0.012}
                    }
                }
                return web.json_response(demo_performance)
                
        except Exception as e:
            self.logger.error(f"Failed to get strategy performance: {e}")
            return web.json_response({'error': str(e)}, status=500)
            
    async def get_anomaly_report(self, request):
        """Get anomaly detection report"""
        try:
            if self.anomaly_auditor:
                report = self.anomaly_auditor.generate_anomaly_report()
                return web.json_response(report)
            else:
                # Demo data
                demo_report = {
                    'timestamp': datetime.now().isoformat(),
                    'summary_24h': {
                        'total_audits': 150,
                        'total_anomalies': 8,
                        'anomaly_rate': 0.053,
                        'critical_issues': 1
                    },
                    'system_health': {
                        'status': 'HEALTHY',
                        'concerns': [],
                        'recommendations': []
                    }
                }
                return web.json_response(demo_report)
                
        except Exception as e:
            self.logger.error(f"Failed to get anomaly report: {e}")
            return web.json_response({'error': str(e)}, status=500)
            
    async def get_ai_health(self, request):
        """Get AI system health report"""
        try:
            if self.ai_orchestrator:
                health = self.ai_orchestrator.get_ai_health_report()
                return web.json_response(health)
            else:
                # Demo data
                demo_health = {
                    'timestamp': datetime.now().isoformat(),
                    'system_health': {'status': 'HEALTHY'},
                    'components_status': {
                        'observer_agent': 'DEMO',
                        'reinforcement_engine': 'DEMO',
                        'anomaly_auditor': 'DEMO'
                    }
                }
                return web.json_response(demo_health)
                
        except Exception as e:
            self.logger.error(f"Failed to get AI health: {e}")
            return web.json_response({'error': str(e)}, status=500)
            
    async def trigger_retrain(self, request):
        """Trigger model retraining"""
        try:
            data = await request.json()
            reason = data.get('reason', 'Manual trigger from dashboard')
            
            if self.ai_orchestrator:
                success = await self.ai_orchestrator.manual_retrain_trigger(reason)
                return web.json_response({'success': success, 'reason': reason})
            else:
                # Demo mode
                self.logger.info(f"Demo retrain triggered: {reason}")
                return web.json_response({'success': True, 'reason': reason, 'demo': True})
                
        except Exception as e:
            self.logger.error(f"Failed to trigger retrain: {e}")
            return web.json_response({'success': False, 'error': str(e)}, status=500)
            
    async def adjust_weights(self, request):
        """Adjust strategy/bot weights"""
        try:
            data = await request.json()
            entity_type = data.get('type')  # 'strategy' or 'bot'
            name = data.get('name')
            weight = float(data.get('weight'))
            
            if self.reinforcement_engine:
                success = self.reinforcement_engine.adjust_allocation(entity_type, name, weight)
                return web.json_response({'success': success})
            else:
                # Demo mode
                self.logger.info(f"Demo weight adjustment: {entity_type} {name} -> {weight}")
                return web.json_response({'success': True, 'demo': True})
                
        except Exception as e:
            self.logger.error(f"Failed to adjust weights: {e}")
            return web.json_response({'success': False, 'error': str(e)}, status=500)
            
    async def websocket_handler(self, request):
        """Handle WebSocket connections for real-time updates"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        self.websocket_connections.add(ws)
        self.logger.info("New WebSocket connection established")
        
        try:
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    # Handle incoming messages if needed
                    pass
                elif msg.type == WSMsgType.ERROR:
                    self.logger.error(f'WebSocket error: {ws.exception()}')
                    break
        except Exception as e:
            self.logger.error(f"WebSocket error: {e}")
        finally:
            self.websocket_connections.discard(ws)
            self.logger.info("WebSocket connection closed")
            
        return ws
        
    async def broadcast_update(self, message: Dict[str, Any]):
        """Broadcast update to all connected WebSocket clients"""
        if not self.websocket_connections:
            return
            
        # Remove closed connections
        closed_connections = set()
        
        for ws in self.websocket_connections.copy():
            try:
                await ws.send_str(json.dumps(message))
            except Exception as e:
                self.logger.warning(f"Failed to send WebSocket message: {e}")
                closed_connections.add(ws)
                
        # Clean up closed connections
        self.websocket_connections -= closed_connections
        
    async def start_dashboard(self):
        """Start the web dashboard server"""
        self.logger.info(f"🌐 Starting AI Dashboard on http://{self.host}:{self.port}")
        
        runner = web.AppRunner(self.app)
        await runner.setup()
        
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        
        self.logger.info(f"✅ AI Dashboard running at http://{self.host}:{self.port}")
        
        # Start periodic updates
        asyncio.create_task(self._periodic_updates())
        
    async def _periodic_updates(self):
        """Send periodic updates to connected clients"""
        while True:
            try:
                # Collect current data
                status_data = {
                    'type': 'system_update',
                    'timestamp': datetime.now().isoformat(),
                    'system_health': {'status': 'HEALTHY'},
                    'metrics': {
                        'anomaly_rate': 0.05,
                        'total_trades': 150,
                        'win_rate': 0.67
                    }
                }
                
                # Get real data if available
                if self.ai_orchestrator:
                    ai_health = self.ai_orchestrator.get_ai_health_report()
                    if isinstance(ai_health, dict):
                        status_data.update(ai_health)
                        
                # Broadcast to all clients
                await self.broadcast_update(status_data)
                
                # Wait 10 seconds before next update
                await asyncio.sleep(10)
                
            except Exception as e:
                self.logger.error(f"Periodic update error: {e}")
                await asyncio.sleep(30)  # Longer wait on error


# Demo function
async def demo_ai_dashboard():
    """Demo the AI dashboard"""
    config = {
        'dashboard_host': 'localhost',
        'dashboard_port': 8080,
        'demo_mode': True
    }
    
    dashboard = AIDashboard(config)
    
    print("🌐 TradeMasterX Phase 14: AI Dashboard Demo")
    print("=" * 50)
    print(f"Dashboard starting at http://{config['dashboard_host']}:{config['dashboard_port']}")
    
    # Start the dashboard
    await dashboard.start_dashboard()
    
    print("✅ AI Dashboard is running!")
    print("📱 Open your browser and navigate to the URL above")
    print("🔄 Dashboard will show real-time AI system metrics")
    print("⌨️  Press Ctrl+C to stop")
    
    try:
        # Keep running
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped")


if __name__ == "__main__":
    asyncio.run(demo_ai_dashboard())
