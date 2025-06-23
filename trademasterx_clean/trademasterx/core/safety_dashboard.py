"""
TradeMasterX 2.0 - Core Safety Dashboard
Phase 12: Live Trade Safety, Failovers & Risk Mitigation Systems

Core safety monitoring and control system.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import yaml


class SafetyDashboard:
    """
    Core safety dashboard for monitoring all safety systems
    """
    
    def __init__(self):
        self.logger = logging.getLogger("SafetyDashboard")
        
        # Initialize safety systems
        self._initialize_safety_systems()
        
    def _initialize_safety_systems(self):
        """Initialize all safety system components"""
        try:
            # Load configuration
            config_file = Path("trademasterx/config/system.yaml")
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = yaml.safe_load(f)
            else:
                config = {}
                
            # Initialize components (lazy loading to avoid circular imports)
            self._kill_switch = None
            self._risk_guard = None
            self._deviation_alert = None
            self._recovery_manager = None
            self.config = config
            
            self.logger.info("Safety Dashboard core initialized")
            
        except Exception as e:
            self.logger.error(f"[ERROR] Safety dashboard initialization failed: {e}")
            self._kill_switch = None
            self._risk_guard = None
            self._deviation_alert = None
            self._recovery_manager = None
    
    def _get_kill_switch(self):
        """Lazy load kill switch"""
        if self._kill_switch is None:
            try:
                from trademasterx.core.kill_switch import KillSwitch
                self._kill_switch = KillSwitch()
            except Exception as e:
                self.logger.error(f"Failed to load KillSwitch: {e}")
                self._kill_switch = None
        return self._kill_switch
    
    def _get_risk_guard(self):
        """Lazy load risk guard"""
        if self._risk_guard is None:
            try:
                from trademasterx.core.risk_guard import RiskGuard
                self._risk_guard = RiskGuard()
            except Exception as e:
                self.logger.error(f"Failed to load RiskGuard: {e}")
                self._risk_guard = None
        return self._risk_guard
    
    def _get_deviation_alert(self):
        """Lazy load deviation alert"""
        if self._deviation_alert is None:
            try:
                from trademasterx.core.trade_deviation_alert import TradeDeviationAlert
                self._deviation_alert = TradeDeviationAlert()
            except Exception as e:
                self.logger.error(f"Failed to load TradeDeviationAlert: {e}")
                self._deviation_alert = None
        return self._deviation_alert
    
    def _get_recovery_manager(self):
        """Lazy load recovery manager"""
        if self._recovery_manager is None:
            try:
                from trademasterx.core.failover_recovery import RecoveryManager
                self._recovery_manager = RecoveryManager()
            except Exception as e:
                self.logger.error(f"Failed to load RecoveryManager: {e}")
                self._recovery_manager = None
        return self._recovery_manager
    
    def get_safety_status(self) -> Dict[str, Any]:
        """Get comprehensive safety system status"""
        try:
            status = {
                'timestamp': datetime.now().isoformat(),
                'overall_status': 'active',
                'components': {}
            }
            
            # Kill Switch Status
            kill_switch = self._get_kill_switch()
            if kill_switch:
                status['components']['kill_switch'] = {
                    'active': kill_switch._kill_switch_active,
                    'live_trading_enabled': kill_switch._live_trading_enabled,
                    'status': 'operational'
                }
            else:
                status['components']['kill_switch'] = {'status': 'error', 'message': 'Failed to load'}
            
            # Risk Guard Status
            risk_guard = self._get_risk_guard()
            if risk_guard:
                status['components']['risk_guard'] = {
                    'auto_halt_active': getattr(risk_guard, 'auto_halt_active', False),
                    'status': 'operational'
                }
            else:
                status['components']['risk_guard'] = {'status': 'error', 'message': 'Failed to load'}
            
            # Deviation Alert Status
            deviation_alert = self._get_deviation_alert()
            if deviation_alert:
                status['components']['deviation_alert'] = {
                    'monitoring_active': getattr(deviation_alert, 'monitoring_active', True),
                    'status': 'operational'
                }
            else:
                status['components']['deviation_alert'] = {'status': 'error', 'message': 'Failed to load'}
            
            # Recovery Manager Status
            recovery_manager = self._get_recovery_manager()
            if recovery_manager:
                status['components']['recovery_manager'] = {
                    'active': getattr(recovery_manager, 'active', True),
                    'status': 'operational'
                }
            else:
                status['components']['recovery_manager'] = {'status': 'error', 'message': 'Failed to load'}
            
            # Add system health overall assessment
            total_components = len(status['components'])
            operational_components = sum(1 for comp in status['components'].values() 
                                       if comp.get('status') == 'operational')
            
            status['system_health'] = {
                'overall_status': 'healthy' if operational_components == total_components else 'degraded',
                'operational_components': operational_components,
                'total_components': total_components,
                'health_percentage': (operational_components / total_components) * 100 if total_components > 0 else 0
            }
            
            # Add flattened access for easier testing  
            status['kill_switch'] = status['components'].get('kill_switch', {})
            status['risk_guard'] = status['components'].get('risk_guard', {})
            status['deviation_alert'] = status['components'].get('deviation_alert', {})
            status['recovery_manager'] = status['components'].get('recovery_manager', {})
            
            return status
            
        except Exception as e:
            self.logger.error(f"[ERROR] Failed to get safety status: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'overall_status': 'error',
                'error': str(e)
            }
    
    def get_risk_metrics(self) -> Dict[str, Any]:
        """Get current risk metrics"""
        try:
            risk_guard = self._get_risk_guard()
            if risk_guard and hasattr(risk_guard, 'get_current_metrics'):
                return risk_guard.get_current_metrics()
            else:
                return {
                    'timestamp': datetime.now().isoformat(),
                    'status': 'unavailable',
                    'message': 'Risk metrics not available'
                }
        except Exception as e:
            self.logger.error(f"Failed to get risk metrics: {e}")
            return {'error': str(e)}
    
    def get_deviation_data(self) -> Dict[str, Any]:
        """Get trade deviation data"""
        try:
            deviation_alert = self._get_deviation_alert()
            if deviation_alert:
                return {
                    'timestamp': datetime.now().isoformat(),
                    'monitoring_active': getattr(deviation_alert, 'monitoring_active', True),
                    'baseline_updated': True,
                    'status': 'operational'
                }
            else:
                return {
                    'timestamp': datetime.now().isoformat(),
                    'status': 'unavailable',
                    'message': 'Deviation monitoring not available'
                }
        except Exception as e:
            self.logger.error(f"Failed to get deviation data: {e}")
            return {'error': str(e)}
    
    def get_recent_alerts(self) -> Dict[str, Any]:
        """Get recent safety alerts"""
        try:
            return {
                'timestamp': datetime.now().isoformat(),
                'alerts': [],
                'count': 0,
                'status': 'no_alerts'
            }
        except Exception as e:
            self.logger.error(f"Failed to get recent alerts: {e}")
            return {'error': str(e)}
    
    def emergency_stop(self) -> Dict[str, Any]:
        """Trigger emergency stop"""
        try:
            kill_switch = self._get_kill_switch()
            if kill_switch and hasattr(kill_switch, 'emergency_stop'):
                result = kill_switch.emergency_stop("SAFETY_DASHBOARD_EMERGENCY")
                return {
                    'timestamp': datetime.now().isoformat(),
                    'action': 'emergency_stop_triggered',
                    'result': result,
                    'status': 'executed'
                }
            else:
                return {
                    'timestamp': datetime.now().isoformat(),
                    'action': 'emergency_stop_failed',
                    'error': 'Kill switch not available',
                    'status': 'error'
                }
        except Exception as e:
            self.logger.error(f"Failed to trigger emergency stop: {e}")
            return {'error': str(e)}
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """
        Get comprehensive dashboard data for display
        
        Returns:
            Dict containing all dashboard data including status, metrics, and alerts
        """
        try:
            # Get all component statuses
            safety_status = self.get_safety_status()
            risk_metrics = self.get_risk_metrics()
            deviation_data = self.get_deviation_data()
            recent_alerts = self.get_recent_alerts()
            
            # Combine into comprehensive dashboard data
            dashboard_data = {
                'timestamp': datetime.now().isoformat(),
                'safety_status': safety_status,
                'risk_metrics': risk_metrics, 
                'deviation_data': deviation_data,
                'recent_alerts': recent_alerts,
                'system_health': safety_status.get('system_health', {}),
                'safety_level': self._calculate_safety_level(),
                'components': safety_status.get('components', {}),
                'alerts_count': recent_alerts.get('count', 0),
                'operational_status': safety_status.get('overall_status', 'unknown')
            }
            
            return dashboard_data
            
        except Exception as e:
            self.logger.error(f"Failed to get dashboard data: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'status': 'error'
            }
    
    def _calculate_safety_level(self) -> str:
        """Calculate overall safety level"""
        try:
            # Check kill switch first
            kill_switch = self._get_kill_switch()
            if kill_switch and getattr(kill_switch, '_kill_switch_active', False):
                return "RED"  # Emergency stop active
            
            # Check risk guard
            risk_guard = self._get_risk_guard()
            if risk_guard and getattr(risk_guard, 'auto_halt_active', False):
                return "RED"  # Risk halt active
            
            # Check if live trading is disabled
            if kill_switch and not getattr(kill_switch, '_live_trading_enabled', False):
                return "YELLOW"  # Demo mode
            
            # All systems operational
            return "GREEN"
            
        except Exception as e:
            self.logger.error(f"Error calculating safety level: {e}")
            return "UNKNOWN"


# Standalone functions for web interface compatibility
def get_risk_metrics() -> Dict[str, Any]:
    """Get risk metrics - standalone function"""
    try:
        dashboard = SafetyDashboard()
        return dashboard.get_risk_metrics()
    except Exception as e:
        return {'error': str(e)}


def get_deviation_data() -> Dict[str, Any]:
    """Get deviation data - standalone function"""
    try:
        dashboard = SafetyDashboard()
        return dashboard.get_deviation_data()
    except Exception as e:
        return {'error': str(e)}


def get_recent_alerts() -> Dict[str, Any]:
    """Get recent alerts - standalone function"""
    try:
        dashboard = SafetyDashboard()
        return dashboard.get_recent_alerts()
    except Exception as e:
        return {'error': str(e)}


def emergency_stop() -> Dict[str, Any]:
    """Emergency stop - standalone function"""
    try:
        dashboard = SafetyDashboard()
        return dashboard.emergency_stop()
    except Exception as e:
        return {'error': str(e)}
