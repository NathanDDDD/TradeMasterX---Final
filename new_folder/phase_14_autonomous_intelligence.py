#!/usr/bin/env python3
"""
TradeMasterX 2.0 - Phase 14: Autonomous Intelligence Integration
Main orchestrator that integrates all AI components and generates ai_status.json
"""

import asyncio
import json
import logging
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add project to path
current_dir = Path(__file__).parent.absolute()
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root))

# Import AI components
from trademasterx.ai.observer_agent import ObserverAgent
from trademasterx.ai.ai_orchestrator import AIOrchestrator
from trademasterx.ai.reinforcement_engine import ReinforcementEngine
from trademasterx.ai.anomaly_auditor import AnomalyAuditor
from trademasterx.interface.web.ai_dashboard import AIDashboard

# Import existing components
try:
    from trademasterx.config.config_loader import ConfigLoader
    from trademasterx.interface.assistant.command_assistant import CommandAssistant
except ImportError as e:
    print(f"Warning: Could not import TradeMasterX components: {e}")
    ConfigLoader = None
    CommandAssistant = None

class Phase14AutonomousIntelligence:
    """Main coordinator for Phase 14 Autonomous Intelligence Layer"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {"demo_mode": True}
        self.logger = logging.getLogger("Phase14AI")
        
        # AI Components
        self.observer_agent = None
        self.ai_orchestrator = None
        self.reinforcement_engine = None
        self.anomaly_auditor = None
        self.ai_dashboard = None
        self.command_assistant = None
        
        # State tracking
        self.system_state = {
            'phase': 14,
            'status': 'INITIALIZING',
            'start_time': datetime.now().isoformat(),
            'components_initialized': [],
            'components_active': [],
            'last_health_check': None
        }
        
        # File paths
        self.ai_status_file = Path("reports/ai_status.json")
        self.ai_status_file.parent.mkdir(exist_ok=True)
        
        # Setup logging
        self._setup_logging()
        
    def _setup_logging(self):
        """Setup comprehensive logging for Phase 14"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "phase_14_autonomous_ai.log", encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
    async def initialize_system(self):
        """Initialize all Phase 14 AI components"""
        self.logger.info(" PHASE 14: AUTONOMOUS INTELLIGENCE LAYER INITIALIZATION")
        self.logger.info("=" * 80)
        
        try:
            # 1. Initialize Observer Agent
            self.logger.info("📡 Initializing Observer Agent...")
            self.observer_agent = ObserverAgent(self.config)
            self.system_state['components_initialized'].append('observer_agent')
            self.logger.info("✅ Observer Agent initialized")
            
            # 2. Initialize Reinforcement Engine
            self.logger.info("⚖️ Initializing Reinforcement Engine...")
            self.reinforcement_engine = ReinforcementEngine(self.config)
            self.system_state['components_initialized'].append('reinforcement_engine')
            self.logger.info("✅ Reinforcement Engine initialized")
            
            # 3. Initialize Anomaly Auditor
            self.logger.info("🚨 Initializing Anomaly Auditor...")
            self.anomaly_auditor = AnomalyAuditor(self.config)
            self.system_state['components_initialized'].append('anomaly_auditor')
            self.logger.info("✅ Anomaly Auditor initialized")
            
            # 4. Initialize AI Orchestrator
            self.logger.info("🎼 Initializing AI Orchestrator...")
            self.ai_orchestrator = AIOrchestrator(self.config)
            self.ai_orchestrator.inject_components(
                observer=self.observer_agent,
                reinforcement=self.reinforcement_engine,
                auditor=self.anomaly_auditor
            )
            self.system_state['components_initialized'].append('ai_orchestrator')
            self.logger.info("✅ AI Orchestrator initialized")
            
            # 5. Initialize AI Dashboard
            self.logger.info("🌐 Initializing AI Dashboard...")
            dashboard_config = {
                **self.config,
                'dashboard_host': 'localhost',
                'dashboard_port': 8080
            }
            self.ai_dashboard = AIDashboard(dashboard_config)
            self.ai_dashboard.inject_components(
                observer=self.observer_agent,
                orchestrator=self.ai_orchestrator,
                reinforcement=self.reinforcement_engine,
                auditor=self.anomaly_auditor
            )
            self.system_state['components_initialized'].append('ai_dashboard')
            self.logger.info("✅ AI Dashboard initialized")
            
            # 6. Initialize Command Assistant Integration
            self.logger.info("🤖 Integrating with Command Assistant...")
            if CommandAssistant:
                self.command_assistant = CommandAssistant('professional')
                # Extend command assistant with AI commands
                self._extend_command_assistant()
                self.system_state['components_initialized'].append('command_assistant')
                self.logger.info("✅ Command Assistant integration completed")
            else:
                self.logger.warning("⚠️ Command Assistant not available, skipping integration")
            
            self.system_state['status'] = 'INITIALIZED'
            self.logger.info("🎉 All Phase 14 components initialized successfully!")
            
            # Generate initial AI status
            await self._generate_ai_status()
            
        except Exception as e:
            self.logger.error(f"❌ Phase 14 initialization failed: {e}")
            self.system_state['status'] = 'FAILED'
            self.system_state['error'] = str(e)
            raise
            
    def _extend_command_assistant(self):
        """Extend the command assistant with AI-specific commands"""
        if not self.command_assistant:
            return
            
        # Add AI health command handler
        async def _handle_ai_health(params):
            """Handle AI health inquiry commands"""
            self.logger.info("🏥 Generating AI health report...")
            
            health_report = await self._get_comprehensive_health_report()
            
            # Display health report
            from rich.table import Table
            from rich import console
            
            console_obj = console.Console()
            
            health_table = Table(title="🤖 AI System Health Report")
            health_table.add_column("Component", style="cyan")
            health_table.add_column("Status", style="magenta")
            health_table.add_column("Details", style="green")
            
            for component, status in health_report['components'].items():
                health_table.add_row(
                    component.replace('_', ' ').title(),
                    status['status'],
                    status.get('details', 'Operational')
                )
                
            console_obj.print(health_table)
            
            # Show overall metrics
            metrics = health_report.get('metrics', {})
            console_obj.print(f"\n📊 Key Metrics:")
            console_obj.print(f"   Anomaly Rate: {metrics.get('anomaly_rate', 0):.2%}")
            console_obj.print(f"   System Health: {health_report.get('overall_health', 'UNKNOWN')}")
            console_obj.print(f"   Total Trades (24h): {metrics.get('total_trades_24h', 0)}")
            
        async def _handle_ai_retrain(params):
            """Handle AI retraining commands"""
            reason = params.get('reason', 'Manual command assistant trigger')
            
            if self.ai_orchestrator:
                success = await self.ai_orchestrator.manual_retrain_trigger(reason)
                if success:
                    self.logger.info("🧠 AI retraining triggered successfully")
                else:
                    self.logger.error("❌ AI retraining failed")
            else:
                self.logger.warning("⚠️ AI Orchestrator not available")
                
        async def _handle_anomaly_report(params):
            """Handle anomaly report commands"""
            if self.anomaly_auditor:
                report = self.anomaly_auditor.generate_anomaly_report()
                
                # Display key metrics
                summary = report.get('summary_24h', {})
                self.logger.info(f"🚨 Anomaly Report (24h):")
                self.logger.info(f"   Total Audits: {summary.get('total_audits', 0)}")
                self.logger.info(f"   Anomaly Rate: {summary.get('anomaly_rate', 0):.2%}")
                self.logger.info(f"   Critical Issues: {summary.get('critical_issues', 0)}")
            else:
                self.logger.warning("⚠️ Anomaly Auditor not available")
                
        # Patch the command assistant parser with new patterns
        if hasattr(self.command_assistant.parser, 'COMMAND_PATTERNS'):
            self.command_assistant.parser.COMMAND_PATTERNS.update({
                'ai_health': [
                    r'ai\s+(health|status)',
                    r'show\s+(me\s+)?ai\s+(health|status)',
                    r'how\s+(is\s+)?the\s+ai\s+(doing|performing)',
                    r'ai\s+system\s+(health|status)'
                ],
                'ai_retrain': [
                    r'trigger\s+(ai\s+)?retrain',
                    r'retrain\s+(the\s+)?ai',
                    r'ai\s+retrain',
                    r'start\s+ai\s+retraining'
                ],
                'anomaly_report': [
                    r'anomaly\s+report',
                    r'show\s+(me\s+)?anomalies',
                    r'ai\s+anomaly\s+(report|status)',
                    r'check\s+for\s+anomalies'
                ]
            })
            
            # Recompile patterns
            self.command_assistant.parser._compile_patterns()
            
            # Add handlers to the command assistant
            self.command_assistant._handle_ai_health = _handle_ai_health
            self.command_assistant._handle_ai_retrain = _handle_ai_retrain
            self.command_assistant._handle_anomaly_report = _handle_anomaly_report
            
            # Extend the main command processor
            original_process_command = self.command_assistant.process_command
            
            async def extended_process_command(user_input: str):
                # Parse the command
                command_type, params = self.command_assistant.parser.parse_command(user_input)
                
                # Handle AI-specific commands
                if command_type == 'ai_health':
                    await _handle_ai_health(params)
                elif command_type == 'ai_retrain':
                    await _handle_ai_retrain(params)
                elif command_type == 'anomaly_report':
                    await _handle_anomaly_report(params)
                else:
                    # Fall back to original processing
                    await original_process_command(user_input)
                    
            # Replace the process_command method
            self.command_assistant.process_command = extended_process_command
            
    async def start_autonomous_operations(self):
        """Start all autonomous AI operations"""
        self.logger.info("🔄 Starting autonomous AI operations...")
        
        try:
            # Start Observer Agent monitoring
            if self.observer_agent:
                asyncio.create_task(self.observer_agent.start_monitoring())
                self.system_state['components_active'].append('observer_agent')
                self.logger.info("✅ Observer Agent monitoring started")
                
            # Start AI Orchestrator
            if self.ai_orchestrator:
                asyncio.create_task(self.ai_orchestrator.start_orchestration())
                self.system_state['components_active'].append('ai_orchestrator')
                self.logger.info("✅ AI Orchestrator started")
                
            # Start AI Dashboard
            if self.ai_dashboard:
                await self.ai_dashboard.start_dashboard()
                self.system_state['components_active'].append('ai_dashboard')
                self.logger.info("✅ AI Dashboard started")
                
            self.system_state['status'] = 'ACTIVE'
            
            # Start health monitoring
            asyncio.create_task(self._health_monitoring_loop())
            
            self.logger.info("🎯 Phase 14 Autonomous Intelligence Layer is fully operational!")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to start autonomous operations: {e}")
            self.system_state['status'] = 'ERROR'
            return False
            
    async def _health_monitoring_loop(self):
        """Continuous health monitoring and status updates"""
        while True:
            try:
                await self._perform_health_check()
                await self._generate_ai_status()
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                self.logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(30)  # Shorter interval on error
                
    async def _perform_health_check(self):
        """Perform comprehensive system health check"""
        try:
            health_data = {
                'timestamp': datetime.now().isoformat(),
                'components': {},
                'overall_health': 'HEALTHY',
                'issues': []
            }
            
            # Check Observer Agent
            if self.observer_agent:
                if self.observer_agent.monitoring:
                    health_data['components']['observer_agent'] = {'status': 'ACTIVE', 'monitoring': True}
                else:
                    health_data['components']['observer_agent'] = {'status': 'INACTIVE', 'monitoring': False}
                    health_data['issues'].append('Observer Agent not monitoring')
            else:
                health_data['components']['observer_agent'] = {'status': 'NOT_INITIALIZED'}
                health_data['issues'].append('Observer Agent not initialized')
                
            # Check AI Orchestrator
            if self.ai_orchestrator:
                health_data['components']['ai_orchestrator'] = {'status': 'ACTIVE'}
            else:
                health_data['components']['ai_orchestrator'] = {'status': 'NOT_INITIALIZED'}
                health_data['issues'].append('AI Orchestrator not initialized')
                
            # Check Reinforcement Engine
            if self.reinforcement_engine:
                performance = self.reinforcement_engine.get_strategy_performance()
                health_data['components']['reinforcement_engine'] = {
                    'status': 'ACTIVE',
                    'strategies_tracked': len(performance.get('strategies', {})),
                    'bots_tracked': len(performance.get('bots', {}))
                }
            else:
                health_data['components']['reinforcement_engine'] = {'status': 'NOT_INITIALIZED'}
                
            # Check Anomaly Auditor
            if self.anomaly_auditor:
                audit_summary = self.anomaly_auditor.get_audit_summary(1)  # Last hour
                health_data['components']['anomaly_auditor'] = {
                    'status': 'ACTIVE',
                    'recent_audits': audit_summary.get('total_audits', 0) if isinstance(audit_summary, dict) else 0
                }
            else:
                health_data['components']['anomaly_auditor'] = {'status': 'NOT_INITIALIZED'}
                
            # Check AI Dashboard
            if self.ai_dashboard:
                health_data['components']['ai_dashboard'] = {
                    'status': 'ACTIVE',
                    'websocket_connections': len(self.ai_dashboard.websocket_connections)
                }
            else:
                health_data['components']['ai_dashboard'] = {'status': 'NOT_INITIALIZED'}
                
            # Determine overall health
            if len(health_data['issues']) > 2:
                health_data['overall_health'] = 'CRITICAL'
            elif len(health_data['issues']) > 0:
                health_data['overall_health'] = 'DEGRADED'
                
            self.system_state['last_health_check'] = health_data
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            
    async def _get_comprehensive_health_report(self):
        """Get comprehensive health report for command assistant"""
        await self._perform_health_check()
        
        health_report = {
            'timestamp': datetime.now().isoformat(),
            'overall_health': self.system_state.get('last_health_check', {}).get('overall_health', 'UNKNOWN'),
            'components': {},
            'metrics': {}
        }
        
        if self.system_state.get('last_health_check'):
            health_report['components'] = self.system_state['last_health_check']['components']
            
        # Add metrics
        if self.observer_agent:
            summary = self.observer_agent.get_observation_summary(24)
            if isinstance(summary, dict):
                health_report['metrics'].update({
                    'total_trades_24h': summary.get('total_trades', 0),
                    'win_rate_24h': summary.get('win_rate', 0),
                    'anomaly_rate': self.observer_agent.get_anomaly_rate(24)
                })
                
        return health_report
        
    async def _generate_ai_status(self):
        """Generate comprehensive AI status file"""
        try:
            status = {
                'timestamp': datetime.now().isoformat(),
                'phase': 14,
                'system_state': self.system_state,
                'health_check': self.system_state.get('last_health_check', {}),
                'components': {
                    'observer_agent': {
                        'initialized': self.observer_agent is not None,
                        'active': 'observer_agent' in self.system_state['components_active'],
                        'monitoring': self.observer_agent.monitoring if self.observer_agent else False
                    },
                    'ai_orchestrator': {
                        'initialized': self.ai_orchestrator is not None,
                        'active': 'ai_orchestrator' in self.system_state['components_active']
                    },
                    'reinforcement_engine': {
                        'initialized': self.reinforcement_engine is not None,
                        'active': self.reinforcement_engine is not None
                    },
                    'anomaly_auditor': {
                        'initialized': self.anomaly_auditor is not None,
                        'active': self.anomaly_auditor is not None
                    },
                    'ai_dashboard': {
                        'initialized': self.ai_dashboard is not None,
                        'active': 'ai_dashboard' in self.system_state['components_active'],
                        'url': f"http://localhost:8080" if self.ai_dashboard else None
                    },
                    'command_assistant': {
                        'initialized': self.command_assistant is not None,
                        'ai_commands_available': self.command_assistant is not None
                    }
                },
                'metrics': {},
                'ai_capabilities': [
                    'Real-time trade monitoring',
                    'Anomaly detection and alerting',
                    'Dynamic strategy weight adjustment',
                    'Automated model retraining',
                    'Web dashboard interface',
                    'Natural language AI commands'
                ]
            }
            
            # Add metrics if available
            if self.observer_agent:
                summary = self.observer_agent.get_observation_summary(24)
                if isinstance(summary, dict):
                    status['metrics']['observer'] = summary
                    
            if self.reinforcement_engine:
                performance = self.reinforcement_engine.get_strategy_performance()
                status['metrics']['reinforcement'] = performance
                
            if self.anomaly_auditor:
                audit_summary = self.anomaly_auditor.get_audit_summary(24)
                if isinstance(audit_summary, dict):
                    status['metrics']['anomaly'] = audit_summary
                    
            # Save to file
            with open(self.ai_status_file, 'w') as f:
                json.dump(status, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to generate AI status: {e}")
            
    async def demo_ai_system(self):
        """Run a comprehensive demo of the Phase 14 AI system"""
        self.logger.info("🎬 Starting Phase 14 AI System Demo")
        self.logger.info("=" * 50)
        
        # Create some demo trade data
        demo_trades = [
            {
                'timestamp': datetime.now().isoformat(),
                'symbol': 'BTCUSDT',
                'signal': 'buy',
                'confidence': 0.85,
                'expected_return': 0.02,
                'actual_return': 0.018,
                'bot_name': 'AnalyticsBot',
                'strategy': 'momentum'
            },
            {
                'timestamp': datetime.now().isoformat(),
                'symbol': 'ETHUSDT',
                'signal': 'sell',
                'confidence': 0.75,
                'expected_return': 0.015,
                'actual_return': -0.25,  # Anomaly
                'bot_name': 'StrategyBot',
                'strategy': 'reversal'
            },
            {
                'timestamp': datetime.now().isoformat(),
                'symbol': 'ADAUSDT',
                'signal': 'buy',
                'confidence': 0.9,
                'expected_return': 0.01,
                'actual_return': 0.035,
                'bot_name': 'AnalyticsBot',
                'strategy': 'momentum'
            }
        ]
        
        # Process demo trades through all components
        for trade in demo_trades:
            # Observer Agent
            if self.observer_agent:
                metrics = self.observer_agent._calculate_trade_metrics(trade)
                self.observer_agent._log_trade_observation(metrics)
                if self.observer_agent._is_anomaly(metrics):
                    self.observer_agent._log_anomaly(metrics)
                    
            # Reinforcement Engine
            if self.reinforcement_engine:
                self.reinforcement_engine.record_trade_performance(trade)
                
            # Anomaly Auditor
            if self.anomaly_auditor:
                audit_result = self.anomaly_auditor.audit_trade(trade)
                if audit_result['anomalies_detected']:
                    self.logger.warning(f"🚨 Anomaly detected in {trade['symbol']}: {len(audit_result['anomalies_detected'])} issues")
                    
        # Generate summary reports
        self.logger.info("\n📊 Demo Results Summary:")
        
        if self.observer_agent:
            summary = self.observer_agent.get_observation_summary(24)
            if isinstance(summary, dict):
                self.logger.info(f"   Trades Observed: {summary.get('total_trades', 0)}")
                self.logger.info(f"   Win Rate: {summary.get('win_rate', 0):.2%}")
                
        if self.reinforcement_engine:
            performance = self.reinforcement_engine.get_strategy_performance()
            self.logger.info(f"   Strategies Tracked: {len(performance.get('strategies', {}))}")
            self.logger.info(f"   Bots Tracked: {len(performance.get('bots', {}))}")
            
        if self.anomaly_auditor:
            audit_summary = self.anomaly_auditor.get_audit_summary(24)
            if isinstance(audit_summary, dict):
                self.logger.info(f"   Anomalies Detected: {audit_summary.get('total_anomalies', 0)}")
                self.logger.info(f"   Anomaly Rate: {audit_summary.get('anomaly_rate', 0):.2%}")
                
        self.logger.info(f"\n🌐 AI Dashboard available at: http://localhost:8080")
        
        if self.command_assistant:
            self.logger.info(f"🤖 Enhanced Command Assistant with AI commands:")
            self.logger.info(f"   • 'show ai health' - Display AI system status")
            self.logger.info(f"   • 'trigger ai retrain' - Manually trigger retraining")
            self.logger.info(f"   • 'anomaly report' - Show recent anomalies")
            
        # Update AI status
        await self._generate_ai_status()
        
        self.logger.info(f"\n📄 AI Status file generated: {self.ai_status_file}")
        self.logger.info("✅ Phase 14 AI System Demo completed successfully!")


# Main execution functions
async def run_phase_14_demo():
    """Run the complete Phase 14 demo"""
    # Configuration
    config = {
        "demo_mode": True,
        "observation_interval": 30,
        "dashboard_port": 8080,
        "log_level": "INFO"
    }
    
    # Initialize Phase 14 AI system
    ai_system = Phase14AutonomousIntelligence(config)
    
    try:
        # Initialize all components
        await ai_system.initialize_system()
        
        # Start autonomous operations
        success = await ai_system.start_autonomous_operations()
        
        if success:
            # Run demo
            await ai_system.demo_ai_system()
            
            # Keep running for demonstration
            print("\n🎯 Phase 14 Autonomous Intelligence Layer is running!")
            print("🌐 Dashboard: http://localhost:8080")
            print("🤖 AI monitoring active")
            print("⌨️  Press Ctrl+C to stop")
            
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Phase 14 AI system stopped")
        else:
            print("❌ Failed to start Phase 14 AI system")
            
    except Exception as e:
        print(f"❌ Phase 14 demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(run_phase_14_demo())
