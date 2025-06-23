"""
TradeMasterX 2.0 - Phase 11: Live Optimization Dashboard
Real-time monitoring dashboard with alerts and visualization for intelligent optimization
"""

import asyncio
import json
import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import numpy as np
import plotly.graph_objects as go
import plotly.utils
from plotly.subplots import make_subplots

@dataclass
class DashboardMetrics:
    """Real-time dashboard metrics"""
    timestamp: str
    system_health_score: float  # 0-100
    optimization_efficiency: float  # 0-100
    active_optimizations: int
    alerts_count: int
    performance_trend: str  # 'improving', 'stable', 'declining'
    
    # Bot metrics aggregation
    total_bots: int
    active_bots: int
    top_bot_performance: float
    avg_bot_reliability: float
    
    # Strategy metrics aggregation
    total_strategies: int
    active_strategies: int
    strategy_switches_24h: int
    best_strategy_roi: float
    
    # Anomaly metrics aggregation
    anomalies_24h: int
    critical_anomalies: int
    anomaly_trend: str
    
    # System performance
    trades_per_hour: float
    avg_confidence: float
    win_rate: float
    total_return: float

@dataclass
class AlertRecord:
    """Alert record for dashboard notifications"""
    alert_id: str
    timestamp: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    category: str  # 'performance', 'system', 'anomaly', 'strategy'
    title: str
    message: str
    source_module: str
    recommended_action: str
    auto_resolved: bool = False
    acknowledged: bool = False
    resolved_at: Optional[str] = None

@dataclass
class OptimizationEvent:
    """Optimization event tracking"""
    event_id: str
    timestamp: str
    event_type: str  # 'bot_adjustment', 'strategy_switch', 'anomaly_detected', 'performance_improvement'
    module: str
    description: str
    impact_score: float  # 0-100
    before_metrics: Dict[str, float]
    after_metrics: Dict[str, float]
    success: bool

@dataclass
class PerformanceSnapshot:
    """Performance snapshot for trend analysis"""
    timestamp: str
    system_performance: float
    bot_performance: float
    strategy_performance: float
    risk_level: float
    optimization_score: float

class LiveOptimizationDashboard:
    """
    Real-time monitoring dashboard for Phase 11 intelligent optimization
    
    Features:
    - Real-time performance monitoring
    - Alert system with severity levels
    - Optimization event tracking
    - Interactive visualizations
    - Trend analysis and predictions
    - System health monitoring
    """
    
    def __init__(self, data_dir: str = "reports", alerts_dir: str = "logs"):
        self.data_dir = Path(data_dir)
        self.alerts_dir = Path(alerts_dir)
        self.dashboard_dir = self.data_dir / "dashboard"
        
        # Create directories
        self.data_dir.mkdir(exist_ok=True)
        self.alerts_dir.mkdir(exist_ok=True)
        self.dashboard_dir.mkdir(exist_ok=True)
        
        # Dashboard state
        self.current_metrics = None
        self.alerts = []
        self.optimization_events = []
        self.performance_history = deque(maxlen=1440)  # 24 hours of minute-by-minute data
        
        # Alert thresholds
        self.alert_thresholds = {
            'system_health_critical': 30.0,
            'system_health_warning': 60.0,
            'performance_decline_critical': -20.0,
            'performance_decline_warning': -10.0,
            'anomaly_spike_critical': 50,
            'anomaly_spike_warning': 20,
            'win_rate_critical': 0.35,
            'win_rate_warning': 0.45,
            'bot_failure_rate_critical': 0.80,
            'bot_failure_rate_warning': 0.60
        }
        
        # Performance baselines
        self.performance_baselines = {
            'system_health': 85.0,
            'win_rate': 0.65,
            'avg_return': 0.02,
            'bot_reliability': 0.75
        }
        
        # Setup logging
        self.logger = self._setup_logging()
        
        # Load existing data
        self._load_dashboard_data()
        
        self.logger.info("Live Optimization Dashboard initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup dashboard logging"""
        logger = logging.getLogger("LiveOptimizationDashboard")
        logger.setLevel(logging.INFO)
        
        # Create file handler
        log_file = self.alerts_dir / "dashboard.log"
        file_handler = logging.FileHandler(log_file)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        
        # Add handler if not already added
        if not logger.handlers:
            logger.addHandler(file_handler)
        
        return logger
    
    def _load_dashboard_data(self):
        """Load existing dashboard data"""
        try:
            # Load alerts
            alerts_file = self.dashboard_dir / "alerts.json"
            if alerts_file.exists():
                with open(alerts_file, 'r') as f:
                    alerts_data = json.load(f)
                    self.alerts = [AlertRecord(**alert) for alert in alerts_data]
            
            # Load optimization events
            events_file = self.dashboard_dir / "optimization_events.json"
            if events_file.exists():
                with open(events_file, 'r') as f:
                    events_data = json.load(f)
                    self.optimization_events = [OptimizationEvent(**event) for event in events_data]
            
            # Load performance history
            history_file = self.dashboard_dir / "performance_history.json"
            if history_file.exists():
                with open(history_file, 'r') as f:
                    history_data = json.load(f)
                    self.performance_history = deque(
                        [PerformanceSnapshot(**snapshot) for snapshot in history_data],
                        maxlen=1440
                    )
            
            self.logger.info("Dashboard data loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Error loading dashboard data: {e}")
    
    def _save_dashboard_data(self):
        """Save dashboard data to files"""
        try:
            # Save alerts
            alerts_file = self.dashboard_dir / "alerts.json"
            with open(alerts_file, 'w') as f:
                json.dump([asdict(alert) for alert in self.alerts], f, indent=2)
            
            # Save optimization events
            events_file = self.dashboard_dir / "optimization_events.json"
            with open(events_file, 'w') as f:
                json.dump([asdict(event) for event in self.optimization_events], f, indent=2)
            
            # Save performance history
            history_file = self.dashboard_dir / "performance_history.json"
            with open(history_file, 'w') as f:
                json.dump([asdict(snapshot) for snapshot in self.performance_history], f, indent=2)
            
        except Exception as e:
            self.logger.error(f"Error saving dashboard data: {e}")
    
    def update_metrics(self, bot_metrics: Dict[str, Any], strategy_metrics: Dict[str, Any], 
                      anomaly_metrics: Dict[str, Any], system_metrics: Dict[str, Any]) -> DashboardMetrics:
        """Update dashboard metrics from all Phase 11 modules"""
        try:
            timestamp = datetime.now().isoformat()
            
            # Aggregate bot metrics
            bot_scores = bot_metrics.get('bot_scores', {})
            total_bots = len(bot_scores)
            active_bots = len([b for b in bot_scores.values() if b.get('total_predictions', 0) >= 10])
            
            if bot_scores:
                reliabilities = [b.get('reliability_score', 0) for b in bot_scores.values()]
                top_bot_performance = max(reliabilities) if reliabilities else 0
                avg_bot_reliability = np.mean(reliabilities) if reliabilities else 0
            else:
                top_bot_performance = 0
                avg_bot_reliability = 0
            
            # Aggregate strategy metrics
            strategy_data = strategy_metrics.get('strategy_performance', {})
            total_strategies = len(strategy_data)
            active_strategies = len([s for s in strategy_data.values() if s.get('active', False)])
            
            # Get strategy switches in last 24h
            switches = strategy_metrics.get('switch_history', [])
            recent_switches = [s for s in switches 
                             if (datetime.now() - datetime.fromisoformat(s.get('timestamp', '2000-01-01'))).total_seconds() < 86400]
            strategy_switches_24h = len(recent_switches)
            
            best_strategy_roi = 0
            if strategy_data:
                roi_values = [s.get('roi', 0) for s in strategy_data.values()]
                best_strategy_roi = max(roi_values) if roi_values else 0
            
            # Aggregate anomaly metrics
            anomalies = anomaly_metrics.get('anomalies', [])
            recent_anomalies = [a for a in anomalies 
                              if (datetime.now() - datetime.fromisoformat(a.get('timestamp', '2000-01-01'))).total_seconds() < 86400]
            anomalies_24h = len(recent_anomalies)
            critical_anomalies = len([a for a in recent_anomalies if a.get('severity') == 'critical'])
            
            # Determine anomaly trend
            if len(self.performance_history) >= 60:  # Last hour
                recent_hour_anomalies = sum(1 for snapshot in list(self.performance_history)[-60:] 
                                          if hasattr(snapshot, 'anomalies_count'))
                prev_hour_anomalies = sum(1 for snapshot in list(self.performance_history)[-120:-60] 
                                        if hasattr(snapshot, 'anomalies_count'))
                
                if recent_hour_anomalies > prev_hour_anomalies * 1.5:
                    anomaly_trend = "increasing"
                elif recent_hour_anomalies < prev_hour_anomalies * 0.5:
                    anomaly_trend = "decreasing"
                else:
                    anomaly_trend = "stable"
            else:
                anomaly_trend = "unknown"
            
            # Aggregate system metrics
            trades_per_hour = system_metrics.get('trades_per_hour', 0)
            avg_confidence = system_metrics.get('avg_confidence', 0)
            win_rate = system_metrics.get('win_rate', 0)
            total_return = system_metrics.get('total_return', 0)
            
            # Calculate system health score
            health_components = [
                min(100, avg_bot_reliability * 100),  # Bot reliability
                min(100, win_rate * 100),  # Win rate
                min(100, (1 - critical_anomalies / max(1, anomalies_24h)) * 100),  # Anomaly control
                min(100, active_bots / max(1, total_bots) * 100) if total_bots > 0 else 0,  # Bot activity
                min(100, trades_per_hour / 60 * 100)  # Trading activity
            ]
            system_health_score = np.mean([c for c in health_components if c > 0])
            
            # Calculate optimization efficiency
            efficiency_components = [
                min(100, strategy_switches_24h / max(1, total_strategies) * 50),  # Strategy adaptation
                min(100, (anomalies_24h - critical_anomalies) / max(1, anomalies_24h) * 100) if anomalies_24h > 0 else 100,  # Anomaly management
                min(100, best_strategy_roi * 1000) if best_strategy_roi > 0 else 50  # Performance
            ]
            optimization_efficiency = np.mean(efficiency_components)
            
            # Determine performance trend
            if len(self.performance_history) >= 60:  # Last hour vs previous hour
                recent_performance = np.mean([s.system_performance for s in list(self.performance_history)[-60:]])
                previous_performance = np.mean([s.system_performance for s in list(self.performance_history)[-120:-60]])
                
                if recent_performance > previous_performance * 1.05:
                    performance_trend = "improving"
                elif recent_performance < previous_performance * 0.95:
                    performance_trend = "declining"
                else:
                    performance_trend = "stable"
            else:
                performance_trend = "unknown"
            
            # Count unresolved alerts
            alerts_count = len([a for a in self.alerts if not a.auto_resolved and not a.acknowledged])
            
            # Count active optimizations (placeholder)
            active_optimizations = strategy_switches_24h + (1 if anomalies_24h > 0 else 0)
            
            # Create metrics object
            self.current_metrics = DashboardMetrics(
                timestamp=timestamp,
                system_health_score=system_health_score,
                optimization_efficiency=optimization_efficiency,
                active_optimizations=active_optimizations,
                alerts_count=alerts_count,
                performance_trend=performance_trend,
                total_bots=total_bots,
                active_bots=active_bots,
                top_bot_performance=top_bot_performance,
                avg_bot_reliability=avg_bot_reliability,
                total_strategies=total_strategies,
                active_strategies=active_strategies,
                strategy_switches_24h=strategy_switches_24h,
                best_strategy_roi=best_strategy_roi,
                anomalies_24h=anomalies_24h,
                critical_anomalies=critical_anomalies,
                anomaly_trend=anomaly_trend,
                trades_per_hour=trades_per_hour,
                avg_confidence=avg_confidence,
                win_rate=win_rate,
                total_return=total_return
            )
            
            # Add to performance history
            snapshot = PerformanceSnapshot(
                timestamp=timestamp,
                system_performance=system_health_score,
                bot_performance=avg_bot_reliability * 100,
                strategy_performance=best_strategy_roi * 100,
                risk_level=critical_anomalies * 10,  # Risk increases with critical anomalies
                optimization_score=optimization_efficiency
            )
            self.performance_history.append(snapshot)
            
            # Check for alerts
            self._check_alert_conditions()
            
            # Save data
            self._save_dashboard_data()
            
            return self.current_metrics
            
        except Exception as e:
            self.logger.error(f"Error updating dashboard metrics: {e}")
            return self.current_metrics or DashboardMetrics(
                timestamp=datetime.now().isoformat(),
                system_health_score=0, optimization_efficiency=0, active_optimizations=0,
                alerts_count=0, performance_trend="unknown", total_bots=0, active_bots=0,
                top_bot_performance=0, avg_bot_reliability=0, total_strategies=0,
                active_strategies=0, strategy_switches_24h=0, best_strategy_roi=0,
                anomalies_24h=0, critical_anomalies=0, anomaly_trend="unknown",
                trades_per_hour=0, avg_confidence=0, win_rate=0, total_return=0
            )
    
    def _check_alert_conditions(self):
        """Check for alert conditions and generate alerts"""
        if not self.current_metrics:
            return
        
        alerts_to_add = []
        
        # System health alerts
        if self.current_metrics.system_health_score <= self.alert_thresholds['system_health_critical']:
            alerts_to_add.append(self._create_alert(
                'critical', 'system', 'Critical System Health',
                f'System health score dropped to {self.current_metrics.system_health_score:.1f}%',
                'Immediate investigation required. Check bot performance and anomaly levels.'
            ))
        elif self.current_metrics.system_health_score <= self.alert_thresholds['system_health_warning']:
            alerts_to_add.append(self._create_alert(
                'high', 'system', 'Low System Health',
                f'System health score is {self.current_metrics.system_health_score:.1f}%',
                'Monitor system closely. Consider bot adjustments or strategy changes.'
            ))
        
        # Performance alerts
        if self.current_metrics.performance_trend == "declining":
            alerts_to_add.append(self._create_alert(
                'medium', 'performance', 'Performance Declining',
                'System performance showing declining trend',
                'Review recent strategy changes and bot performance metrics.'
            ))
        
        # Win rate alerts
        if self.current_metrics.win_rate <= self.alert_thresholds['win_rate_critical']:
            alerts_to_add.append(self._create_alert(
                'critical', 'performance', 'Critical Win Rate',
                f'Win rate dropped to {self.current_metrics.win_rate:.1%}',
                'Immediate strategy review required. Consider emergency strategy switch.'
            ))
        elif self.current_metrics.win_rate <= self.alert_thresholds['win_rate_warning']:
            alerts_to_add.append(self._create_alert(
                'high', 'performance', 'Low Win Rate',
                f'Win rate is {self.current_metrics.win_rate:.1%}',
                'Monitor trades closely. Consider strategy adjustments.'
            ))
        
        # Anomaly alerts
        if self.current_metrics.critical_anomalies >= self.alert_thresholds['anomaly_spike_critical']:
            alerts_to_add.append(self._create_alert(
                'critical', 'anomaly', 'Critical Anomaly Spike',
                f'{self.current_metrics.critical_anomalies} critical anomalies detected',
                'Investigate anomaly patterns immediately. Consider system pause.'
            ))
        elif self.current_metrics.anomalies_24h >= self.alert_thresholds['anomaly_spike_warning']:
            alerts_to_add.append(self._create_alert(
                'medium', 'anomaly', 'Anomaly Increase',
                f'{self.current_metrics.anomalies_24h} anomalies in last 24 hours',
                'Review anomaly patterns and adjust detection thresholds if needed.'
            ))
        
        # Bot failure rate alert
        if self.current_metrics.total_bots > 0:
            bot_failure_rate = (self.current_metrics.total_bots - self.current_metrics.active_bots) / self.current_metrics.total_bots
            if bot_failure_rate >= self.alert_thresholds['bot_failure_rate_critical']:
                alerts_to_add.append(self._create_alert(
                    'critical', 'system', 'High Bot Failure Rate',
                    f'{bot_failure_rate:.1%} of bots are inactive',
                    'Check bot configurations and restart failed bots.'
                ))
            elif bot_failure_rate >= self.alert_thresholds['bot_failure_rate_warning']:
                alerts_to_add.append(self._create_alert(
                    'medium', 'system', 'Bot Failures Detected',
                    f'{bot_failure_rate:.1%} of bots are inactive',
                    'Monitor bot performance and investigate failures.'
                ))
        
        # Add new alerts (avoid duplicates)
        for alert in alerts_to_add:
            # Check if similar alert exists in last hour
            recent_alerts = [a for a in self.alerts 
                           if (datetime.now() - datetime.fromisoformat(a.timestamp)).total_seconds() < 3600
                           and a.category == alert.category and a.title == alert.title]
            
            if not recent_alerts:
                self.alerts.append(alert)
                self.logger.warning(f"Alert generated: {alert.severity.upper()} - {alert.title}")
    
    def _create_alert(self, severity: str, category: str, title: str, message: str, action: str) -> AlertRecord:
        """Create a new alert record"""
        alert_id = f"{category}_{int(time.time())}_{hash(title) % 10000}"
        
        return AlertRecord(
            alert_id=alert_id,
            timestamp=datetime.now().isoformat(),
            severity=severity,
            category=category,
            title=title,
            message=message,
            source_module="LiveOptimizationDashboard",
            recommended_action=action
        )
    
    def log_optimization_event(self, event_type: str, module: str, description: str,
                             before_metrics: Dict[str, float], after_metrics: Dict[str, float],
                             success: bool = True) -> str:
        """Log an optimization event"""
        event_id = f"{module}_{int(time.time())}_{hash(description) % 10000}"
        
        # Calculate impact score
        impact_score = 0
        if before_metrics and after_metrics:
            # Calculate percentage improvements
            improvements = []
            for key in before_metrics:
                if key in after_metrics and before_metrics[key] != 0:
                    improvement = (after_metrics[key] - before_metrics[key]) / abs(before_metrics[key]) * 100
                    improvements.append(improvement)
            
            if improvements:
                impact_score = max(0, min(100, np.mean(improvements)))
        
        event = OptimizationEvent(
            event_id=event_id,
            timestamp=datetime.now().isoformat(),
            event_type=event_type,
            module=module,
            description=description,
            impact_score=impact_score,
            before_metrics=before_metrics,
            after_metrics=after_metrics,
            success=success
        )
        
        self.optimization_events.append(event)
        self.logger.info(f"Optimization event logged: {event_type} - {description} (Impact: {impact_score:.1f})")
        
        return event_id
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert"""
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                self._save_dashboard_data()
                self.logger.info(f"Alert acknowledged: {alert_id}")
                return True
        return False
    
    def resolve_alert(self, alert_id: str, auto_resolved: bool = False) -> bool:
        """Resolve an alert"""
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.auto_resolved = auto_resolved
                alert.resolved_at = datetime.now().isoformat()
                self._save_dashboard_data()
                self.logger.info(f"Alert resolved: {alert_id} ({'auto' if auto_resolved else 'manual'})")
                return True
        return False
    
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get dashboard summary for display"""
        if not self.current_metrics:
            return {"error": "No metrics available"}
        
        # Get recent alerts
        recent_alerts = [a for a in self.alerts 
                        if not a.auto_resolved and not a.acknowledged][:10]
        
        # Get recent optimization events
        recent_events = sorted(self.optimization_events, 
                             key=lambda x: x.timestamp, reverse=True)[:10]
        
        # Calculate trend indicators
        trends = self._calculate_trends()
        
        return {
            "timestamp": self.current_metrics.timestamp,
            "system_health": {
                "score": self.current_metrics.system_health_score,
                "status": self._get_health_status(self.current_metrics.system_health_score),
                "trend": trends.get("health_trend", "stable")
            },
            "optimization": {
                "efficiency": self.current_metrics.optimization_efficiency,
                "active_count": self.current_metrics.active_optimizations,
                "trend": trends.get("optimization_trend", "stable")
            },
            "performance": {
                "win_rate": self.current_metrics.win_rate,
                "total_return": self.current_metrics.total_return,
                "trades_per_hour": self.current_metrics.trades_per_hour,
                "trend": self.current_metrics.performance_trend
            },
            "bots": {
                "total": self.current_metrics.total_bots,
                "active": self.current_metrics.active_bots,
                "top_performance": self.current_metrics.top_bot_performance,
                "avg_reliability": self.current_metrics.avg_bot_reliability
            },
            "strategies": {
                "total": self.current_metrics.total_strategies,
                "active": self.current_metrics.active_strategies,
                "switches_24h": self.current_metrics.strategy_switches_24h,
                "best_roi": self.current_metrics.best_strategy_roi
            },
            "anomalies": {
                "total_24h": self.current_metrics.anomalies_24h,
                "critical": self.current_metrics.critical_anomalies,
                "trend": self.current_metrics.anomaly_trend
            },
            "alerts": {
                "total": len(recent_alerts),
                "critical": len([a for a in recent_alerts if a.severity == 'critical']),
                "recent": [asdict(a) for a in recent_alerts]
            },
            "recent_events": [asdict(e) for e in recent_events],
            "trends": trends
        }
    
    def _get_health_status(self, score: float) -> str:
        """Get health status string"""
        if score >= 80:
            return "excellent"
        elif score >= 60:
            return "good"
        elif score >= 40:
            return "fair"
        elif score >= 20:
            return "poor"
        else:
            return "critical"
    
    def _calculate_trends(self) -> Dict[str, str]:
        """Calculate trend indicators"""
        trends = {}
        
        if len(self.performance_history) >= 60:  # Last hour
            recent_data = list(self.performance_history)[-60:]
            previous_data = list(self.performance_history)[-120:-60] if len(self.performance_history) >= 120 else []
            
            # Health trend
            recent_health = np.mean([s.system_performance for s in recent_data])
            if previous_data:
                previous_health = np.mean([s.system_performance for s in previous_data])
                if recent_health > previous_health * 1.05:
                    trends["health_trend"] = "improving"
                elif recent_health < previous_health * 0.95:
                    trends["health_trend"] = "declining"
                else:
                    trends["health_trend"] = "stable"
            
            # Optimization trend
            recent_opt = np.mean([s.optimization_score for s in recent_data])
            if previous_data:
                previous_opt = np.mean([s.optimization_score for s in previous_data])
                if recent_opt > previous_opt * 1.05:
                    trends["optimization_trend"] = "improving"
                elif recent_opt < previous_opt * 0.95:
                    trends["optimization_trend"] = "declining"
                else:
                    trends["optimization_trend"] = "stable"
        
        return trends
    
    def generate_performance_chart(self, hours: int = 24) -> str:
        """Generate performance chart as JSON for web display"""
        try:
            if len(self.performance_history) == 0:
                return json.dumps({"error": "No performance data available"})
            
            # Get data for specified hours
            cutoff_time = datetime.now() - timedelta(hours=hours)
            filtered_data = [s for s in self.performance_history 
                           if datetime.fromisoformat(s.timestamp) >= cutoff_time]
            
            if not filtered_data:
                return json.dumps({"error": "No data for specified time range"})
            
            # Prepare data
            timestamps = [s.timestamp for s in filtered_data]
            system_performance = [s.system_performance for s in filtered_data]
            bot_performance = [s.bot_performance for s in filtered_data]
            strategy_performance = [s.strategy_performance for s in filtered_data]
            optimization_score = [s.optimization_score for s in filtered_data]
            
            # Create plotly figure
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('System Performance', 'Bot Performance', 
                              'Strategy Performance', 'Optimization Score'),
                vertical_spacing=0.1
            )
            
            # Add traces
            fig.add_trace(
                go.Scatter(x=timestamps, y=system_performance, name='System', line=dict(color='blue')),
                row=1, col=1
            )
            fig.add_trace(
                go.Scatter(x=timestamps, y=bot_performance, name='Bots', line=dict(color='green')),
                row=1, col=2
            )
            fig.add_trace(
                go.Scatter(x=timestamps, y=strategy_performance, name='Strategies', line=dict(color='orange')),
                row=2, col=1
            )
            fig.add_trace(
                go.Scatter(x=timestamps, y=optimization_score, name='Optimization', line=dict(color='red')),
                row=2, col=2
            )
            
            # Update layout
            fig.update_layout(
                title=f'Performance Metrics - Last {hours} Hours',
                showlegend=False,
                height=600
            )
            
            return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            
        except Exception as e:
            self.logger.error(f"Error generating performance chart: {e}")
            return json.dumps({"error": str(e)})
    
    def export_dashboard_data(self, format: str = "json") -> str:
        """Export dashboard data for analysis"""
        try:
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "current_metrics": asdict(self.current_metrics) if self.current_metrics else None,
                "alerts": [asdict(a) for a in self.alerts],
                "optimization_events": [asdict(e) for e in self.optimization_events],
                "performance_history": [asdict(s) for s in self.performance_history],
                "alert_thresholds": self.alert_thresholds,
                "performance_baselines": self.performance_baselines
            }
            
            if format.lower() == "json":
                export_file = self.dashboard_dir / f"dashboard_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(export_file, 'w') as f:
                    json.dump(export_data, f, indent=2)
                return str(export_file)
            
            else:
                raise ValueError(f"Unsupported export format: {format}")
                
        except Exception as e:
            self.logger.error(f"Error exporting dashboard data: {e}")
            return ""
    
    async def start_real_time_monitoring(self, update_interval: int = 60):
        """Start real-time dashboard monitoring"""
        self.logger.info(f"Starting real-time monitoring with {update_interval}s intervals")
        
        while True:
            try:
                # This would be called by the main optimization system
                # For now, we'll just save the current state
                if self.current_metrics:
                    self._save_dashboard_data()
                
                # Auto-resolve old alerts
                cutoff_time = datetime.now() - timedelta(hours=24)
                for alert in self.alerts:
                    if (not alert.auto_resolved and not alert.acknowledged and 
                        datetime.fromisoformat(alert.timestamp) < cutoff_time):
                        self.resolve_alert(alert.alert_id, auto_resolved=True)
                
                await asyncio.sleep(update_interval)
                
            except Exception as e:
                self.logger.error(f"Error in real-time monitoring: {e}")
                await asyncio.sleep(update_interval)

    def get_alert_statistics(self) -> Dict[str, Any]:
        """Get alert statistics for analysis"""
        if not self.alerts:
            return {"total": 0, "by_severity": {}, "by_category": {}}
        
        # Calculate statistics
        total_alerts = len(self.alerts)
        by_severity = defaultdict(int)
        by_category = defaultdict(int)
        resolution_times = []
        
        for alert in self.alerts:
            by_severity[alert.severity] += 1
            by_category[alert.category] += 1
            
            if alert.resolved_at:
                resolution_time = (datetime.fromisoformat(alert.resolved_at) - 
                                 datetime.fromisoformat(alert.timestamp)).total_seconds()
                resolution_times.append(resolution_time)
        
        return {
            "total": total_alerts,
            "by_severity": dict(by_severity),
            "by_category": dict(by_category),
            "resolution_stats": {
                "total_resolved": len(resolution_times),
                "avg_resolution_time_minutes": np.mean(resolution_times) / 60 if resolution_times else 0,
                "median_resolution_time_minutes": np.median(resolution_times) / 60 if resolution_times else 0
            },
            "active_alerts": len([a for a in self.alerts if not a.auto_resolved and not a.acknowledged])
        }
