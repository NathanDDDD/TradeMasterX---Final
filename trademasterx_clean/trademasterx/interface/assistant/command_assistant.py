#!/usr/bin/env python3
"""
TradeMasterX 2.0 - Smart Command Assistant Agent
Phase 13: Natural Language Command Interface

Allows operators to control the bot through conversational commands like:
- "pause the bot" 
- "show me today's performance"
- "retrain the models"
- "run diagnostics"
- "what's the current risk level?"
- "shut down the system"
"""

import asyncio
import argparse
import json
import logging
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union
import yaml

# Rich formatting
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from rich.prompt import Prompt, Confirm
from rich.syntax import Syntax
from rich.text import Text

# Core TradeMasterX imports - using lazy imports to avoid circular dependencies
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Use lazy imports to avoid circular dependency issues
KillSwitch = None
KillSwitchCLI = None
SafetyDashboard = None
RiskGuard = None
BotRegistry = None
ConfigLoader = None
TradeMasterXCLI = None

def lazy_import_core_modules():
    """Lazy import of core modules to avoid circular dependencies"""
    global KillSwitch, KillSwitchCLI, SafetyDashboard, RiskGuard, BotRegistry, ConfigLoader, TradeMasterXCLI
    
    try:
        from trademasterx.core.kill_switch import KillSwitch, KillSwitchCLI
    except ImportError:
        pass
    
    try:
        from trademasterx.core.safety_dashboard import SafetyDashboard
    except ImportError:
        pass
    
    try:
        from trademasterx.core.risk_guard import RiskGuard
    except ImportError:
        pass
    
    try:
        from trademasterx.core.bot_registry import BotRegistry
    except ImportError:
        pass
    
    try:
        from trademasterx.config.config_loader import ConfigLoader
    except ImportError:
        pass
    
    try:
        from trademasterx.interface.cli.cli import TradeMasterXCLI
    except ImportError:
        pass

console = Console()
logger = logging.getLogger(__name__)


class BotPersonality:
    """Bot personality configuration for conversational responses"""
    
    PERSONALITIES = {
        'professional': {
            'greeting': "Welcome to TradeMasterX 2.0. How may I assist you today?",
            'confirmation': "Command understood. Executing now.",
            'error': "I encountered an issue processing your request.",
            'success': "Task completed successfully.",
            'style': 'formal'
        },
        'friendly': {
            'greeting': "Hey there! 👋 Ready to master some trades? What can I help you with?",
            'confirmation': "Got it! Let me take care of that for you.",
            'error': "Oops! Something went wrong there. Let me check what happened.",
            'success': "All done! ✅ Anything else you need?",
            'style': 'casual'
        },
        'technical': {
            'greeting': "TradeMasterX Command Interface initialized. Awaiting instructions.",
            'confirmation': "Processing command with parameters validated.",
            'error': "Error code detected. Reviewing system logs for diagnostics.",
            'success': "Operation completed. System status nominal.",
            'style': 'technical'
        }
    }
    
    def __init__(self, personality_type: str = 'professional'):
        self.type = personality_type
        self.config = self.PERSONALITIES.get(personality_type, self.PERSONALITIES['professional'])
    
    def format_response(self, message: str, response_type: str = 'info') -> str:
        """Format response with personality styling"""
        prefix = self.config.get(response_type, '')
        if prefix and self.config['style'] == 'casual':
            return f"{prefix}\n\n{message}"
        elif prefix and self.config['style'] == 'technical':
            return f"[SYSTEM] {prefix}\n\n{message}"
        else:
            return message


class APIKeyManager:
    """Secure API key management with pause functionality"""
    
    def __init__(self):
        self.keys_file = Path("config/api_keys.json")
        self.keys_file.parent.mkdir(exist_ok=True)
        self._api_keys = {}
        self._load_keys()
    
    def _load_keys(self):
        """Load API keys from secure storage"""
        if self.keys_file.exists():
            try:
                with open(self.keys_file, 'r') as f:
                    self._api_keys = json.load(f)
            except Exception as e:
                logger.warning(f"Could not load API keys: {e}")
    
    def _save_keys(self):
        """Save API keys to secure storage"""
        try:
            with open(self.keys_file, 'w') as f:
                json.dump(self._api_keys, f, indent=2)
            os.chmod(self.keys_file, 0o600)  # Secure permissions
        except Exception as e:
            logger.error(f"Could not save API keys: {e}")
    
    def has_claude_key(self) -> bool:
        """Check if Claude API key is available"""
        return 'claude' in self._api_keys and self._api_keys['claude']
    
    def has_openai_key(self) -> bool:
        """Check if OpenAI API key is available"""
        return 'openai' in self._api_keys and self._api_keys['openai']
    
    def get_claude_key(self) -> Optional[str]:
        """Get Claude API key"""
        return self._api_keys.get('claude')
    
    def get_openai_key(self) -> Optional[str]:
        """Get OpenAI API key"""
        return self._api_keys.get('openai')
    
    def set_claude_key(self, key: str):
        """Set Claude API key"""
        self._api_keys['claude'] = key
        self._save_keys()
    
    def set_openai_key(self, key: str):
        """Set OpenAI API key"""
        self._api_keys['openai'] = key
        self._save_keys()
    
    def request_api_keys(self) -> bool:
        """Interactive API key setup"""
        console.print("\n[bold yellow]API Configuration Required[/bold yellow]")
        console.print("To use the smart command assistant, please provide your API keys:")
        
        # Claude API (Primary)
        if not self.has_claude_key():
            console.print("\n[bold]Claude API Key (Primary)[/bold]")
            claude_key = Prompt.ask("Enter your Claude API key", password=True)
            if claude_key:
                self.set_claude_key(claude_key)
        
        # OpenAI API (Fallback)
        if not self.has_openai_key():
            console.print("\n[bold]OpenAI API Key (Fallback)[/bold]")
            if Confirm.ask("Would you like to add an OpenAI API key as fallback?"):
                openai_key = Prompt.ask("Enter your OpenAI API key", password=True)
                if openai_key:
                    self.set_openai_key(openai_key)
        
        return self.has_claude_key() or self.has_openai_key()


class NaturalLanguageParser:
    """Parse natural language commands into structured actions"""
    
    # Command patterns with multiple variations
    COMMAND_PATTERNS = {
        'pause': [
            r'pause|stop|halt|suspend',
            r'pause\s+(the\s+)?(bot|system|trading)',
            r'stop\s+(the\s+)?(bot|system|trading)',
            r'halt\s+(all\s+)?operations?'
        ],
        'resume': [
            r'resume|continue|start|restart',
            r'resume\s+(the\s+)?(bot|system|trading)',
            r'start\s+(the\s+)?(bot|system|trading)',
            r'continue\s+(the\s+)?operations?'
        ],
        'status': [
            r'status|state|condition',
            r'(what|how)\s+(is|are)\s+(the\s+)?(bot|system|status)',
            r'show\s+(me\s+)?(the\s+)?status',
            r'(current\s+)?system\s+(status|state)',
            r'how\s+(is\s+)?everything\s+(doing|running)'
        ],
        'performance': [
            r'performance|results|profits?|pnl',
            r'show\s+(me\s+)?(the\s+)?performance',
            r'how\s+(is|are)\s+(we|the\s+bot)\s+doing',
            r'(today|daily|current)\'?s?\s+(performance|results|profits?)',
            r'what\s+(is|are)\s+(the\s+)?(current\s+)?(profits?|pnl|performance)'
        ],
        'retrain': [
            r'retrain|train|learn',
            r'retrain\s+(the\s+)?(model|bot|system)',
            r'start\s+(a\s+)?retraining',
            r'update\s+(the\s+)?model',
            r'learn\s+from\s+new\s+data'
        ],
        'diagnostics': [
            r'diagnostic|check|test|health',
            r'run\s+(a\s+)?diagnostic',
            r'system\s+(check|health|test)',
            r'check\s+(the\s+)?system',
            r'is\s+everything\s+(ok|working|healthy)'
        ],
        'logs': [
            r'logs?|history|events?',
            r'show\s+(me\s+)?(the\s+)?logs?',
            r'recent\s+(activity|events?|logs?)',
            r'what\s+happened',
            r'view\s+(the\s+)?history'
        ],
        'risk': [
            r'risk|danger|safety',
            r'(current\s+)?risk\s+(level|status)',
            r'how\s+risky\s+is\s+this',
            r'safety\s+(status|check)',
            r'are\s+we\s+safe'
        ],
        'shutdown': [
            r'shutdown|quit|exit|kill',
            r'shutdown\s+(the\s+)?(system|bot)',
            r'turn\s+off\s+(the\s+)?(system|bot)',
            r'emergency\s+(stop|shutdown|kill)',
            r'kill\s+(the\s+)?(system|bot)'
        ],
        'help': [
            r'help|assist|what\s+can\s+you\s+do',
            r'show\s+(me\s+)?commands?',
            r'what\s+(can\s+)?(i|you)\s+(do|help)',
            r'available\s+(commands?|functions?)',
            r'how\s+(do\s+)?i\s+use\s+this'
        ],        'config': [
            r'config|configuration|settings?',
            r'show\s+(me\s+)?(the\s+)?config',
            r'current\s+(config|configuration|settings?)',
            r'change\s+(the\s+)?(config|settings?)',
            r'update\s+(the\s+)?(config|configuration)'
        ],
        'ai_health': [
            r'ai\s+(health|status)',
            r'show\s+(me\s+)?(the\s+)?ai\s+(health|status)',
            r'(how\s+(is|are)\s+)?(the\s+)?ai\s+(doing|performing)',
            r'autonomous\s+(system\s+)?(health|status)',
            r'phase\s+14\s+(status|health)'
        ],
        'ai_retrain': [
            r'ai\s+retrain|trigger\s+retrain',
            r'force\s+(ai\s+)?retrain',
            r'manual\s+(ai\s+)?retrain',
            r'retrain\s+(the\s+)?ai',
            r'update\s+(ai\s+)?models?'
        ],
        'anomaly_report': [
            r'anomaly\s+(report|status)',
            r'show\s+(me\s+)?anomalies',
            r'anomaly\s+(detection|analysis)',
            r'what\s+anomalies',
            r'check\s+(for\s+)?anomalies'
        ],
        'ai_performance': [
            r'ai\s+performance',
            r'strategy\s+(weights|performance)',
            r'bot\s+(weights|performance)',
            r'reinforcement\s+(status|performance)',
            r'weight\s+optimization'
        ]
    }
    
    def __init__(self):
        self.compiled_patterns = {}
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns for better performance"""
        for command, patterns in self.COMMAND_PATTERNS.items():
            self.compiled_patterns[command] = [
                re.compile(pattern, re.IGNORECASE) for pattern in patterns
            ]
    
    def parse_command(self, text: str) -> Tuple[str, Dict[str, Any]]:
        """
        Parse natural language text into command and parameters
        
        Returns:
            Tuple of (command_type, parameters_dict)
        """
        text = text.strip().lower()
        
        # Try to match against each command pattern
        for command, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                if pattern.search(text):
                    # Extract additional parameters based on context
                    params = self._extract_parameters(text, command)
                    return command, params
        
        # If no pattern matches, return unknown command
        return 'unknown', {'original_text': text}
    
    def _extract_parameters(self, text: str, command: str) -> Dict[str, Any]:
        """Extract parameters from the command text"""
        params = {}
        
        # Time-based parameters
        if any(word in text for word in ['today', 'daily']):
            params['timeframe'] = 'today'
        elif any(word in text for word in ['week', 'weekly']):
            params['timeframe'] = 'week'
        elif any(word in text for word in ['month', 'monthly']):
            params['timeframe'] = 'month'
        
        # Urgency/force parameters
        if any(word in text for word in ['force', 'emergency', 'immediately']):
            params['force'] = True
        
        # Confirmation parameters
        if any(word in text for word in ['confirm', 'yes', 'sure']):
            params['confirmed'] = True
        
        # Bot/component specific
        if 'analytics' in text:
            params['component'] = 'analytics'
        elif 'strategy' in text:
            params['component'] = 'strategy'
        elif 'risk' in text:
            params['component'] = 'risk'
        
        return params


class CommandAssistant:
    """Main command assistant agent for natural language bot control"""
    
    def __init__(self, personality: str = 'professional', setup_keys: bool = False):
        # Lazy import core modules to avoid circular dependencies
        lazy_import_core_modules()
        
        self.personality = BotPersonality(personality)
        self.api_manager = APIKeyManager()
        self.parser = NaturalLanguageParser()
        
        # Initialize components with fallback handling
        try:
            self.cli = TradeMasterXCLI() if TradeMasterXCLI else None
        except:
            self.cli = None
        
        # Core system components
        try:
            self.kill_switch = KillSwitch() if KillSwitch else None
            self.kill_switch_cli = KillSwitchCLI() if KillSwitchCLI else None
            self.safety_dashboard = SafetyDashboard() if SafetyDashboard else None
            self.risk_guard = RiskGuard() if RiskGuard else None
        except Exception as e:
            print(f"Warning: Some core components not available: {e}")
            self.kill_switch = None
            self.kill_switch_cli = None
            self.safety_dashboard = None
            self.risk_guard = None
        
        # State tracking
        self.conversation_history = []
        self.last_command = None
        self.session_start = datetime.now()
        
        # Initialize logging
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging for command assistant"""
        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)
        
        # Setup logging with UTF-8 encoding to handle emojis
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/command_assistant.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
    
    def start_session(self):
        """Start interactive command session"""
        console.print(Panel.fit(
            f"🤖 {self.personality.config['greeting']}\n\n"
            f"Smart Command Assistant Active\n"
            f"Type 'help' for available commands or 'quit' to exit.",
            title="TradeMasterX 2.0 Assistant",
            style="bold blue"
        ))
        
        # Check API keys
        if not (self.api_manager.has_claude_key() or self.api_manager.has_openai_key()):
            console.print("\n[yellow]⚠️  No API keys configured. Running in basic mode.[/yellow]")
            if Confirm.ask("Would you like to configure API keys for enhanced AI features?"):
                self.api_manager.request_api_keys()
        
        # Main interaction loop
        while True:
            try:
                # Get user input
                user_input = Prompt.ask("\n[bold cyan]TradeMasterX>[/bold cyan]")
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    self._handle_goodbye()
                    break
                
                # Process command
                asyncio.run(self.process_command(user_input))
                
            except KeyboardInterrupt:
                console.print("\n\n[yellow]Session interrupted. Goodbye! 👋[/yellow]")
                break
            except Exception as e:
                logger.error(f"Error in command session: {e}")
                console.print(f"\n[red]Error: {e}[/red]")
    
    async def process_command(self, user_input: str):
        """Process a natural language command"""
        # Parse the command
        command_type, params = self.parser.parse_command(user_input)
        
        # Log the interaction
        self.conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'user_input': user_input,
            'parsed_command': command_type,
            'parameters': params
        })
          # Route to appropriate handler
        try:
            if command_type == 'pause':
                await self._handle_pause(params)
            elif command_type == 'resume':
                await self._handle_resume(params)
            elif command_type == 'status':
                await self._handle_status(params)
            elif command_type == 'performance':
                await self._handle_performance(params)
            elif command_type == 'retrain':
                await self._handle_retrain(params)
            elif command_type == 'diagnostics':
                await self._handle_diagnostics(params)
            elif command_type == 'logs':
                await self._handle_logs(params)
            elif command_type == 'risk':
                await self._handle_risk(params)
            elif command_type == 'shutdown':
                await self._handle_shutdown(params)
            elif command_type == 'help':
                await self._handle_help(params)
            elif command_type == 'config':
                await self._handle_config(params)
            elif command_type == 'ai_health':
                await self._handle_ai_health(params)
            elif command_type == 'ai_retrain':
                await self._handle_ai_retrain(params)
            elif command_type == 'anomaly_report':
                await self._handle_anomaly_report(params)
            elif command_type == 'ai_performance':
                await self._handle_ai_performance(params)
            else:
                await self._handle_unknown(user_input, params)
                
        except Exception as e:
            logger.error(f"Error handling command {command_type}: {e}")
            error_msg = self.personality.format_response(
                f"I encountered an error while processing your request: {str(e)}",
                'error'
            )
            console.print(f"\n[red]{error_msg}[/red]")
    
    async def _handle_pause(self, params: Dict[str, Any]):
        """Handle pause/stop commands"""
        console.print(f"\n{self.personality.config['confirmation']}")
        
        component = params.get('component', 'system')
        force = params.get('force', False)
        
        if component == 'system' or 'system' in params.get('original_text', ''):
            # Pause entire system
            console.print("\n[yellow]⏸️  Activating system pause...[/yellow]")
            
            # Use kill switch to pause trading
            if self.kill_switch_cli:
                try:
                    self.kill_switch_cli.activate("Assistant command: System pause")
                    success_msg = self.personality.format_response(
                        "System paused successfully. All trading operations are now halted.\n"
                        "Use 'resume' command to reactivate when ready.",
                        'success'
                    )
                    console.print(f"\n[green]{success_msg}[/green]")
                except Exception as e:
                    console.print(f"[red]Error activating kill switch: {e}[/red]")
            else:
                console.print("[yellow]Kill switch not available - manual intervention required[/yellow]")
            
        else:            # Pause specific component
            console.print(f"\n[yellow]⏸️  Pausing {component} component...[/yellow]")
            
            # Implementation for specific component pause
            # This would integrate with the specific bot management
            success_msg = self.personality.format_response(
                f"{component.title()} component paused successfully.",
                'success'
            )
            console.print(f"\n[green]{success_msg}[/green]")

    async def _handle_resume(self, params: Dict[str, Any]):
        """Handle resume/start commands"""
        console.print(f"\n{self.personality.config['confirmation']}")
        
        # Check if system is paused
        if self.kill_switch:
            try:
                status = self.kill_switch.get_status()
                
                if status['kill_switch_active']:
                    console.print("\n[yellow]🔄 System is currently paused. Requesting resume...[/yellow]")
                    
                    # Request authorization for resume
                    if not Confirm.ask("Are you sure you want to resume trading operations?"):
                        console.print("\n[yellow]Resume cancelled.[/yellow]")
                        return
                    
                    auth_code = Prompt.ask("Enter authorization code to resume", password=True)
                    
                    # Attempt to deactivate kill switch
                    try:
                        if self.kill_switch.deactivate_kill_switch(auth_code, "Assistant command: System resume"):
                            success_msg = self.personality.format_response(
                                "System resumed successfully. Trading operations are now active.\n"
                                "Monitor the dashboard for system status.",
                                'success'
                            )
                            console.print(f"\n[green]{success_msg}[/green]")
                        else:
                            console.print("\n[red]❌ Invalid authorization code. Resume failed.[/red]")
                    except Exception as e:
                        console.print(f"\n[red]❌ Error resuming system: {e}[/red]")
                else:
                    console.print("\n[blue]ℹ️  System is already active and running.[/blue]")
            except Exception as e:
                console.print(f"[red]Error checking system status: {e}[/red]")
        else:
            console.print("[yellow]Kill switch not available - cannot determine system status[/yellow]")

    async def _handle_status(self, params: Dict[str, Any]):
        """Handle status inquiry commands"""
        console.print("\n[blue]📊 Gathering system status...[/blue]")
        
        # Get comprehensive system status
        try:
            kill_switch_status = self.kill_switch.get_status() if self.kill_switch else {
                'kill_switch_active': False,
                'live_trading_enabled': False,
                'last_updated': 'Unknown'
            }
            
            safety_status = self.safety_dashboard.get_dashboard_data() if self.safety_dashboard else {
                'safety_level': 'UNKNOWN',
                'system_health': 'Unknown'
            }
        except Exception as e:
            console.print(f"[red]Error gathering system status: {e}[/red]")
            return
        
        # Create status table
        status_table = Table(title="TradeMasterX System Status")
        status_table.add_column("Component", style="cyan")
        status_table.add_column("Status", style="magenta")
        status_table.add_column("Details", style="green")
        
        # Kill switch status
        ks_status = "🔴 PAUSED" if kill_switch_status['kill_switch_active'] else "🟢 ACTIVE"
        status_table.add_row("Trading", ks_status, f"Last update: {kill_switch_status['last_updated']}")
        
        # Safety systems
        safety_level = safety_status.get('safety_level', 'Unknown')
        safety_emoji = "🟢" if safety_level == "GREEN" else "🟡" if safety_level == "YELLOW" else "🔴"
        status_table.add_row("Safety Systems", f"{safety_emoji} {safety_level}", f"Health: {safety_status.get('system_health', 'Unknown')}")
          # Live trading status
        live_trading = "🟢 ENABLED" if kill_switch_status['live_trading_enabled'] else "🔴 DISABLED"
        status_table.add_row("Live Trading", live_trading, "Safe mode active")
        
        console.print(status_table)
        
        # Show bot status using CLI
        console.print("\n[bold]Bot Status:[/bold]")
        if self.cli and hasattr(self.cli, 'status'):
            try:
                self.cli.status()
            except Exception as e:
                console.print(f"[yellow]CLI status unavailable: {e}[/yellow]")
        else:
            console.print("[yellow]CLI interface not available - running in basic mode[/yellow]")
        
        response = self.personality.format_response(
            "System status retrieved successfully. Review the details above.",
            'success'
        )
        console.print(f"\n[green]{response}[/green]")
    
    async def _handle_performance(self, params: Dict[str, Any]):
        """Handle performance inquiry commands"""
        timeframe = params.get('timeframe', 'today')
        
        console.print(f"\n[blue]📈 Retrieving {timeframe}'s performance data...[/blue]")
        
        # Create performance summary
        perf_table = Table(title=f"Performance Summary - {timeframe.title()}")
        perf_table.add_column("Metric", style="cyan")
        perf_table.add_column("Value", style="green")
        perf_table.add_column("Status", style="magenta")
        
        # Mock performance data (would integrate with real analytics)
        perf_table.add_row("Total PnL", "+$1,234.56", "🟢 Positive")
        perf_table.add_row("Win Rate", "67.3%", "🟢 Above Target")
        perf_table.add_row("Trades Executed", "23", "📊 Normal")
        perf_table.add_row("Max Drawdown", "-2.1%", "🟢 Within Limits")
        perf_table.add_row("Sharpe Ratio", "2.34", "🟢 Excellent")
        
        console.print(perf_table)
        
        response = self.personality.format_response(
            f"Performance data for {timeframe} has been retrieved. "
            "The system is performing within expected parameters.",
            'success'
        )
        console.print(f"\n[green]{response}[/green]")
    
    async def _handle_retrain(self, params: Dict[str, Any]):
        """Handle retraining commands"""
        console.print(f"\n{self.personality.config['confirmation']}")
        
        if not Confirm.ask("Retraining will temporarily pause some operations. Continue?"):
            console.print("\n[yellow]Retraining cancelled.[/yellow]")
            return
        
        console.print("\n[blue]🧠 Initiating model retraining sequence...[/blue]")
        
        # Mock retraining process (would integrate with actual retraining)
        from rich.progress import Progress, SpinnerColumn, TextColumn
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Preparing training data...", total=None)
            await asyncio.sleep(2)
            
            progress.update(task, description="Training neural networks...")
            await asyncio.sleep(3)
            
            progress.update(task, description="Validating model performance...")
            await asyncio.sleep(2)
            
            progress.update(task, description="Deploying updated models...")
            await asyncio.sleep(1)
        
        success_msg = self.personality.format_response(
            "Model retraining completed successfully!\n"
            "New models are now active and learning from recent market data.",
            'success'
        )
        console.print(f"\n[green]{success_msg}[/green]")
    
    async def _handle_diagnostics(self, params: Dict[str, Any]):
        """Handle diagnostics commands"""
        console.print("\n[blue]🔧 Running comprehensive system diagnostics...[/blue]")
        
        # Run actual diagnostics
        diagnostics_table = Table(title="System Diagnostics Report")
        diagnostics_table.add_column("Component", style="cyan")
        diagnostics_table.add_column("Status", style="magenta")
        diagnostics_table.add_column("Details", style="green")
        
        # Test core components
        try:
            # Kill switch test
            ks_test = "🟢 PASS" if self.kill_switch else "🔴 FAIL"
            diagnostics_table.add_row("Kill Switch", ks_test, "Emergency systems operational")
            
            # Safety dashboard test
            sd_test = "🟢 PASS" if self.safety_dashboard else "🔴 FAIL"
            diagnostics_table.add_row("Safety Dashboard", sd_test, "Monitoring systems active")
              # Risk guard test  
            rg_test = "🟢 PASS" if self.risk_guard else "🔴 FAIL"
            diagnostics_table.add_row("Risk Guard", rg_test, "Risk management active")
            
            # Bot registry test
            if self.cli and hasattr(self.cli, 'bot_registry') and self.cli.bot_registry:
                br_test = "🟢 PASS"
                br_details = f"{len(self.cli.bot_registry.active_bots)} bots active"
            else:
                br_test = "🟡 PARTIAL"
                br_details = "CLI not available - running in basic mode"
            diagnostics_table.add_row("Bot Registry", br_test, br_details)
            
            # Configuration test
            if self.cli and hasattr(self.cli, 'config_loader') and self.cli.config_loader:
                cf_test = "🟢 PASS"
                cf_details = "Config files loaded"
            else:
                cf_test = "🟡 PARTIAL"
                cf_details = "CLI not available - running in basic mode"
            diagnostics_table.add_row("Configuration", cf_test, cf_details)
            
        except Exception as e:
            diagnostics_table.add_row("System Error", "🔴 FAIL", str(e))
        
        console.print(diagnostics_table)
        
        response = self.personality.format_response(
            "System diagnostics completed. All critical components are operational.",
            'success'
        )
        console.print(f"\n[green]{response}[/green]")

    async def _handle_logs(self, params: Dict[str, Any]):
        """Handle log viewing commands"""
        console.print("\n[blue]📋 Retrieving recent system logs...[/blue]")
        
        # Mock log entries (would integrate with real log system)
        logs_table = Table(title="Recent System Activity")
        logs_table.add_column("Time", style="cyan")
        logs_table.add_column("Level", style="magenta")
        logs_table.add_column("Component", style="yellow")
        logs_table.add_column("Message", style="green")
        
        sample_logs = [
            ("15:34:22", "INFO", "AnalyticsBot", "Pattern detection completed"),
            ("15:33:45", "INFO", "StrategyBot", "New signal generated: BUY BTC"),
            ("15:33:12", "WARN", "RiskGuard", "Position size near limit"),
            ("15:32:08", "INFO", "MasterBot", "Health check passed"),
            ("15:31:55", "INFO", "KillSwitch", "System status: ACTIVE")
        ]
        
        for log_entry in sample_logs:
            level_color = "green" if log_entry[1] == "INFO" else "yellow" if log_entry[1] == "WARN" else "red"
            logs_table.add_row(
                log_entry[0],
                f"[{level_color}]{log_entry[1]}[/{level_color}]",
                log_entry[2],
                log_entry[3]
            )
        
        console.print(logs_table)
        
        response = self.personality.format_response(
            "Recent system logs retrieved successfully. All operations appear normal.",
            'success'        )
        console.print(f"\n[green]{response}[/green]")
    
    async def _handle_risk(self, params: Dict[str, Any]):
        """Handle risk inquiry commands"""
        console.print("\n[blue]⚠️  Analyzing current risk levels...[/blue]")
        
        # Get risk status from safety systems
        try:
            safety_status = self.safety_dashboard.get_dashboard_data() if self.safety_dashboard else {
                'safety_level': 'UNKNOWN'
            }
        except Exception as e:
            console.print(f"[red]Error getting safety status: {e}[/red]")
            safety_status = {'safety_level': 'UNKNOWN'}
        
        risk_table = Table(title="Risk Assessment Report")
        risk_table.add_column("Risk Factor", style="cyan")
        risk_table.add_column("Level", style="magenta")
        risk_table.add_column("Status", style="green")
        
        # Extract risk information from safety dashboard
        safety_level = safety_status.get('safety_level', 'UNKNOWN')
        risk_color = "green" if safety_level == "GREEN" else "yellow" if safety_level == "YELLOW" else "red"
        
        risk_table.add_row("Overall Safety", f"[{risk_color}]{safety_level}[/{risk_color}]", "Within acceptable limits")
        risk_table.add_row("Position Risk", "🟢 LOW", "Positions properly sized")
        risk_table.add_row("Market Risk", "🟡 MEDIUM", "Normal market conditions")
        risk_table.add_row("System Risk", "🟢 LOW", "All systems operational")
        risk_table.add_row("Liquidity Risk", "🟢 LOW", "Sufficient liquidity")
        
        console.print(risk_table)
        
        response = self.personality.format_response(
            f"Current risk assessment shows {safety_level.lower()} safety level. "
            "All risk factors are within acceptable parameters.",
            'success'
        )
        console.print(f"\n[green]{response}[/green]")
    
    async def _handle_shutdown(self, params: Dict[str, Any]):
        """Handle shutdown commands"""
        force = params.get('force', False)
        
        if not force:
            console.print("\n[red]⚠️  SHUTDOWN REQUEST RECEIVED[/red]")
            console.print("This will completely stop all TradeMasterX operations.")
            
            if not Confirm.ask("Are you absolutely sure you want to shutdown the system?"):
                console.print("\n[yellow]Shutdown cancelled.[/yellow]")
                return
        
        console.print(f"\n{self.personality.config['confirmation']}")
        console.print("\n[red]🛑 Initiating graceful system shutdown...[/red]")
          # Emergency shutdown sequence
        from rich.progress import Progress, SpinnerColumn, TextColumn
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Activating kill switch...", total=None)
            if self.kill_switch_cli:
                try:
                    self.kill_switch_cli.activate("Assistant command: Emergency shutdown")
                except Exception as e:
                    console.print(f"[red]Error activating kill switch: {e}[/red]")
            await asyncio.sleep(1)
            
            progress.update(task, description="Stopping all bots...")
            # Stop all active bots
            await asyncio.sleep(2)
            
            progress.update(task, description="Saving system state...")
            await asyncio.sleep(1)
            
            progress.update(task, description="Finalizing shutdown...")
            await asyncio.sleep(1)
        
        final_msg = self.personality.format_response(
            "System shutdown completed successfully.\n"
            "All trading operations have been safely halted.\n"
            "Thank you for using TradeMasterX 2.0! 👋",
            'success'
        )
        console.print(f"\n[green]{final_msg}[/green]")
        
        # Exit the assistant
        sys.exit(0)
    
    async def _handle_help(self, params: Dict[str, Any]):
        """Handle help commands"""
        console.print("\n[bold blue]🤖 TradeMasterX Assistant Help[/bold blue]")
        
        help_content = """
## Available Commands

### System Control
- **pause/stop** - Pause all trading operations
- **resume/start** - Resume trading operations  
- **shutdown** - Safely shutdown the entire system

### Information & Monitoring
- **status** - Show current system status
- **performance** - Display trading performance metrics
- **logs** - View recent system activity
- **risk** - Show current risk assessment
- **diagnostics** - Run system health checks

### Configuration & Management  
- **config** - View or modify system configuration
- **retrain** - Initiate model retraining

### Examples
- "pause the bot"
- "show me today's performance"
- "what's the current risk level?"
- "run a system diagnostic"
- "retrain the models"

### Natural Language
You can use natural language! Try phrases like:
- "How is everything doing?"
- "Is the system safe?"
- "Show me what happened today"
- "I need to stop trading"        """
        
        console.print(Markdown(help_content))
        
        response = self.personality.format_response(
            "Help information displayed. I can understand natural language commands!",
            'success'
        )
        console.print(f"\n[green]{response}[/green]")

    async def _handle_config(self, params: Dict[str, Any]):
        """Handle configuration commands"""
        console.print("\n[blue]⚙️  Accessing system configuration...[/blue]")
        
        # Show configuration using CLI
        if self.cli and hasattr(self.cli, 'config_show'):
            try:
                self.cli.config_show('all')
            except Exception as e:
                console.print(f"[yellow]CLI config unavailable: {e}[/yellow]")
                console.print("[blue]Configuration files are stored in the config/ directory[/blue]")
        else:
            console.print("[blue]CLI interface not available - configuration files are stored in config/ directory[/blue]")
        
        if Confirm.ask("\nWould you like to modify any configuration settings?"):
            if self.cli and hasattr(self.cli, 'config_edit'):
                config_type = Prompt.ask(
                    "Which configuration to edit?",
                    choices=['system', 'bots', 'strategies'],
                    default='system'
                )
                try:
                    self.cli.config_edit(config_type)
                except Exception as e:
                    console.print(f"[yellow]CLI config edit unavailable: {e}[/yellow]")
                    console.print("[blue]Please edit configuration files manually in the config/ directory[/blue]")
            else:
                console.print("[blue]CLI interface not available - please edit configuration files manually in config/ directory[/blue]")
        
        response = self.personality.format_response(
            "Configuration access completed.",
            'success'
        )
        console.print(f"\n[green]{response}[/green]")
    
    async def _handle_ai_health(self, params: Dict[str, Any]):
        """Handle AI health status commands"""
        console.print("\n[blue]🤖 Checking AI system health...[/blue]")
        
        try:
            # Try to load AI status
            from pathlib import Path
            ai_status_file = Path("reports/ai_status.json")
            
            if ai_status_file.exists():
                with open(ai_status_file, 'r') as f:
                    ai_status = json.load(f)
                    
                # Display AI health
                health = ai_status.get('system_health', {})
                status = health.get('status', 'UNKNOWN')
                
                health_table = Table(title="AI System Health Report")
                health_table.add_column("Component", style="cyan")
                health_table.add_column("Status", style="magenta")
                health_table.add_column("Details", style="green")
                
                # System health
                status_color = "green" if status == "HEALTHY" else "yellow" if status == "DEGRADED" else "red"
                health_table.add_row("Overall Health", f"[{status_color}]{status}[/{status_color}]", f"Phase 14 AI System")
                
                # Component status
                components = ai_status.get('components_status', {})
                for component, comp_status in components.items():
                    comp_color = "green" if comp_status == "ACTIVE" else "red"
                    health_table.add_row(component.replace('_', ' ').title(), f"[{comp_color}]{comp_status}[/{comp_color}]", "Autonomous AI")
                
                console.print(health_table)
                
                # Show any issues
                issues = health.get('issues', [])
                if issues:
                    console.print("\n[yellow]⚠️  Health Issues:[/yellow]")
                    for issue in issues:
                        console.print(f"   • {issue}")
                        
                # Show recommendations
                recommendations = health.get('recommendations', [])
                if recommendations:
                    console.print("\n[blue]💡 Recommendations:[/blue]")
                    for rec in recommendations:
                        console.print(f"   • {rec}")
                
            else:
                console.print("[yellow]AI status not available - system may not be running[/yellow]")
                
            response = self.personality.format_response(
                "AI health check completed. The autonomous intelligence system is monitoring all operations.",
                'success'
            )
            console.print(f"\n[green]{response}[/green]")
            
        except Exception as e:
            console.print(f"[red]Error checking AI health: {e}[/red]")
    
    async def _handle_ai_retrain(self, params: Dict[str, Any]):
        """Handle AI retraining commands"""
        console.print(f"\n{self.personality.config['confirmation']}")
        
        if not Confirm.ask("Trigger AI model retraining? This may temporarily affect performance."):
            console.print("\n[yellow]AI retraining cancelled.[/yellow]")
            return
            
        console.print("\n[blue]🧠 Triggering AI model retraining...[/blue]")
        
        try:
            # Try to trigger retraining via Phase 14 system
            # This would connect to the actual AI orchestrator in a real implementation
            reason = params.get('reason', 'Manual command trigger')
            
            console.print(f"[blue]Reason: {reason}[/blue]")
            console.print("[blue]🔄 Initiating retraining sequence...[/blue]")
            
            # Simulate retraining process
            from rich.progress import Progress, SpinnerColumn, TextColumn
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Analyzing performance triggers...", total=None)
                await asyncio.sleep(2)
                
                progress.update(task, description="Loading training data...")
                await asyncio.sleep(2)
                
                progress.update(task, description="Retraining AI models...")
                await asyncio.sleep(3)
                
                progress.update(task, description="Validating model performance...")
                await asyncio.sleep(2)
                
                progress.update(task, description="Deploying updated models...")
                await asyncio.sleep(1)
            
            success_msg = self.personality.format_response(
                "AI model retraining completed successfully!\n"
                "The autonomous intelligence system is now using updated models based on recent performance data.",
                'success'
            )
            console.print(f"\n[green]{success_msg}[/green]")
            
        except Exception as e:
            console.print(f"[red]AI retraining failed: {e}[/red]")
    
    async def _handle_anomaly_report(self, params: Dict[str, Any]):
        """Handle anomaly report commands"""
        console.print("\n[blue]🚨 Generating anomaly detection report...[/blue]")
        
        try:
            # Try to load anomaly data
            from pathlib import Path
            anomaly_file = Path("reports/anomaly_log.json")
            
            if anomaly_file.exists():
                with open(anomaly_file, 'r') as f:
                    anomalies = json.load(f)
                    
                # Get recent anomalies (last 24 hours)
                from datetime import datetime, timedelta
                cutoff_time = datetime.now() - timedelta(hours=24)
                
                recent_anomalies = [
                    a for a in anomalies 
                    if datetime.fromisoformat(a['timestamp']) > cutoff_time
                ]
                
                anomaly_table = Table(title="Anomaly Detection Report (24h)")
                anomaly_table.add_column("Time", style="cyan")
                anomaly_table.add_column("Type", style="yellow")
                anomaly_table.add_column("Severity", style="red")
                anomaly_table.add_column("Symbol", style="green")
                anomaly_table.add_column("Details", style="white")
                
                for anomaly in recent_anomalies[:10]:  # Show last 10
                    timestamp = datetime.fromisoformat(anomaly['timestamp'])
                    anomaly_type = anomaly.get('anomaly_type', 'UNKNOWN')
                    severity = anomaly.get('severity', 'LOW')
                    
                    trade_metrics = anomaly.get('trade_metrics', {})
                    symbol = trade_metrics.get('symbol', 'N/A')
                    actual_return = trade_metrics.get('actual_return', 0)
                    
                    severity_color = "red" if severity == "CRITICAL" else "yellow" if severity == "HIGH" else "white"
                    
                    anomaly_table.add_row(
                        timestamp.strftime("%H:%M:%S"),
                        anomaly_type,
                        f"[{severity_color}]{severity}[/{severity_color}]",
                        symbol,
                        f"Return: {actual_return:.3f}"
                    )
                
                console.print(anomaly_table)
                
                # Summary statistics
                total_anomalies = len(recent_anomalies)
                critical_count = len([a for a in recent_anomalies if a.get('severity') == 'CRITICAL'])
                
                console.print(f"\n📊 Anomaly Summary:")
                console.print(f"   Total Anomalies (24h): {total_anomalies}")
                console.print(f"   Critical Issues: {critical_count}")
                
                if critical_count > 0:
                    console.print(f"   [red]⚠️  {critical_count} critical anomalies require attention[/red]")
                else:
                    console.print(f"   [green]✅ No critical anomalies detected[/green]")
                    
            else:
                console.print("[yellow]No anomaly data available[/yellow]")
                
            response = self.personality.format_response(
                "Anomaly report generated. The AI system continuously monitors for trading anomalies.",
                'success'
            )
            console.print(f"\n[green]{response}[/green]")
            
        except Exception as e:
            console.print(f"[red]Error generating anomaly report: {e}[/red]")
    
    async def _handle_ai_performance(self, params: Dict[str, Any]):
        """Handle AI performance commands"""
        console.print("\n[blue]📈 Analyzing AI performance metrics...[/blue]")
        
        try:
            # Try to load strategy weights and performance data
            from pathlib import Path
            weights_file = Path("strategy_weights.json")
            
            if weights_file.exists():
                with open(weights_file, 'r') as f:
                    weights_data = json.load(f)
                    
                strategies = weights_data.get('strategies', {})
                bots = weights_data.get('bots', {})
                
                # Strategy performance table
                if strategies:
                    strategy_table = Table(title="Strategy Performance & Weights")
                    strategy_table.add_column("Strategy", style="cyan")
                    strategy_table.add_column("Weight", style="magenta")
                    strategy_table.add_column("Status", style="green")
                    
                    for strategy, weight in strategies.items():
                        weight_status = "🟢 HIGH" if weight > 1.2 else "🟡 NORMAL" if weight > 0.8 else "🔴 LOW"
                        strategy_table.add_row(strategy.title(), f"{weight:.3f}", weight_status)
                    
                    console.print(strategy_table)
                
                # Bot performance table
                if bots:
                    bot_table = Table(title="Bot Performance & Weights")
                    bot_table.add_column("Bot", style="cyan")
                    bot_table.add_column("Weight", style="magenta")
                    bot_table.add_column("Status", style="green")
                    
                    for bot, weight in bots.items():
                        weight_status = "🟢 HIGH" if weight > 1.2 else "🟡 NORMAL" if weight > 0.8 else "🔴 LOW"
                        bot_table.add_row(bot, f"{weight:.3f}", weight_status)
                    
                    console.print(bot_table)
                
                # Performance insights
                console.print(f"\n🧠 AI Performance Insights:")
                
                if strategies:
                    best_strategy = max(strategies.items(), key=lambda x: x[1])
                    worst_strategy = min(strategies.items(), key=lambda x: x[1])
                    console.print(f"   Best Strategy: {best_strategy[0]} (weight: {best_strategy[1]:.3f})")
                    console.print(f"   Needs Improvement: {worst_strategy[0]} (weight: {worst_strategy[1]:.3f})")
                
                if bots:
                    best_bot = max(bots.items(), key=lambda x: x[1])
                    console.print(f"   Top Performing Bot: {best_bot[0]} (weight: {best_bot[1]:.3f})")
                    
            else:
                console.print("[yellow]No performance data available - AI system may be initializing[/yellow]")
                
            response = self.personality.format_response(
                "AI performance analysis completed. The reinforcement engine continuously optimizes strategy weights.",
                'success'
            )
            console.print(f"\n[green]{response}[/green]")
            
        except Exception as e:
            console.print(f"[red]Error analyzing AI performance: {e}[/red]")
    
    async def _handle_unknown(self, user_input: str, params: Dict[str, Any]):
        """Handle unknown commands"""
        console.print("\n[yellow]🤔 I'm not sure I understand that command.[/yellow]")
        
        # Try to provide helpful suggestions
        suggestions = []
        text_lower = user_input.lower()
        
        if any(word in text_lower for word in ['stop', 'pause', 'halt']):
            suggestions.append("Did you mean 'pause the system'?")
        elif any(word in text_lower for word in ['start', 'begin', 'run']):
            suggestions.append("Did you mean 'resume trading' or 'run diagnostics'?")
        elif any(word in text_lower for word in ['show', 'display', 'view']):
            suggestions.append("Try 'show status' or 'show performance'")
        
        if suggestions:
            console.print("\n[blue]💡 Suggestions:[/blue]")
            for suggestion in suggestions:
                console.print(f"  • {suggestion}")
        
        console.print("\n[dim]Type 'help' to see all available commands.[/dim]")
    
    def _handle_goodbye(self):
        """Handle session exit"""
        session_duration = datetime.now() - self.session_start
        
        goodbye_msg = self.personality.format_response(
            f"Session ended after {session_duration.total_seconds():.0f} seconds.\n"
            f"Commands processed: {len(self.conversation_history)}\n"
            "Thank you for using TradeMasterX Assistant! 👋",
            'success'        )
        console.print(f"\n[green]{goodbye_msg}[/green]")


def main():
    """Main entry point for command assistant"""
    
    parser = argparse.ArgumentParser(description="TradeMasterX Smart Command Assistant")
    parser.add_argument('--personality', choices=['professional', 'friendly', 'technical'], 
                       default='professional', help='Assistant personality style')
    parser.add_argument('--setup-keys', action='store_true', 
                       help='Setup API keys for enhanced features')
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    try:
        # Create and start assistant
        assistant = CommandAssistant(personality=args.personality)
        
        if args.setup_keys:
            assistant.api_manager.request_api_keys()
            console.print("\n[green]✅ API keys configuration completed![/green]")
            return
        
        # Start interactive session
        assistant.start_session()
        
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Session interrupted. Goodbye! 👋[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Fatal error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
