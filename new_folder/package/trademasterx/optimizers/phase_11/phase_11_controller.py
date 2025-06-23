"""
TradeMasterX 2.0 - Phase 11: Intelligent Optimization Controller
Main controller that integrates all Phase 11 components for self-improving intelligence
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List
import time

from .adaptive_strategy_reinforcer import AdaptiveStrategyReinforcer
from .bot_performance_scorer import BotPerformanceScorer
from .strategy_switcher import StrategySwitcher
from .anomaly_detector import AnomalyDetector
from .live_optimization_dashboard import LiveOptimizationDashboard

class Phase11Controller:
    """
    Main controller for Phase 11 Intelligent Optimization
    
    Orchestrates all self-improving intelligence components:
    - AdaptiveStrategyReinforcer: Analyzes and adjusts strategy weights
    - BotPerformanceScorer: Tracks individual bot performance
    - StrategySwitcher: Auto-switches underperforming strategies
    - AnomalyDetector: Identifies outlier trades
    - LiveOptimizationDashboard: Real-time performance monitoring
    """
    
    def __init__(self, data_dir: str = "reports", logs_dir: str = "logs"):
        self.data_dir = Path(data_dir)
        self.logs_dir = Path(logs_dir)
        
        # Ensure directories exist
        self.data_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)        # Initialize all Phase 11 components with proper parameters
        self.strategy_reinforcer = AdaptiveStrategyReinforcer(str(self.data_dir / "adaptive_weights.yaml"))
        self.bot_scorer = BotPerformanceScorer({'data_dir': str(self.data_dir)})
        self.strategy_switcher = StrategySwitcher({'data_dir': str(self.data_dir)})
        self.anomaly_detector = AnomalyDetector({'data_dir': str(self.logs_dir)})
        self.dashboard = LiveOptimizationDashboard(str(self.data_dir), str(self.logs_dir))
        
        # Controller state
        self.is_running = False
        self.optimization_cycle_count = 0
        self.last_optimization_time = None
        
        # Configuration
        self.config = {
            'optimization_interval_seconds': 300,  # 5 minutes
            'dashboard_update_interval_seconds': 60,  # 1 minute
            'anomaly_check_interval_seconds': 30,  # 30 seconds
            'strategy_evaluation_interval_seconds': 600,  # 10 minutes
            'bot_scoring_interval_seconds': 180,  # 3 minutes
            'max_optimization_cycles': None,  # No limit
            'enable_auto_switching': True,
            'enable_anomaly_detection': True,
            'enable_dashboard': True
        }
        
        # Setup logging
        self.logger = self._setup_logging()
        
        self.logger.info("Phase 11 Intelligent Optimization Controller initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup controller logging"""
        logger = logging.getLogger("Phase11Controller")
        logger.setLevel(logging.INFO)
        
        # Create file handler
        log_file = self.logs_dir / "phase_11_controller.log"
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
    
    def update_configuration(self, config_updates: Dict[str, Any]):
        """Update controller configuration"""
        self.config.update(config_updates)
        self.logger.info(f"Configuration updated: {config_updates}")
    
    async def process_trade_result(self, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single trade result through all Phase 11 components
        
        Args:
            trade_data: Trade result data including:
                - symbol, signal, confidence, expected_return, actual_return
                - bot_id, strategy_id, timestamp, position_size, etc.
        
        Returns:
            Dict containing optimization results from all components
        """
        try:
            start_time = time.time()
            results = {
                'timestamp': datetime.now().isoformat(),
                'trade_id': trade_data.get('trade_id', f"trade_{int(time.time())}"),
                'optimization_results': {}
            }
            
            # 1. Strategy Reinforcement
            try:
                strategy_result = self.strategy_reinforcer.analyze_trade_outcome(trade_data)
                results['optimization_results']['strategy_reinforcement'] = strategy_result
                
                # Log optimization event in dashboard
                if strategy_result.get('weight_adjusted'):
                    self.dashboard.log_optimization_event(
                        'strategy_adjustment',
                        'AdaptiveStrategyReinforcer',
                        f"Strategy {trade_data.get('strategy_id', 'unknown')} weight adjusted",
                        strategy_result.get('before_weights', {}),
                        strategy_result.get('after_weights', {}),
                        True
                    )
            except Exception as e:
                self.logger.error(f"Strategy reinforcement error: {e}")
                results['optimization_results']['strategy_reinforcement'] = {'error': str(e)}
            
            # 2. Bot Performance Scoring
            try:
                scoring_result = self.bot_scorer.score_prediction(
                    trade_data.get('bot_id', 'unknown'),
                    trade_data.get('confidence', 0.5),
                    trade_data.get('expected_return', 0),
                    trade_data.get('actual_return', 0),
                    trade_data.get('timestamp', datetime.now().isoformat())
                )
                results['optimization_results']['bot_scoring'] = scoring_result
            except Exception as e:
                self.logger.error(f"Bot scoring error: {e}")
                results['optimization_results']['bot_scoring'] = {'error': str(e)}
            
            # 3. Anomaly Detection
            try:
                anomaly_result = self.anomaly_detector.detect_trade_anomaly(trade_data)
                results['optimization_results']['anomaly_detection'] = anomaly_result
                
                # Log anomaly events in dashboard
                if anomaly_result.get('is_anomaly'):
                    self.dashboard.log_optimization_event(
                        'anomaly_detected',
                        'AnomalyDetector',
                        f"Anomaly detected: {anomaly_result.get('anomaly_type', 'unknown')}",
                        {'normal_range': anomaly_result.get('baseline', {})},
                        {'detected_value': anomaly_result.get('detected_value', {})},
                        True
                    )
            except Exception as e:
                self.logger.error(f"Anomaly detection error: {e}")
                results['optimization_results']['anomaly_detection'] = {'error': str(e)}
            
            # 4. Strategy Switching Evaluation (less frequent)
            try:
                if self.config['enable_auto_switching']:
                    switch_result = self.strategy_switcher.evaluate_current_strategy(
                        trade_data.get('strategy_id', 'unknown'),
                        trade_data.get('actual_return', 0)
                    )
                    results['optimization_results']['strategy_switching'] = switch_result
                    
                    # Log strategy switches in dashboard
                    if switch_result.get('switch_recommended') or switch_result.get('switched'):
                        self.dashboard.log_optimization_event(
                            'strategy_switch',
                            'StrategySwitcher',
                            f"Strategy switch: {switch_result.get('reason', 'performance')}",
                            {'old_strategy': switch_result.get('old_strategy', {})},
                            {'new_strategy': switch_result.get('new_strategy', {})},
                            switch_result.get('switched', False)
                        )
                else:
                    results['optimization_results']['strategy_switching'] = {'disabled': True}
            except Exception as e:
                self.logger.error(f"Strategy switching error: {e}")
                results['optimization_results']['strategy_switching'] = {'error': str(e)}
            
            # Record processing time
            processing_time = time.time() - start_time
            results['processing_time_seconds'] = processing_time
            
            self.logger.debug(f"Trade processed in {processing_time:.3f}s: {trade_data.get('trade_id', 'unknown')}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error processing trade result: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'trade_id': trade_data.get('trade_id', 'unknown'),
                'error': str(e),
                'optimization_results': {}
            }
    
    async def run_optimization_cycle(self) -> Dict[str, Any]:
        """
        Run a complete optimization cycle across all components
        
        Returns:
            Dict containing cycle results and updated metrics
        """
        try:
            cycle_start = time.time()
            self.optimization_cycle_count += 1
            
            self.logger.info(f"Starting optimization cycle #{self.optimization_cycle_count}")
            
            cycle_results = {
                'cycle_number': self.optimization_cycle_count,
                'timestamp': datetime.now().isoformat(),
                'component_results': {}
            }
            
            # 1. Update bot rankings and performance scores
            try:
                bot_rankings = self.bot_scorer.rank_bots()
                cycle_results['component_results']['bot_rankings'] = {
                    'updated': True,
                    'top_bots': bot_rankings[:5] if bot_rankings else [],
                    'total_bots': len(bot_rankings)
                }
            except Exception as e:
                self.logger.error(f"Bot ranking error: {e}")
                cycle_results['component_results']['bot_rankings'] = {'error': str(e)}
            
            # 2. Evaluate all strategies and recommend switches
            try:
                strategy_evaluation = self.strategy_switcher.evaluate_all_strategies()
                cycle_results['component_results']['strategy_evaluation'] = strategy_evaluation
            except Exception as e:
                self.logger.error(f"Strategy evaluation error: {e}")
                cycle_results['component_results']['strategy_evaluation'] = {'error': str(e)}
            
            # 3. Analyze anomaly patterns
            try:
                pattern_analysis = self.anomaly_detector.analyze_patterns()
                cycle_results['component_results']['anomaly_patterns'] = pattern_analysis
            except Exception as e:
                self.logger.error(f"Anomaly pattern analysis error: {e}")
                cycle_results['component_results']['anomaly_patterns'] = {'error': str(e)}
            
            # 4. Update adaptive strategy weights
            try:
                reinforcement_update = self.strategy_reinforcer.update_all_strategies()
                cycle_results['component_results']['strategy_reinforcement'] = reinforcement_update
            except Exception as e:
                self.logger.error(f"Strategy reinforcement error: {e}")
                cycle_results['component_results']['strategy_reinforcement'] = {'error': str(e)}
            
            # 5. Update dashboard metrics
            try:
                if self.config['enable_dashboard']:
                    dashboard_metrics = await self._update_dashboard_metrics()
                    cycle_results['component_results']['dashboard_update'] = {
                        'updated': True,
                        'metrics_summary': {
                            'system_health': dashboard_metrics.system_health_score,
                            'optimization_efficiency': dashboard_metrics.optimization_efficiency,
                            'active_alerts': dashboard_metrics.alerts_count
                        }
                    }
                else:
                    cycle_results['component_results']['dashboard_update'] = {'disabled': True}
            except Exception as e:
                self.logger.error(f"Dashboard update error: {e}")
                cycle_results['component_results']['dashboard_update'] = {'error': str(e)}
            
            # Calculate cycle performance
            cycle_time = time.time() - cycle_start
            cycle_results['cycle_time_seconds'] = cycle_time
            cycle_results['cycle_efficiency'] = min(100, (1 / max(cycle_time, 0.1)) * 10)  # Efficiency score
            
            self.last_optimization_time = datetime.now()
            
            self.logger.info(f"Optimization cycle #{self.optimization_cycle_count} completed in {cycle_time:.2f}s")
            
            return cycle_results
            
        except Exception as e:
            self.logger.error(f"Error in optimization cycle: {e}")
            return {
                'cycle_number': self.optimization_cycle_count,
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'component_results': {}
            }
    
    async def _update_dashboard_metrics(self):
        """Update dashboard with latest metrics from all components"""
        try:
            # Collect metrics from all components
            bot_metrics = self.bot_scorer.get_performance_summary()
            strategy_metrics = self.strategy_switcher.get_switching_statistics()
            anomaly_metrics = self.anomaly_detector.get_anomaly_statistics()
            
            # System metrics (would come from main trading system)
            system_metrics = {
                'trades_per_hour': 12.0,  # Mock data
                'avg_confidence': 0.75,
                'win_rate': 0.68,
                'total_return': 0.045
            }
            
            # Update dashboard
            dashboard_metrics = self.dashboard.update_metrics(
                bot_metrics, strategy_metrics, anomaly_metrics, system_metrics
            )
            
            return dashboard_metrics
            
        except Exception as e:
            self.logger.error(f"Error updating dashboard metrics: {e}")
            return None
    
    async def start_continuous_optimization(self):
        """Start continuous optimization loop"""
        if self.is_running:
            self.logger.warning("Optimization already running")
            return
        
        self.is_running = True
        self.logger.info("Starting continuous Phase 11 optimization")
        
        # Start dashboard monitoring if enabled
        dashboard_task = None
        if self.config['enable_dashboard']:
            dashboard_task = asyncio.create_task(
                self.dashboard.start_real_time_monitoring(
                    self.config['dashboard_update_interval_seconds']
                )
            )
        
        try:
            while self.is_running:
                cycle_start_time = time.time()
                
                # Run optimization cycle
                cycle_results = await self.run_optimization_cycle()
                
                # Check if we've reached max cycles
                if (self.config['max_optimization_cycles'] and 
                    self.optimization_cycle_count >= self.config['max_optimization_cycles']):
                    self.logger.info(f"Reached maximum optimization cycles: {self.config['max_optimization_cycles']}")
                    break
                
                # Calculate sleep time to maintain interval
                cycle_time = time.time() - cycle_start_time
                sleep_time = max(0, self.config['optimization_interval_seconds'] - cycle_time)
                
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
                else:
                    self.logger.warning(f"Optimization cycle took longer than interval: {cycle_time:.2f}s")
                
        except Exception as e:
            self.logger.error(f"Error in continuous optimization: {e}")
        finally:
            self.is_running = False
            if dashboard_task:
                dashboard_task.cancel()
            self.logger.info("Continuous optimization stopped")
    
    def stop_optimization(self):
        """Stop continuous optimization"""
        self.is_running = False
        self.logger.info("Optimization stop requested")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall Phase 11 system status"""
        return {
            'timestamp': datetime.now().isoformat(),
            'is_running': self.is_running,
            'optimization_cycles_completed': self.optimization_cycle_count,
            'last_optimization_time': self.last_optimization_time.isoformat() if self.last_optimization_time else None,
            'configuration': self.config,
            'component_status': {
                'strategy_reinforcer': 'active',
                'bot_scorer': 'active',
                'strategy_switcher': 'active' if self.config['enable_auto_switching'] else 'disabled',
                'anomaly_detector': 'active' if self.config['enable_anomaly_detection'] else 'disabled',
                'dashboard': 'active' if self.config['enable_dashboard'] else 'disabled'
            },
            'dashboard_summary': self.dashboard.get_dashboard_summary() if self.config['enable_dashboard'] else None
        }
    
    def get_optimization_report(self) -> Dict[str, Any]:
        """Generate comprehensive optimization report"""
        try:            # Collect reports from all components
            bot_report = self.bot_scorer.generate_performance_report()
            strategy_report = self.strategy_switcher.generate_switching_report()
            anomaly_report = self.anomaly_detector.generate_anomaly_report()
            dashboard_summary = self.dashboard.get_dashboard_summary()
            
            return {
                'report_timestamp': datetime.now().isoformat(),
                'report_period': '24_hours',
                'system_overview': {
                    'optimization_cycles': self.optimization_cycle_count,
                    'system_health': dashboard_summary.get('system_health', {}) if dashboard_summary else {},
                    'optimization_efficiency': dashboard_summary.get('optimization', {}) if dashboard_summary else {}
                },
                'bot_performance': bot_report,
                'strategy_analysis': strategy_report,
                'anomaly_analysis': anomaly_report,
                'dashboard_metrics': dashboard_summary,
                'recommendations': self._generate_recommendations(bot_report, strategy_report, anomaly_report)
            }
            
        except Exception as e:
            self.logger.error(f"Error generating optimization report: {e}")
            return {
                'report_timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def _generate_recommendations(self, bot_report: Dict, strategy_report: Dict, anomaly_report: Dict) -> List[str]:
        """Generate optimization recommendations based on component reports"""
        recommendations = []
        
        try:
            # Bot recommendations
            if bot_report.get('avg_reliability', 0) < 0.6:
                recommendations.append("Consider retraining or replacing low-performing bots")
            
            if bot_report.get('active_bots', 0) < bot_report.get('total_bots', 1) * 0.8:
                recommendations.append("Investigate and restart inactive bots")
            
            # Strategy recommendations
            if strategy_report.get('switch_success_rate', 0) < 0.6:
                recommendations.append("Review strategy switching thresholds and criteria")
            
            if strategy_report.get('switches_24h', 0) > 10:
                recommendations.append("Strategy switching may be too frequent - consider increasing cooldown")
            
            # Anomaly recommendations
            if anomaly_report.get('critical_anomalies_24h', 0) > 5:
                recommendations.append("High number of critical anomalies detected - review system stability")
            
            if anomaly_report.get('recurring_patterns', 0) > 3:
                recommendations.append("Recurring anomaly patterns detected - investigate root causes")
            
            # General recommendations
            if not recommendations:
                recommendations.append("System performing well - continue monitoring")
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")
            recommendations.append("Error generating recommendations - manual review required")
        
        return recommendations

    async def integrate_with_phase10(self, phase10_optimizer):
        """
        Integration method for Phase 10 optimizer
        
        This method would be called by the Phase 10 system to integrate
        Phase 11 intelligent optimization capabilities
        """
        try:
            self.logger.info("Integrating Phase 11 with Phase 10 optimizer")
            
            # Get Phase 10 metrics and trade data
            phase10_metrics = phase10_optimizer.get_system_metrics()
            recent_trades = phase10_optimizer.get_recent_trades(limit=100)
            
            # Process recent trades through Phase 11
            for trade in recent_trades:
                await self.process_trade_result(trade)
            
            # Run optimization cycle
            optimization_results = await self.run_optimization_cycle()
            
            # Provide recommendations back to Phase 10
            recommendations = self._generate_phase10_recommendations(optimization_results)
            
            return {
                'integration_status': 'success',
                'optimization_results': optimization_results,
                'recommendations': recommendations,
                'phase11_metrics': self.get_system_status()
            }
            
        except Exception as e:
            self.logger.error(f"Error integrating with Phase 10: {e}")
            return {
                'integration_status': 'error',
                'error': str(e)
            }
    
    def _generate_phase10_recommendations(self, optimization_results: Dict) -> Dict[str, Any]:
        """Generate specific recommendations for Phase 10 integration"""
        recommendations = {
            'bot_adjustments': [],
            'strategy_changes': [],
            'risk_alerts': [],
            'system_optimizations': []
        }
        
        try:
            # Bot recommendations
            bot_results = optimization_results.get('component_results', {}).get('bot_rankings', {})
            if bot_results.get('top_bots'):
                recommendations['bot_adjustments'].append({
                    'action': 'increase_weight',
                    'targets': bot_results['top_bots'][:3],
                    'reason': 'High performance bots identified'
                })
            
            # Strategy recommendations
            strategy_results = optimization_results.get('component_results', {}).get('strategy_evaluation', {})
            if strategy_results.get('recommended_switches'):
                recommendations['strategy_changes'].append({
                    'action': 'switch_strategy',
                    'details': strategy_results['recommended_switches'],
                    'reason': 'Underperforming strategies detected'
                })
            
            # Risk alerts
            anomaly_results = optimization_results.get('component_results', {}).get('anomaly_patterns', {})
            if anomaly_results.get('critical_patterns'):
                recommendations['risk_alerts'].append({
                    'alert_level': 'high',
                    'patterns': anomaly_results['critical_patterns'],
                    'action': 'increase_monitoring'
                })
            
        except Exception as e:
            self.logger.error(f"Error generating Phase 10 recommendations: {e}")
        
        return recommendations
