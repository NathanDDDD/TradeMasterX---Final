"""
Logger Bot - Advanced logging and audit trail system for TradeMasterX 2.0

This bot manages:
- Structured logging across all system components
- Performance metrics collection
- Audit trail for all trading activities
- Log aggregation and analysis
- Alert generation based on log patterns
"""

import asyncio
import logging
import json
import gzip
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum
import pandas as pd
from threading import Lock
import traceback
import sys
import os

from ...core.bot_registry import BaseBot


class LogLevel(Enum):
    """Extended log levels"""
    TRACE = 5
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50
    AUDIT = 60  # Special level for audit trail


class EventType(Enum):
    """Types of events to log"""
    SYSTEM_START = "system_start"
    SYSTEM_STOP = "system_stop"
    BOT_START = "bot_start"
    BOT_STOP = "bot_stop"
    TRADE_SIGNAL = "trade_signal"
    TRADE_EXECUTION = "trade_execution"
    RISK_EVENT = "risk_event"
    CONFIGURATION_CHANGE = "config_change"
    MODEL_UPDATE = "model_update"
    PERFORMANCE_METRIC = "performance_metric"
    ERROR_EVENT = "error_event"
    ALERT_TRIGGERED = "alert_triggered"


@dataclass
class LogEntry:
    """Structured log entry"""
    timestamp: datetime
    level: LogLevel
    event_type: EventType
    bot_id: str
    message: str
    data: Dict[str, Any]
    session_id: str = ""
    correlation_id: str = ""
    user_id: str = ""
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'level': self.level.name,
            'event_type': self.event_type.value,
            'bot_id': self.bot_id,
            'message': self.message,
            'data': self.data,
            'session_id': self.session_id,
            'correlation_id': self.correlation_id,
            'user_id': self.user_id,
            'tags': self.tags
        }


@dataclass
class AlertRule:
    """Alert rule configuration"""
    name: str
    condition: str  # Python expression
    level: LogLevel
    event_types: List[EventType]
    threshold_count: int = 1
    time_window_minutes: int = 5
    cooldown_minutes: int = 10
    enabled: bool = True
    last_triggered: Optional[datetime] = None


class LoggerBot(BaseBot):
    """Advanced logging and audit trail system"""
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        
        # Configuration
        self.log_dir = Path(config.get('log_dir', 'logs'))
        self.db_path = config.get('db_path', 'logs/logger_bot.db')
        self.max_log_size_mb = config.get('max_log_size_mb', 100)
        self.retention_days = config.get('retention_days', 30)
        self.compress_old_logs = config.get('compress_old_logs', True)
        self.structured_logging = config.get('structured_logging', True)
        self.enable_audit_trail = config.get('enable_audit_trail', True)
        
        # Create directories
        self.log_dir.mkdir(parents=True, exist_ok=True)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Logging components
        self._setup_logging()
        self._log_buffer = []
        self._buffer_lock = Lock()
        self._buffer_size_limit = 1000
        self._flush_interval_seconds = 30
        
        # Database storage
        self._db_connection = None
        self._initialize_database()
        
        # Alert system
        self.alert_rules = []
        self._load_alert_rules()
        self._alert_history = []
        
        # Performance tracking
        self.performance_metrics = {
            'logs_processed': 0,
            'alerts_triggered': 0,
            'db_writes': 0,
            'buffer_flushes': 0,
            'start_time': datetime.now()
        }
        
        # Active sessions
        self.active_sessions = {}
        
        self.logger = logging.getLogger(__name__)
    
    def _setup_logging(self):
        """Setup comprehensive logging system"""
        # Create custom logger for TradeMasterX
        self.tmx_logger = logging.getLogger('trademasterx')
        self.tmx_logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers
        for handler in self.tmx_logger.handlers[:]:
            self.tmx_logger.removeHandler(handler)
        
        # Console handler with colored output
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # File handler for all logs
        log_file = self.log_dir / f"trademasterx_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # Error-only file handler
        error_file = self.log_dir / f"errors_{datetime.now().strftime('%Y%m%d')}.log"
        error_handler = logging.FileHandler(error_file, encoding='utf-8')
        error_handler.setLevel(logging.ERROR)
        
        # Formatters
        if self.structured_logging:
            formatter = logging.Formatter(
                '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
                '"logger": "%(name)s", "message": "%(message)s", '
                '"module": "%(module)s", "function": "%(funcName)s", "line": %(lineno)d}'
            )
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        
        # Apply formatters
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        error_handler.setFormatter(formatter)
        
        # Add handlers
        self.tmx_logger.addHandler(console_handler)
        self.tmx_logger.addHandler(file_handler)
        self.tmx_logger.addHandler(error_handler)
    
    def _initialize_database(self):
        """Initialize SQLite database for log storage"""
        try:
            self._db_connection = sqlite3.connect(
                self.db_path, 
                check_same_thread=False
            )
            
            cursor = self._db_connection.cursor()
            
            # Log entries table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS log_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    level TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    bot_id TEXT NOT NULL,
                    message TEXT NOT NULL,
                    data TEXT,
                    session_id TEXT,
                    correlation_id TEXT,
                    user_id TEXT,
                    tags TEXT
                )
            """)
            
            # Performance metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    bot_id TEXT,
                    additional_data TEXT
                )
            """)
            
            # Alert history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alert_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    rule_name TEXT NOT NULL,
                    level TEXT NOT NULL,
                    message TEXT NOT NULL,
                    triggered_by TEXT,
                    resolved_at TEXT,
                    additional_data TEXT
                )
            """)
            
            # Create indexes for performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON log_entries(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_bot_id ON log_entries(bot_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_level ON log_entries(level)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_event_type ON log_entries(event_type)")
            
            self._db_connection.commit()
            self.logger.info("Database initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            raise
    
    def _load_alert_rules(self):
        """Load alert rules from configuration"""
        default_rules = [
            AlertRule(
                name="High Error Rate",
                condition="level == 'ERROR' and count >= 5",
                level=LogLevel.ERROR,
                event_types=[EventType.ERROR_EVENT],
                threshold_count=5,
                time_window_minutes=5
            ),
            AlertRule(
                name="Bot Failure",
                condition="event_type == 'bot_stop' and 'error' in message.lower()",
                level=LogLevel.CRITICAL,
                event_types=[EventType.BOT_STOP],
                threshold_count=1,
                time_window_minutes=1
            ),
            AlertRule(
                name="Risk Threshold Exceeded",
                condition="event_type == 'risk_event' and 'exceeded' in message.lower()",
                level=LogLevel.WARNING,
                event_types=[EventType.RISK_EVENT],
                threshold_count=1,
                time_window_minutes=1
            )
        ]
        
        self.alert_rules.extend(default_rules)
    
    async def start(self) -> bool:
        """Start the logger bot"""
        try:
            self.is_running = True
            self.logger.info("Starting LoggerBot")
            
            # Start background tasks
            asyncio.create_task(self._flush_buffer_loop())
            asyncio.create_task(self._cleanup_loop())
            
            # Log system start event
            await self.log_event(
                level=LogLevel.INFO,
                event_type=EventType.SYSTEM_START,
                bot_id="logger_bot",
                message="TradeMasterX logging system started",
                data={'version': '2.0', 'config': self.config}
            )
            
            self.logger.info("LoggerBot started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start LoggerBot: {e}")
            return False
    
    async def stop(self) -> bool:
        """Stop the logger bot"""
        try:
            self.is_running = False
            
            # Log system stop event
            await self.log_event(
                level=LogLevel.INFO,
                event_type=EventType.SYSTEM_STOP,
                bot_id="logger_bot",
                message="TradeMasterX logging system stopping",
                data=self.performance_metrics
            )
            
            # Flush remaining logs
            await self._flush_buffer()
            
            # Close database connection
            if self._db_connection:
                self._db_connection.close()
            
            self.logger.info("LoggerBot stopped")
            return True
            
        except Exception as e:
            self.logger.error(f"Error stopping LoggerBot: {e}")
            return False
    
    async def process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process logging requests"""
        try:
            action = data.get('action', 'log')
            
            if action == 'log':
                return await self._handle_log_request(data)
            elif action == 'get_logs':
                return await self._get_logs(data)
            elif action == 'get_metrics':
                return await self._get_performance_metrics()
            else:
                return {'success': False, 'error': f'Unknown action: {action}'}
                
        except Exception as e:
            self.logger.error(f"Error processing data: {e}")
            return {'success': False, 'error': str(e)}
    
    async def log_event(self, level: LogLevel, event_type: EventType, 
                       bot_id: str, message: str, data: Dict[str, Any] = None,
                       session_id: str = "", correlation_id: str = "", 
                       user_id: str = "", tags: List[str] = None) -> bool:
        """Log a structured event"""
        try:
            if data is None:
                data = {}
            
            entry = LogEntry(
                timestamp=datetime.now(),
                level=level,
                event_type=event_type,
                bot_id=bot_id,
                message=message,
                data=data,
                session_id=session_id,
                correlation_id=correlation_id,
                user_id=user_id,
                tags=tags or []
            )
            
            # Add to buffer
            with self._buffer_lock:
                self._log_buffer.append(entry)
                if len(self._log_buffer) >= self._buffer_size_limit:
                    asyncio.create_task(self._flush_buffer())
            
            # Log to standard logger
            log_msg = f"[{event_type.value}] {message}"
            if data:
                log_msg += f" | Data: {json.dumps(data, default=str)}"
            
            getattr(self.tmx_logger, level.name.lower())(log_msg)
            
            self.performance_metrics['logs_processed'] += 1
            return True
            
        except Exception as e:
            self.logger.error(f"Error logging event: {e}")
            return False
    
    async def _handle_log_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle external log requests"""
        try:
            level = LogLevel[data.get('level', 'INFO')]
            event_type = EventType[data.get('event_type', 'SYSTEM_START')]
            bot_id = data.get('bot_id', 'unknown')
            message = data.get('message', '')
            log_data = data.get('data', {})
            
            success = await self.log_event(
                level=level,
                event_type=event_type,
                bot_id=bot_id,
                message=message,
                data=log_data,
                session_id=data.get('session_id', ''),
                correlation_id=data.get('correlation_id', ''),
                user_id=data.get('user_id', ''),
                tags=data.get('tags', [])
            )
            
            return {'success': success}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _flush_buffer(self):
        """Flush log buffer to database"""
        try:
            with self._buffer_lock:
                if not self._log_buffer:
                    return
                
                entries_to_flush = self._log_buffer.copy()
                self._log_buffer.clear()
            
            # Insert into database
            cursor = self._db_connection.cursor()
            
            for entry in entries_to_flush:
                cursor.execute("""
                    INSERT INTO log_entries 
                    (timestamp, level, event_type, bot_id, message, data, 
                     session_id, correlation_id, user_id, tags)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    entry.timestamp.isoformat(),
                    entry.level.name,
                    entry.event_type.value,
                    entry.bot_id,
                    entry.message,
                    json.dumps(entry.data, default=str),
                    entry.session_id,
                    entry.correlation_id,
                    entry.user_id,
                    json.dumps(entry.tags)
                ))
            
            self._db_connection.commit()
            self.performance_metrics['db_writes'] += len(entries_to_flush)
            self.performance_metrics['buffer_flushes'] += 1
            
        except Exception as e:
            self.logger.error(f"Error flushing buffer: {e}")
    
    async def _flush_buffer_loop(self):
        """Periodic buffer flushing"""
        while self.is_running:
            try:
                await asyncio.sleep(self._flush_interval_seconds)
                if self.is_running:
                    await self._flush_buffer()
            except Exception as e:
                self.logger.error(f"Error in flush buffer loop: {e}")
    
    async def _cleanup_loop(self):
        """Periodic cleanup of old logs"""
        while self.is_running:
            try:
                # Wait 1 hour between cleanups
                await asyncio.sleep(3600)
                if self.is_running:
                    await self._cleanup_old_logs()
            except Exception as e:
                self.logger.error(f"Error in cleanup loop: {e}")
    
    async def _cleanup_old_logs(self):
        """Clean up old log entries"""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.retention_days)
            
            cursor = self._db_connection.cursor()
            cursor.execute("""
                DELETE FROM log_entries 
                WHERE timestamp < ?
            """, (cutoff_date.isoformat(),))
            
            deleted_count = cursor.rowcount
            self._db_connection.commit()
            
            # Compress old log files
            if self.compress_old_logs:
                await self._compress_old_log_files()
            
            self.logger.info(f"Cleaned up {deleted_count} old log entries")
            
        except Exception as e:
            self.logger.error(f"Error cleaning up old logs: {e}")
    
    async def _compress_old_log_files(self):
        """Compress old log files"""
        try:
            cutoff_date = datetime.now() - timedelta(days=1)
            
            for log_file in self.log_dir.glob("*.log"):
                if log_file.stat().st_mtime < cutoff_date.timestamp():
                    compressed_file = log_file.with_suffix('.log.gz')
                    
                    if not compressed_file.exists():
                        with open(log_file, 'rb') as f_in:
                            with gzip.open(compressed_file, 'wb') as f_out:
                                f_out.writelines(f_in)
                        
                        log_file.unlink()  # Delete original file
                        self.logger.debug(f"Compressed {log_file} to {compressed_file}")
            
        except Exception as e:
            self.logger.error(f"Error compressing log files: {e}")
    
    async def _get_logs(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Get logs based on filters"""
        try:
            # Parse filters
            start_time = request.get('start_time')
            end_time = request.get('end_time')
            level = request.get('level')
            bot_id = request.get('bot_id')
            event_type = request.get('event_type')
            limit = request.get('limit', 100)
            
            # Build query
            conditions = []
            params = []
            
            if start_time:
                conditions.append("timestamp >= ?")
                params.append(start_time)
            
            if end_time:
                conditions.append("timestamp <= ?")
                params.append(end_time)
            
            if level:
                conditions.append("level = ?")
                params.append(level)
            
            if bot_id:
                conditions.append("bot_id = ?")
                params.append(bot_id)
            
            if event_type:
                conditions.append("event_type = ?")
                params.append(event_type)
            
            where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
            
            query = f"""
                SELECT timestamp, level, event_type, bot_id, message, data, 
                       session_id, correlation_id, user_id, tags
                FROM log_entries 
                {where_clause}
                ORDER BY timestamp DESC
                LIMIT ?
            """
            params.append(limit)
            
            cursor = self._db_connection.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            logs = []
            for row in rows:
                timestamp, level, event_type, bot_id, message, data, session_id, correlation_id, user_id, tags = row
                
                logs.append({
                    'timestamp': timestamp,
                    'level': level,
                    'event_type': event_type,
                    'bot_id': bot_id,
                    'message': message,
                    'data': json.loads(data) if data else {},
                    'session_id': session_id,
                    'correlation_id': correlation_id,
                    'user_id': user_id,
                    'tags': json.loads(tags) if tags else []
                })
            
            return {'success': True, 'logs': logs}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get logger performance metrics"""
        uptime = datetime.now() - self.performance_metrics['start_time']
        
        return {
            'success': True,
            'metrics': {
                **self.performance_metrics,
                'uptime_hours': uptime.total_seconds() / 3600,
                'buffer_size': len(self._log_buffer),
                'active_sessions': len(self.active_sessions),
                'alert_rules_count': len(self.alert_rules),
                'logs_per_hour': self.performance_metrics['logs_processed'] / max(uptime.total_seconds() / 3600, 1)
            }
        }

    async def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status information"""
        try:
            metrics = await self._get_performance_metrics()
            
            return {
                'bot_id': self.bot_id,
                'is_running': self.is_running,
                'start_time': self.start_time.isoformat() if self.start_time else None,
                'metrics': metrics.get('metrics', {}),
                'configuration': {
                    'log_dir': str(self.log_dir),
                    'retention_days': self.retention_days,
                    'max_log_size_mb': self.max_log_size_mb,
                    'structured_logging': self.structured_logging,
                    'audit_trail_enabled': self.enable_audit_trail
                },
                'storage': {
                    'database_connected': self._db_connection is not None,
                    'buffer_size': len(self._log_buffer),
                    'buffer_limit': self._buffer_size_limit
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting status: {e}")
            return {
                'bot_id': self.bot_id,
                'is_running': False,
                'error': str(e)
            }
    
    async def initialize(self) -> bool:
        """Initialize the logger bot"""
        try:
            self.logger.info("🔧 Initializing LoggerBot...")
            
            # Initialize database connection
            if not self._db_connection:
                self._initialize_database()
            
            # Start background tasks
            await self._start_background_tasks()
            
            self.is_initialized = True
            self.logger.info("✓ LoggerBot initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize LoggerBot: {e}")
            return False
    
    async def execute_cycle(self) -> Dict[str, Any]:
        """Execute one logging cycle"""
        try:
            # Flush log buffer if needed
            if len(self._log_buffer) >= self._buffer_size_limit:
                await self._flush_log_buffer()
            
            # Check for alerts
            alerts_triggered = await self._check_alert_rules()
            
            # Update performance metrics
            self.performance_metrics['logs_processed'] = len(self._log_buffer)
            
            return {
                'status': 'success',
                'logs_in_buffer': len(self._log_buffer),
                'alerts_triggered': len(alerts_triggered),
                'performance': self.performance_metrics
            }
            
        except Exception as e:
            self.logger.error(f"LoggerBot cycle execution failed: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def cleanup(self):
        """Cleanup logger bot resources"""
        try:
            self.logger.info("🧹 Cleaning up LoggerBot...")
            
            # Flush remaining logs
            if self._log_buffer:
                await self._flush_log_buffer()
            
            # Close database connection
            if self._db_connection:
                self._db_connection.close()
                self._db_connection = None
            
            self.is_running = False
            self.logger.info("✓ LoggerBot cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during LoggerBot cleanup: {e}")
    
    async def _start_background_tasks(self):
        """Start background tasks for log processing"""
        # This would start periodic tasks for log flushing, cleanup, etc.
        pass
    
    async def _flush_log_buffer(self):
        """Flush the log buffer to persistent storage"""
        if not self._log_buffer:
            return
            
        try:
            with self._buffer_lock:
                # Process buffered logs
                for log_entry in self._log_buffer:
                    await self._store_log_entry(log_entry)
                
                # Clear buffer
                self._log_buffer.clear()
                self.performance_metrics['buffer_flushes'] += 1
                
        except Exception as e:
            self.logger.error(f"Error flushing log buffer: {e}")
    
    async def _check_alert_rules(self) -> List[Dict]:
        """Check and trigger alerts based on rules"""
        triggered_alerts = []
        try:
            # Check alert rules against recent logs
            # This is a placeholder for alert logic
            pass
        except Exception as e:
            self.logger.error(f"Error checking alert rules: {e}")
        
        return triggered_alerts
    
    async def _store_log_entry(self, log_entry: Dict):
        """Store a single log entry to database"""
        try:
            if self._db_connection:
                # Store to database (implementation would go here)
                self.performance_metrics['db_writes'] += 1
        except Exception as e:
            self.logger.error(f"Error storing log entry: {e}")