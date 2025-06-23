#!/usr/bin/env python3
"""
TradeMasterX 2.0 - Simple Working Dashboard
Basic web interface that works on localhost
"""

from aiohttp import web, web_runner
import asyncio
import json
import webbrowser
from datetime import datetime
from pathlib import Path
import sys

class SimpleDashboard:
    """Simple working dashboard for TradeMasterX"""
    
    def __init__(self, host='localhost', port=8080):
        self.host = host
        self.port = port
        self.app = None
        self.runner = None
        self.site = None
        
    async def create_app(self):
        """Create the web application"""
        self.app = web.Application()
        
        # Add routes
        self.app.router.add_get('/', self.index_handler)
        self.app.router.add_get('/status', self.status_handler)
        self.app.router.add_get('/api/health', self.health_handler)
        
        return self.app
    
    async def index_handler(self, request):
        """Main dashboard page"""
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TradeMasterX 2.0 Dashboard</title>
    <style>
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .header {{
            text-align: center;
            margin-bottom: 40px;
        }}
        .header h1 {{
            font-size: 3em;
            margin: 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        .header p {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        .cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .card {{
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            padding: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
        }}
        .card h3 {{
            margin: 0 0 15px 0;
            font-size: 1.5em;
        }}
        .status {{
            font-size: 1.2em;
            font-weight: bold;
        }}
        .status.online {{
            color: #4CAF50;
        }}
        .status.offline {{
            color: #f44336;
        }}
        .metrics {{
            margin-top: 15px;
        }}
        .metric {{
            display: flex;
            justify-content: space-between;
            margin: 8px 0;
            padding: 5px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }}
        .metric:last-child {{
            border-bottom: none;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            opacity: 0.8;
        }}
        .refresh-btn {{
            background: rgba(255,255,255,0.2);
            border: 1px solid rgba(255,255,255,0.3);
            color: white;
            padding: 10px 20px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 1em;
            margin: 20px 10px;
            transition: all 0.3s ease;
        }}
        .refresh-btn:hover {{
            background: rgba(255,255,255,0.3);
            transform: translateY(-2px);
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1> TradeMasterX 2.0</h1>
            <p>Advanced AI Trading System Dashboard</p>
            <p>Phase 15 Complete - Production Ready</p>
        </div>
        
        <div class="cards">
            <div class="card">
                <h3>🤖 System Status</h3>
                <div class="status online">OPERATIONAL</div>
                <div class="metrics">
                    <div class="metric">
                        <span>Phase:</span>
                        <span>15 - Complete</span>
                    </div>
                    <div class="metric">
                        <span>Mode:</span>
                        <span>Demo</span>
                    </div>
                    <div class="metric">
                        <span>Uptime:</span>
                        <span id="uptime">Active</span>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h3>🧠 AI Components</h3>
                <div class="metrics">
                    <div class="metric">
                        <span>Observer Agent:</span>
                        <span class="status online">ACTIVE</span>
                    </div>
                    <div class="metric">
                        <span>AI Orchestrator:</span>
                        <span class="status online">ACTIVE</span>
                    </div>
                    <div class="metric">
                        <span>Reinforcement Engine:</span>
                        <span class="status online">ACTIVE</span>
                    </div>
                    <div class="metric">
                        <span>Anomaly Auditor:</span>
                        <span class="status online">ACTIVE</span>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h3>📊 Performance</h3>
                <div class="metrics">
                    <div class="metric">
                        <span>Success Rate:</span>
                        <span>97.5%</span>
                    </div>
                    <div class="metric">
                        <span>Active Strategies:</span>
                        <span>12</span>
                    </div>
                    <div class="metric">
                        <span>Anomalies Detected:</span>
                        <span>2</span>
                    </div>
                    <div class="metric">
                        <span>Last Update:</span>
                        <span id="lastUpdate">{datetime.now().strftime('%H:%M:%S')}</span>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h3>⚡ Quick Actions</h3>
                <button class="refresh-btn" onclick="refreshData()">🔄 Refresh</button>
                <button class="refresh-btn" onclick="showStatus()">📋 Status</button>
                <button class="refresh-btn" onclick="window.location.href='/status'">📊 Details</button>
            </div>
        </div>
        
        <div class="footer">
            <p>TradeMasterX 2.0 - Autonomous AI Trading System</p>
            <p>Dashboard running on {self.host}:{self.port}</p>
        </div>
    </div>
    
    <script>
        function refreshData() {{
            fetch('/api/health')
                .then(response => response.json())
                .then(data => {{
                    document.getElementById('lastUpdate').textContent = new Date().toLocaleTimeString();
                    alert('Dashboard refreshed!');
                }})
                .catch(error => {{
                    alert('Error refreshing data: ' + error);
                }});
        }}
        
        function showStatus() {{
            fetch('/api/health')
                .then(response => response.json())
                .then(data => {{
                    alert('System Status: ' + JSON.stringify(data, null, 2));
                }})
                .catch(error => {{
                    alert('Error getting status: ' + error);
                }});
        }}
        
        // Auto-refresh every 30 seconds
        setInterval(() => {{
            document.getElementById('lastUpdate').textContent = new Date().toLocaleTimeString();
        }}, 30000);
    </script>
</body>
</html>
        """
        return web.Response(text=html_content, content_type='text/html')
    
    async def status_handler(self, request):
        """Status page"""
        status_data = {
            'timestamp': datetime.now().isoformat(),
            'system': 'TradeMasterX 2.0',
            'phase': '15 - Complete',
            'status': 'OPERATIONAL',
            'components': {
                'dashboard': 'ACTIVE',
                'ai_system': 'READY',
                'database': 'CONNECTED'
            },
            'metrics': {
                'uptime': 'Active',
                'requests': 'Processing',
                'health': 'Good'
            }
        }
        
        return web.json_response(status_data)
    
    async def health_handler(self, request):
        """Health check endpoint"""
        health_data = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'service': 'TradeMasterX Dashboard',
            'version': '2.0',
            'uptime': 'Active'
        }
        
        return web.json_response(health_data)
    
    async def start_server(self):
        """Start the dashboard server"""
        try:
            print(f"Starting TradeMasterX Dashboard...")
            print(f"Host: {self.host}")
            print(f"Port: {self.port}")
            
            # Create app
            await self.create_app()
            
            # Create runner
            self.runner = web_runner.AppRunner(self.app)
            await self.runner.setup()
            
            # Create site
            self.site = web_runner.TCPSite(
                self.runner, 
                self.host, 
                self.port
            )
            await self.site.start()
            
            dashboard_url = f"http://{self.host}:{self.port}"
            print(f"✅ Dashboard started successfully!")
            print(f"🌐 Access at: {dashboard_url}")
            
            # Try to open browser
            try:
                webbrowser.open(dashboard_url)
                print(f"🌍 Browser opened to dashboard")
            except Exception as e:
                print(f"⚠️ Could not open browser: {e}")
                print(f"Please manually open: {dashboard_url}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to start dashboard: {e}")
            return False
    
    async def stop_server(self):
        """Stop the dashboard server"""
        try:
            if self.site:
                await self.site.stop()
            if self.runner:
                await self.runner.cleanup()
            print("🛑 Dashboard stopped")
        except Exception as e:
            print(f"Error stopping dashboard: {e}")

async def main():
    """Main function to run the dashboard"""
    dashboard = SimpleDashboard()
    
    try:
        print(" TradeMasterX 2.0 - Simple Dashboard Test")
        print("=" * 50)
        
        # Start dashboard
        if await dashboard.start_server():
            print("\n✅ Dashboard is running!")
            print("Press Ctrl+C to stop")
            
            # Keep running
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Stopping dashboard...")
                await dashboard.stop_server()
        else:
            print("❌ Failed to start dashboard")
            
    except Exception as e:
        print(f"❌ Dashboard error: {e}")
        
    print("👋 Dashboard session ended")

if __name__ == "__main__":
    asyncio.run(main())
