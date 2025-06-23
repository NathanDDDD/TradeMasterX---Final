"""
TradeMasterX 2.0 - Phase 14: AI Copilot Assistant
Real-time monitoring, intelligent analysis, and human-like feedback capabilities
"""

import asyncio
import json
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
import threading
import time
from collections import deque
import sqlite3

from ...core.bot_registry import BaseBot
from ...interface.assistant.conversation_engine import ConversationEngine
from ...interface.assistant.api_integration import APIIntegration
from ..phase_11.anomaly_detector import AnomalyDetector
from ...bots.analytics.analytics_bot import AnalyticsBot
from .real_time_monitor import RealTimeMonitor
from .intelligent_analyzer import IntelligentAnalyzer
from .feedback_generator import FeedbackGenerator


@dataclass
class CopilotAlert:
    """AI Copilot alert data structure"""
    alert_id: str
    timestamp: str
    alert_type: str  # 'anomaly', 'pattern', 'performance', 'system', 'prediction'
    severity: str  # 'low', 'medium', 'high', 'critical'
    title: str
    description: str
    data: Dict[str, Any]
    recommendations: List[str]
    auto_resolved: bool = False
    human_acknowledged: bool = False
    resolved_timestamp: Optional[str] = None


@dataclass
class CopilotInsight:
    """AI Copilot insight data structure"""
    insight_id: str
    timestamp: str
    insight_type: str  # 'pattern', 'optimization', 'risk', 'opportunity'
    confidence: float
    title: str
    description: str
    impact_score: float  # 0-100
    supporting_data: Dict[str, Any]
    actionable_recommendations: List[str]
    follow_up_required: bool = False


@dataclass
class SystemHealthStatus:
    """Comprehensive system health status"""
    timestamp: str
    overall_health: str  # 'excellent', 'good', 'fair', 'poor', 'critical'
    health_score: float  # 0-100
    active_bots: int
    failed_bots: int
    anomalies_24h: int
    critical_anomalies: int
    win_rate_24h: float
    pnl_24h: float
    system_uptime: float
    memory_usage: float
    cpu_usage: float
    active_alerts: int
    resolved_alerts_24h: int


class AICopilot(BaseBot):
    """
    AI Copilot Assistant - The central intelligence system for TradeMasterX
    
    Provides:
    - Real-time monitoring and anomaly detection    - Intelligent pattern recognition and analysis
    - Human-like feedback and recommendations
    - Proactive alert management
    - Continuous system optimization insights
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize AI Copilot Assistant"""
        super().__init__(
            name="AI Copilot Assistant",
            config=config or {}
        )
        
        self.config = config or {}
        self.logger = self._setup_logging()
        
        # Core components
        self.real_time_monitor = RealTimeMonitor(config.get('monitor', {}))
        self.intelligent_analyzer = IntelligentAnalyzer(config.get('analyzer', {}))
        self.feedback_generator = FeedbackGenerator(config.get('feedback', {}))
        
        # Integration with existing systems
        self.anomaly_detector = AnomalyDetector(config.get('anomaly_detector', {}))
        self.analytics_bot = AnalyticsBot(config.get('analytics', {}))
        self.conversation_engine = ConversationEngine(config.get('conversation', {}))
        
        # State management
        self.active_alerts = {}
        self.recent_insights = deque(maxlen=100)
        self.system_health_history = deque(maxlen=1440)  # 24 hours of minute-by-minute data
        self.performance_metrics = {}
        
        # Configuration
        self.monitoring_interval = config.get('monitoring_interval', 30)  # seconds
        self.alert_thresholds = config.get('alert_thresholds', {
            'anomaly_spike': 5,
            'performance_drop': 0.2,
            'system_resource': 0.85,
            'bot_failure_rate': 0.3
        })
        
        # Data storage
        self.data_dir = Path(config.get('data_dir', 'data/ai_copilot'))
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.data_dir / 'copilot_data.db'
        
        # Control flags
        self.is_monitoring = False
        self.monitoring_thread = None
        
        # Initialize database and load existing data
        self._init_database()
        self._load_existing_data()
        
        self.logger.info("🤖 AI Copilot Assistant initialized successfully")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for AI Copilot"""
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
    
    def _init_database(self):
        """Initialize AI Copilot database"""
        with sqlite3.connect(self.db_path) as conn:
            # Alerts table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    alert_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    alert_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    data TEXT,
                    recommendations TEXT,
                    auto_resolved BOOLEAN DEFAULT 0,
                    human_acknowledged BOOLEAN DEFAULT 0,
                    resolved_timestamp TEXT
                )
            """)
            
            # Insights table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS insights (
                    insight_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    insight_type TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    impact_score REAL,
                    supporting_data TEXT,
                    recommendations TEXT,
                    follow_up_required BOOLEAN DEFAULT 0
                )
            """)
            
            # System health table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS system_health (
                    timestamp TEXT PRIMARY KEY,
                    overall_health TEXT NOT NULL,
                    health_score REAL NOT NULL,
                    active_bots INTEGER,
                    failed_bots INTEGER,
                    anomalies_24h INTEGER,
                    critical_anomalies INTEGER,
                    win_rate_24h REAL,
                    pnl_24h REAL,
                    system_uptime REAL,
                    memory_usage REAL,
                    cpu_usage REAL,
                    active_alerts INTEGER,
                    resolved_alerts_24h INTEGER
                )
            """)
            
            # Performance metrics table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    timestamp TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    metric_unit TEXT,
                    bot_id TEXT,
                    PRIMARY KEY (timestamp, metric_name, bot_id)
                )
            """)
    
    def _load_existing_data(self):
        """Load existing alerts and insights from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Load active alerts
                cursor = conn.execute("""
                    SELECT * FROM alerts 
                    WHERE auto_resolved = 0 AND resolved_timestamp IS NULL
                    ORDER BY timestamp DESC
                """)
                
                for row in cursor.fetchall():
                    alert = CopilotAlert(
                        alert_id=row[0],
                        timestamp=row[1],
                        alert_type=row[2],
                        severity=row[3],
                        title=row[4],
                        description=row[5],
                        data=json.loads(row[6]) if row[6] else {},
                        recommendations=json.loads(row[7]) if row[7] else [],
                        auto_resolved=bool(row[8]),
                        human_acknowledged=bool(row[9]),
                        resolved_timestamp=row[10]
                    )
                    self.active_alerts[alert.alert_id] = alert
                
                # Load recent insights
                cursor = conn.execute("""
                    SELECT * FROM insights 
                    ORDER BY timestamp DESC 
                    LIMIT 50
                """)
                
                for row in cursor.fetchall():
                    insight = CopilotInsight(
                        insight_id=row[0],
                        timestamp=row[1],
                        insight_type=row[2],
                        confidence=row[3],
                        title=row[4],
                        description=row[5],
                        impact_score=row[6],
                        supporting_data=json.loads(row[7]) if row[7] else {},
                        actionable_recommendations=json.loads(row[8]) if row[8] else [],
                        follow_up_required=bool(row[9])
                    )
                    self.recent_insights.append(insight)
                
                self.logger.info(f"Loaded {len(self.active_alerts)} active alerts and {len(self.recent_insights)} recent insights")
                
        except Exception as e:
            self.logger.error(f"Error loading existing data: {e}")
    
    async def start_monitoring(self):
        """Start continuous monitoring and analysis"""
        if self.is_monitoring:
            self.logger.warning("AI Copilot monitoring already running")
            return
        
        self.is_monitoring = True
        self.logger.info(" Starting AI Copilot continuous monitoring...")
        
        # Start monitoring thread
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        # Start real-time monitor
        await self.real_time_monitor.start()
        
        self.logger.info("✅ AI Copilot monitoring started successfully")
    
    async def stop_monitoring(self):
        """Stop continuous monitoring"""
        if not self.is_monitoring:
            return
        
        self.is_monitoring = False
        self.logger.info("🛑 Stopping AI Copilot monitoring...")
        
        # Stop real-time monitor
        await self.real_time_monitor.stop()
        
        # Wait for monitoring thread to finish
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5)
        
        self.logger.info("✅ AI Copilot monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop running in separate thread"""
        while self.is_monitoring:
            try:
                # Run monitoring cycle
                asyncio.run(self._monitoring_cycle())
                
                # Sleep until next cycle
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(5)  # Brief pause before retrying
    
    async def _monitoring_cycle(self):
        """Single monitoring cycle - performs all monitoring tasks"""
        try:
            # 1. Collect system health data
            health_status = await self._collect_system_health()
            self.system_health_history.append(health_status)
            
            # 2. Run intelligent analysis
            analysis_results = await self.intelligent_analyzer.analyze_system_state(
                health_status, self.recent_insights, self.active_alerts
            )
            
            # 3. Check for new anomalies
            await self._check_anomalies()
            
            # 4. Generate insights and alerts
            await self._process_analysis_results(analysis_results)
            
            # 5. Update performance metrics
            await self._update_performance_metrics()
            
            # 6. Auto-resolve expired alerts
            await self._auto_resolve_alerts()
            
            # 7. Save to database
            await self._save_monitoring_data(health_status)
            
        except Exception as e:
            self.logger.error(f"Error in monitoring cycle: {e}")
    
    async def _collect_system_health(self) -> SystemHealthStatus:
        """Collect comprehensive system health data"""
        try:
            # Get real-time metrics from monitor
            metrics = await self.real_time_monitor.get_current_metrics()
            
            # Calculate health score
            health_score = self._calculate_health_score(metrics)
            
            # Determine overall health status
            if health_score >= 90:
                overall_health = 'excellent'
            elif health_score >= 75:
                overall_health = 'good'
            elif health_score >= 60:
                overall_health = 'fair'
            elif health_score >= 40:
                overall_health = 'poor'
            else:
                overall_health = 'critical'
            
            return SystemHealthStatus(
                timestamp=datetime.now().isoformat(),
                overall_health=overall_health,
                health_score=health_score,
                active_bots=metrics.get('active_bots', 0),
                failed_bots=metrics.get('failed_bots', 0),
                anomalies_24h=metrics.get('anomalies_24h', 0),
                critical_anomalies=metrics.get('critical_anomalies', 0),
                win_rate_24h=metrics.get('win_rate_24h', 0.0),
                pnl_24h=metrics.get('pnl_24h', 0.0),
                system_uptime=metrics.get('system_uptime', 0.0),
                memory_usage=metrics.get('memory_usage', 0.0),
                cpu_usage=metrics.get('cpu_usage', 0.0),
                active_alerts=len(self.active_alerts),
                resolved_alerts_24h=metrics.get('resolved_alerts_24h', 0)
            )
            
        except Exception as e:
            self.logger.error(f"Error collecting system health: {e}")
            # Return basic health status in case of error
            return SystemHealthStatus(
                timestamp=datetime.now().isoformat(),
                overall_health='unknown',
                health_score=0.0,
                active_bots=0,
                failed_bots=0,
                anomalies_24h=0,
                critical_anomalies=0,
                win_rate_24h=0.0,
                pnl_24h=0.0,
                system_uptime=0.0,
                memory_usage=0.0,
                cpu_usage=0.0,
                active_alerts=len(self.active_alerts),
                resolved_alerts_24h=0
            )
    
    def _calculate_health_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate overall system health score (0-100)"""
        try:
            score = 100.0
            
            # Performance factors
            win_rate = metrics.get('win_rate_24h', 0.5)
            if win_rate < 0.4:
                score -= 20
            elif win_rate < 0.5:
                score -= 10
            
            # Bot health factors
            total_bots = metrics.get('active_bots', 0) + metrics.get('failed_bots', 0)
            if total_bots > 0:
                bot_failure_rate = metrics.get('failed_bots', 0) / total_bots
                score -= bot_failure_rate * 30
            
            # Anomaly factors
            critical_anomalies = metrics.get('critical_anomalies', 0)
            if critical_anomalies > 0:
                score -= min(critical_anomalies * 15, 30)
            
            anomalies_24h = metrics.get('anomalies_24h', 0)
            if anomalies_24h > 10:
                score -= min((anomalies_24h - 10) * 2, 20)
            
            # System resource factors
            memory_usage = metrics.get('memory_usage', 0.0)
            if memory_usage > 0.9:
                score -= 15
            elif memory_usage > 0.8:
                score -= 5
            
            cpu_usage = metrics.get('cpu_usage', 0.0)
            if cpu_usage > 0.9:
                score -= 10
            elif cpu_usage > 0.8:
                score -= 3
            
            return max(0.0, min(100.0, score))
            
        except Exception as e:
            self.logger.error(f"Error calculating health score: {e}")
            return 50.0  # Default middle score on error
    
    async def _check_anomalies(self):
        """Check for new anomalies and create alerts"""
        try:
            # Get recent trades from analytics bot
            analytics_data = await self.analytics_bot.analyze_market()
            
            if analytics_data.get('status') == 'success':
                # Check for performance anomalies
                win_rate = analytics_data.get('win_rate', 0.5)
                if win_rate < 0.3:
                    await self._create_alert(
                        alert_type='performance',
                        severity='high',
                        title='Low Win Rate Detected',
                        description=f'Current win rate is {win_rate:.1%}, below critical threshold',
                        data={'win_rate': win_rate, 'threshold': 0.3},
                        recommendations=[
                            'Review trading strategies',
                            'Consider reducing position sizes',
                            'Analyze recent market conditions',
                            'Check bot configurations'
                        ]
                    )
                
                # Check for unusual market volatility
                volatility = analytics_data.get('market_volatility', 0)
                if volatility > 0.05:  # 5% volatility threshold
                    await self._create_alert(
                        alert_type='anomaly',
                        severity='medium',
                        title='High Market Volatility',
                        description=f'Market volatility is {volatility:.1%}, above normal levels',
                        data={'volatility': volatility, 'threshold': 0.05},
                        recommendations=[
                            'Monitor positions closely',
                            'Consider tightening stop losses',
                            'Reduce exposure if necessary',
                            'Stay alert for major news events'
                        ]
                    )
            
        except Exception as e:
            self.logger.error(f"Error checking anomalies: {e}")
    
    async def _create_alert(self, alert_type: str, severity: str, title: str, 
                           description: str, data: Dict[str, Any], recommendations: List[str]):
        """Create a new alert"""
        try:
            alert_id = f"alert_{int(datetime.now().timestamp() * 1000)}"
            
            alert = CopilotAlert(
                alert_id=alert_id,
                timestamp=datetime.now().isoformat(),
                alert_type=alert_type,
                severity=severity,
                title=title,
                description=description,
                data=data,
                recommendations=recommendations
            )
            
            self.active_alerts[alert_id] = alert
            
            # Save to database
            await self._save_alert(alert)
            
            # Generate human-like feedback
            feedback = await self.feedback_generator.generate_alert_feedback(alert)
            
            self.logger.warning(f"🚨 {severity.upper()} ALERT: {title}")
            self.logger.info(f"📝 Copilot says: {feedback}")
            
            return alert_id
            
        except Exception as e:
            self.logger.error(f"Error creating alert: {e}")
            return None
    
    async def _create_insight(self, insight_type: str, confidence: float, title: str,
                             description: str, impact_score: float, supporting_data: Dict[str, Any],
                             recommendations: List[str], follow_up_required: bool = False):
        """Create a new insight"""
        try:
            insight_id = f"insight_{int(datetime.now().timestamp() * 1000)}"
            
            insight = CopilotInsight(
                insight_id=insight_id,
                timestamp=datetime.now().isoformat(),
                insight_type=insight_type,
                confidence=confidence,
                title=title,
                description=description,
                impact_score=impact_score,
                supporting_data=supporting_data,
                actionable_recommendations=recommendations,
                follow_up_required=follow_up_required
            )
            
            self.recent_insights.append(insight)
            
            # Save to database
            await self._save_insight(insight)
            
            # Generate human-like feedback for high-impact insights
            if impact_score > 70:
                feedback = await self.feedback_generator.generate_insight_feedback(insight)
                self.logger.info(f"💡 {title}")
                self.logger.info(f"🤖 Copilot insight: {feedback}")
            
            return insight_id
            
        except Exception as e:
            self.logger.error(f"Error creating insight: {e}")
            return None
    
    async def _process_analysis_results(self, analysis_results: Dict[str, Any]):
        """Process results from intelligent analyzer"""
        try:
            # Process patterns
            patterns = analysis_results.get('patterns', [])
            for pattern in patterns:
                if pattern.get('confidence', 0) > 0.7:
                    await self._create_insight(
                        insight_type='pattern',
                        confidence=pattern['confidence'],
                        title=f"Pattern Detected: {pattern['name']}",
                        description=pattern['description'],
                        impact_score=pattern.get('impact_score', 50),
                        supporting_data=pattern.get('data', {}),
                        recommendations=pattern.get('recommendations', [])
                    )
            
            # Process optimization opportunities
            optimizations = analysis_results.get('optimizations', [])
            for opt in optimizations:
                if opt.get('potential_improvement', 0) > 0.1:  # 10% improvement threshold
                    await self._create_insight(
                        insight_type='optimization',
                        confidence=opt.get('confidence', 0.5),
                        title=f"Optimization Opportunity: {opt['name']}",
                        description=opt['description'],
                        impact_score=opt.get('potential_improvement', 0) * 100,
                        supporting_data=opt.get('data', {}),
                        recommendations=opt.get('recommendations', []),
                        follow_up_required=True
                    )
            
            # Process risk assessments
            risks = analysis_results.get('risks', [])
            for risk in risks:
                if risk.get('severity') in ['high', 'critical']:
                    await self._create_alert(
                        alert_type='risk',
                        severity=risk['severity'],
                        title=f"Risk Alert: {risk['name']}",
                        description=risk['description'],
                        data=risk.get('data', {}),
                        recommendations=risk.get('mitigation_steps', [])
                    )
            
        except Exception as e:
            self.logger.error(f"Error processing analysis results: {e}")
    
    async def _update_performance_metrics(self):
        """Update performance metrics tracking"""
        try:
            timestamp = datetime.now().isoformat()
            
            # Get current system metrics
            metrics = await self.real_time_monitor.get_current_metrics()
            
            # Store key metrics
            performance_data = []
            for metric_name, value in metrics.items():
                if isinstance(value, (int, float)):
                    performance_data.append((timestamp, metric_name, value, None, 'system'))
            
            # Save to database
            with sqlite3.connect(self.db_path) as conn:
                conn.executemany("""
                    INSERT OR REPLACE INTO performance_metrics 
                    (timestamp, metric_name, metric_value, metric_unit, bot_id)
                    VALUES (?, ?, ?, ?, ?)
                """, performance_data)
            
        except Exception as e:
            self.logger.error(f"Error updating performance metrics: {e}")
    
    async def _auto_resolve_alerts(self):
        """Auto-resolve alerts that are no longer relevant"""
        try:
            current_time = datetime.now()
            resolved_count = 0
            
            for alert_id, alert in list(self.active_alerts.items()):
                alert_time = datetime.fromisoformat(alert.timestamp)
                age_hours = (current_time - alert_time).total_seconds() / 3600
                
                # Auto-resolve old alerts based on type and severity
                should_resolve = False
                
                if alert.alert_type == 'performance' and age_hours > 2:
                    # Check if performance has improved
                    current_metrics = await self.real_time_monitor.get_current_metrics()
                    if current_metrics.get('win_rate_24h', 0) > 0.5:
                        should_resolve = True
                
                elif alert.alert_type == 'anomaly' and age_hours > 1:
                    # Anomaly alerts auto-resolve after 1 hour
                    should_resolve = True
                
                elif alert.severity == 'low' and age_hours > 24:
                    # Low severity alerts auto-resolve after 24 hours
                    should_resolve = True
                
                if should_resolve:
                    alert.auto_resolved = True
                    alert.resolved_timestamp = current_time.isoformat()
                    
                    # Update in database
                    with sqlite3.connect(self.db_path) as conn:
                        conn.execute("""
                            UPDATE alerts 
                            SET auto_resolved = 1, resolved_timestamp = ?
                            WHERE alert_id = ?
                        """, (alert.resolved_timestamp, alert_id))
                    
                    # Remove from active alerts
                    del self.active_alerts[alert_id]
                    resolved_count += 1
            
            if resolved_count > 0:
                self.logger.info(f"Auto-resolved {resolved_count} alerts")
                
        except Exception as e:
            self.logger.error(f"Error auto-resolving alerts: {e}")
    
    async def _save_monitoring_data(self, health_status: SystemHealthStatus):
        """Save monitoring data to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Save system health
                conn.execute("""
                    INSERT OR REPLACE INTO system_health
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    health_status.timestamp,
                    health_status.overall_health,
                    health_status.health_score,
                    health_status.active_bots,
                    health_status.failed_bots,
                    health_status.anomalies_24h,
                    health_status.critical_anomalies,
                    health_status.win_rate_24h,
                    health_status.pnl_24h,
                    health_status.system_uptime,
                    health_status.memory_usage,
                    health_status.cpu_usage,
                    health_status.active_alerts,
                    health_status.resolved_alerts_24h
                ))
                
        except Exception as e:
            self.logger.error(f"Error saving monitoring data: {e}")
    
    async def _save_alert(self, alert: CopilotAlert):
        """Save alert to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO alerts
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    alert.alert_id,
                    alert.timestamp,
                    alert.alert_type,
                    alert.severity,
                    alert.title,
                    alert.description,
                    json.dumps(alert.data),
                    json.dumps(alert.recommendations),
                    alert.auto_resolved,
                    alert.human_acknowledged,
                    alert.resolved_timestamp
                ))
                
        except Exception as e:
            self.logger.error(f"Error saving alert: {e}")
    
    async def _save_insight(self, insight: CopilotInsight):
        """Save insight to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO insights
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    insight.insight_id,
                    insight.timestamp,
                    insight.insight_type,
                    insight.confidence,
                    insight.title,
                    insight.description,
                    insight.impact_score,
                    json.dumps(insight.supporting_data),
                    json.dumps(insight.actionable_recommendations),
                    insight.follow_up_required
                ))
                
        except Exception as e:
            self.logger.error(f"Error saving insight: {e}")
    
    # Public API methods
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get current system status and health"""
        try:
            if self.system_health_history:
                latest_health = self.system_health_history[-1]
                
                return {
                    'status': 'success',
                    'system_health': asdict(latest_health),
                    'active_alerts': len(self.active_alerts),
                    'recent_insights': len(self.recent_insights),
                    'monitoring_active': self.is_monitoring,
                    'last_updated': latest_health.timestamp
                }
            else:
                return {
                    'status': 'no_data',
                    'message': 'No health data available yet'
                }
                
        except Exception as e:
            self.logger.error(f"Error getting system status: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get all active alerts"""
        try:
            return [asdict(alert) for alert in self.active_alerts.values()]
        except Exception as e:
            self.logger.error(f"Error getting active alerts: {e}")
            return []
    
    async def get_recent_insights(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent insights"""
        try:
            recent = list(self.recent_insights)[-limit:]
            return [asdict(insight) for insight in recent]
        except Exception as e:
            self.logger.error(f"Error getting recent insights: {e}")
            return []
    
    async def acknowledge_alert(self, alert_id: str) -> bool:
        """Mark an alert as acknowledged by human operator"""
        try:
            if alert_id in self.active_alerts:
                self.active_alerts[alert_id].human_acknowledged = True
                
                # Update in database
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("""
                        UPDATE alerts 
                        SET human_acknowledged = 1
                        WHERE alert_id = ?
                    """, (alert_id,))
                
                self.logger.info(f"Alert {alert_id} acknowledged by human operator")
                return True
            else:
                self.logger.warning(f"Alert {alert_id} not found")
                return False
                
        except Exception as e:
            self.logger.error(f"Error acknowledging alert: {e}")
            return False
    
    async def resolve_alert(self, alert_id: str, resolution_notes: str = None) -> bool:
        """Manually resolve an alert"""
        try:
            if alert_id in self.active_alerts:
                alert = self.active_alerts[alert_id]
                alert.resolved_timestamp = datetime.now().isoformat()
                alert.human_acknowledged = True
                
                # Update in database
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("""
                        UPDATE alerts 
                        SET resolved_timestamp = ?, human_acknowledged = 1
                        WHERE alert_id = ?
                    """, (alert.resolved_timestamp, alert_id))
                
                # Remove from active alerts
                del self.active_alerts[alert_id]
                
                self.logger.info(f"Alert {alert_id} resolved manually")
                return True
            else:
                self.logger.warning(f"Alert {alert_id} not found")
                return False
                
        except Exception as e:
            self.logger.error(f"Error resolving alert: {e}")
            return False
    
    async def generate_copilot_response(self, query: str) -> str:
        """Generate AI Copilot response to human query"""
        try:
            # Get current system context
            system_status = await self.get_system_status()
            active_alerts = await self.get_active_alerts()
            recent_insights = await self.get_recent_insights(5)
            
            context = {
                'system_status': system_status,
                'active_alerts': active_alerts,
                'recent_insights': recent_insights,
                'query': query
            }
            
            # Generate response using feedback generator
            response = await self.feedback_generator.generate_query_response(context)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error generating copilot response: {e}")
            return "I'm experiencing some technical difficulties right now. Please try again in a moment."
    
    async def get_performance_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance summary for specified time period"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            with sqlite3.connect(self.db_path) as conn:
                # Get performance metrics
                cursor = conn.execute("""
                    SELECT metric_name, AVG(metric_value) as avg_value, 
                           MIN(metric_value) as min_value, MAX(metric_value) as max_value
                    FROM performance_metrics 
                    WHERE timestamp >= ?
                    GROUP BY metric_name
                """, (cutoff_time.isoformat(),))
                
                metrics = {}
                for row in cursor.fetchall():
                    metrics[row[0]] = {
                        'average': row[1],
                        'minimum': row[2],
                        'maximum': row[3]
                    }
                
                # Get alert summary
                cursor = conn.execute("""
                    SELECT alert_type, severity, COUNT(*) as count
                    FROM alerts 
                    WHERE timestamp >= ?
                    GROUP BY alert_type, severity
                """, (cutoff_time.isoformat(),))
                
                alert_summary = {}
                for row in cursor.fetchall():
                    alert_type = row[0]
                    if alert_type not in alert_summary:
                        alert_summary[alert_type] = {}
                    alert_summary[alert_type][row[1]] = row[2]
                
                return {
                    'status': 'success',
                    'time_period_hours': hours,
                    'performance_metrics': metrics,
                    'alert_summary': alert_summary,
                    'summary_timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"Error getting performance summary: {e}")
            return {'status': 'error', 'error': str(e)}
    
    # Bot lifecycle methods
    
    async def start(self) -> bool:
        """Start AI Copilot Assistant"""
        try:
            await self.start_monitoring()
            self.status = "running"
            self.logger.info("🤖 AI Copilot Assistant started successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error starting AI Copilot: {e}")
            self.status = "error"
            return False
    
    async def stop(self) -> bool:
        """Stop AI Copilot Assistant"""
        try:
            await self.stop_monitoring()
            self.status = "stopped"
            self.logger.info("🤖 AI Copilot Assistant stopped successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error stopping AI Copilot: {e}")
            return False
    
    async def get_status(self) -> Dict[str, Any]:
        """Get AI Copilot status"""
        try:
            system_status = await self.get_system_status()
            
            return {
                'bot_id': self.bot_id,
                'name': self.name,
                'status': self.status,
                'monitoring_active': self.is_monitoring,
                'active_alerts': len(self.active_alerts),
                'recent_insights': len(self.recent_insights),
                'system_health': system_status.get('system_health', {}),
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting AI Copilot status: {e}")
            return {
                'bot_id': self.bot_id,
                'name': self.name,
                'status': 'error',
                'error': str(e)
            }
    
    # Required abstract methods from BaseBot
    async def initialize(self) -> bool:
        """Initialize AI Copilot and all components"""
        try:
            # Initialize core components
            monitor_init = await self.real_time_monitor.initialize() if hasattr(self.real_time_monitor, 'initialize') else True
            analyzer_init = await self.intelligent_analyzer.initialize()
            feedback_init = await self.feedback_generator.initialize()
            
            if not all([monitor_init, analyzer_init, feedback_init]):
                self.logger.error("Failed to initialize one or more components")
                return False
            
            # Start monitoring
            if not self.monitoring_active:
                await self.start_monitoring()
            
            self.is_initialized = True
            self.logger.info("🤖 AI Copilot initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error initializing AI Copilot: {e}")
            return False
    
    async def execute_cycle(self) -> Dict[str, Any]:
        """Execute one AI Copilot cycle"""
        try:
            if not self.is_initialized:
                return {'status': 'not_initialized', 'timestamp': datetime.now().isoformat()}
            
            # Get system status
            system_status = await self.get_system_health()
            
            # Check for new alerts
            if self.monitoring_active:
                new_alerts = len([a for a in self.active_alerts.values() 
                                if (datetime.now() - datetime.fromisoformat(a.timestamp)).seconds < 60])
            else:
                new_alerts = 0
            
            # Generate insights if needed
            if len(self.recent_insights) < 5:  # Generate more insights if needed
                try:
                    insight = await self.intelligent_analyzer.generate_insight()
                    if insight:
                        self.recent_insights.append(insight)
                except:
                    pass  # Insight generation is optional
            
            return {
                'status': 'active',
                'timestamp': datetime.now().isoformat(),
                'system_health': system_status.get('overall_health', 'unknown'),
                'active_alerts': len(self.active_alerts),
                'new_alerts': new_alerts,
                'recent_insights': len(self.recent_insights),
                'monitoring_active': self.monitoring_active
            }
            
        except Exception as e:
            self.logger.error(f"Error in AI Copilot cycle: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def cleanup(self):
        """Cleanup AI Copilot resources"""
        try:
            # Stop monitoring
            if self.monitoring_active:
                await self.stop_monitoring()
            
            # Cleanup components
            if hasattr(self.real_time_monitor, 'cleanup'):
                await self.real_time_monitor.cleanup()
            
            await self.intelligent_analyzer.cleanup()
            await self.feedback_generator.cleanup()
            
            self.is_initialized = False
            self.logger.info("🤖 AI Copilot cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during AI Copilot cleanup: {e}")
