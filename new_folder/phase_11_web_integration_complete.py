"""
TradeMasterX 2.0 - Phase 11 Web Dashboard Integration
Integrates Phase 11 intelligent optimization with the existing web interface
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional
import sys

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from trademasterx.optimizers.phase_11.phase_11_controller import Phase11Controller
from trademasterx.optimizers.phase_11.config import Phase11Config, PRODUCTION_CONFIG

class Phase11WebIntegration:
    """
    Web integration layer for Phase 11 Intelligent Optimization
    
    Provides REST API endpoints and WebSocket connections for the web dashboard
    to display Phase 11 metrics, alerts, and optimization status in real-time
    """
    
    def __init__(self, web_port: int = 8080, websocket_port: int = 8765):
        self.web_port = web_port
        self.websocket_port = websocket_port
        
        # Initialize Phase 11 controller
        self.controller = Phase11Controller()
        
        # Configure for production
        prod_config = PRODUCTION_CONFIG.to_dict()
        prod_config.update({
            'dashboard_port': websocket_port,
            'web_dashboard_integration': True
        })
        self.controller.update_configuration(prod_config)
        
        self.logger = self._setup_logging()
        self.is_running = False
        
        # Web interface data cache
        self.web_cache = {
            'last_update': None,
            'system_status': {},
            'optimization_metrics': {},
            'recent_alerts': [],
            'performance_summary': {}
        }
    
    def _setup_logging(self):
        """Setup web integration logging"""
        logger = logging.getLogger("Phase11WebIntegration")
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        
        if not logger.handlers:
            logger.addHandler(handler)
        
        return logger
    
    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data for web interface"""
        try:
            # Get system status
            system_status = self.controller.get_system_status()
            
            # Get dashboard summary
            dashboard_summary = self.controller.dashboard.get_dashboard_summary()
            
            # Get optimization report
            optimization_report = self.controller.get_optimization_report()
            
            # Compile dashboard data
            dashboard_data = {
                'timestamp': datetime.now().isoformat(),
                'phase_11_status': {
                    'is_active': system_status['is_running'],
                    'optimization_cycles': system_status['optimization_cycles_completed'],
                    'last_optimization': system_status['last_optimization_time'],
                    'components_active': len([k for k, v in system_status['component_status'].items() if v == 'active'])
                },
                'system_health': {
                    'overall_score': dashboard_summary.get('system_health', {}).get('score', 0) if dashboard_summary else 0,
                    'optimization_efficiency': dashboard_summary.get('optimization', {}).get('efficiency_score', 0) if dashboard_summary else 0,
                    'memory_usage': dashboard_summary.get('system', {}).get('memory_usage_mb', 0) if dashboard_summary else 0,
                    'cpu_usage': dashboard_summary.get('system', {}).get('cpu_usage_percent', 0) if dashboard_summary else 0
                },
                'performance_metrics': {
                    'total_trades_processed': dashboard_summary.get('trading', {}).get('total_trades', 0) if dashboard_summary else 0,
                    'avg_processing_time': dashboard_summary.get('optimization', {}).get('avg_processing_time', 0) if dashboard_summary else 0,
                    'success_rate': dashboard_summary.get('trading', {}).get('optimization_success_rate', 0) if dashboard_summary else 0,
                    'anomalies_detected': dashboard_summary.get('anomalies', {}).get('total_24h', 0) if dashboard_summary else 0
                },
                'bot_performance': self._format_bot_performance(optimization_report.get('bot_performance', {})),
                'strategy_analysis': self._format_strategy_analysis(optimization_report.get('strategy_analysis', {})),
                'recent_alerts': self._get_recent_alerts(),
                'recommendations': optimization_report.get('recommendations', [])[:5],  # Top 5
                'charts_data': await self._generate_charts_data()
            }
            
            # Update cache
            self.web_cache.update({
                'last_update': datetime.now().isoformat(),
                'dashboard_data': dashboard_data
            })
            
            return dashboard_data
            
        except Exception as e:
            self.logger.error(f"Error getting dashboard data: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'phase_11_status': {'is_active': False}
            }
    
    def _format_bot_performance(self, bot_performance: Dict) -> Dict[str, Any]:
        """Format bot performance data for web display"""
        if not bot_performance:
            return {'bots': [], 'summary': {}}
        
        return {
            'summary': {
                'total_bots': bot_performance.get('total_bots', 0),
                'active_bots': bot_performance.get('active_bots', 0),
                'avg_reliability': bot_performance.get('avg_reliability', 0),
                'top_performer': bot_performance.get('top_bot_id', 'None')
            },
            'top_bots': bot_performance.get('top_performers', [])[:10],  # Top 10
            'performance_trends': bot_performance.get('performance_trends', {}),
            'reliability_distribution': bot_performance.get('reliability_distribution', {})
        }
    
    def _format_strategy_analysis(self, strategy_analysis: Dict) -> Dict[str, Any]:
        """Format strategy analysis for web display"""
        if not strategy_analysis:
            return {'strategies': [], 'summary': {}}
        
        return {
            'summary': {
                'total_strategies': strategy_analysis.get('total_strategies', 0),
                'switches_24h': strategy_analysis.get('switches_24h', 0),
                'switch_success_rate': strategy_analysis.get('switch_success_rate', 0),
                'best_strategy': strategy_analysis.get('best_strategy_id', 'None')
            },
            'strategy_performance': strategy_analysis.get('strategy_performance', {}),
            'switching_history': strategy_analysis.get('recent_switches', [])[:10],  # Recent 10
            'performance_comparison': strategy_analysis.get('performance_comparison', {})
        }
    
    def _get_recent_alerts(self) -> list:
        """Get recent alerts for web display"""
        try:
            dashboard_summary = self.controller.dashboard.get_dashboard_summary()
            if not dashboard_summary or 'alerts' not in dashboard_summary:
                return []
            
            alerts = dashboard_summary['alerts'].get('recent', [])
            
            # Format alerts for web
            formatted_alerts = []
            for alert in alerts[:20]:  # Latest 20
                formatted_alerts.append({
                    'id': alert.get('id', 'unknown'),
                    'type': alert.get('type', 'info'),
                    'message': alert.get('message', 'No message'),
                    'timestamp': alert.get('timestamp', datetime.now().isoformat()),
                    'severity': alert.get('severity', 'info'),
                    'component': alert.get('component', 'system'),
                    'is_resolved': alert.get('resolved', False)
                })
            
            return formatted_alerts
            
        except Exception as e:
            self.logger.error(f"Error getting recent alerts: {e}")
            return []
    
    async def _generate_charts_data(self) -> Dict[str, Any]:
        """Generate chart data for web dashboard"""
        try:
            # Performance trends over time
            dashboard_summary = self.controller.dashboard.get_dashboard_summary()
            
            if not dashboard_summary:
                return {}
            
            charts_data = {
                'performance_timeline': {
                    'labels': [],
                    'datasets': [
                        {
                            'label': 'System Health',
                            'data': [],
                            'borderColor': 'rgb(75, 192, 192)',
                            'backgroundColor': 'rgba(75, 192, 192, 0.2)'
                        },
                        {
                            'label': 'Optimization Efficiency',
                            'data': [],
                            'borderColor': 'rgb(255, 99, 132)',
                            'backgroundColor': 'rgba(255, 99, 132, 0.2)'
                        }
                    ]
                },
                'bot_performance_pie': {
                    'labels': ['High Performance', 'Medium Performance', 'Low Performance'],
                    'datasets': [{
                        'data': [40, 35, 25],  # Mock data - would be calculated from actual bot performance
                        'backgroundColor': ['#28a745', '#ffc107', '#dc3545']
                    }]
                },
                'anomaly_trends': {
                    'labels': [],
                    'data': [],
                    'backgroundColor': 'rgba(220, 53, 69, 0.8)'
                },
                'strategy_performance': {
                    'labels': [],
                    'datasets': [{
                        'label': 'Strategy Success Rate',
                        'data': [],
                        'backgroundColor': [
                            '#007bff', '#28a745', '#ffc107', '#dc3545', '#6f42c1'
                        ]
                    }]
                }
            }
            
            # Mock time series data (in production, this would come from actual metrics)
            now = datetime.now()
            for i in range(24):  # Last 24 hours
                time_label = (now - timedelta(hours=23-i)).strftime('%H:%M')
                charts_data['performance_timeline']['labels'].append(time_label)
                charts_data['performance_timeline']['datasets'][0]['data'].append(
                    dashboard_summary.get('system_health', {}).get('score', 0)
                )
                charts_data['performance_timeline']['datasets'][1]['data'].append(
                    dashboard_summary.get('optimization', {}).get('efficiency_score', 0)
                )
            
            return charts_data
            
        except Exception as e:
            self.logger.error(f"Error generating charts data: {e}")
            return {}
    
    async def handle_web_request(self, endpoint: str, params: Dict = None) -> Dict[str, Any]:
        """Handle web dashboard API requests"""
        try:
            if endpoint == '/api/phase11/status':
                return await self.get_dashboard_data()
            
            elif endpoint == '/api/phase11/start':
                if not self.controller.is_running:
                    asyncio.create_task(self.controller.start_continuous_optimization())
                    return {'status': 'started', 'message': 'Phase 11 optimization started'}
                else:
                    return {'status': 'already_running', 'message': 'Phase 11 already running'}
            
            elif endpoint == '/api/phase11/stop':
                self.controller.stop_optimization()
                return {'status': 'stopped', 'message': 'Phase 11 optimization stopped'}
            
            elif endpoint == '/api/phase11/report':
                report = self.controller.get_optimization_report()
                return {'status': 'success', 'report': report}
            
            elif endpoint == '/api/phase11/config':
                if params and 'update' in params:
                    # Update configuration
                    self.controller.update_configuration(params['update'])
                    return {'status': 'updated', 'message': 'Configuration updated'}
                else:
                    # Get current configuration
                    status = self.controller.get_system_status()
                    return {'status': 'success', 'config': status['configuration']}
            
            elif endpoint == '/api/phase11/alerts':
                alerts = self._get_recent_alerts()
                return {'status': 'success', 'alerts': alerts}
            
            else:
                return {'status': 'error', 'message': f'Unknown endpoint: {endpoint}'}
                
        except Exception as e:
            self.logger.error(f"Error handling web request {endpoint}: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def start_web_integration(self):
        """Start the web integration service"""
        if self.is_running:
            self.logger.warning("Web integration already running")
            return
        
        self.is_running = True
        self.logger.info(f"Starting Phase 11 web integration on port {self.web_port}")
        
        try:
            # Start Phase 11 dashboard WebSocket server
            if self.controller.config['enable_dashboard']:
                dashboard_task = asyncio.create_task(
                    self.controller.dashboard.start_real_time_monitoring()
                )
                self.logger.info(f"Phase 11 dashboard WebSocket running on port {self.websocket_port}")
            
            # Web integration monitoring loop
            while self.is_running:
                try:
                    # Update web cache periodically
                    await self.get_dashboard_data()
                    await asyncio.sleep(30)  # Update every 30 seconds
                    
                except Exception as e:
                    self.logger.error(f"Error in web integration loop: {e}")
                    await asyncio.sleep(5)
            
        except Exception as e:
            self.logger.error(f"Error in web integration: {e}")
        finally:
            self.is_running = False
            self.logger.info("Phase 11 web integration stopped")
    
    def stop_web_integration(self):
        """Stop the web integration service"""
        self.is_running = False
        self.controller.stop_optimization()
        self.logger.info("Stopping Phase 11 web integration")
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Get web integration status"""
        return {
            'timestamp': datetime.now().isoformat(),
            'web_integration_running': self.is_running,
            'web_port': self.web_port,
            'websocket_port': self.websocket_port,
            'phase11_status': self.controller.get_system_status(),
            'cache_last_update': self.web_cache.get('last_update'),
            'recent_alerts_count': len(self._get_recent_alerts())
        }

# Flask web application integration (optional)
def create_flask_integration(phase11_integration: Phase11WebIntegration):
    """Create Flask web application with Phase 11 integration"""
    try:
        from flask import Flask, jsonify, request, render_template
        from flask_socketio import SocketIO, emit
        
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'phase11_secret_key'
        socketio = SocketIO(app, cors_allowed_origins="*")
        
        @app.route('/api/phase11/status')
        async def api_status():
            data = await phase11_integration.get_dashboard_data()
            return jsonify(data)
        
        @app.route('/api/phase11/<endpoint>')
        async def api_endpoint(endpoint):
            params = request.get_json() if request.is_json else request.args.to_dict()
            result = await phase11_integration.handle_web_request(f'/api/phase11/{endpoint}', params)
            return jsonify(result)
        
        @app.route('/phase11/dashboard')
        def dashboard():
            return render_template('phase11_dashboard.html')
        
        @socketio.on('connect')
        def handle_connect():
            emit('status', {'message': 'Connected to Phase 11 real-time updates'})
        
        @socketio.on('request_update')
        async def handle_update_request():
            data = await phase11_integration.get_dashboard_data()
            emit('dashboard_update', data)
        
        return app, socketio
        
    except ImportError:
        print("Flask not available. Install with: pip install flask flask-socketio")
        return None, None

async def main():
    """Main web integration execution"""
    print("TradeMasterX 2.0 - Phase 11 Web Integration")
    print("=" * 50)
    
    # Initialize web integration
    web_integration = Phase11WebIntegration()
    
    try:
        # Start web integration
        print("🌐 Starting Phase 11 web integration...")
        await web_integration.start_web_integration()
        
    except KeyboardInterrupt:
        print("\n🛑 Stopping web integration...")
        web_integration.stop_web_integration()
    except Exception as e:
        print(f"💥 Web integration error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
