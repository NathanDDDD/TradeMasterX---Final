#!/usr/bin/env python3
"""
TradeMasterX 2.0 - Main Application Launcher (Clean Version)
Final Production-Ready AI Trading System

Launch Command: python main_app_clean.py
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
    print(f"Import Error: {e}")
    print("Please ensure you're running from the project root directory")
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
                logging.FileHandler(logs_dir / "trademasterx_main.log", encoding='utf-8'),
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
║  Autonomous AI Trading Intelligence                                          ║
║  Real-time Monitoring & Analytics                                            ║
║  Machine Learning Optimization                                               ║
║  Advanced Anomaly Detection                                                  ║
║  Web Dashboard Interface                                                     ║
║  Command Assistant Integration                                               ║
╚══════════════════════════════════════════════════════════════════════════════╝
        """
        print(banner)
        print(f"Launch Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Project Root: {PROJECT_ROOT}")
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
            self.logger.info("Configuration loaded successfully")
            return config
            
        except Exception as e:
            self.logger.warning(f"Using default configuration due to: {e}")
            return {
                'app_name': self.app_name,
                'version': self.version,
                'web_port': self.web_port,
                'auto_open_browser': True,
                'demo_mode': True,
                'enable_command_assistant': True,
                'log_level': 'INFO'
            }
    
    def check_environment(self) -> dict:
        """Check if environment is properly configured"""
        self.logger.info("Checking environment...")
        
        # Check required directories
        required_dirs = ['logs_clean', 'reports_clean', 'core_clean']
        for dir_name in required_dirs:
            dir_path = Path(dir_name)
            if not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)
                self.logger.info(f"Created directory: {dir_name}")
        
        # Check .env file
        env_file = Path('.env')
        if not env_file.exists():
            self.logger.warning(".env file not found - using demo mode")
            self.create_sample_env()
        
        # Check dependencies
        issues = []
        try:
            import numpy, pandas, aiohttp, scipy
            self.logger.info("Dependencies check passed")
        except ImportError as e:
            self.logger.error(f"Missing dependencies: {e}")
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
            
        self.logger.info("Created .env.example file - please configure for live trading")
    
    async def initialize_components(self, config: dict):
        """Initialize all TradeMasterX components"""
        self.logger.info("Initializing TradeMasterX components...")
        
        try:
            # Initialize Phase 14 Autonomous AI System
            self.logger.info("Starting Autonomous AI System...")
            self.autonomous_ai = Phase14AutonomousAI(config)
            
            # Initialize Command Assistant if enabled
            if config.get('enable_command_assistant', True):
                self.logger.info("Starting Command Assistant...")
                self.command_assistant = CommandAssistant(personality='professional')
                
            self.logger.info("All components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Component initialization failed: {e}")
            raise
    
    async def start_background_systems(self):
        """Start background systems"""
        self.logger.info("Starting background systems...")
        
        # Start autonomous AI system
        if self.autonomous_ai:
            await self.autonomous_ai.start_autonomous_system()
            self.logger.info("Autonomous AI system started in background")
        
        # Command assistant is ready
        if self.command_assistant:
            self.logger.info("Command Assistant ready for use")
    
    def print_startup_summary(self, config: dict):
        """Print startup summary"""
        print("\n" + "=" * 80)
        print("TRADEMASTERX 2.0 SUCCESSFULLY LAUNCHED!")
        print("=" * 80)
        print()
        print("SYSTEM STATUS:")
        print("   Autonomous AI: Active")
        print("   Command Assistant: Active")
        print("   Web Dashboard: Active (Port 8080)")
        print("   Trading Mode: Demo Mode")
        print()
        print("ACCESS POINTS:")
        print(f"   Web Dashboard: http://localhost:{self.web_port}")
        print(f"   Logs: {Path('logs_clean').absolute()}")
        print(f"   Reports: {Path('reports_clean').absolute()}")
        print()
        print("AVAILABLE COMMANDS:")
        print("   ai status       - Check AI system health")
        print("   ai retrain      - Trigger model retraining")
        print("   ai monitor      - View monitoring data")
        print("   ai anomalies    - Check anomaly reports")
        print("   ai dashboard    - Open web dashboard")
        print()
        print("CONFIGURATION:")
        print(f"   Demo Mode: {config.get('demo_mode', True)}")
        print("   Auto Retrain: True")
        print("   Anomaly Detection: True")
        print()
        print("GETTING STARTED:")
        print("   1. You're in DEMO MODE - safe to explore all features")
        print("   2. Open the web dashboard to monitor system")
        print("   3. Try command assistant: 'ai status'")
        print("   4. Watch real-time monitoring and AI decisions")
        print("   5. Configure .env file for live trading")
        print()
        print("IMPORTANT:")
        print("   • Press Ctrl+C to gracefully shutdown")
        print("   • Monitor logs for system health")
        print("   • Backup important data regularly")
        print()
        print("=" * 80)
        print()
        print("Interactive Mode Active - Type 'help' for commands")
        print("Type 'exit' to shutdown gracefully")
        print()
    
    async def run_interactive_mode(self):
        """Run interactive command mode"""
        print("TradeMasterX> ", end="", flush=True)
        
        while self.running:
            try:
                command = await asyncio.get_event_loop().run_in_executor(None, input)
                command = command.strip().lower()
                
                if command in ['exit', 'quit', 'stop']:
                    await self.shutdown()
                    break
                elif command == 'help':
                    self.print_help()
                elif command == 'status':
                    await self.show_status()
                elif command.startswith('ai '):
                    if self.command_assistant:
                        response = await self.command_assistant.process_command(command[3:])
                        print(f"Response: {response}")
                    else:
                        print("Command Assistant not available")
                else:
                    print(f"Unknown command: {command}")
                    print("Type 'help' for available commands")
                
                print("TradeMasterX> ", end="", flush=True)
                
            except KeyboardInterrupt:
                await self.shutdown()
                break
            except Exception as e:
                self.logger.error(f"Error in interactive mode: {e}")
                print("TradeMasterX> ", end="", flush=True)
    
    def print_help(self):
        """Print help information"""
        print("\nAvailable Commands:")
        print("  help          - Show this help")
        print("  status        - Show system status")
        print("  ai status     - Check AI system health")
        print("  ai retrain    - Trigger model retraining")
        print("  ai monitor    - View monitoring data")
        print("  ai anomalies  - Check anomaly reports")
        print("  ai dashboard  - Open web dashboard")
        print("  exit          - Shutdown gracefully")
        print()
    
    async def show_status(self):
        """Show system status"""
        print("\nSystem Status:")
        print(f"  App Name: {self.app_name}")
        print(f"  Version: {self.version}")
        print(f"  Running: {self.running}")
        print(f"  Web Port: {self.web_port}")
        print(f"  Autonomous AI: {'Active' if self.autonomous_ai else 'Inactive'}")
        print(f"  Command Assistant: {'Active' if self.command_assistant else 'Inactive'}")
        print()
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            self.logger.info("Received shutdown signal")
            asyncio.create_task(self.shutdown())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def shutdown(self):
        """Gracefully shutdown the application"""
        self.logger.info("Shutting down TradeMasterX...")
        self.running = False
        
        if self.autonomous_ai:
            await self.autonomous_ai.shutdown()
        
        self.logger.info("TradeMasterX shutdown complete")
    
    async def run(self):
        """Main application run loop"""
        try:
            # Load configuration
            config = self.load_configuration()
            
            # Check environment
            env_check = self.check_environment()
            if not env_check['ready']:
                self.logger.error(f"Environment issues: {env_check['issues']}")
                return False
            
            # Initialize components
            await self.initialize_components(config)
            
            # Start background systems
            await self.start_background_systems()
            
            # Print startup summary
            self.print_startup_summary(config)
            
            # Setup signal handlers
            self.setup_signal_handlers()
            
            # Set running flag
            self.running = True
            
            # Run interactive mode
            await self.run_interactive_mode()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Application error: {e}")
            return False

async def main():
    """Main entry point"""
    app = TradeMasterXApp()
    app.print_banner()
    
    try:
        success = await app.run()
        return 0 if success else 1
    except Exception as e:
        app.logger.error(f"Fatal error: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 