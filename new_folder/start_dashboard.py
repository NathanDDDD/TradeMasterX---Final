#!/usr/bin/env python3
"""
TradeMasterX 2.0 - Standalone Dashboard Launcher
Starts the AI dashboard directly without the main application
"""

import asyncio
import sys
from pathlib import Path

async def start_dashboard():
    """Start the AI dashboard directly"""
    print("TradeMasterX 2.0 - Standalone Dashboard")
    print("=" * 40)
    
    try:
        # Import the dashboard
        from trademasterx.interface.web.ai_dashboard import AIDashboard
        
        # Create config
        config = {
            'dashboard_host': 'localhost',
            'dashboard_port': 8080,
            'demo_mode': True
        }
        
        # Create and start dashboard
        dashboard = AIDashboard(config)
        
        print(f"Starting dashboard on http://{config['dashboard_host']}:{config['dashboard_port']}")
        print("Press Ctrl+C to stop")
        
        # Start the dashboard
        await dashboard.start_dashboard()
        
        # Keep running
        while True:
            await asyncio.sleep(1)
            
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure you're in the correct directory")
        return False
    except Exception as e:
        print(f"Error starting dashboard: {e}")
        return False

def main():
    """Main function"""
    try:
        asyncio.run(start_dashboard())
        return 0
    except KeyboardInterrupt:
        print("\nDashboard stopped")
        return 0
    except Exception as e:
        print(f"Fatal error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 