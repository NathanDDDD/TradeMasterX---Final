"""
TradeMasterX 2.0 - Phase 14: Real-Time Monitor
Real-time system monitoring and data collection component
"""

import asyncio
import json
import logging
import psutil
import time
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
import sqlite3
import threading
from collections import deque, defaultdict

from ...core.bot_registry import BotRegistry


@dataclass
class SystemMetrics:
    """Real-time system metrics"""
    timestamp: str
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, int]
    active_processes: int
    system_uptime: float


@dataclass
class TradingMetrics:
    """Real-time trading metrics"""
    timestamp: str
    active_bots: int
    failed_bots: int
    total_trades_1h: int
    successful_trades_1h: int
    win_rate_1h: float
    win_rate_24h: float
    pnl_1h: float
    pnl_24h: float
    avg_trade_duration: float
    current_positions: int
    total_volume_1h: float


@dataclass
class AnomalyMetrics:
    """Real-time anomaly metrics"""
    timestamp: str
    anomalies_1h: int
    anomalies_24h: int
    critical_anomalies: int
    anomaly_types: Dict[str, int]
    avg_severity_score: float
    unresolved_anomalies: int


class RealTimeMonitor:
    """
    Real-time monitoring system for TradeMasterX
    
    Continuously monitors:
    - System resources (CPU, memory, disk, network)
    - Trading performance metrics
    - Anomaly detection status
    - Bot health and status
    - Market data freshness
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize Real-Time Monitor"""
        self.config = config or {}
        self.logger = self._setup_logging()
        
        # Configuration
        self.update_interval = config.get('update_interval', 10)  # seconds
        self.metrics_history_size = config.get('metrics_history_size', 1440)  # 24 hours at 1min intervals
        self.data_dir = Path(config.get('data_dir', 'data/real_time_monitor'))
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Metrics storage
        self.system_metrics_history = deque(maxlen=self.metrics_history_size)
        self.trading_metrics_history = deque(maxlen=self.metrics_history_size)
        self.anomaly_metrics_history = deque(maxlen=self.metrics_history_size)
        
        # Current metrics cache
        self.current_metrics = {}
        self.last_update = None
        
        # Monitoring state
        self.is_monitoring = False
        self.monitoring_task = None
        
        # Data sources
        self.bot_registry = None
        self.trade_data_sources = []
        self.anomaly_data_sources = []
        
        # Callbacks for metric updates
        self.metric_callbacks = []
        
        # Performance tracking
        self.performance_counters = defaultdict(int)
        self.last_network_io = None
        
        self.logger.info("📊 Real-Time Monitor initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for Real-Time Monitor"""
        logger = logging.getLogger(f"{self.__class__.__name__}")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def add_metric_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Add callback function to be called when metrics are updated"""
        self.metric_callbacks.append(callback)
    
    def remove_metric_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Remove metric callback"""
        if callback in self.metric_callbacks:
            self.metric_callbacks.remove(callback)
    
    async def start(self):
        """Start real-time monitoring"""
        if self.is_monitoring:
            self.logger.warning("Real-time monitoring already running")
            return
        
        self.is_monitoring = True
        self.logger.info(" Starting real-time monitoring...")
        
        # Initialize bot registry connection
        try:
            from ...core.bot_registry import BotRegistry
            self.bot_registry = BotRegistry()
        except Exception as e:
            self.logger.warning(f"Could not connect to bot registry: {e}")
        
        # Start monitoring task
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        
        self.logger.info("✅ Real-time monitoring started")
    
    async def stop(self):
        """Stop real-time monitoring"""
        if not self.is_monitoring:
            return
        
        self.is_monitoring = False
        self.logger.info("🛑 Stopping real-time monitoring...")
        
        # Cancel monitoring task
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("✅ Real-time monitoring stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                start_time = time.time()
                
                # Collect all metrics
                await self._collect_metrics()
                
                # Update current metrics cache
                self._update_current_metrics_cache()
                
                # Notify callbacks
                self._notify_metric_callbacks()
                
                # Calculate collection time
                collection_time = time.time() - start_time
                self.performance_counters['metric_collection_time'] = collection_time
                
                # Sleep until next collection
                sleep_time = max(0, self.update_interval - collection_time)
                await asyncio.sleep(sleep_time)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(5)  # Brief pause before retrying
    
    async def _collect_metrics(self):
        """Collect all types of metrics"""
        timestamp = datetime.now().isoformat()
        
        # Collect system metrics
        system_metrics = await self._collect_system_metrics(timestamp)
        self.system_metrics_history.append(system_metrics)
        
        # Collect trading metrics
        trading_metrics = await self._collect_trading_metrics(timestamp)
        self.trading_metrics_history.append(trading_metrics)
        
        # Collect anomaly metrics
        anomaly_metrics = await self._collect_anomaly_metrics(timestamp)
        self.anomaly_metrics_history.append(anomaly_metrics)
        
        self.last_update = timestamp
    
    async def _collect_system_metrics(self, timestamp: str) -> SystemMetrics:
        """Collect system resource metrics"""
        try:
            # CPU usage
            cpu_usage = psutil.cpu_percent(interval=None) / 100.0
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_usage = memory.percent / 100.0
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_usage = disk.percent / 100.0
            
            # Network I/O
            network_io_counters = psutil.net_io_counters()
            network_io = {
                'bytes_sent': network_io_counters.bytes_sent,
                'bytes_recv': network_io_counters.bytes_recv,
                'packets_sent': network_io_counters.packets_sent,
                'packets_recv': network_io_counters.packets_recv
            }
            
            # Calculate network rates if we have previous data
            if self.last_network_io:
                time_diff = time.time() - self.last_network_io['timestamp']
                if time_diff > 0:
                    network_io['bytes_sent_rate'] = (
                        network_io['bytes_sent'] - self.last_network_io['bytes_sent']
                    ) / time_diff
                    network_io['bytes_recv_rate'] = (
                        network_io['bytes_recv'] - self.last_network_io['bytes_recv']
                    ) / time_diff
            
            self.last_network_io = {
                'timestamp': time.time(),
                'bytes_sent': network_io['bytes_sent'],
                'bytes_recv': network_io['bytes_recv']
            }
            
            # Active processes
            active_processes = len(psutil.pids())
            
            # System uptime
            boot_time = psutil.boot_time()
            system_uptime = time.time() - boot_time
            
            return SystemMetrics(
                timestamp=timestamp,
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                disk_usage=disk_usage,
                network_io=network_io,
                active_processes=active_processes,
                system_uptime=system_uptime
            )
            
        except Exception as e:
            self.logger.error(f"Error collecting system metrics: {e}")
            return SystemMetrics(
                timestamp=timestamp,
                cpu_usage=0.0,
                memory_usage=0.0,
                disk_usage=0.0,
                network_io={},
                active_processes=0,
                system_uptime=0.0
            )
    
    async def _collect_trading_metrics(self, timestamp: str) -> TradingMetrics:
        """Collect trading performance metrics"""
        try:
            # Initialize default values
            active_bots = 0
            failed_bots = 0
            total_trades_1h = 0
            successful_trades_1h = 0
            win_rate_1h = 0.0
            win_rate_24h = 0.0
            pnl_1h = 0.0
            pnl_24h = 0.0
            avg_trade_duration = 0.0
            current_positions = 0
            total_volume_1h = 0.0
            
            # Get bot status from registry
            if self.bot_registry:
                try:
                    bots = self.bot_registry.get_all_bots()
                    for bot in bots.values():
                        if hasattr(bot, 'status'):
                            if bot.status == 'running':
                                active_bots += 1
                            elif bot.status in ['error', 'failed']:
                                failed_bots += 1
                except Exception as e:
                    self.logger.debug(f"Error getting bot status: {e}")
            
            # Load trade data from files
            try:
                # Try to load from performance data
                performance_file = Path('data/performance/performance_data.json')
                if performance_file.exists():
                    with open(performance_file, 'r') as f:
                        performance_data = json.load(f)
                    
                    # Extract metrics from performance data
                    if 'trades' in performance_data:
                        trades = performance_data['trades']
                        current_time = datetime.now()
                        
                        # Filter trades by time
                        trades_1h = []
                        trades_24h = []
                        
                        for trade in trades:
                            trade_time = datetime.fromisoformat(trade.get('timestamp', timestamp))
                            time_diff = current_time - trade_time
                            
                            if time_diff <= timedelta(hours=1):
                                trades_1h.append(trade)
                            if time_diff <= timedelta(hours=24):
                                trades_24h.append(trade)
                        
                        # Calculate 1h metrics
                        total_trades_1h = len(trades_1h)
                        if total_trades_1h > 0:
                            successful_trades_1h = sum(1 for t in trades_1h if t.get('result') == 'WIN')
                            win_rate_1h = successful_trades_1h / total_trades_1h
                            pnl_1h = sum(t.get('pnl', 0) for t in trades_1h)
                            total_volume_1h = sum(t.get('volume', 0) for t in trades_1h)
                            
                            # Calculate average trade duration
                            durations = [t.get('duration', 0) for t in trades_1h if t.get('duration')]
                            if durations:
                                avg_trade_duration = sum(durations) / len(durations)
                        
                        # Calculate 24h metrics
                        if len(trades_24h) > 0:
                            successful_trades_24h = sum(1 for t in trades_24h if t.get('result') == 'WIN')
                            win_rate_24h = successful_trades_24h / len(trades_24h)
                            pnl_24h = sum(t.get('pnl', 0) for t in trades_24h)
                        
                        # Count current positions (approximate)
                        current_positions = len([t for t in trades_1h if t.get('status') == 'open'])
                
                # Try to load from CSV trade log
                trade_log_file = Path('data/performance/trade_log.csv')
                if trade_log_file.exists() and trade_log_file.stat().st_size > 0:
                    try:
                        df = pd.read_csv(trade_log_file)
                        if not df.empty and 'timestamp' in df.columns:
                            df['timestamp'] = pd.to_datetime(df['timestamp'])
                            current_time = pd.Timestamp.now()
                            
                            # Filter for recent trades
                            recent_1h = df[df['timestamp'] >= current_time - pd.Timedelta(hours=1)]
                            recent_24h = df[df['timestamp'] >= current_time - pd.Timedelta(hours=24)]
                            
                            if not recent_1h.empty:
                                total_trades_1h = len(recent_1h)
                                if 'result' in recent_1h.columns:
                                    successful_trades_1h = len(recent_1h[recent_1h['result'] == 'WIN'])
                                    win_rate_1h = successful_trades_1h / total_trades_1h if total_trades_1h > 0 else 0
                                if 'pnl' in recent_1h.columns:
                                    pnl_1h = recent_1h['pnl'].sum()
                            
                            if not recent_24h.empty:
                                if 'result' in recent_24h.columns:
                                    successful_24h = len(recent_24h[recent_24h['result'] == 'WIN'])
                                    win_rate_24h = successful_24h / len(recent_24h)
                                if 'pnl' in recent_24h.columns:
                                    pnl_24h = recent_24h['pnl'].sum()
                    except Exception as e:
                        self.logger.debug(f"Error reading trade log CSV: {e}")
                        
            except Exception as e:
                self.logger.debug(f"Error loading trade data: {e}")
            
            return TradingMetrics(
                timestamp=timestamp,
                active_bots=active_bots,
                failed_bots=failed_bots,
                total_trades_1h=total_trades_1h,
                successful_trades_1h=successful_trades_1h,
                win_rate_1h=win_rate_1h,
                win_rate_24h=win_rate_24h,
                pnl_1h=pnl_1h,
                pnl_24h=pnl_24h,
                avg_trade_duration=avg_trade_duration,
                current_positions=current_positions,
                total_volume_1h=total_volume_1h
            )
            
        except Exception as e:
            self.logger.error(f"Error collecting trading metrics: {e}")
            return TradingMetrics(
                timestamp=timestamp,
                active_bots=0,
                failed_bots=0,
                total_trades_1h=0,
                successful_trades_1h=0,
                win_rate_1h=0.0,
                win_rate_24h=0.0,
                pnl_1h=0.0,
                pnl_24h=0.0,
                avg_trade_duration=0.0,
                current_positions=0,
                total_volume_1h=0.0
            )
    
    async def _collect_anomaly_metrics(self, timestamp: str) -> AnomalyMetrics:
        """Collect anomaly detection metrics"""
        try:
            # Initialize default values
            anomalies_1h = 0
            anomalies_24h = 0
            critical_anomalies = 0
            anomaly_types = {}
            avg_severity_score = 0.0
            unresolved_anomalies = 0
            
            # Try to load anomaly data
            try:
                anomaly_data_file = Path('data/anomaly_detector/anomaly_records.json')
                if anomaly_data_file.exists():
                    with open(anomaly_data_file, 'r') as f:
                        anomaly_data = json.load(f)
                    
                    current_time = datetime.now()
                    severity_scores = []
                    
                    for anomaly in anomaly_data.get('anomalies', []):
                        anomaly_time = datetime.fromisoformat(anomaly.get('timestamp', timestamp))
                        time_diff = current_time - anomaly_time
                        
                        # Count by time periods
                        if time_diff <= timedelta(hours=1):
                            anomalies_1h += 1
                        if time_diff <= timedelta(hours=24):
                            anomalies_24h += 1
                        
                        # Count by severity
                        severity = anomaly.get('severity', 'low')
                        if severity == 'critical':
                            critical_anomalies += 1
                        
                        # Count by type
                        anomaly_type = anomaly.get('anomaly_type', 'unknown')
                        anomaly_types[anomaly_type] = anomaly_types.get(anomaly_type, 0) + 1
                        
                        # Calculate severity score (critical=4, high=3, medium=2, low=1)
                        severity_score = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}.get(severity, 1)
                        severity_scores.append(severity_score)
                        
                        # Count unresolved
                        if not anomaly.get('resolved', False):
                            unresolved_anomalies += 1
                    
                    # Calculate average severity score
                    if severity_scores:
                        avg_severity_score = sum(severity_scores) / len(severity_scores)
                        
            except Exception as e:
                self.logger.debug(f"Error loading anomaly data: {e}")
            
            return AnomalyMetrics(
                timestamp=timestamp,
                anomalies_1h=anomalies_1h,
                anomalies_24h=anomalies_24h,
                critical_anomalies=critical_anomalies,
                anomaly_types=anomaly_types,
                avg_severity_score=avg_severity_score,
                unresolved_anomalies=unresolved_anomalies
            )
            
        except Exception as e:
            self.logger.error(f"Error collecting anomaly metrics: {e}")
            return AnomalyMetrics(
                timestamp=timestamp,
                anomalies_1h=0,
                anomalies_24h=0,
                critical_anomalies=0,
                anomaly_types={},
                avg_severity_score=0.0,
                unresolved_anomalies=0
            )
    
    def _update_current_metrics_cache(self):
        """Update the current metrics cache with latest data"""
        try:
            if (self.system_metrics_history and 
                self.trading_metrics_history and 
                self.anomaly_metrics_history):
                
                latest_system = self.system_metrics_history[-1]
                latest_trading = self.trading_metrics_history[-1]
                latest_anomaly = self.anomaly_metrics_history[-1]
                
                self.current_metrics = {
                    # System metrics
                    'cpu_usage': latest_system.cpu_usage,
                    'memory_usage': latest_system.memory_usage,
                    'disk_usage': latest_system.disk_usage,
                    'system_uptime': latest_system.system_uptime,
                    'active_processes': latest_system.active_processes,
                    
                    # Trading metrics
                    'active_bots': latest_trading.active_bots,
                    'failed_bots': latest_trading.failed_bots,
                    'total_trades_1h': latest_trading.total_trades_1h,
                    'successful_trades_1h': latest_trading.successful_trades_1h,
                    'win_rate_1h': latest_trading.win_rate_1h,
                    'win_rate_24h': latest_trading.win_rate_24h,
                    'pnl_1h': latest_trading.pnl_1h,
                    'pnl_24h': latest_trading.pnl_24h,
                    'avg_trade_duration': latest_trading.avg_trade_duration,
                    'current_positions': latest_trading.current_positions,
                    'total_volume_1h': latest_trading.total_volume_1h,
                    
                    # Anomaly metrics
                    'anomalies_1h': latest_anomaly.anomalies_1h,
                    'anomalies_24h': latest_anomaly.anomalies_24h,
                    'critical_anomalies': latest_anomaly.critical_anomalies,
                    'unresolved_anomalies': latest_anomaly.unresolved_anomalies,
                    'avg_severity_score': latest_anomaly.avg_severity_score,
                    
                    # Meta information
                    'last_update': self.last_update,
                    'monitoring_active': self.is_monitoring,
                    'collection_time': self.performance_counters.get('metric_collection_time', 0)
                }
                
                # Add network rates if available
                if 'bytes_sent_rate' in latest_system.network_io:
                    self.current_metrics['network_bytes_sent_rate'] = latest_system.network_io['bytes_sent_rate']
                    self.current_metrics['network_bytes_recv_rate'] = latest_system.network_io['bytes_recv_rate']
                    
        except Exception as e:
            self.logger.error(f"Error updating current metrics cache: {e}")
    
    def _notify_metric_callbacks(self):
        """Notify all registered callbacks with current metrics"""
        try:
            if self.current_metrics:
                for callback in self.metric_callbacks:
                    try:
                        callback(self.current_metrics.copy())
                    except Exception as e:
                        self.logger.error(f"Error in metric callback: {e}")
        except Exception as e:
            self.logger.error(f"Error notifying metric callbacks: {e}")
    
    # Public API methods
    
    async def get_current_metrics(self) -> Dict[str, Any]:
        """Get current real-time metrics"""
        return self.current_metrics.copy()
    
    async def get_system_metrics_history(self, hours: int = 1) -> List[Dict[str, Any]]:
        """Get system metrics history for specified hours"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            history = []
            for metric in self.system_metrics_history:
                metric_time = datetime.fromisoformat(metric.timestamp)
                if metric_time >= cutoff_time:
                    history.append({
                        'timestamp': metric.timestamp,
                        'cpu_usage': metric.cpu_usage,
                        'memory_usage': metric.memory_usage,
                        'disk_usage': metric.disk_usage,
                        'network_io': metric.network_io,
                        'active_processes': metric.active_processes,
                        'system_uptime': metric.system_uptime
                    })
            
            return history
            
        except Exception as e:
            self.logger.error(f"Error getting system metrics history: {e}")
            return []
    
    async def get_trading_metrics_history(self, hours: int = 1) -> List[Dict[str, Any]]:
        """Get trading metrics history for specified hours"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            history = []
            for metric in self.trading_metrics_history:
                metric_time = datetime.fromisoformat(metric.timestamp)
                if metric_time >= cutoff_time:
                    history.append({
                        'timestamp': metric.timestamp,
                        'active_bots': metric.active_bots,
                        'failed_bots': metric.failed_bots,
                        'total_trades_1h': metric.total_trades_1h,
                        'successful_trades_1h': metric.successful_trades_1h,
                        'win_rate_1h': metric.win_rate_1h,
                        'win_rate_24h': metric.win_rate_24h,
                        'pnl_1h': metric.pnl_1h,
                        'pnl_24h': metric.pnl_24h,
                        'avg_trade_duration': metric.avg_trade_duration,
                        'current_positions': metric.current_positions,
                        'total_volume_1h': metric.total_volume_1h
                    })
            
            return history
            
        except Exception as e:
            self.logger.error(f"Error getting trading metrics history: {e}")
            return []
    
    async def get_anomaly_metrics_history(self, hours: int = 1) -> List[Dict[str, Any]]:
        """Get anomaly metrics history for specified hours"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            history = []
            for metric in self.anomaly_metrics_history:
                metric_time = datetime.fromisoformat(metric.timestamp)
                if metric_time >= cutoff_time:
                    history.append({
                        'timestamp': metric.timestamp,
                        'anomalies_1h': metric.anomalies_1h,
                        'anomalies_24h': metric.anomalies_24h,
                        'critical_anomalies': metric.critical_anomalies,
                        'anomaly_types': metric.anomaly_types,
                        'avg_severity_score': metric.avg_severity_score,
                        'unresolved_anomalies': metric.unresolved_anomalies
                    })
            
            return history
            
        except Exception as e:
            self.logger.error(f"Error getting anomaly metrics history: {e}")
            return []
    
    async def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary of the monitoring system"""
        try:
            return {
                'monitoring_active': self.is_monitoring,
                'update_interval': self.update_interval,
                'last_update': self.last_update,
                'metrics_collected': {
                    'system_metrics': len(self.system_metrics_history),
                    'trading_metrics': len(self.trading_metrics_history),
                    'anomaly_metrics': len(self.anomaly_metrics_history)
                },
                'performance_counters': dict(self.performance_counters),
                'callbacks_registered': len(self.metric_callbacks)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting performance summary: {e}")
            return {'error': str(e)}
    
    async def force_metrics_collection(self):
        """Force immediate metrics collection (useful for testing)"""
        try:
            if self.is_monitoring:
                await self._collect_metrics()
                self._update_current_metrics_cache()
                self._notify_metric_callbacks()
                self.logger.info("Forced metrics collection completed")
            else:
                self.logger.warning("Cannot force collection - monitoring not active")
                
        except Exception as e:
            self.logger.error(f"Error in forced metrics collection: {e}")
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get current monitoring status"""
        return {
            'is_monitoring': self.is_monitoring,
            'last_update': self.last_update,
            'metrics_history_sizes': {
                'system': len(self.system_metrics_history),
                'trading': len(self.trading_metrics_history),
                'anomaly': len(self.anomaly_metrics_history)
            },
            'performance_counters': dict(self.performance_counters)
        }
