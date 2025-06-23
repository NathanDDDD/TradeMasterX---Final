#!/usr/bin/env python3
"""
TradeMasterX CLI Interface
Command-line interface for TradeMasterX with comprehensive bot management
"""

import os
import sys
import json
import argparse
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich.syntax import Syntax
import yaml

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

# Use lazy imports to avoid circular dependencies
MasterBot = None
BotRegistry = None
ScoringEngine = None
ConfigLoader = None
AnalyticsBot = None

def lazy_import_core_modules():
    """Lazy import of core modules to avoid circular dependencies"""
    global MasterBot, BotRegistry, ScoringEngine, ConfigLoader, AnalyticsBot
    
    try:
        from trademasterx.core.master_bot import MasterBot
    except ImportError:
        pass
    
    try:
        from trademasterx.core.bot_registry import BotRegistry
    except ImportError:
        pass
    
    try:
        from trademasterx.core.scoring import ScoringEngine
    except ImportError:
        pass
    
    try:
        from trademasterx.config.config_loader import ConfigLoader
    except ImportError:
        pass
    
    try:
        from trademasterx.bots.analytics.analytics_bot import AnalyticsBot
    except ImportError:
        pass

console = Console()

class TradeMasterXCLI:
    """
    Advanced CLI interface for TradeMasterX with rich formatting and interactive features
    """
    
    def __init__(self, config_path: Optional[str] = None):
        # Lazy import core modules to avoid circular dependencies
        lazy_import_core_modules()
        
        self.config_loader = ConfigLoader() if ConfigLoader else None
        self.bot_registry = BotRegistry() if BotRegistry else None
        self.master_bot = None
        self.scoring_engine = ScoringEngine() if ScoringEngine else None
          # Initialize bots if registry is available
        if self.bot_registry:
            self._register_bots()
        
        console.print(Panel.fit("TradeMasterX 2.0 CLI", style="bold blue"))
    
    def _register_bots(self):
        """Register all available bot types"""
        if not self.bot_registry:
            console.print("⚠ Bot registry not available", style="yellow")
            return
            
        try:
            if AnalyticsBot:
                self.bot_registry.register_bot('analytics', AnalyticsBot)
            
            # Note: Other bot types would be registered here when available
            # self.bot_registry.register_bot('strategy', StrategyBot)
            # self.bot_registry.register_bot('risk', RiskBot)
            # self.bot_registry.register_bot('memory', MemoryBot)
            # self.bot_registry.register_bot('logger', LoggerBot)
            
            console.print("✓ Available bot types registered successfully", style="green")
            
        except Exception as e:
            console.print(f"✗ Error registering bots: {e}", style="red")
    
    def status(self):
        """Display system status"""
        console.print("\n[bold]System Status[/bold]")
        
        # System information
        status_table = Table(title="TradeMasterX System Status")
        status_table.add_column("Component", style="cyan", no_wrap=True)
        status_table.add_column("Status", style="magenta")
        status_table.add_column("Details", style="green")
        
        # Master bot status
        master_status = "Active" if self.master_bot and self.master_bot.is_active else "Inactive"
        master_style = "green" if master_status == "Active" else "red"
        status_table.add_row("Master Bot", f"[{master_style}]{master_status}[/{master_style}]", 
                           f"Started: {getattr(self.master_bot, 'start_time', 'N/A')}")
        
        # Bot registry status
        active_count = len(self.bot_registry.active_bots)
        total_types = len(self.bot_registry.registered_bots)
        status_table.add_row("Bot Registry", f"[green]{active_count} Active[/green]", 
                           f"{total_types} types registered")
        
        # Scoring engine status
        scoring_status = "Available" if self.scoring_engine else "Unavailable"
        status_table.add_row("Scoring Engine", f"[green]{scoring_status}[/green]", 
                           "Performance monitoring ready")
        
        console.print(status_table)
        
        # Active bots table
        if self.bot_registry.active_bots:
            console.print("\n[bold]Active Bots[/bold]")
            bots_table = Table(title="Active Bot Instances")
            bots_table.add_column("Bot ID", style="cyan")
            bots_table.add_column("Type", style="magenta")
            bots_table.add_column("Status", style="green")
            bots_table.add_column("Created", style="yellow")
            
            for bot_id, bot in self.bot_registry.active_bots.items():
                bot_status = "Active" if hasattr(bot, 'is_active') and bot.is_active else "Inactive"
                status_style = "green" if bot_status == "Active" else "red"
                created_time = getattr(bot, 'created_at', 'Unknown')
                
                bots_table.add_row(
                    bot_id,
                    bot.__class__.__name__,
                    f"[{status_style}]{bot_status}[/{status_style}]",
                    str(created_time)
                )
            
            console.print(bots_table)
        else:
            console.print("\n[yellow]No active bots[/yellow]")
    
    def list_bots(self, category: Optional[str] = None):
        """List available and active bots"""
        console.print(f"\n[bold]Bot Management[/bold]")
        
        # Available bot types
        available_table = Table(title="Available Bot Types")
        available_table.add_column("Type", style="cyan")
        available_table.add_column("Class", style="magenta")
        available_table.add_column("Description", style="green")
        
        descriptions = {
            'analytics': 'Pattern analysis and market insights',
            'strategy': 'Trading strategy execution and signals',
            'risk': 'Risk management and portfolio monitoring',
            'memory': 'Intelligent caching and data management',
            'logger': 'Logging, audit trails, and alerts'
        }
        
        for bot_type, bot_class in self.bot_registry.registered_bots.items():
            if category and category.lower() not in bot_type.lower():
                continue
                
            available_table.add_row(
                bot_type,
                bot_class.__name__,
                descriptions.get(bot_type, 'Advanced bot functionality')
            )
        
        console.print(available_table)
        
        # Active instances
        if self.bot_registry.active_bots:
            active_table = Table(title="Active Bot Instances")
            active_table.add_column("Bot ID", style="cyan")
            active_table.add_column("Type", style="magenta")
            active_table.add_column("Status", style="green")
            active_table.add_column("Config", style="yellow")
            
            for bot_id, bot in self.bot_registry.active_bots.items():
                if category and category.lower() not in bot.__class__.__name__.lower():
                    continue
                    
                bot_status = "Active" if hasattr(bot, 'is_active') and bot.is_active else "Inactive"
                status_style = "green" if bot_status == "Active" else "red"
                config_summary = str(len(getattr(bot, 'config', {}))) + " settings"
                
                active_table.add_row(
                    bot_id,
                    bot.__class__.__name__,
                    f"[{status_style}]{bot_status}[/{status_style}]",
                    config_summary
                )
            
            console.print(active_table)
    
    def create_bot(self, bot_type: str, config: Optional[Dict[str, Any]] = None):
        """Create a new bot instance"""
        console.print(f"\n[bold]Creating {bot_type} bot...[/bold]")
        
        if bot_type not in self.bot_registry.registered_bots:
            console.print(f"✗ Unknown bot type: {bot_type}", style="red")
            console.print(f"Available types: {list(self.bot_registry.registered_bots.keys())}")
            return False
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Creating bot...", total=None)
                
                # Get configuration interactively if not provided
                if not config:
                    config = self._get_bot_config_interactive(bot_type)
                
                # Create the bot
                bot_id = self.bot_registry.create_bot(bot_type, config)
                progress.update(task, description="Bot created successfully!")
            
            console.print(f"✓ Bot created successfully with ID: [bold cyan]{bot_id}[/bold cyan]", style="green")
            return True
            
        except Exception as e:
            console.print(f"✗ Error creating bot: {e}", style="red")
            return False
    
    def _get_bot_config_interactive(self, bot_type: str) -> Dict[str, Any]:
        """Get bot configuration interactively"""
        config = {}
        
        console.print(f"\n[bold]Configuration for {bot_type} bot:[/bold]")
        
        if bot_type == 'analytics':
            config['analysis_interval'] = int(Prompt.ask("Analysis interval (minutes)", default="5"))
            config['pattern_threshold'] = float(Prompt.ask("Pattern detection threshold", default="0.7"))
            config['enable_notifications'] = Confirm.ask("Enable notifications?", default=True)
            
        elif bot_type == 'strategy':
            strategy_types = ['momentum', 'mean_reversion', 'breakout']
            config['strategy_type'] = Prompt.ask("Strategy type", choices=strategy_types, default='momentum')
            config['risk_level'] = Prompt.ask("Risk level", choices=['low', 'medium', 'high'], default='medium')
            config['position_size'] = float(Prompt.ask("Position size (%)", default="1.0"))
            
        elif bot_type == 'risk':
            config['max_risk_per_trade'] = float(Prompt.ask("Max risk per trade (%)", default="2.0"))
            config['alert_threshold'] = float(Prompt.ask("Alert threshold", default="0.8"))
            config['enable_emergency_stop'] = Confirm.ask("Enable emergency stop?", default=True)
            
        elif bot_type == 'memory':
            config['cache_size'] = int(Prompt.ask("Cache size (MB)", default="100"))
            config['enable_redis'] = Confirm.ask("Enable Redis backend?", default=False)
            config['cleanup_interval'] = int(Prompt.ask("Cleanup interval (hours)", default="24"))
            
        elif bot_type == 'logger':
            config['log_level'] = Prompt.ask("Log level", choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], default='INFO')
            config['enable_file_logging'] = Confirm.ask("Enable file logging?", default=True)
            config['enable_database_logging'] = Confirm.ask("Enable database logging?", default=True)
        
        # Common settings
        config['name'] = Prompt.ask("Bot name (optional)", default="")
        config['description'] = Prompt.ask("Description (optional)", default="")
        
        return config
    
    def start_bot(self, bot_id: str):
        """Start a bot"""
        console.print(f"\n[bold]Starting bot {bot_id}...[/bold]")
        
        bot = self.bot_registry.get_bot(bot_id)
        if not bot:
            console.print(f"✗ Bot {bot_id} not found", style="red")
            return False
        
        try:
            if hasattr(bot, 'start'):
                bot.start()
                console.print(f"✓ Bot {bot_id} started successfully", style="green")
                return True
            else:
                console.print(f"✗ Bot {bot_id} does not support start operation", style="red")
                return False
                
        except Exception as e:
            console.print(f"✗ Error starting bot: {e}", style="red")
            return False
    
    def stop_bot(self, bot_id: str):
        """Stop a bot"""
        console.print(f"\n[bold]Stopping bot {bot_id}...[/bold]")
        
        bot = self.bot_registry.get_bot(bot_id)
        if not bot:
            console.print(f"✗ Bot {bot_id} not found", style="red")
            return False
        
        try:
            if hasattr(bot, 'stop'):
                bot.stop()
                console.print(f"✓ Bot {bot_id} stopped successfully", style="green")
                return True
            else:
                console.print(f"✗ Bot {bot_id} does not support stop operation", style="red")
                return False
                
        except Exception as e:
            console.print(f"✗ Error stopping bot: {e}", style="red")
            return False
    
    def delete_bot(self, bot_id: str, force: bool = False):
        """Delete a bot"""
        if not force:
            if not Confirm.ask(f"Are you sure you want to delete bot {bot_id}?"):
                console.print("Operation cancelled", style="yellow")
                return False
        
        console.print(f"\n[bold]Deleting bot {bot_id}...[/bold]")
        
        try:
            success = self.bot_registry.remove_bot(bot_id)
            if success:
                console.print(f"✓ Bot {bot_id} deleted successfully", style="green")
                return True
            else:
                console.print(f"✗ Bot {bot_id} not found", style="red")
                return False
                
        except Exception as e:
            console.print(f"✗ Error deleting bot: {e}", style="red")
            return False
    
    def bot_info(self, bot_id: str):
        """Show detailed bot information"""
        bot = self.bot_registry.get_bot(bot_id)
        if not bot:
            console.print(f"✗ Bot {bot_id} not found", style="red")
            return
        
        console.print(f"\n[bold]Bot Information: {bot_id}[/bold]")
        
        # Basic info panel
        info_content = f"""
[cyan]Type:[/cyan] {bot.__class__.__name__}
[cyan]Status:[/cyan] {'Active' if hasattr(bot, 'is_active') and bot.is_active else 'Inactive'}
[cyan]Created:[/cyan] {getattr(bot, 'created_at', 'Unknown')}
[cyan]Last Update:[/cyan] {getattr(bot, 'last_update', 'Never')}
        """
        
        console.print(Panel(info_content.strip(), title="Basic Information", border_style="blue"))
        
        # Configuration
        config = getattr(bot, 'config', {})
        if config:
            console.print("\n[bold]Configuration:[/bold]")
            config_syntax = Syntax(json.dumps(config, indent=2), "json", theme="monokai", line_numbers=True)
            console.print(config_syntax)
        
        # Bot-specific information
        if isinstance(bot, AnalyticsBot):
            self._show_analytics_info(bot)
        elif isinstance(bot, StrategyBot):
            self._show_strategy_info(bot)
        elif isinstance(bot, RiskBot):
            self._show_risk_info(bot)
    
    def _show_analytics_info(self, bot):
        """Show analytics bot specific information"""
        console.print("\n[bold]Analytics Information:[/bold]")
        
        analytics_table = Table()
        analytics_table.add_column("Metric", style="cyan")
        analytics_table.add_column("Value", style="green")
        
        analytics_table.add_row("Patterns Detected", str(len(getattr(bot.pattern_analyzer, 'patterns', []))))
        analytics_table.add_row("Active Signals", str(len(getattr(bot.signal_analyzer, 'active_signals', []))))
        analytics_table.add_row("Analysis Count", str(getattr(bot, 'analysis_count', 0)))
        
        console.print(analytics_table)
    
    def _show_strategy_info(self, bot):
        """Show strategy bot specific information"""
        console.print("\n[bold]Strategy Information:[/bold]")
        
        strategy_table = Table()
        strategy_table.add_column("Metric", style="cyan")
        strategy_table.add_column("Value", style="green")
        
        strategy_table.add_row("Active Strategies", str(len(getattr(bot, 'active_strategies', []))))
        strategy_table.add_row("Signals Generated", str(getattr(bot, 'signals_generated', 0)))
        strategy_table.add_row("Current Position", str(getattr(bot, 'current_position', 'None')))
        
        console.print(strategy_table)
    
    def _show_risk_info(self, bot):
        """Show risk bot specific information"""
        console.print("\n[bold]Risk Information:[/bold]")
        
        risk_table = Table()
        risk_table.add_column("Metric", style="cyan")
        risk_table.add_column("Value", style="green")
        
        risk_table.add_row("Risk Level", str(getattr(bot, 'current_risk_level', 'Unknown')))
        risk_table.add_row("Active Alerts", str(len(getattr(bot, 'active_alerts', []))))
        risk_table.add_row("Risk Assessments", str(getattr(bot, 'assessments_count', 0)))
        
        console.print(risk_table)
    
    def config_show(self, config_type: str = 'all'):
        """Show configuration"""
        console.print(f"\n[bold]Configuration ({config_type})[/bold]")
        
        if config_type == 'all':
            config_types = ['system', 'bots', 'strategies']
        else:
            config_types = [config_type]
        
        for ctype in config_types:
            config_data = self.config_loader.get_config(ctype, {})
            
            if config_data:
                console.print(f"\n[bold cyan]{ctype.title()} Configuration:[/bold cyan]")
                config_syntax = Syntax(
                    yaml.dump(config_data, default_flow_style=False), 
                    "yaml", 
                    theme="monokai",
                    line_numbers=True
                )
                console.print(config_syntax)
            else:
                console.print(f"\n[yellow]No {ctype} configuration found[/yellow]")
    
    def config_edit(self, config_type: str):
        """Edit configuration interactively"""
        console.print(f"\n[bold]Editing {config_type} configuration[/bold]")
        
        current_config = self.config_loader.get_config(config_type, {})
        
        # Show current configuration
        if current_config:
            console.print("\n[bold]Current configuration:[/bold]")
            console.print(Syntax(yaml.dump(current_config, default_flow_style=False), "yaml"))
        
        # Get new configuration
        console.print("\n[bold]Enter new configuration (YAML format):[/bold]")
        console.print("[dim]Press Ctrl+D when finished[/dim]")
        
        try:
            lines = []
            while True:
                try:
                    line = input()
                    lines.append(line)
                except EOFError:
                    break
            
            yaml_content = '\n'.join(lines)
            new_config = yaml.safe_load(yaml_content)
            
            # Save configuration
            self.config_loader.save_config(config_type, new_config)
            console.print(f"✓ {config_type} configuration saved successfully", style="green")
            
        except yaml.YAMLError as e:
            console.print(f"✗ Invalid YAML format: {e}", style="red")
        except Exception as e:
            console.print(f"✗ Error saving configuration: {e}", style="red")


# CLI Commands using Click
@click.group(invoke_without_command=True)
@click.option('--config', '-c', help='Configuration file path')
@click.pass_context
def cli(ctx, config):
    """TradeMasterX 2.0 Command Line Interface"""
    ctx.ensure_object(dict)
    ctx.obj['cli'] = TradeMasterXCLI(config)
    
    if ctx.invoked_subcommand is None:
        ctx.obj['cli'].status()

@cli.command()
@click.pass_context
def status(ctx):
    """Show system status"""
    ctx.obj['cli'].status()

@cli.command()
@click.option('--category', '-c', help='Filter by bot category')
@click.pass_context
def list(ctx, category):
    """List available and active bots"""
    ctx.obj['cli'].list_bots(category)

@cli.command()
@click.argument('bot_type')
@click.option('--config-file', help='Configuration file for the bot')
@click.pass_context
def create(ctx, bot_type, config_file):
    """Create a new bot instance"""
    config = None
    if config_file:
        try:
            with open(config_file, 'r') as f:
                if config_file.endswith('.yaml') or config_file.endswith('.yml'):
                    config = yaml.safe_load(f)
                else:
                    config = json.load(f)
        except Exception as e:
            console.print(f"✗ Error loading config file: {e}", style="red")
            return
    
    ctx.obj['cli'].create_bot(bot_type, config)

@cli.command()
@click.argument('bot_id')
@click.pass_context
def start(ctx, bot_id):
    """Start a bot"""
    ctx.obj['cli'].start_bot(bot_id)

@cli.command()
@click.argument('bot_id')
@click.pass_context
def stop(ctx, bot_id):
    """Stop a bot"""
    ctx.obj['cli'].stop_bot(bot_id)

@cli.command()
@click.argument('bot_id')
@click.option('--force', '-f', is_flag=True, help='Force deletion without confirmation')
@click.pass_context
def delete(ctx, bot_id, force):
    """Delete a bot"""
    ctx.obj['cli'].delete_bot(bot_id, force)

@cli.command()
@click.argument('bot_id')
@click.pass_context
def info(ctx, bot_id):
    """Show detailed bot information"""
    ctx.obj['cli'].bot_info(bot_id)

@cli.group()
def config():
    """Configuration management"""
    pass

@config.command('show')
@click.argument('config_type', default='all')
@click.pass_context
def config_show(ctx, config_type):
    """Show configuration"""
    ctx.obj['cli'].config_show(config_type)

@config.command('edit')
@click.argument('config_type')
@click.pass_context
def config_edit(ctx, config_type):
    """Edit configuration"""
    ctx.obj['cli'].config_edit(config_type)

@cli.command()
@click.option('--personality', type=click.Choice(['professional', 'friendly', 'technical']), 
              default='professional', help='Assistant personality style')
@click.option('--setup-keys', is_flag=True, help='Setup API keys for enhanced features')
@click.pass_context
def chat(ctx, personality, setup_keys):
    """Start the smart command assistant for natural language bot control"""
    try:
        # Import here to avoid circular imports
        from trademasterx.interface.assistant.command_assistant import CommandAssistant
        
        console.print("\n[bold blue] Starting TradeMasterX Smart Assistant...[/bold blue]")
        
        assistant = CommandAssistant(personality=personality)
        
        if setup_keys:
            assistant.api_manager.request_api_keys()
            console.print("\n[green]✅ API keys configuration completed![/green]")
            return
        
        # Start interactive session
        assistant.start_session()
        
    except ImportError as e:
        console.print(f"[red]✗ Error importing assistant: {e}[/red]")
        console.print("[yellow]Make sure the assistant module is properly installed.[/yellow]")
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Assistant session interrupted. Goodbye! 👋[/yellow]")
    except Exception as e:
        console.print(f"[red]✗ Error starting assistant: {e}[/red]")


if __name__ == '__main__':
    cli()
