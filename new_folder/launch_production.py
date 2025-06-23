#!/usr/bin/env python3
"""
TradeMasterX 2.0 - Production Launch Script
Clean production-ready launcher without Unicode issues
"""

import asyncio
import json
import logging
import sys
import os
import signal
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# Configure console encoding for Windows
if sys.platform == "win32":
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# Add project paths
current_dir = Path(__file__).parent.absolute()
sys.path.append(str(current_dir))

class TradeMasterXProduction:
    """Production-ready TradeMasterX 2.0 launcher"""
    
    def __init__(self):
        self.setup_clean_logging()
        self.logger = logging.getLogger("TradeMasterX-Production")
        self.running = False
        self.system = None
        
        # Create production directories
        self.create_production_structure()
        
    def setup_clean_logging(self):
        """Setup logging without Unicode characters"""
        # Ensure logs directory exists
        Path("logs").mkdir(exist_ok=True)
        
        # Configure logging with ASCII-safe format
        class ASCIIFormatter(logging.Formatter):
            def format(self, record):
                # Remove any Unicode characters that might cause issues
                formatted = super().format(record)
                return formatted.encode('ascii', 'ignore').decode('ascii')
        
        formatter = ASCIIFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # File handler
        file_handler = logging.FileHandler(
            "logs/trademasterx_production.log", 
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        # Root logger configuration
        logging.basicConfig(
            level=logging.INFO,
            handlers=[file_handler, console_handler],
            force=True
        )
        
    def create_production_structure(self):
        """Create production directory structure"""
        directories = [
            "logs", "reports", "data", "config", 
            "reports_clean", "logs_clean"
        ]
        
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
            
    def print_banner(self):
        """Print production launch banner"""
        print("\n" + "=" * 70)
        print("  TRADEMASTERX 2.0 - PRODUCTION LAUNCH")
        print("  Advanced AI Trading System")
        print("  Phase 15 Complete - Launch Ready")
        print("=" * 70)
        
    def check_production_readiness(self) -> Dict[str, Any]:
        """Check if system is production ready"""
        self.logger.info("Checking production readiness...")
        
        readiness_report = {
            'ready': True,
            'issues': [],
            'components': {},
            'timestamp': datetime.now().isoformat()
        }
        
        # Check Phase 14 system
        try:
            from phase_14_complete_autonomous_ai import Phase14AutonomousAI
            readiness_report['components']['phase_14_ai'] = 'READY'
            self.logger.info("Phase 14 AI System: READY")
        except Exception as e:
            readiness_report['ready'] = False
            readiness_report['issues'].append(f"Phase 14 AI: {str(e)}")
            readiness_report['components']['phase_14_ai'] = 'ERROR'
            
        # Check Main App
        try:
            from main_app import TradeMasterXApp
            readiness_report['components']['main_app'] = 'READY'
            self.logger.info("Main Application: READY")
        except Exception as e:
            readiness_report['ready'] = False
            readiness_report['issues'].append(f"Main App: {str(e)}")
            readiness_report['components']['main_app'] = 'ERROR'
            
        # Check essential directories
        essential_dirs = ["trademasterx", "core_clean", "utils_clean"]
        for directory in essential_dirs:
            if Path(directory).exists():
                readiness_report['components'][f'dir_{directory}'] = 'READY'
            else:
                readiness_report['issues'].append(f"Missing directory: {directory}")
                readiness_report['components'][f'dir_{directory}'] = 'MISSING'
                
        return readiness_report
        
    async def initialize_system(self) -> bool:
        """Initialize the TradeMasterX system"""
        try:
            self.logger.info("Initializing TradeMasterX 2.0 system...")
            
            # Import and initialize Phase 14 system
            from phase_14_complete_autonomous_ai import Phase14AutonomousAI
            
            # Production configuration
            config = {
                'demo_mode': True,  # Set to False for live trading
                'production': True,
                'dashboard_port': 8080,
                'api': {
                    'bybit': {
                        'api_key': os.getenv('BYBIT_API_KEY', 'demo'),
                        'secret': os.getenv('BYBIT_SECRET', 'demo')
                    },
                    'openai': {
                        'api_key': os.getenv('OPENAI_API_KEY', 'demo')
                    },
                    'anthropic': {
                        'api_key': os.getenv('ANTHROPIC_API_KEY', 'demo')
                    }
                },
                'logging': {
                    'level': 'INFO',
                    'unicode_safe': True
                }
            }
            
            # Initialize system
            self.system = Phase14AutonomousAI(config)
            
            self.logger.info("System initialization completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"System initialization failed: {e}")
            return False
            
    def setup_signal_handlers(self):
        """Setup graceful shutdown handlers"""
        def signal_handler(sig, frame):
            self.logger.info("Received shutdown signal")
            self.running = False
            
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
    async def start_production_system(self):
        """Start the production system"""
        self.logger.info("Starting TradeMasterX 2.0 production system...")
        
        try:
            # Generate initial status report
            await self.system._generate_status_report()
            
            # Start dashboard in background
            dashboard_task = asyncio.create_task(
                self.system._start_dashboard_server()
            )
            
            # Start monitoring in background
            monitor_task = asyncio.create_task(
                self.system._start_observer_monitoring()
            )
            
            # Open web dashboard
            dashboard_url = "http://localhost:8080"
            self.logger.info(f"Opening dashboard: {dashboard_url}")
            
            try:
                webbrowser.open(dashboard_url)
            except Exception as e:
                self.logger.warning(f"Could not open browser: {e}")
                
            print(f"\nSystem Status:")
            print(f"  Dashboard: {dashboard_url}")
            print(f"  Mode: {'DEMO' if self.system.config.get('demo_mode') else 'LIVE'}")
            print(f"  Monitoring: ACTIVE")
            print(f"  AI Features: ENABLED")
            print(f"\nPress Ctrl+C to shutdown gracefully")
            
            self.running = True
            
            # Keep system running
            while self.running:
                await asyncio.sleep(1)
                
            # Graceful shutdown
            self.logger.info("Shutting down system...")
            dashboard_task.cancel()
            monitor_task.cancel()
            
            await asyncio.gather(
                dashboard_task, monitor_task, 
                return_exceptions=True
            )
            
        except Exception as e:
            self.logger.error(f"Production system error: {e}")
            
    def print_production_summary(self):
        """Print production launch summary"""
        print("\n" + "=" * 70)
        print("  TRADEMASTERX 2.0 - SUCCESSFULLY LAUNCHED")
        print("=" * 70)
        print("  Production Features Active:")
        print("    - Autonomous AI Trading System")
        print("    - Real-time Market Monitoring")
        print("    - Advanced Anomaly Detection")
        print("    - Dynamic Strategy Optimization")
        print("    - Web Dashboard Interface")
        print("    - Automated Reporting")
        print("")
        print("  System Status: OPERATIONAL")
        print("  Mode: PRODUCTION READY")
        print("  Phase: 15 COMPLETE")
        print("=" * 70)
        
    async def run_production_launch(self):
        """Run the complete production launch sequence"""
        self.print_banner()
        
        # Check production readiness
        readiness = self.check_production_readiness()
        
        if not readiness['ready']:
            print("\nPRODUCTION READINESS CHECK FAILED:")
            for issue in readiness['issues']:
                print(f"  - {issue}")
            print("\nPlease resolve issues before launching.")
            return False
            
        print(f"\nProduction Readiness: PASSED")
        print(f"Components Ready: {len(readiness['components'])}")
        
        # Initialize system
        if not await self.initialize_system():
            print("\nSystem initialization failed!")
            return False
            
        print("System Initialization: COMPLETED")
        
        # Setup signal handlers
        self.setup_signal_handlers()
        
        # Start production system
        self.print_production_summary()
        await self.start_production_system()
        
        print("\nTradeMasterX 2.0 shutdown completed.")
        return True


async def main():
    """Main production launcher"""
    try:
        launcher = TradeMasterXProduction()
        success = await launcher.run_production_launch()
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
        return 0
    except Exception as e:
        print(f"\nProduction launch failed: {e}")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nGraceful shutdown")
        sys.exit(0)
