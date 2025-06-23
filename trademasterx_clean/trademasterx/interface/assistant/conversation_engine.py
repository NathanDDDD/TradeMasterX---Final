#!/usr/bin/env python3
"""
TradeMasterX 2.0 - Conversation Engine
Phase 13: Context-Aware Chat System

Manages conversation context, system data integration, and intelligent responses
for the smart command interface. Provides the "voice" and personality of the bot.
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import sqlite3

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown

from .api_integration import APIIntegration, MockAPIIntegration

console = Console()
logger = logging.getLogger(__name__)


class ConversationMemory:
    """Manages conversation history and context"""
    
    def __init__(self, db_path: str = "data/conversation_memory.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize conversation memory database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    user_input TEXT NOT NULL,
                    parsed_command TEXT,
                    bot_response TEXT,
                    context_data TEXT,
                    success BOOLEAN DEFAULT 1
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS system_context (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    component TEXT NOT NULL,
                    data TEXT NOT NULL
                )
            """)
    
    def store_conversation(self, session_id: str, user_input: str, parsed_command: str, 
                          bot_response: str, context: Dict[str, Any], success: bool = True):
        """Store conversation entry"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO conversations 
                (session_id, timestamp, user_input, parsed_command, bot_response, context_data, success)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                session_id,
                datetime.now().isoformat(),
                user_input,
                parsed_command,
                bot_response,
                json.dumps(context),
                success
            ))
    
    def get_recent_conversations(self, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversations for context"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT timestamp, user_input, parsed_command, bot_response, success
                FROM conversations 
                WHERE session_id = ?
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (session_id, limit))
            
            return [
                {
                    'timestamp': row[0],
                    'user_input': row[1],
                    'parsed_command': row[2],
                    'bot_response': row[3],
                    'success': bool(row[4])
                }
                for row in cursor.fetchall()
            ]
    
    def store_system_context(self, component: str, data: Dict[str, Any]):
        """Store system context data"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO system_context (timestamp, component, data)
                VALUES (?, ?, ?)
            """, (
                datetime.now().isoformat(),
                component,
                json.dumps(data)
            ))
    
    def get_system_context(self, component: str = None, hours_back: int = 24) -> List[Dict[str, Any]]:
        """Get recent system context"""
        cutoff_time = (datetime.now() - timedelta(hours=hours_back)).isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            if component:
                cursor = conn.execute("""
                    SELECT timestamp, component, data
                    FROM system_context 
                    WHERE component = ? AND timestamp > ?
                    ORDER BY timestamp DESC
                """, (component, cutoff_time))
            else:
                cursor = conn.execute("""
                    SELECT timestamp, component, data
                    FROM system_context 
                    WHERE timestamp > ?
                    ORDER BY timestamp DESC
                """, (cutoff_time,))
            
            return [
                {
                    'timestamp': row[0],
                    'component': row[1],
                    'data': json.loads(row[2])
                }
                for row in cursor.fetchall()
            ]


class SystemDataCollector:
    """Collects system data for conversation context"""
    
    def __init__(self, cli_instance, safety_dashboard, kill_switch):
        self.cli = cli_instance
        self.safety_dashboard = safety_dashboard
        self.kill_switch = kill_switch
    
    def collect_system_status(self) -> Dict[str, Any]:
        """Collect comprehensive system status"""
        try:
            # Kill switch status
            kill_switch_status = self.kill_switch.get_status() if self.kill_switch else {'active': False, 'message': 'Not available'}
            
            # Safety dashboard data  
            safety_data = self.safety_dashboard.get_dashboard_data() if self.safety_dashboard else {'status': 'Not available'}
            
            # Bot registry status
            active_bots = len(self.cli.bot_registry.active_bots)
            registered_bots = len(self.cli.bot_registry.registered_bots)
            
            return {
                'trading_active': not kill_switch_status['kill_switch_active'],
                'live_trading_enabled': kill_switch_status['live_trading_enabled'],
                'safety_level': safety_data.get('safety_level', 'UNKNOWN'),
                'system_health': safety_data.get('system_health', 'Unknown'),
                'active_bots': active_bots,
                'registered_bots': registered_bots,
                'last_updated': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error collecting system status: {e}")
            return {
                'error': str(e),
                'last_updated': datetime.now().isoformat()
            }
    
    def collect_performance_data(self, timeframe: str = 'today') -> Dict[str, Any]:
        """Collect performance data (mock for now)"""
        # In a real implementation, this would integrate with actual analytics
        return {
            'timeframe': timeframe,
            'total_pnl': 1234.56,
            'win_rate': 67.3,
            'trades_executed': 23,
            'max_drawdown': 2.1,
            'sharpe_ratio': 2.34,
            'last_updated': datetime.now().isoformat()
        }
    
    def collect_risk_data(self) -> Dict[str, Any]:
        """Collect risk assessment data"""
        try:
            safety_data = self.safety_dashboard.get_dashboard_data()
            
            return {
                'overall_risk': safety_data.get('safety_level', 'UNKNOWN'),
                'position_risk': 'LOW',
                'market_risk': 'MEDIUM', 
                'system_risk': 'LOW',
                'liquidity_risk': 'LOW',
                'last_updated': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error collecting risk data: {e}")
            return {
                'error': str(e),
                'last_updated': datetime.now().isoformat()
            }
    
    def collect_logs_data(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Collect recent log entries (mock for now)"""
        # In a real implementation, this would read from actual log files
        return [
            {
                'timestamp': '15:34:22',
                'level': 'INFO',
                'component': 'AnalyticsBot',
                'message': 'Pattern detection completed'
            },
            {
                'timestamp': '15:33:45',
                'level': 'INFO',
                'component': 'StrategyBot',
                'message': 'New signal generated: BUY BTC'
            },
            {
                'timestamp': '15:33:12',
                'level': 'WARN',
                'component': 'RiskGuard',
                'message': 'Position size near limit'
            },
            {
                'timestamp': '15:32:08',
                'level': 'INFO',
                'component': 'MasterBot',
                'message': 'Health check passed'
            },
            {
                'timestamp': '15:31:55',
                'level': 'INFO',
                'component': 'KillSwitch',
                'message': 'System status: ACTIVE'
            }
        ][:limit]


class ConversationEngine:
    """
    Main conversation engine that manages context, personality, and intelligent responses
    """
    
    def __init__(self, command_assistant=None):
        self.assistant = command_assistant
        self.memory = ConversationMemory()
        
        # Initialize data collector with fallback handling
        if command_assistant:
            self.data_collector = SystemDataCollector(
                getattr(command_assistant, 'cli', None),
                getattr(command_assistant, 'safety_dashboard', None),
                getattr(command_assistant, 'kill_switch', None)
            )
        else:
            self.data_collector = SystemDataCollector(None, None, None)
        
        # Initialize API integration
        self.api_integration = self._init_api_integration()
        
        # Session management
        self.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.conversation_count = 0
        
        # Context tracking
        self.current_context = {}
        self.update_system_context()
    
    def _init_api_integration(self) -> APIIntegration:
        """Initialize API integration with fallback to mock"""
        if (self.assistant.api_manager.has_claude_key() or 
            self.assistant.api_manager.has_openai_key()):
            return APIIntegration(self.assistant.api_manager)
        else:
            logger.info("No API keys available, using mock integration")
            return MockAPIIntegration(self.assistant.api_manager)
    
    def update_system_context(self):
        """Update current system context"""
        self.current_context = {
            'system_status': self.data_collector.collect_system_status(),
            'performance_data': self.data_collector.collect_performance_data(),
            'risk_data': self.data_collector.collect_risk_data(),
            'recent_logs': self.data_collector.collect_logs_data(5)
        }
        
        # Store in memory
        self.memory.store_system_context('system_status', self.current_context['system_status'])
        self.memory.store_system_context('performance', self.current_context['performance_data'])
        self.memory.store_system_context('risk', self.current_context['risk_data'])
    
    async def process_conversation(self, user_input: str) -> Tuple[str, Dict[str, Any]]:
        """
        Process a conversation turn with enhanced AI understanding
        
        Returns:
            Tuple of (bot_response, execution_result)
        """
        try:
            # Update system context
            self.update_system_context()
            
            # Get enhanced understanding from AI APIs
            ai_understanding = await self.api_integration.enhance_command_understanding(
                user_input, 
                self.current_context
            )
            
            # Use AI-enhanced command if confidence is high enough
            if ai_understanding.get('confidence', 0) >= 0.7:
                command_type = ai_understanding['command']
                params = ai_understanding.get('parameters', {})
                
                console.print(f"\n[dim]🤖 AI Understanding: {ai_understanding.get('explanation', 'Processed command')}[/dim]")
            else:
                # Fallback to original parser
                command_type, params = self.assistant.parser.parse_command(user_input)
                
                if ai_understanding.get('suggestions'):
                    console.print(f"\n[dim]💡 AI Suggestions: {', '.join(ai_understanding['suggestions'])}[/dim]")
            
            # Execute the command
            execution_result = await self._execute_command(command_type, params, user_input)
            
            # Generate intelligent response
            bot_response = await self.api_integration.generate_response(
                command_type,
                execution_result,
                self.assistant.personality.type
            )
            
            # Store conversation
            self.memory.store_conversation(
                self.session_id,
                user_input,
                command_type,
                bot_response,
                self.current_context,
                execution_result.get('success', False)
            )
            
            self.conversation_count += 1
            return bot_response, execution_result
            
        except Exception as e:
            logger.error(f"Error processing conversation: {e}")
            error_response = f"I encountered an error processing your request: {str(e)}"
            
            self.memory.store_conversation(
                self.session_id,
                user_input,
                'error',
                error_response,
                self.current_context,
                False
            )
            
            return error_response, {'success': False, 'error': str(e)}
    
    async def _execute_command(self, command_type: str, params: Dict[str, Any], original_input: str) -> Dict[str, Any]:
        """Execute the parsed command and return result"""
        try:
            # Route to appropriate command handler in the assistant
            if command_type == 'pause':
                await self.assistant._handle_pause(params)
                return {'success': True, 'message': 'System paused successfully'}
            
            elif command_type == 'resume':
                await self.assistant._handle_resume(params)
                return {'success': True, 'message': 'System resumed successfully'}
            
            elif command_type == 'status':
                await self.assistant._handle_status(params)
                return {'success': True, 'message': 'System status retrieved'}
            
            elif command_type == 'performance':
                await self.assistant._handle_performance(params)
                return {'success': True, 'message': 'Performance data retrieved'}
            
            elif command_type == 'retrain':
                await self.assistant._handle_retrain(params)
                return {'success': True, 'message': 'Model retraining completed'}
            
            elif command_type == 'diagnostics':
                await self.assistant._handle_diagnostics(params)
                return {'success': True, 'message': 'System diagnostics completed'}
            
            elif command_type == 'logs':
                await self.assistant._handle_logs(params)
                return {'success': True, 'message': 'System logs retrieved'}
            
            elif command_type == 'risk':
                await self.assistant._handle_risk(params)
                return {'success': True, 'message': 'Risk assessment completed'}
            
            elif command_type == 'shutdown':
                await self.assistant._handle_shutdown(params)
                return {'success': True, 'message': 'System shutdown initiated'}
            
            elif command_type == 'help':
                await self.assistant._handle_help(params)
                return {'success': True, 'message': 'Help information displayed'}
            
            elif command_type == 'config':
                await self.assistant._handle_config(params)
                return {'success': True, 'message': 'Configuration accessed'}
            
            else:
                await self.assistant._handle_unknown(original_input, params)
                return {'success': False, 'message': 'Unknown command'}
                
        except Exception as e:
            logger.error(f"Error executing command {command_type}: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get summary of current conversation session"""
        recent_conversations = self.memory.get_recent_conversations(self.session_id, 20)
        
        successful_commands = sum(1 for conv in recent_conversations if conv['success'])
        
        return {
            'session_id': self.session_id,
            'conversation_count': self.conversation_count,
            'successful_commands': successful_commands,
            'success_rate': successful_commands / max(self.conversation_count, 1),
            'session_duration': datetime.now() - datetime.fromisoformat(self.session_id.split('_')[1] + '_' + self.session_id.split('_')[2]),
            'api_stats': self.api_integration.get_stats(),
            'recent_commands': [conv['parsed_command'] for conv in recent_conversations[:5]]
        }
    
    def display_conversation_stats(self):
        """Display conversation statistics"""
        stats = self.get_conversation_summary()
        
        stats_table = Table(title="Conversation Session Statistics")
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="green")
        
        stats_table.add_row("Session ID", stats['session_id'])
        stats_table.add_row("Commands Processed", str(stats['conversation_count']))
        stats_table.add_row("Success Rate", f"{stats['success_rate']:.1%}")
        stats_table.add_row("API Success Rate", f"{stats['api_stats']['success_rate']:.1%}")
        stats_table.add_row("Recent Commands", ", ".join(stats['recent_commands']))
        
        console.print(stats_table)
    
    async def close(self):
        """Close conversation engine and cleanup resources"""
        if hasattr(self.api_integration, 'close'):
            await self.api_integration.close()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


def create_enhanced_assistant(personality: str = 'professional'):
    """
    Factory function to create an enhanced command assistant with conversation engine
    """
    from .command_assistant import CommandAssistant
    
    # Create base assistant
    assistant = CommandAssistant(personality)
    
    # Add conversation engine
    assistant.conversation_engine = ConversationEngine(assistant)
    
    # Override process_command to use conversation engine
    original_process_command = assistant.process_command
    
    async def enhanced_process_command(user_input: str):
        """Enhanced command processing with conversation context"""
        bot_response, execution_result = await assistant.conversation_engine.process_conversation(user_input)
        
        # Display the AI-generated response
        if execution_result.get('success', False):
            console.print(f"\n[green]{bot_response}[/green]")
        else:
            console.print(f"\n[yellow]{bot_response}[/yellow]")
    
    assistant.process_command = enhanced_process_command
    
    return assistant
