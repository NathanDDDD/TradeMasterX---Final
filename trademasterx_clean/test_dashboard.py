#!/usr/bin/env python3
"""
TradeMasterX 2.0 - Simple Dashboard Test
Test localhost dashboard functionality
"""

import asyncio
import sys
from pathlib import Path
import webbrowser
import time

# Add project paths
current_dir = Path(__file__).parent.absolute()
sys.path.append(str(current_dir))

async def test_dashboard():
    """Test dashboard startup"""
    print("🌐 Testing TradeMasterX Dashboard...")
    
    try:
        # Import dashboard
        from trademasterx.interface.web.ai_dashboard import AIDashboard
        
        # Create simple config
        config = {
            'demo_mode': True,
            'web_dashboard': {
                'host': 'localhost',
                'port': 8080
            }
        }
        
        # Initialize dashboard
        dashboard = AIDashboard(config)
        
        print(f"Dashboard initialized")
        print(f"Host: {dashboard.host}")
        print(f"Port: {dashboard.port}")
        print(f"Dashboard URL: http://{dashboard.host}:{dashboard.port}")
        
        # Start server in background
        print("\nStarting dashboard server...")
          # Create a task to start the server
        server_task = asyncio.create_task(dashboard.start_dashboard())
        
        # Wait a moment for server to start
        await asyncio.sleep(2)
        
        # Try to open browser
        dashboard_url = f"http://{dashboard.host}:{dashboard.port}"
        print(f"Opening browser to: {dashboard_url}")
        
        try:
            webbrowser.open(dashboard_url)
            print("✅ Browser opened successfully")
        except Exception as e:
            print(f"⚠️ Could not open browser: {e}")
        
        print("\n🔗 Dashboard should now be accessible at:")
        print(f"   {dashboard_url}")
        print("\nPress Ctrl+C to stop the dashboard")
        
        # Keep server running
        try:
            await server_task
        except asyncio.CancelledError:
            print("\n🛑 Dashboard stopped")
        
    except Exception as e:
        print(f"❌ Dashboard test failed: {e}")
        return False
    
    return True

async def quick_dashboard_test():
    """Quick test without starting full server"""
    print("🔍 Quick Dashboard Component Test...")
    
    try:
        from trademasterx.interface.web.ai_dashboard import AIDashboard
        
        config = {'demo_mode': True}
        dashboard = AIDashboard(config)
        
        print(f"✅ Dashboard component created")
        print(f"   Host: {dashboard.host}")
        print(f"   Port: {dashboard.port}")
        print(f"   URL: http://{dashboard.host}:{dashboard.port}")
        
        return True
        
    except Exception as e:
        print(f"❌ Dashboard component test failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("TRADEMASTERX 2.0 - DASHBOARD TEST")
    print("=" * 60)
    
    # First do quick test
    if asyncio.run(quick_dashboard_test()):
        print("\n" + "=" * 60)
        print("STARTING FULL DASHBOARD TEST")
        print("=" * 60)
        
        try:
            asyncio.run(test_dashboard())
        except KeyboardInterrupt:
            print("\n👋 Dashboard test ended by user")
        except Exception as e:
            print(f"\n❌ Dashboard test error: {e}")
    else:
        print("\n❌ Quick test failed - skipping full test")
        
    print("\n🎯 Dashboard test complete")
