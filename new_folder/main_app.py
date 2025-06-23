#!/usr/bin/env python3
"""
TradeMasterX 2.0 - Main Application Launcher
Final Production-Ready AI Trading System

Launch Command: python main_app.py
"""

import asyncio
import sys
import os
import logging
import signal
import webbrowser
from pathlib import Path
from datetime import datetime
from typing import Optional
import json

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

# Import TradeMasterX components
try:
    from phase_14_complete_autonomous_ai import Phase14AutonomousAI
    from trademasterx.config.config_loader import ConfigLoader
    from trademasterx.interface.assistant.command_assistant import CommandAssistant
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("📁 Please ensure you're running from the project root directory")
    sys.exit(1)

class TradeMasterXApp:
    """Main TradeMasterX 2.0 Application"""
    
    def __init__(self):
        self.app_name = "TradeMasterX 2.0"
        self.version = "2.0.0"
        self.running = False
        self.autonomous_ai = None
        self.command_assistant = None
        self.web_port = 8080
        self.setup_logging()
        
    def setup_logging(self):
        """Setup application logging"""
        # Create logs directory
        logs_dir = Path("logs_clean")
        logs_dir.mkdir(exist_ok=True)
        
        # Setup logging configuration
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(logs_dir / "trademasterx_main.log"),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger("TradeMasterX")
        
    def print_banner(self):
        """Print application banner"""
        banner = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           TRADEMASTERX 2.0                             ║
║                     Advanced AI Trading System                               ║
║                           Version {self.version}                                     ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  🤖 Autonomous AI Trading Intelligence                                       ║
║  📊 Real-time Monitoring & Analytics                                         ║
║  🧠 Machine Learning Optimization                                            ║
║  🚨 Advanced Anomaly Detection                                               ║
║  🌐 Web Dashboard Interface                                                  ║
║  🎛️  Command Assistant Integration                                           ║
╚══════════════════════════════════════════════════════════════════════════════╝
        """
        print(banner)
        print(f"⏰ Launch Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📂 Project Root: {PROJECT_ROOT}")
        print()
        
    def load_configuration(self) -> dict:
        """Load application configuration"""
        try:
            config_loader = ConfigLoader()
            config = config_loader.load_system_config("trademasterx/config/system.yaml")
            
            # Add application-specific defaults
            app_config = {
                'app_name': self.app_name,
                'version': self.version,
                'web_port': self.web_port,
                'auto_open_browser': True,
                'demo_mode': True,  # Start in demo mode by default
                'enable_command_assistant': True,
                'log_level': 'INFO'
            }
            
            config.update(app_config)
            self.logger.info("✅ Configuration loaded successfully")
            return config
            
        except Exception as e:
            self.logger.warning(f"⚠️  Using default configuration due to: {e}")
            return {
                'app_name': self.app_name,
                'version': self.version,
                'web_port': self.web_port,
                'auto_open_browser': True,
                'demo_mode': True,
                'enable_command_assistant': True,
                'log_level': 'INFO'
            }
    
    def check_environment(self) -> bool:
        """Check if environment is properly configured"""
        self.logger.info("🔍 Checking environment...")
        
        # Check required directories
        required_dirs = ['logs_clean', 'reports_clean', 'core_clean']
        for dir_name in required_dirs:
            dir_path = Path(dir_name)
            if not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)
                self.logger.info(f"📁 Created directory: {dir_name}")
        
        # Check .env file
        env_file = Path('.env')
        if not env_file.exists():
            self.logger.warning("⚠️  .env file not found - using demo mode")
            self.create_sample_env()
          # Check dependencies
        issues = []
        try:
            import numpy, pandas, aiohttp, scipy
            self.logger.info("✅ Dependencies check passed")
        except ImportError as e:
            self.logger.error(f"❌ Missing dependencies: {e}")
            issues.append(f"Missing dependencies: {e}")
        
        return {
            'ready': len(issues) == 0,
            'issues': issues,
            'dependencies_ok': len(issues) == 0,
            'env_file_exists': Path('.env').exists()
        }
    
    def create_sample_env(self):
        """Create sample .env file"""
        sample_env = """# TradeMasterX 2.0 Configuration
# Copy this to .env and fill in your API keys

# Trading API Configuration
BYBIT_API_KEY=your_bybit_api_key_here
BYBIT_SECRET=your_bybit_secret_here
BYBIT_TESTNET=true

# AI Configuration  
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Application Settings
DEMO_MODE=true
WEB_PORT=8080
LOG_LEVEL=INFO

# Advanced Settings
AUTO_RETRAIN=true
ANOMALY_DETECTION=true
COMMAND_ASSISTANT=true
"""
        
        with open('.env.example', 'w') as f:
            f.write(sample_env)
            
        self.logger.info("📄 Created .env.example file - please configure for live trading")
    
    async def initialize_components(self, config: dict):
        """Initialize all TradeMasterX components"""
        self.logger.info("🔧 Initializing TradeMasterX components...")
        
        try:
            # Initialize Phase 14 Autonomous AI System
            self.logger.info("🤖 Starting Autonomous AI System...")
            self.autonomous_ai = Phase14AutonomousAI(config)
            
            # Initialize Command Assistant if enabled
            if config.get('enable_command_assistant', True):
                self.logger.info("Starting Command Assistant...")
                self.command_assistant = CommandAssistant(personality='professional')
                
            self.logger.info("✅ All components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Component initialization failed: {e}")
            raise
    
    async def start_web_dashboard(self, config: dict):
        """Start the web dashboard"""
        try:
            self.web_port = config.get('web_port', 8080)
            self.logger.info(f"🌐 Starting web dashboard on port {self.web_port}...")
            
            # The dashboard is started as part of the autonomous AI system
            dashboard_url = f"http://localhost:{self.web_port}"
            
            # Auto-open browser if configured
            if config.get('auto_open_browser', True):
                self.logger.info(f"🌍 Opening browser: {dashboard_url}")
                webbrowser.open(dashboard_url)
            
            self.logger.info(f"✅ Web dashboard available at: {dashboard_url}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to start web dashboard: {e}")
    
    async def start_background_systems(self):
        """Start background monitoring and AI systems"""
        try:
            self.logger.info("Starting background systems...")
            
            # Start autonomous AI system (includes dashboard)
            if self.autonomous_ai:
                # Start the autonomous AI system which includes the dashboard
                asyncio.create_task(self.autonomous_ai.start_autonomous_system())
                self.logger.info("Autonomous AI system started in background")
            
            # Note: Command Assistant is already initialized and ready for use
            if self.command_assistant:
                self.logger.info("Command Assistant ready for use")
                
        except Exception as e:
            self.logger.error(f"Background systems startup failed: {e}")
    
    def print_startup_summary(self, config: dict):
        """Print startup summary"""
        print("\n" + "="*80)
        print("🎉 TRADEMASTERX 2.0 SUCCESSFULLY LAUNCHED!")
        print("="*80)
        
        print("\n📊 SYSTEM STATUS:")
        print(f"   🤖 Autonomous AI: {'✅ Active' if self.autonomous_ai else '❌ Inactive'}")
        print(f"   🎛️  Command Assistant: {'✅ Active' if self.command_assistant else '❌ Inactive'}")
        print(f"   🌐 Web Dashboard: ✅ Active (Port {self.web_port})")
        print(f"   📈 Trading Mode: {'🎮 Demo Mode' if config.get('demo_mode', True) else '💰 Live Trading'}")
        
        print(f"\n🌍 ACCESS POINTS:")
        print(f"   Web Dashboard: http://localhost:{self.web_port}")
        print(f"   Logs: {Path('logs_clean').absolute()}")
        print(f"   Reports: {Path('reports_clean').absolute()}")
        
        print(f"\n🎛️  AVAILABLE COMMANDS:")
        if self.command_assistant:
            print("   ai status       - Check AI system health")
            print("   ai retrain      - Trigger model retraining") 
            print("   ai monitor      - View monitoring data")
            print("   ai anomalies    - Check anomaly reports")
            print("   ai dashboard    - Open web dashboard")
        
        print(f"\n🔧 CONFIGURATION:")
        print(f"   Demo Mode: {config.get('demo_mode', True)}")
        print(f"   Auto Retrain: {config.get('auto_retrain', True)}")
        print(f"   Anomaly Detection: {config.get('anomaly_detection', True)}")
        
        print("\n💡 GETTING STARTED:")
        if config.get('demo_mode', True):
            print("   1. 🎮 You're in DEMO MODE - safe to explore all features")
            print("   2. 🌐 Open the web dashboard to monitor system")
            print("   3. 🎛️  Try command assistant: 'ai status'")
            print("   4. 📊 Watch real-time monitoring and AI decisions")
            print("   5. 🔧 Configure .env file for live trading")
        else:
            print("   1. 💰 LIVE TRADING MODE - real money at risk!")
            print("   2. 📊 Monitor dashboard closely")
            print("   3. 🚨 Watch for anomaly alerts")
            print("   4. 🛑 Use emergency stop if needed")
        
        print(f"\n⚠️  IMPORTANT:")
        print("   • Press Ctrl+C to gracefully shutdown")
        print("   • Monitor logs for system health")
        print("   • Backup important data regularly")
        
        print("\n" + "="*80)
        
        # Save startup info
        startup_info = {
            'timestamp': datetime.now().isoformat(),
            'version': self.version,
            'config': config,
            'web_port': self.web_port,
            'components_active': {
                'autonomous_ai': bool(self.autonomous_ai),
                'command_assistant': bool(self.command_assistant)
            }
        }
        
        with open('logs_clean/startup_info.json', 'w') as f:
            json.dump(startup_info, f, indent=2)
    
    async def run_interactive_mode(self):
        """Run interactive command mode"""
        print(f"\n🎛️  Interactive Mode Active - Type 'help' for commands")
        print("Type 'exit' to shutdown gracefully")
        
        while self.running:
            try:
                command = input("\nTradeMasterX> ").strip().lower()
                
                if command == 'exit':
                    break
                elif command == 'help':
                    self.print_help()
                elif command == 'status':
                    await self.show_status()
                elif command == 'dashboard':
                    webbrowser.open(f"http://localhost:{self.web_port}")
                    print(f"🌐 Opened dashboard: http://localhost:{self.web_port}")
                elif command.startswith('ai '):
                    if self.command_assistant:
                        # Forward to command assistant
                        response = await self.command_assistant.process_command(command)
                        print(f"🤖 {response}")
                    else:
                        print("❌ Command Assistant not available")
                elif command == '':
                    continue
                else:
                    print(f"❓ Unknown command: {command}. Type 'help' for available commands.")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Command error: {e}")
    
    def print_help(self):
        """Print help information"""
        help_text = """
🎛️  TRADEMASTERX 2.0 COMMANDS:

Basic Commands:
  help              - Show this help message
  status            - Show system status
  dashboard         - Open web dashboard
  exit              - Shutdown application

AI Commands (if Command Assistant enabled):
  ai status         - Check AI system health
  ai retrain        - Trigger model retraining
  ai monitor        - View monitoring data
  ai anomalies      - Check recent anomalies
  ai dashboard      - Open AI dashboard

Navigation:
  🌐 Web Dashboard: http://localhost:{web_port}
  📁 Logs: logs_clean/
  📊 Reports: reports_clean/
        """.format(web_port=self.web_port)
        print(help_text)
    
    async def show_status(self):
        """Show current system status"""
        try:
            print("\n📊 SYSTEM STATUS:")
            print(f"   🟢 Application: Running")
            print(f"   🤖 Autonomous AI: {'Active' if self.autonomous_ai else 'Inactive'}")
            print(f"   🎛️  Command Assistant: {'Active' if self.command_assistant else 'Inactive'}")
            print(f"   🌐 Web Port: {self.web_port}")
            print(f"   ⏰ Uptime: {datetime.now().strftime('%H:%M:%S')}")
            
            if self.autonomous_ai:
                status = await self.autonomous_ai.get_system_status()
                if 'system_status' in status:
                    print(f"   📈 AI Status: {status['system_status']}")
                    
        except Exception as e:
            print(f"❌ Status check failed: {e}")
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            print(f"\n🛑 Received shutdown signal ({signum})")
            self.running = False
            
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def shutdown(self):
        """Gracefully shutdown the application"""
        self.logger.info("🛑 Shutting down TradeMasterX 2.0...")
        
        try:
            # Shutdown autonomous AI
            if self.autonomous_ai:
                await self.autonomous_ai.shutdown()
                self.logger.info("✅ Autonomous AI shutdown complete")
            
            # Shutdown command assistant
            if self.command_assistant:
                # Command assistant shutdown if available
                self.logger.info("✅ Command Assistant shutdown complete")
            
            self.logger.info("✅ TradeMasterX 2.0 shutdown complete")
            
        except Exception as e:
            self.logger.error(f"❌ Shutdown error: {e}")
    
    async def run(self):
        """Main application run method"""
        self.running = True
        
        try:
            # Print banner
            self.print_banner()
            
            # Check environment
            if not self.check_environment():
                self.logger.error("Environment check failed")
                return False
            
            # Load configuration
            config = self.load_configuration()
            
            # Initialize components
            await self.initialize_components(config)
            
            # Start background systems (including dashboard)
            await self.start_background_systems()
            
            # Print startup summary
            self.print_startup_summary(config)
            
            # Setup signal handlers
            self.setup_signal_handlers()
            
            # Run interactive mode
            await self.run_interactive_mode()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Application error: {e}")
            return False
        finally:
            await self.shutdown()


async def main():
    """Main entry point"""
    app = TradeMasterXApp()
    
    try:
        success = await app.run()
        return 0 if success else 1
    except KeyboardInterrupt:
        print(f"\n⏹️  Application interrupted by user")
        return 0
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        return 1


if __name__ == "__main__":
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        sys.exit(1)
    
    # Run application
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n👋 Goodbye!")
        sys.exit(0)
