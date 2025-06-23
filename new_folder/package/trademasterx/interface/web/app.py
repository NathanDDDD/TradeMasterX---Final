#!/usr/bin/env python3
"""
TradeMasterX Web Interface
Advanced Flask web application with real-time updates and comprehensive dashboard
"""

import os
import sys
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.security import generate_password_hash, check_password_hash
import threading
import traceback
import logging

# Add root directory to path for absolute imports
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, root_dir)

from trademasterx.core.master_bot import MasterBot
from trademasterx.core.bot_registry import BotRegistry
from trademasterx.core.scoring import ScoringEngine
from trademasterx.config.config_loader import ConfigLoader
from trademasterx.bots.analytics.analytics_bot import AnalyticsBot
from trademasterx.bots.strategy.strategy import StrategyBot
from trademasterx.bots.system.risk_bot import RiskBot
from trademasterx.bots.system.memory_bot import MemoryBot
from trademasterx.bots.system.logger_bot import LoggerBot

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TradeMasterXWebApp:
    """
    Advanced web interface for TradeMasterX with real-time monitoring,
    bot control, and comprehensive analytics dashboard
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-me')
        
        # Initialize SocketIO with CORS support
        self.socketio = SocketIO(
            self.app,
            cors_allowed_origins="*",
            async_mode='threading'
        )
          # Initialize core components
        self.config_loader = ConfigLoader()
        self.bot_registry = BotRegistry()
        self.master_bot = None
        self.scoring_engine = ScoringEngine()
        
        # Active connections tracking
        self.active_connections = set()
        self.room_connections = {}
        
        # Background task control
        self._monitoring_active = False
        self._monitoring_thread = None
        
        # Setup routes and event handlers
        self._setup_routes()
        self._setup_socket_events()
        
        # Initialize bots
        self._initialize_bots()
        
        logger.info("TradeMasterX Web Interface initialized")
    
    def _initialize_bots(self):
        """Initialize all bot instances"""
        try:
            # Register all bot types
            self.bot_registry.register_bot('analytics', AnalyticsBot)
            self.bot_registry.register_bot('strategy', StrategyBot)
            self.bot_registry.register_bot('risk', RiskBot)
            self.bot_registry.register_bot('memory', MemoryBot)
            self.bot_registry.register_bot('logger', LoggerBot)
            
            # Initialize master bot
            config = self.config_loader.get_config('system', {})
            self.master_bot = MasterBot(config)
            
            logger.info("All bots initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing bots: {e}")
            traceback.print_exc()
    
    def _setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def index():
            """Main dashboard"""
            return render_template('dashboard.html')
        
        @self.app.route('/bots')
        def bots():
            """Bot management page"""
            return render_template('bots.html')
        
        @self.app.route('/analytics')
        def analytics():
            """Analytics dashboard"""
            return render_template('analytics.html')
        
        @self.app.route('/strategies')
        def strategies():
            """Strategy management page"""
            return render_template('strategies.html')
        
        @self.app.route('/risk')
        def risk():
            """Risk monitoring page"""
            return render_template('risk.html')
        
        @self.app.route('/config')
        def config():
            """Configuration management"""
            return render_template('config.html')
        
        @self.app.route('/logs')
        def logs():
            """Log viewer"""
            return render_template('logs.html')
        
        # API Routes
        @self.app.route('/api/status')
        def api_status():
            """Get system status"""
            try:
                status = {
                    'timestamp': datetime.now().isoformat(),
                    'master_bot_active': self.master_bot.is_active if self.master_bot else False,
                    'active_bots': len(self.bot_registry.active_bots),
                    'total_bots': len(self.bot_registry.registered_bots),
                    'system_health': 'healthy',
                    'active_connections': len(self.active_connections)
                }
                
                # Get bot statuses
                if self.master_bot:
                    bot_statuses = {}
                    for bot_id, bot in self.bot_registry.active_bots.items():
                        try:
                            bot_statuses[bot_id] = {
                                'active': hasattr(bot, 'is_active') and bot.is_active,
                                'type': bot.__class__.__name__,
                                'last_update': getattr(bot, 'last_update', None)
                            }
                        except Exception as e:
                            bot_statuses[bot_id] = {
                                'active': False,
                                'type': 'unknown',
                                'error': str(e)
                            }
                    
                    status['bots'] = bot_statuses
                
                return jsonify(status)
                
            except Exception as e:
                logger.error(f"Error getting status: {e}")
                return jsonify({
                    'error': str(e),
                    'timestamp': datetime.now().isoformat(),
                    'system_health': 'error'
                }), 500
        
        @self.app.route('/api/bots', methods=['GET'])
        def api_get_bots():
            """Get all registered bots"""
            try:
                bots_info = {
                    'registered': list(self.bot_registry.registered_bots.keys()),
                    'active': {},
                    'available_types': list(self.bot_registry.registered_bots.keys())
                }
                
                for bot_id, bot in self.bot_registry.active_bots.items():
                    bots_info['active'][bot_id] = {
                        'type': bot.__class__.__name__,
                        'status': 'active' if hasattr(bot, 'is_active') and bot.is_active else 'inactive',
                        'created': getattr(bot, 'created_at', None),
                        'config': getattr(bot, 'config', {})
                    }
                
                return jsonify(bots_info)
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/bots/<bot_type>', methods=['POST'])
        def api_create_bot(bot_type):
            """Create a new bot instance"""
            try:
                config = request.get_json() or {}
                bot_id = self.bot_registry.create_bot(bot_type, config)
                
                return jsonify({
                    'success': True,
                    'bot_id': bot_id,
                    'message': f'Bot {bot_id} created successfully'
                })
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/bots/<bot_id>', methods=['DELETE'])
        def api_delete_bot(bot_id):
            """Delete a bot instance"""
            try:
                success = self.bot_registry.remove_bot(bot_id)
                
                if success:
                    return jsonify({
                        'success': True,
                        'message': f'Bot {bot_id} deleted successfully'
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': f'Bot {bot_id} not found'
                    }), 404
                    
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/bots/<bot_id>/start', methods=['POST'])
        def api_start_bot(bot_id):
            """Start a bot"""
            try:
                bot = self.bot_registry.get_bot(bot_id)
                if not bot:
                    return jsonify({'error': 'Bot not found'}), 404
                
                if hasattr(bot, 'start'):
                    bot.start()
                    return jsonify({'success': True, 'message': f'Bot {bot_id} started'})
                else:
                    return jsonify({'error': 'Bot does not support start operation'}), 400
                    
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/bots/<bot_id>/stop', methods=['POST'])
        def api_stop_bot(bot_id):
            """Stop a bot"""
            try:
                bot = self.bot_registry.get_bot(bot_id)
                if not bot:
                    return jsonify({'error': 'Bot not found'}), 404
                
                if hasattr(bot, 'stop'):
                    bot.stop()
                    return jsonify({'success': True, 'message': f'Bot {bot_id} stopped'})
                else:
                    return jsonify({'error': 'Bot does not support stop operation'}), 400
                    
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/analytics/summary')
        def api_analytics_summary():
            """Get analytics summary"""
            try:
                # Get analytics bot if available
                analytics_bot = None
                for bot in self.bot_registry.active_bots.values():
                    if isinstance(bot, AnalyticsBot):
                        analytics_bot = bot
                        break
                
                if analytics_bot:
                    summary = {
                        'total_patterns': len(analytics_bot.pattern_analyzer.patterns),
                        'active_signals': len(analytics_bot.signal_analyzer.active_signals),
                        'bot_performance': analytics_bot.get_performance_summary(),
                        'market_analysis': analytics_bot.get_market_analysis(),
                        'last_update': analytics_bot.last_update
                    }
                else:
                    summary = {
                        'error': 'Analytics bot not active',
                        'total_patterns': 0,
                        'active_signals': 0,
                        'bot_performance': {},
                        'market_analysis': {}
                    }
                
                return jsonify(summary)
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/config')
        def api_get_config():
            """Get current configuration"""
            try:
                config = {
                    'system': self.config_loader.get_config('system', {}),
                    'bots': self.config_loader.get_config('bots', {}),
                    'strategies': self.config_loader.get_config('strategies', {})
                }
                return jsonify(config)
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/config', methods=['POST'])
        def api_update_config():
            """Update configuration"""
            try:
                new_config = request.get_json()
                
                for config_type, config_data in new_config.items():
                    self.config_loader.save_config(config_type, config_data)
                
                return jsonify({
                    'success': True,
                    'message': 'Configuration updated successfully'
                })
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
    
    def _setup_socket_events(self):
        """Setup SocketIO event handlers"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection"""
            session_id = request.sid
            self.active_connections.add(session_id)
            
            emit('connected', {
                'session_id': session_id,
                'timestamp': datetime.now().isoformat(),
                'message': 'Connected to TradeMasterX'
            })
            
            logger.info(f"Client connected: {session_id}")
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection"""
            session_id = request.sid
            self.active_connections.discard(session_id)
            
            # Remove from all rooms
            for room, members in self.room_connections.items():
                members.discard(session_id)
            
            logger.info(f"Client disconnected: {session_id}")
        
        @self.socketio.on('join_room')
        def handle_join_room(data):
            """Handle room joining"""
            room = data.get('room', 'general')
            session_id = request.sid
            
            join_room(room)
            
            if room not in self.room_connections:
                self.room_connections[room] = set()
            self.room_connections[room].add(session_id)
            
            emit('room_joined', {
                'room': room,
                'timestamp': datetime.now().isoformat()
            })
            
            logger.info(f"Client {session_id} joined room: {room}")
        
        @self.socketio.on('leave_room')
        def handle_leave_room(data):
            """Handle room leaving"""
            room = data.get('room', 'general')
            session_id = request.sid
            
            leave_room(room)
            
            if room in self.room_connections:
                self.room_connections[room].discard(session_id)
            
            emit('room_left', {
                'room': room,
                'timestamp': datetime.now().isoformat()
            })
        
        @self.socketio.on('request_status')
        def handle_request_status():
            """Handle status request"""
            try:
                status = self._get_real_time_status()
                emit('status_update', status)
            except Exception as e:
                emit('error', {'message': str(e)})
        
        @self.socketio.on('bot_command')
        def handle_bot_command(data):
            """Handle bot commands"""
            try:
                command = data.get('command')
                bot_id = data.get('bot_id')
                params = data.get('params', {})
                
                result = self._execute_bot_command(command, bot_id, params)
                emit('bot_command_result', result)
                
            except Exception as e:
                emit('error', {'message': str(e)})
    
    def _get_real_time_status(self) -> Dict[str, Any]:
        """Get real-time system status"""
        try:
            status = {
                'timestamp': datetime.now().isoformat(),
                'system': {
                    'active': self.master_bot.is_active if self.master_bot else False,
                    'uptime': self._get_uptime(),
                    'memory_usage': self._get_memory_usage(),
                    'active_connections': len(self.active_connections)
                },
                'bots': {},
                'performance': self.scoring_engine.get_current_scores() if hasattr(self.scoring_engine, 'get_current_scores') else {}
            }
            
            # Get bot statuses
            for bot_id, bot in self.bot_registry.active_bots.items():
                try:
                    bot_status = {
                        'id': bot_id,
                        'type': bot.__class__.__name__,
                        'active': hasattr(bot, 'is_active') and bot.is_active,
                        'last_update': getattr(bot, 'last_update', None)
                    }
                    
                    # Add specific metrics for different bot types
                    if isinstance(bot, AnalyticsBot):
                        bot_status['metrics'] = {
                            'patterns_detected': len(bot.pattern_analyzer.patterns),
                            'signals_active': len(bot.signal_analyzer.active_signals)
                        }
                    elif isinstance(bot, RiskBot):
                        bot_status['metrics'] = {
                            'risk_level': getattr(bot, 'current_risk_level', 'unknown'),
                            'alerts_active': len(getattr(bot, 'active_alerts', []))
                        }
                    
                    status['bots'][bot_id] = bot_status
                    
                except Exception as e:
                    status['bots'][bot_id] = {
                        'id': bot_id,
                        'error': str(e),
                        'active': False
                    }
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting real-time status: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'system': {'active': False}
            }
    
    def _execute_bot_command(self, command: str, bot_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a bot command"""
        try:
            bot = self.bot_registry.get_bot(bot_id)
            if not bot:
                return {'success': False, 'error': f'Bot {bot_id} not found'}
            
            if command == 'start':
                if hasattr(bot, 'start'):
                    bot.start()
                    return {'success': True, 'message': f'Bot {bot_id} started'}
                else:
                    return {'success': False, 'error': 'Bot does not support start operation'}
            
            elif command == 'stop':
                if hasattr(bot, 'stop'):
                    bot.stop()
                    return {'success': True, 'message': f'Bot {bot_id} stopped'}
                else:
                    return {'success': False, 'error': 'Bot does not support stop operation'}
            
            elif command == 'configure':
                if hasattr(bot, 'update_config'):
                    bot.update_config(params)
                    return {'success': True, 'message': f'Bot {bot_id} configured'}
                else:
                    return {'success': False, 'error': 'Bot does not support configuration updates'}
            
            else:
                return {'success': False, 'error': f'Unknown command: {command}'}
                
        except Exception as e:
            logger.error(f"Error executing bot command: {e}")
            return {'success': False, 'error': str(e)}
    
    def _get_uptime(self) -> str:
        """Get system uptime"""
        # This would need to be implemented based on when the system started
        return "Unknown"
    
    def _get_memory_usage(self) -> Dict[str, Any]:
        """Get memory usage statistics"""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            
            return {
                'rss': memory_info.rss,
                'vms': memory_info.vms,
                'percent': process.memory_percent()
            }
        except ImportError:
            return {'error': 'psutil not available'}
        except Exception as e:
            return {'error': str(e)}
    
    def start_monitoring(self):
        """Start real-time monitoring"""
        if self._monitoring_active:
            return
        
        self._monitoring_active = True
        self._monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self._monitoring_thread.start()
        logger.info("Real-time monitoring started")
    
    def stop_monitoring(self):
        """Stop real-time monitoring"""
        self._monitoring_active = False
        if self._monitoring_thread and self._monitoring_thread.is_alive():
            self._monitoring_thread.join(timeout=5)
        logger.info("Real-time monitoring stopped")
    
    def _monitoring_loop(self):
        """Background monitoring loop"""
        while self._monitoring_active:
            try:
                if self.active_connections:
                    status = self._get_real_time_status()
                    self.socketio.emit('status_update', status, room='monitoring')
                
                # Sleep for monitoring interval
                threading.Event().wait(5)  # 5 second intervals
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                threading.Event().wait(10)  # Longer wait on error
    
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """Run the web application"""
        logger.info(f"Starting TradeMasterX Web Interface on {host}:{port}")
        
        # Start monitoring
        self.start_monitoring()
        
        try:
            self.socketio.run(
                self.app,
                host=host,
                port=port,
                debug=debug,
                allow_unsafe_werkzeug=True
            )
        except KeyboardInterrupt:
            logger.info("Shutting down web interface...")
        finally:
            self.stop_monitoring()


def create_app(config_path: Optional[str] = None) -> TradeMasterXWebApp:
    """Factory function to create the Flask app"""
    return TradeMasterXWebApp(config_path)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='TradeMasterX Web Interface')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--config', help='Path to configuration file')
    
    args = parser.parse_args()
    
    # Create and run the app
    app = create_app(args.config)
    app.run(host=args.host, port=args.port, debug=args.debug)