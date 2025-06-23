#!/usr/bin/env python3
"""
TradeMasterX 2.0 - Phase 11 Web Dashboard Integration
Integrates Phase 11 Intelligent Optimization with the existing web interface
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List
import sys

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from trademasterx.optimizers.phase_11 import Phase11Controller
from trademasterx.config.config_loader import ConfigLoader

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/phase_11_web_integration.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("Phase11WebIntegration")

class Phase11WebAPI:
    """
    Web API integration for Phase 11 Intelligent Optimization
    Provides endpoints for the web dashboard to access Phase 11 data
    """
    
    def __init__(self):
        self.controller = Phase11Controller()
        self.config = ConfigLoader().load_config("trademasterx/config/phase_11.yaml")
        self.logger = logger
        
        # API endpoints data cache
        self._cache = {}
        self._cache_timestamps = {}
        self._cache_ttl = 60  # 60 seconds cache TTL
        
        self.logger.info("Phase 11 Web API initialized")
    
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cache entry is still valid"""
        if key not in self._cache_timestamps:
            return False
        
        cache_time = self._cache_timestamps[key]
        return (datetime.now() - cache_time).total_seconds() < self._cache_ttl
    
    def _update_cache(self, key: str, data: Any):
        """Update cache with new data"""
        self._cache[key] = data
        self._cache_timestamps[key] = datetime.now()
    
    # API Endpoints for Web Dashboard
    
    def get_system_overview(self) -> Dict[str, Any]:
        """Get Phase 11 system overview for dashboard"""
        cache_key = "system_overview"
        
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]
        
        try:
            status = self.controller.get_system_status()
            report = self.controller.get_optimization_report()
            
            overview = {
                'timestamp': datetime.now().isoformat(),
                'system_health': {
                    'status': 'healthy' if len([c for c in status['component_status'].values() if c == 'active']) >= 4 else 'degraded',
                    'active_components': len([c for c in status['component_status'].values() if c == 'active']),
                    'total_components': len(status['component_status']),
                    'uptime_hours': status.get('uptime_hours', 0)
                },
                'optimization_metrics': {
                    'cycle_count': status.get('optimization_cycles', 0),
                    'last_cycle_time': status.get('last_optimization', 'Never'),
                    'efficiency_score': status.get('optimization_efficiency', 0),
                    'processing_rate': status.get('processing_rate', 0)
                },
                'component_status': status['component_status'],
                'recent_alerts': self._get_recent_alerts(limit=5),
                'performance_summary': self._get_performance_summary()
            }
            
            self._update_cache(cache_key, overview)
            return overview
            
        except Exception as e:
            self.logger.error(f"Error getting system overview: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'system_health': {'status': 'error'}
            }
    
    def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get real-time metrics for dashboard updates"""
        cache_key = "real_time_metrics"
        
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]
        
        try:
            dashboard_metrics = self.controller.dashboard.aggregate_real_time_metrics()
            
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'system_health_score': dashboard_metrics.system_health_score,
                'optimization_efficiency': dashboard_metrics.optimization_efficiency,
                'active_alerts_count': dashboard_metrics.alerts_count,
                'component_health': {
                    'strategy_reinforcer': dashboard_metrics.component_health.get('strategy_reinforcer', 0),
                    'bot_scorer': dashboard_metrics.component_health.get('bot_scorer', 0),
                    'strategy_switcher': dashboard_metrics.component_health.get('strategy_switcher', 0),
                    'anomaly_detector': dashboard_metrics.component_health.get('anomaly_detector', 0),
                    'dashboard': dashboard_metrics.component_health.get('dashboard', 0)
                },
                'processing_stats': {
                    'trades_processed_hour': dashboard_metrics.trades_processed_last_hour,
                    'optimizations_completed': dashboard_metrics.optimizations_completed,
                    'avg_processing_time': dashboard_metrics.avg_processing_time_ms,
                    'error_rate': dashboard_metrics.error_rate_percent
                }
            }
            
            self._update_cache(cache_key, metrics)
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error getting real-time metrics: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def get_optimization_history(self, hours: int = 24) -> Dict[str, Any]:
        """Get optimization history for the specified time period"""
        cache_key = f"optimization_history_{hours}"
        
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]
        
        try:
            # Get optimization events from dashboard
            events = self.controller.dashboard.get_optimization_events(
                since=datetime.now() - timedelta(hours=hours)
            )
            
            history = {
                'timestamp': datetime.now().isoformat(),
                'time_period_hours': hours,
                'total_events': len(events),
                'events': events[:100],  # Limit to 100 most recent
                'event_types': self._categorize_events(events),
                'performance_trends': self._calculate_performance_trends(events)
            }
            
            self._update_cache(cache_key, history)
            return history
            
        except Exception as e:
            self.logger.error(f"Error getting optimization history: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'time_period_hours': hours
            }
    
    def get_bot_performance_data(self) -> Dict[str, Any]:
        """Get bot performance data for charts"""
        cache_key = "bot_performance_data"
        
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]
        
        try:
            # Get bot rankings and scores
            rankings = self.controller.bot_scorer.get_bot_rankings()
            
            performance_data = {
                'timestamp': datetime.now().isoformat(),
                'bot_rankings': rankings.get('rankings', []),
                'performance_metrics': {
                    'top_performers': rankings.get('top_performers', []),
                    'improvement_needed': rankings.get('improvement_needed', []),
                    'reliability_scores': rankings.get('reliability_distribution', {})
                },
                'trends': self._get_bot_performance_trends(),
                'charts': self._generate_bot_performance_charts()
            }
            
            self._update_cache(cache_key, performance_data)
            return performance_data
            
        except Exception as e:
            self.logger.error(f"Error getting bot performance data: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def get_strategy_analysis(self) -> Dict[str, Any]:
        """Get strategy switching and performance analysis"""
        cache_key = "strategy_analysis"
        
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]
        
        try:
            # Get strategy evaluation data
            evaluation = self.controller.strategy_switcher.evaluate_all_strategies()
            weights = self.controller.strategy_reinforcer.get_current_weights()
            
            analysis = {
                'timestamp': datetime.now().isoformat(),
                'current_weights': weights,
                'strategy_evaluation': evaluation,
                'switch_recommendations': evaluation.get('recommended_switches', []),
                'performance_grades': evaluation.get('strategy_grades', {}),
                'switching_history': self._get_strategy_switching_history(),
                'weight_evolution': self._get_weight_evolution_data()
            }
            
            self._update_cache(cache_key, analysis)
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error getting strategy analysis: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def get_anomaly_reports(self, severity: str = "all") -> Dict[str, Any]:
        """Get anomaly detection reports"""
        cache_key = f"anomaly_reports_{severity}"
        
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]
        
        try:
            # Get anomaly patterns and recent detections
            patterns = self.controller.anomaly_detector.analyze_patterns()
            recent_anomalies = self._get_recent_anomalies(severity)
            
            reports = {
                'timestamp': datetime.now().isoformat(),
                'severity_filter': severity,
                'anomaly_patterns': patterns,
                'recent_anomalies': recent_anomalies,
                'anomaly_statistics': self._calculate_anomaly_statistics(),
                'risk_assessment': self._assess_anomaly_risks(patterns)
            }
            
            self._update_cache(cache_key, reports)
            return reports
            
        except Exception as e:
            self.logger.error(f"Error getting anomaly reports: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'severity_filter': severity
            }
    
    def get_alerts(self, active_only: bool = True) -> Dict[str, Any]:
        """Get system alerts"""
        try:
            alerts_data = self.controller.dashboard.get_active_alerts() if active_only else self.controller.dashboard.get_all_alerts()
            
            return {
                'timestamp': datetime.now().isoformat(),
                'active_only': active_only,
                'alerts': alerts_data.get('alerts', []),
                'total_count': alerts_data.get('total_count', 0),
                'severity_breakdown': alerts_data.get('severity_breakdown', {}),
                'alert_trends': self._get_alert_trends()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting alerts: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'active_only': active_only
            }
    
    async def trigger_optimization_cycle(self) -> Dict[str, Any]:
        """Manually trigger an optimization cycle"""
        try:
            self.logger.info("Manual optimization cycle triggered via web API")
            result = await self.controller.run_optimization_cycle()
            
            return {
                'timestamp': datetime.now().isoformat(),
                'status': 'success',
                'cycle_result': result,
                'message': f"Optimization cycle #{result.get('cycle_number', 'unknown')} completed"
            }
            
        except Exception as e:
            self.logger.error(f"Error triggering optimization cycle: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'status': 'error',
                'error': str(e),
                'message': 'Failed to trigger optimization cycle'
            }
    
    def update_configuration(self, config_updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update Phase 11 configuration via web interface"""
        try:
            self.logger.info(f"Configuration update requested via web API: {config_updates}")
            
            # Validate configuration updates
            valid_updates = self._validate_config_updates(config_updates)
            
            if valid_updates:
                self.controller.update_configuration(valid_updates)
                
                return {
                    'timestamp': datetime.now().isoformat(),
                    'status': 'success',
                    'updates_applied': valid_updates,
                    'message': 'Configuration updated successfully'
                }
            else:
                return {
                    'timestamp': datetime.now().isoformat(),
                    'status': 'error',
                    'error': 'No valid configuration updates provided',
                    'message': 'Configuration update failed'
                }
                
        except Exception as e:
            self.logger.error(f"Error updating configuration: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'status': 'error',
                'error': str(e),
                'message': 'Configuration update failed'
            }
    
    # Helper methods
    
    def _get_recent_alerts(self, limit: int = 10) -> List[Dict]:
        """Get recent alerts for dashboard display"""
        try:
            alerts_data = self.controller.dashboard.get_active_alerts()
            return alerts_data.get('alerts', [])[:limit]
        except:
            return []
    
    def _get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary statistics"""
        try:
            status = self.controller.get_system_status()
            return {
                'optimization_cycles': status.get('optimization_cycles', 0),
                'avg_cycle_time': status.get('avg_cycle_time', 0),
                'success_rate': status.get('success_rate', 0),
                'error_rate': status.get('error_rate', 0)
            }
        except:
            return {}
    
    def _categorize_events(self, events: List[Dict]) -> Dict[str, int]:
        """Categorize optimization events by type"""
        categories = {}
        for event in events:
            event_type = event.get('event_type', 'unknown')
            categories[event_type] = categories.get(event_type, 0) + 1
        return categories
    
    def _calculate_performance_trends(self, events: List[Dict]) -> Dict[str, Any]:
        """Calculate performance trends from events"""
        if not events:
            return {}
        
        # Simple trend calculation
        recent_events = events[:20]  # Last 20 events
        successful_events = len([e for e in recent_events if e.get('success', False)])
        
        return {
            'recent_success_rate': successful_events / len(recent_events) if recent_events else 0,
            'trend_direction': 'improving' if successful_events > len(recent_events) / 2 else 'declining',
            'total_events_analyzed': len(recent_events)
        }
    
    def _get_bot_performance_trends(self) -> Dict[str, Any]:
        """Get bot performance trend data"""
        # Placeholder - would implement actual trend analysis
        return {
            'trend_period': '24h',
            'improving_bots': [],
            'declining_bots': [],
            'stable_bots': []
        }
    
    def _generate_bot_performance_charts(self) -> Dict[str, Any]:
        """Generate chart data for bot performance visualization"""
        # Placeholder - would generate actual chart data
        return {
            'accuracy_chart': {'labels': [], 'data': []},
            'reliability_chart': {'labels': [], 'data': []},
            'performance_timeline': {'labels': [], 'data': []}
        }
    
    def _get_strategy_switching_history(self) -> List[Dict]:
        """Get strategy switching history"""
        # Placeholder - would implement actual history retrieval
        return []
    
    def _get_weight_evolution_data(self) -> Dict[str, Any]:
        """Get strategy weight evolution data for charts"""
        # Placeholder - would implement actual weight evolution tracking
        return {'labels': [], 'datasets': []}
    
    def _get_recent_anomalies(self, severity: str) -> List[Dict]:
        """Get recent anomalies filtered by severity"""
        # Placeholder - would implement actual anomaly retrieval
        return []
    
    def _calculate_anomaly_statistics(self) -> Dict[str, Any]:
        """Calculate anomaly detection statistics"""
        # Placeholder - would implement actual statistics calculation
        return {
            'total_anomalies_24h': 0,
            'anomaly_rate': 0,
            'most_common_type': 'none'
        }
    
    def _assess_anomaly_risks(self, patterns: Dict) -> Dict[str, Any]:
        """Assess risks based on anomaly patterns"""
        # Placeholder - would implement actual risk assessment
        return {
            'risk_level': 'low',
            'critical_patterns': [],
            'recommendations': []
        }
    
    def _get_alert_trends(self) -> Dict[str, Any]:
        """Get alert trend data"""
        # Placeholder - would implement actual trend analysis
        return {
            'trend_24h': 'stable',
            'alert_frequency': 0,
            'resolution_rate': 0
        }
    
    def _validate_config_updates(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Validate configuration updates"""
        valid_keys = [
            'optimization_interval_seconds',
            'enable_auto_switching',
            'enable_anomaly_detection',
            'enable_dashboard'
        ]
        
        return {k: v for k, v in updates.items() if k in valid_keys}

def create_web_dashboard_endpoints():
    """Create web dashboard endpoints for Phase 11 integration"""
    
    # This would be integrated with the existing Flask/FastAPI web application
    api = Phase11WebAPI()
    
    endpoints = {
        '/api/phase11/overview': api.get_system_overview,
        '/api/phase11/metrics': api.get_real_time_metrics,
        '/api/phase11/history': lambda: api.get_optimization_history(24),
        '/api/phase11/bots': api.get_bot_performance_data,
        '/api/phase11/strategies': api.get_strategy_analysis,
        '/api/phase11/anomalies': lambda: api.get_anomaly_reports("all"),
        '/api/phase11/alerts': lambda: api.get_alerts(True),
        '/api/phase11/optimize': api.trigger_optimization_cycle,
        '/api/phase11/config': api.update_configuration
    }
    
    return endpoints

def generate_dashboard_html():
    """Generate HTML template for Phase 11 dashboard integration"""
    
    html_template = """
<!-- Phase 11 Intelligent Optimization Dashboard -->
<div id="phase11-dashboard" class="container-fluid mt-4">
    <!-- System Overview Section -->
    <div class="row mb-4">
        <div class="col-12">
            <div class="card">
                <div class="card-header bg-primary text-white">
                    <h5 class="mb-0"><i class="fas fa-brain"></i> Phase 11 Intelligent Optimization</h5>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-3">
                            <div class="metric-card">
                                <h6>System Health</h6>
                                <span id="system-health-status" class="badge badge-success">Healthy</span>
                                <small id="active-components" class="text-muted d-block">5/5 Components Active</small>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="metric-card">
                                <h6>Optimization Cycles</h6>
                                <span id="cycle-count" class="h4">0</span>
                                <small id="last-cycle" class="text-muted d-block">Never</small>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="metric-card">
                                <h6>Efficiency Score</h6>
                                <span id="efficiency-score" class="h4">0%</span>
                                <small id="processing-rate" class="text-muted d-block">0 trades/sec</small>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="metric-card">
                                <h6>Active Alerts</h6>
                                <span id="alert-count" class="h4">0</span>
                                <button id="trigger-optimization" class="btn btn-sm btn-primary mt-2">
                                    <i class="fas fa-sync"></i> Optimize Now
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Component Status Section -->
    <div class="row mb-4">
        <div class="col-md-6">
            <div class="card">
                <div class="card-header">
                    <h6><i class="fas fa-cogs"></i> Component Status</h6>
                </div>
                <div class="card-body">
                    <div id="component-status-list">
                        <!-- Component status items will be populated here -->
                    </div>
                </div>
            </div>
        </div>
        <div class="col-md-6">
            <div class="card">
                <div class="card-header">
                    <h6><i class="fas fa-exclamation-triangle"></i> Recent Alerts</h6>
                </div>
                <div class="card-body">
                    <div id="recent-alerts-list">
                        <!-- Recent alerts will be populated here -->
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Performance Charts Section -->
    <div class="row mb-4">
        <div class="col-md-6">
            <div class="card">
                <div class="card-header">
                    <h6><i class="fas fa-chart-line"></i> Bot Performance</h6>
                </div>
                <div class="card-body">
                    <canvas id="bot-performance-chart"></canvas>
                </div>
            </div>
        </div>
        <div class="col-md-6">
            <div class="card">
                <div class="card-header">
                    <h6><i class="fas fa-exchange-alt"></i> Strategy Analysis</h6>
                </div>
                <div class="card-body">
                    <canvas id="strategy-analysis-chart"></canvas>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Optimization History Section -->
    <div class="row">
        <div class="col-12">
            <div class="card">
                <div class="card-header">
                    <h6><i class="fas fa-history"></i> Optimization History</h6>
                </div>
                <div class="card-body">
                    <div id="optimization-timeline">
                        <!-- Optimization timeline will be populated here -->
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
// Phase 11 Dashboard JavaScript
class Phase11Dashboard {
    constructor() {
        this.updateInterval = 30000; // 30 seconds
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.startAutoRefresh();
        this.loadInitialData();
    }
    
    setupEventListeners() {
        document.getElementById('trigger-optimization').addEventListener('click', () => {
            this.triggerOptimization();
        });
    }
    
    async loadInitialData() {
        await this.updateOverview();
        await this.updateComponentStatus();
        await this.updateAlerts();
        await this.updateCharts();
    }
    
    async updateOverview() {
        try {
            const response = await fetch('/api/phase11/overview');
            const data = await response.json();
            
            document.getElementById('system-health-status').textContent = data.system_health.status;
            document.getElementById('active-components').textContent = 
                `${data.system_health.active_components}/${data.system_health.total_components} Components Active`;
            document.getElementById('cycle-count').textContent = data.optimization_metrics.cycle_count;
            document.getElementById('last-cycle').textContent = data.optimization_metrics.last_cycle_time;
            document.getElementById('efficiency-score').textContent = 
                `${data.optimization_metrics.efficiency_score}%`;
            document.getElementById('alert-count').textContent = data.recent_alerts.length;
            
        } catch (error) {
            console.error('Error updating overview:', error);
        }
    }
    
    async updateComponentStatus() {
        try {
            const response = await fetch('/api/phase11/overview');
            const data = await response.json();
            
            const statusList = document.getElementById('component-status-list');
            statusList.innerHTML = '';
            
            Object.entries(data.component_status).forEach(([component, status]) => {
                const statusItem = document.createElement('div');
                statusItem.className = 'component-status-item mb-2';
                statusItem.innerHTML = `
                    <div class="d-flex justify-content-between align-items-center">
                        <span>${component.replace('_', ' ').toUpperCase()}</span>
                        <span class="badge badge-${status === 'active' ? 'success' : 'danger'}">${status}</span>
                    </div>
                `;
                statusList.appendChild(statusItem);
            });
            
        } catch (error) {
            console.error('Error updating component status:', error);
        }
    }
    
    async updateAlerts() {
        try {
            const response = await fetch('/api/phase11/alerts');
            const data = await response.json();
            
            const alertsList = document.getElementById('recent-alerts-list');
            alertsList.innerHTML = '';
            
            data.alerts.slice(0, 5).forEach(alert => {
                const alertItem = document.createElement('div');
                alertItem.className = 'alert-item mb-2';
                alertItem.innerHTML = `
                    <div class="d-flex justify-content-between align-items-start">
                        <div>
                            <span class="badge badge-${this.getSeverityClass(alert.severity)}">${alert.severity}</span>
                            <small class="d-block text-muted">${alert.message}</small>
                        </div>
                        <small class="text-muted">${new Date(alert.timestamp).toLocaleTimeString()}</small>
                    </div>
                `;
                alertsList.appendChild(alertItem);
            });
            
        } catch (error) {
            console.error('Error updating alerts:', error);
        }
    }
    
    async updateCharts() {
        try {
            const [botData, strategyData] = await Promise.all([
                fetch('/api/phase11/bots').then(r => r.json()),
                fetch('/api/phase11/strategies').then(r => r.json())
            ]);
            
            // Update bot performance chart
            this.updateBotChart(botData);
            
            // Update strategy analysis chart
            this.updateStrategyChart(strategyData);
            
        } catch (error) {
            console.error('Error updating charts:', error);
        }
    }
    
    updateBotChart(data) {
        // Implement bot performance chart using Chart.js
        // This would create a chart showing bot performance metrics
    }
    
    updateStrategyChart(data) {
        // Implement strategy analysis chart using Chart.js
        // This would show strategy weights and performance
    }
    
    async triggerOptimization() {
        try {
            const button = document.getElementById('trigger-optimization');
            button.disabled = true;
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Optimizing...';
            
            const response = await fetch('/api/phase11/optimize', { method: 'POST' });
            const result = await response.json();
            
            if (result.status === 'success') {
                this.showNotification('Optimization cycle completed successfully', 'success');
                await this.updateOverview();
            } else {
                this.showNotification('Optimization cycle failed: ' + result.error, 'error');
            }
            
        } catch (error) {
            this.showNotification('Error triggering optimization: ' + error.message, 'error');
        } finally {
            const button = document.getElementById('trigger-optimization');
            button.disabled = false;
            button.innerHTML = '<i class="fas fa-sync"></i> Optimize Now';
        }
    }
    
    getSeverityClass(severity) {
        const classes = {
            'low': 'info',
            'medium': 'warning',
            'high': 'danger',
            'critical': 'dark'
        };
        return classes[severity] || 'secondary';
    }
    
    showNotification(message, type) {
        // Implement notification system (could use toastr or similar)
        console.log(`${type.toUpperCase()}: ${message}`);
    }
    
    startAutoRefresh() {
        setInterval(() => {
            this.loadInitialData();
        }, this.updateInterval);
    }
}

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', () => {
    new Phase11Dashboard();
});
</script>

<style>
.metric-card {
    text-align: center;
    padding: 15px;
    border: 1px solid #e0e0e0;
    border-radius: 5px;
    background: #f8f9fa;
}

.component-status-item, .alert-item {
    padding: 8px;
    border: 1px solid #e0e0e0;
    border-radius: 3px;
    background: #ffffff;
}

#phase11-dashboard .card {
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

#phase11-dashboard .card-header {
    border-bottom: 2px solid #007bff;
}
</style>
"""
    
    return html_template

async def test_web_integration():
    """Test the web integration functionality"""
    print("🌐 Testing Phase 11 Web Integration...")
    
    try:
        # Initialize API
        api = Phase11WebAPI()
        
        # Test all endpoints
        endpoints_to_test = [
            ('System Overview', api.get_system_overview),
            ('Real-time Metrics', api.get_real_time_metrics),
            ('Optimization History', lambda: api.get_optimization_history(1)),
            ('Bot Performance', api.get_bot_performance_data),
            ('Strategy Analysis', api.get_strategy_analysis),
            ('Anomaly Reports', lambda: api.get_anomaly_reports("all")),
            ('Alerts', lambda: api.get_alerts(True))
        ]
        
        test_results = []
        
        for name, endpoint in endpoints_to_test:
            try:
                if asyncio.iscoroutinefunction(endpoint):
                    result = await endpoint()
                else:
                    result = endpoint()
                
                if isinstance(result, dict) and 'error' not in result:
                    test_results.append((name, True, "Success"))
                    print(f"   ✅ {name}: Working")
                else:
                    test_results.append((name, False, result.get('error', 'Unknown error')))
                    print(f"   ❌ {name}: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                test_results.append((name, False, str(e)))
                print(f"   ❌ {name}: {e}")
        
        # Test optimization trigger
        try:
            optimization_result = await api.trigger_optimization_cycle()
            if optimization_result.get('status') == 'success':
                print("   ✅ Manual Optimization Trigger: Working")
                test_results.append(("Manual Optimization", True, "Success"))
            else:
                print(f"   ❌ Manual Optimization Trigger: {optimization_result.get('error', 'Failed')}")
                test_results.append(("Manual Optimization", False, optimization_result.get('error', 'Failed')))
        except Exception as e:
            print(f"   ❌ Manual Optimization Trigger: {e}")
            test_results.append(("Manual Optimization", False, str(e)))
        
        # Summary
        successful_tests = len([r for r in test_results if r[1]])
        total_tests = len(test_results)
        
        print(f"\n📊 Web Integration Test Results: {successful_tests}/{total_tests} passed")
        
        if successful_tests == total_tests:
            print("🎉 All web integration tests passed!")
            return True
        else:
            print("⚠️  Some web integration tests failed")
            return False
            
    except Exception as e:
        print(f"❌ Web integration test failed: {e}")
        return False

if __name__ == "__main__":
    print("TradeMasterX 2.0 - Phase 11 Web Dashboard Integration")
    print("Select action:")
    print("1. Test Web Integration")
    print("2. Generate Dashboard HTML")
    print("3. Create API Endpoints")
    
    choice = input("\nEnter choice (1-3): ").strip() or "1"
    
    if choice == "1":
        success = asyncio.run(test_web_integration())
        print(f"\nResult: {'✅ Integration Ready' if success else '❌ Integration Issues'}")
    elif choice == "2":
        html = generate_dashboard_html()
        output_file = Path("phase_11_dashboard_template.html")
        with open(output_file, 'w') as f:
            f.write(html)
        print(f"✅ Dashboard HTML template saved to {output_file}")
    elif choice == "3":
        endpoints = create_web_dashboard_endpoints()
        print(f"✅ Created {len(endpoints)} API endpoints for Phase 11 integration")
        for endpoint in endpoints.keys():
            print(f"   - {endpoint}")
    else:
        print("Invalid choice")
