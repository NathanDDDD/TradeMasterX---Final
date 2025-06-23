#!/usr/bin/env python3
"""
TradeMasterX 2.0 - Phase 14: AI Orchestrator (Clean Implementation)
Coordinates retraining, auditing, and performance optimization
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

class AIOrchestrator:
    """Central coordinator for AI system operations"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger("AIOrchestrator")
        
        # Component references (will be injected)
        self.observer_agent = None
        self.reinforcement_engine = None
        self.anomaly_auditor = None
        
        # State tracking
        self.orchestrator_state = {
            'last_retrain_time': None,
            'retrain_triggers': [],
            'system_health': 'HEALTHY',
            'performance_trend': 'STABLE'
        }
        
        # Thresholds
        self.sharpe_threshold = 0.10  # 10% drop triggers retrain
        self.anomaly_threshold = 0.15  # 15% anomaly rate triggers retrain
        self.min_retrain_interval = 3600  # 1 hour minimum between retrains
        
        # File paths
        self.reports_dir = Path("reports")
        self.data_dir = Path("data")
        self.ai_status_file = self.reports_dir / "ai_status.json"
        
        # Ensure directories exist
        self.reports_dir.mkdir(exist_ok=True)
        self.data_dir.mkdir(exist_ok=True)
        
    def inject_components(self, observer=None, reinforcement=None, auditor=None):
        """Inject component dependencies"""
        if observer:
            self.observer_agent = observer
        if reinforcement:
            self.reinforcement_engine = reinforcement
        if auditor:
            self.anomaly_auditor = auditor
            
    async def start_orchestration(self):
        """Start the AI orchestration loop"""
        self.logger.info("🎼 AI Orchestrator started - coordinating system optimization")
        
        while True:
            try:
                await self._orchestration_cycle()
                await asyncio.sleep(300)  # Run every 5 minutes
            except Exception as e:
                self.logger.error(f"Orchestration cycle error: {e}")
                await asyncio.sleep(60)  # Brief pause before retry
                
    async def _orchestration_cycle(self):
        """Single orchestration cycle"""
        self.logger.info("🔄 Starting orchestration cycle...")
        
        # Collect system metrics
        metrics = await self._collect_system_metrics()
        
        # Assess system health
        health_assessment = self._assess_system_health(metrics)
        
        # Check if retraining is needed
        retrain_needed = await self._check_retrain_triggers(metrics)
        
        if retrain_needed:
            await self._trigger_retraining(metrics)
            
        # Update system status
        await self._update_ai_status(metrics, health_assessment)
        
        self.logger.info(f"🎼 Orchestration cycle complete - Health: {health_assessment.get('status', 'Unknown')}")
        
    async def _collect_system_metrics(self) -> Dict[str, Any]:
        """Collect metrics from all system components"""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'observer_summary': {},
            'reinforcement_metrics': {},
            'anomaly_stats': {},
            'performance_data': {}
        }
        
        try:
            # Collect from Observer Agent
            if self.observer_agent:
                metrics['observer_summary'] = self.observer_agent.get_observation_summary(24)
                
            # Collect from Reinforcement Engine
            if self.reinforcement_engine:
                metrics['reinforcement_metrics'] = self.reinforcement_engine.get_strategy_performance()
                
            # Collect from Anomaly Auditor  
            if self.anomaly_auditor:
                metrics['anomaly_stats'] = self.anomaly_auditor.get_audit_summary(24)
                
            # Get performance metrics
            performance = await self._get_performance_metrics()
            metrics['performance_data'] = performance
            
        except Exception as e:
            self.logger.error(f"Failed to collect system metrics: {e}")
            
        return metrics
        
    async def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get overall system performance metrics"""
        return {
            'sharpe_ratio': 0.0,
            'max_drawdown': 0.0,
            'win_rate': 0.0,
            'total_trades': 0,
            'avg_return': 0.0
        }
        
    def _assess_system_health(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall system health"""
        health = {
            'status': 'HEALTHY',
            'issues': [],
            'score': 100
        }
        
        # Check anomaly rate
        anomaly_stats = metrics.get('anomaly_stats', {})
        if isinstance(anomaly_stats, dict):
            anomaly_rate = anomaly_stats.get('anomaly_rate', 0)
            if anomaly_rate > self.anomaly_threshold:
                health['issues'].append(f'High anomaly rate: {anomaly_rate:.2%}')
                health['score'] -= 20
                
        # Check performance metrics
        performance = metrics.get('performance_data', {})
        sharpe_ratio = performance.get('sharpe_ratio', 0)
        if sharpe_ratio < 0.5:
            health['issues'].append(f'Low Sharpe ratio: {sharpe_ratio:.2f}')
            health['score'] -= 15
            
        # Determine overall status
        if health['score'] < 60:
            health['status'] = 'CRITICAL'
        elif health['score'] < 80:
            health['status'] = 'DEGRADED'
            
        return health
        
    async def _check_retrain_triggers(self, metrics: Dict[str, Any]) -> bool:
        """Check if retraining should be triggered"""
        triggers = []
        
        # Check Sharpe ratio decline
        performance = metrics.get('performance_data', {})
        current_sharpe = performance.get('sharpe_ratio', 0)
        baseline_sharpe = self._get_baseline_sharpe()
        
        if baseline_sharpe and current_sharpe < baseline_sharpe * (1 - self.sharpe_threshold):
            triggers.append(f'Sharpe ratio decline: {current_sharpe:.3f} < {baseline_sharpe:.3f}')
            
        # Check anomaly rate
        anomaly_stats = metrics.get('anomaly_stats', {})
        if isinstance(anomaly_stats, dict):
            anomaly_rate = anomaly_stats.get('anomaly_rate', 0)
            if anomaly_rate > self.anomaly_threshold:
                triggers.append(f'High anomaly rate: {anomaly_rate:.2%}')
                
        # Check time since last retrain
        if self.orchestrator_state.get('last_retrain_time'):
            last_retrain = datetime.fromisoformat(self.orchestrator_state['last_retrain_time'])
            time_since = (datetime.now() - last_retrain).total_seconds()
            if time_since < self.min_retrain_interval:
                self.logger.info(f"Retrain triggers found but cooling down: {time_since:.0f}s < {self.min_retrain_interval}s")
                return False
                
        if triggers:
            self.orchestrator_state['retrain_triggers'] = triggers
            self.logger.info(f"🚨 Retrain triggers: {', '.join(triggers)}")
            return True
            
        return False
        
    def _get_baseline_sharpe(self) -> Optional[float]:
        """Get baseline Sharpe ratio for comparison"""
        try:
            return 1.0  # Default baseline
        except:
            return None
            
    async def _trigger_retraining(self, metrics: Dict[str, Any]):
        """Trigger system retraining"""
        self.logger.info("🧠 Triggering AI system retraining...")
        
        try:
            # Update state
            self.orchestrator_state['last_retrain_time'] = datetime.now().isoformat()
            
            # Log retraining event
            retrain_log = {
                'timestamp': datetime.now().isoformat(),
                'triggers': self.orchestrator_state.get('retrain_triggers', []),
                'pre_retrain_metrics': metrics,
                'status': 'initiated'
            }
            
            retrain_file = self.reports_dir / "retrain_log.json"
            logs = []
            if retrain_file.exists():
                with open(retrain_file, 'r') as f:
                    logs = json.load(f)
            logs.append(retrain_log)
            
            with open(retrain_file, 'w') as f:
                json.dump(logs, f, indent=2)
                
            self.logger.info("✅ Retraining process initiated")
            
        except Exception as e:
            self.logger.error(f"Retraining failed: {e}")
            
    async def _update_ai_status(self, metrics: Dict[str, Any], health: Dict[str, Any]):
        """Update AI system status file"""
        try:
            status = {
                'timestamp': datetime.now().isoformat(),
                'phase': 14,
                'orchestrator_state': self.orchestrator_state,
                'system_metrics': metrics,
                'system_health': health,
                'components': {
                    'observer_agent': self.observer_agent is not None,
                    'reinforcement_engine': self.reinforcement_engine is not None,
                    'anomaly_auditor': self.anomaly_auditor is not None
                }
            }
            
            with open(self.ai_status_file, 'w') as f:
                json.dump(status, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to update AI status: {e}")
            
    def get_ai_health_report(self) -> Dict[str, Any]:
        """Get current AI system health report"""
        try:
            if self.ai_status_file.exists():
                with open(self.ai_status_file, 'r') as f:
                    return json.load(f)
            return {"error": "AI status not available"}
        except Exception as e:
            return {"error": str(e)}
            
    async def manual_retrain_trigger(self, reason: str = "Manual trigger"):
        """Manually trigger retraining"""
        self.logger.info(f"🔧 Manual retrain triggered: {reason}")
        
        # Collect current metrics
        metrics = await self._collect_system_metrics()
        
        # Add manual trigger
        self.orchestrator_state['retrain_triggers'] = [f"Manual: {reason}"]
        
        # Execute retraining
        await self._trigger_retraining(metrics)
        
        return True
