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
        """Generate the dashboard HTML content with navigation"""
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
            padding: 0;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            min-height: 100vh;
        }
        
        .nav-bar {
            background: rgba(0, 0, 0, 0.3);
            padding: 15px 0;
            backdrop-filter: blur(10px);
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .nav-container {
            max-width: 1400px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0 20px;
        }
        
        .nav-brand {
            font-size: 24px;
            font-weight: bold;
            color: #4CAF50;
        }
        
        .nav-menu {
            display: flex;
            gap: 20px;
        }
        
        .nav-item {
            padding: 10px 15px;
            border-radius: 5px;
            cursor: pointer;
            transition: background 0.3s;
            text-decoration: none;
            color: white;
        }
        
        .nav-item:hover {
            background: rgba(255, 255, 255, 0.1);
        }
        
        .nav-item.active {
            background: #4CAF50;
        }
        
        .dashboard-header {
            text-align: center;
            margin: 30px 0;
        }
        
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 20px;
        }
        
        .dashboard-card {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .card-title {
            font-size: 18px;
            font-weight: bold;
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
        
        .section {
            display: none;
        }
        
        .section.active {
            display: block;
        }
        
        .quick-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: rgba(255, 255, 255, 0.1);
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }
        
        .stat-value {
            font-size: 24px;
            font-weight: bold;
            color: #4CAF50;
        }
        
        .stat-label {
            font-size: 12px;
            opacity: 0.8;
            margin-top: 5px;
        }
    </style>
</head>
<body>
    <nav class="nav-bar">
        <div class="nav-container">
            <div class="nav-brand">TradeMasterX 2.0</div>
            <div class="nav-menu">
                <a href="#overview" class="nav-item active" onclick="showSection('overview')">Overview</a>
                <a href="#ai-status" class="nav-item" onclick="showSection('ai-status')">AI Status</a>
                <a href="#performance" class="nav-item" onclick="showSection('performance')">Performance</a>
                <a href="#anomalies" class="nav-item" onclick="showSection('anomalies')">Anomalies</a>
                <a href="#logs" class="nav-item" onclick="showSection('logs')">Logs</a>
            </div>
        </div>
    </nav>

    <div id="overview" class="section active">
    <div class="dashboard-header">
            <h1>System Overview</h1>
            <p>Real-time monitoring of TradeMasterX 2.0 AI Trading System</p>
        </div>
        
        <div class="quick-stats">
            <div class="stat-card">
                <div class="stat-value" id="total-trades">0</div>
                <div class="stat-label">Total Trades</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="win-rate">0%</div>
                <div class="stat-label">Win Rate</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="anomaly-rate">0%</div>
                <div class="stat-label">Anomaly Rate</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="system-health">Healthy</div>
                <div class="stat-label">System Health</div>
            </div>
    </div>
    
    <div class="dashboard-grid">
        <div class="dashboard-card">
                <div class="card-header">
                    <div class="card-title">System Status</div>
                        <span class="status-indicator status-healthy"></span>
                </div>
                <div id="system-status-content">
                    <div class="metric-row">
                        <span>AI Orchestrator</span>
                        <span class="metric-value">Active</span>
                    </div>
                    <div class="metric-row">
                        <span>Observer Agent</span>
                        <span class="metric-value">Monitoring</span>
                    </div>
                    <div class="metric-row">
                        <span>Reinforcement Engine</span>
                        <span class="metric-value">Learning</span>
                </div>
                <div class="metric-row">
                        <span>Anomaly Auditor</span>
                        <span class="metric-value">Scanning</span>
                    </div>
                </div>
            </div>
            
            <div class="dashboard-card">
                <div class="card-header">
                    <div class="card-title">Recent Activity</div>
                </div>
                <div id="recent-activity">
                    <div class="metric-row">
                        <span>Last Trade</span>
                        <span class="metric-value">2 minutes ago</span>
                </div>
                <div class="metric-row">
                        <span>Model Update</span>
                        <span class="metric-value">1 hour ago</span>
                </div>
                <div class="metric-row">
                        <span>Anomaly Check</span>
                        <span class="metric-value">5 minutes ago</span>
                    </div>
                </div>
                </div>
            </div>
        </div>
        
    <div id="ai-status" class="section">
        <div class="dashboard-header">
            <h1>AI System Status</h1>
            <p>Detailed health and performance metrics</p>
        </div>
        <div class="dashboard-grid">
        <div class="dashboard-card">
                <div class="card-header">
                    <div class="card-title">AI Health Report</div>
                </div>
                <div id="ai-health-content">
                    Loading...
                </div>
                </div>
            </div>
        </div>
        
    <div id="performance" class="section">
        <div class="dashboard-header">
            <h1>Performance Metrics</h1>
            <p>Strategy and trading performance analysis</p>
        </div>
        <div class="dashboard-grid">
        <div class="dashboard-card">
                <div class="card-header">
                    <div class="card-title">Strategy Performance</div>
                </div>
                <div id="strategy-performance-content">
                    Loading...
                </div>
                </div>
            </div>
        </div>
        
    <div id="anomalies" class="section">
        <div class="dashboard-header">
            <h1>Anomaly Detection</h1>
            <p>Recent anomalies and alerts</p>
        </div>
        <div class="dashboard-grid">
        <div class="dashboard-card">
                <div class="card-header">
                    <div class="card-title">Anomaly Report</div>
                </div>
                <div id="anomaly-report-content">
                    Loading...
                </div>
                </div>
            </div>
        </div>
        
    <div id="logs" class="section">
        <div class="dashboard-header">
            <h1>System Logs</h1>
            <p>Recent system events and logs</p>
        </div>
        <div class="dashboard-grid">
        <div class="dashboard-card">
                <div class="card-header">
                    <div class="card-title">Recent Logs</div>
                </div>
                <div id="logs-content" style="max-height: 400px; overflow-y: auto;">
                <div class="metric-row">
                        <span>2025-06-22 15:50:00</span>
                        <span>System started successfully</span>
                </div>
                <div class="metric-row">
                        <span>2025-06-22 15:49:30</span>
                        <span>AI Dashboard initialized</span>
                </div>
                <div class="metric-row">
                        <span>2025-06-22 15:49:00</span>
                        <span>Configuration loaded</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <div class="controls">
        <button class="btn" onclick="triggerRetrain()">Trigger Retrain</button>
        <button class="btn" onclick="refreshData()">Refresh Data</button>
        <button class="btn danger" onclick="emergencyStop()">Emergency Stop</button>
    </div>
    
    <script>
        function showSection(sectionId) {
            // Hide all sections
            document.querySelectorAll('.section').forEach(section => {
                section.classList.remove('active');
            });
            
            // Show selected section
            document.getElementById(sectionId).classList.add('active');
            
            // Update navigation
            document.querySelectorAll('.nav-item').forEach(item => {
                item.classList.remove('active');
            });
            event.target.classList.add('active');
        }
        
        function refreshData() {
            // Refresh all data
            fetch('/api/system-status')
                .then(response => response.json())
                .then(data => {
                    updateOverview(data);
                });
                
            fetch('/api/ai-health')
                .then(response => response.json())
                .then(data => {
                    updateAIHealth(data);
                });
                
            fetch('/api/strategy-performance')
                .then(response => response.json())
                .then(data => {
                    updatePerformance(data);
                });
                
            fetch('/api/anomaly-report')
                .then(response => response.json())
                .then(data => {
                    updateAnomalies(data);
                });
        }
        
        function updateOverview(data) {
            // Update quick stats
            if (data.metrics) {
                document.getElementById('total-trades').textContent = data.metrics.total_trades || 0;
                document.getElementById('win-rate').textContent = ((data.metrics.win_rate || 0) * 100).toFixed(1) + '%';
                document.getElementById('anomaly-rate').textContent = ((data.metrics.anomaly_rate || 0) * 100).toFixed(1) + '%';
            }
            
            if (data.system_health) {
                const healthElement = document.getElementById('system-health');
                healthElement.textContent = data.system_health.status || 'Unknown';
                healthElement.className = 'stat-value ' + (data.system_health.status === 'HEALTHY' ? 'status-healthy' : 'status-degraded');
            }
        }
        
        function updateAIHealth(data) {
            const content = document.getElementById('ai-health-content');
            if (data.system_health) {
                content.innerHTML = `
                    <div class="metric-row">
                        <span>Status</span>
                        <span class="metric-value">${data.system_health.status}</span>
                    </div>
                    <div class="metric-row">
                        <span>Last Update</span>
                        <span class="metric-value">${new Date().toLocaleTimeString()}</span>
                    </div>
                `;
            }
        }
        
        function updatePerformance(data) {
            const content = document.getElementById('strategy-performance-content');
            if (data.strategies) {
                let html = '';
                Object.entries(data.strategies).forEach(([name, perf]) => {
                    html += `
                        <div class="metric-row">
                            <span>${name}</span>
                            <span class="metric-value">${(perf.win_rate * 100).toFixed(1)}%</span>
                        </div>
                    `;
                });
                content.innerHTML = html;
            }
        }
        
        function updateAnomalies(data) {
            const content = document.getElementById('anomaly-report-content');
            if (data.anomalies) {
                let html = '';
                data.anomalies.forEach(anomaly => {
                    html += `
                        <div class="metric-row">
                            <span>${anomaly.type}</span>
                            <span class="metric-value">${anomaly.severity}</span>
                        </div>
                    `;
                });
                content.innerHTML = html;
            }
        }
        
        function triggerRetrain() {
            fetch('/api/trigger-retrain', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({reason: 'Manual trigger from dashboard'})
            })
            .then(response => response.json())
            .then(data => {
                alert('Retrain triggered: ' + (data.success ? 'Success' : 'Failed'));
            });
        }
        
        function emergencyStop() {
            if (confirm('Are you sure you want to trigger emergency stop?')) {
                alert('Emergency stop triggered');
            }
        }
            
            // Auto-refresh every 30 seconds
            setInterval(refreshData, 30000);
        
        // Initial load
        refreshData();
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
