#!/usr/bin/env python3
"""
Simple web server test for TradeMasterX 2.0
"""

import asyncio
import socket
import sys
from aiohttp import web

def check_port_available(host, port):
    """Check if a port is available"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, port))
            return True
    except OSError:
        return False

async def simple_dashboard(request):
    """Simple dashboard page"""
    html = """
<!DOCTYPE html>
<html>
<head>
    <title>TradeMasterX 2.0 - Test Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f0f0f0; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }
        .status { padding: 10px; margin: 10px 0; border-radius: 5px; }
        .success { background: #d4edda; color: #155724; }
        .info { background: #d1ecf1; color: #0c5460; }
    </style>
</head>
<body>
    <div class="container">
        <h1> TradeMasterX 2.0 - Test Dashboard</h1>
        <div class="status success">
            ✅ Web server is running successfully!
        </div>
        <div class="status info">
            📊 This is a test dashboard to verify web server functionality.
        </div>
        <h2>System Status</h2>
        <ul>
            <li>🌐 Web Server: Running</li>
            <li>🔧 Port: 8080</li>
            <li>📁 Status: Test Mode</li>
        </ul>
        <h2>Next Steps</h2>
        <p>If you can see this page, the web server is working correctly. The main application should now be able to start its dashboard.</p>
    </div>
</body>
</html>
    """
    return web.Response(text=html, content_type='text/html')

async def api_status(request):
    """API status endpoint"""
    return web.json_response({
        'status': 'success',
        'message': 'Web server is running',
        'port': 8080
    })

async def start_test_server():
    """Start a simple test web server"""
    print("Testing web server functionality...")
    
    # Check if port is available
    if not check_port_available('localhost', 8080):
        print("❌ Port 8080 is already in use!")
        print("   Try using a different port or stop other services using port 8080")
        return False
    
    print("✅ Port 8080 is available")
    
    # Create web app
    app = web.Application()
    app.router.add_get('/', simple_dashboard)
    app.router.add_get('/api/status', api_status)
    
    # Start server
    runner = web.AppRunner(app)
    await runner.setup()
    
    site = web.TCPSite(runner, 'localhost', 8080)
    await site.start()
    
    print("✅ Test web server started successfully!")
    print("🌐 Dashboard available at: http://localhost:8080")
    print("📊 API status at: http://localhost:8080/api/status")
    print("🔄 Server will run for 30 seconds...")
    
    # Run for 30 seconds
    await asyncio.sleep(30)
    
    # Shutdown
    await runner.cleanup()
    print("🛑 Test server stopped")
    
    return True

def main():
    """Main function"""
    print("TradeMasterX 2.0 - Web Server Test")
    print("=" * 40)
    
    try:
        success = asyncio.run(start_test_server())
        if success:
            print("✅ Web server test completed successfully!")
            return 0
        else:
            print("❌ Web server test failed!")
            return 1
    except Exception as e:
        print(f"❌ Error during web server test: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 