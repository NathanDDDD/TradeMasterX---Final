#!/usr/bin/env python3
"""
TradeMasterX 2.0 - Phase 10 Direct Learning Controller
Simplified controller for running Phase 10 learning loop without complex dependencies
"""

import asyncio
import logging
import time
import json
import csv
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional

class Phase10LearningController:
    """
    Simplified controller for Phase 10 mainnet demo learning loop
    """
    
    def __init__(self, config: Dict[str, Any], bot_registry=None):
        self.config = config
        self.bot_registry = bot_registry
        self.logger = logging.getLogger("Phase10Learning")
        
        # Learning parameters
        self.trade_frequency = config.get('learning', {}).get('trade_frequency', 30)  # 30 seconds
        self.retrain_interval = config.get('learning', {}).get('retrain_interval', 43200)  # 12 hours
        self.weekly_report = config.get('learning', {}).get('weekly_report', True)
        
        # Trading thresholds
        self.confidence_threshold = config.get('safety', {}).get('confidence_threshold', 0.80)
        self.min_return_threshold = config.get('safety', {}).get('min_return_threshold', 0.15)
        
        # State tracking
        self.learning_active = False
        self.last_retrain_time = None
        self.last_weekly_report = None
        self.trade_count = 0
        self.session_start_time = None
        
        # Data paths
        self.data_dir = Path("data/performance")
        self.models_dir = Path("models")
        self.configs_dir = Path("configs")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.configs_dir.mkdir(parents=True, exist_ok=True)
        
        # Performance tracking
        self.performance_data = {
            'trades': [],
            'bot_scores': {},
            'market_data': [],
            'retraining_history': []
        }
        
        self.logger.info("🎯 Phase10LearningController initialized for mainnet demo learning")
        
    async def start_learning_phase(self):
        """Start the continuous learning loop"""
        # Basic safety check
        demo_mode = self.config.get('trading_mode', {}).get('DEMO_MODE', True)
        live_mode = self.config.get('trading_mode', {}).get('LIVE_MODE', False)
        
        if not demo_mode or live_mode:
            self.logger.error("❌ Safety validation failed - demo mode must be enabled, live mode must be disabled")
            return False
            
        self.learning_active = True
        self.session_start_time = datetime.now()
        self.last_retrain_time = datetime.now()
        self.last_weekly_report = datetime.now()
        
        self.logger.info(" Starting Phase 10: Mainnet Demo Learning Loop")
        self.logger.info(f"📊 Trade frequency: {self.trade_frequency}s")
        self.logger.info(f"🔄 Retrain interval: {self.retrain_interval}s ({self.retrain_interval/3600:.1f}h)")
        self.logger.info(f"📈 Confidence threshold: {self.confidence_threshold}")
        self.logger.info(f"💰 Min return threshold: {self.min_return_threshold}")
        
        try:
            # Start concurrent tasks
            await asyncio.gather(
                self._trading_loop(),
                self._retraining_monitor(),
                self._weekly_report_monitor(),
                self._performance_tracker()
            )
        except KeyboardInterrupt:
            self.logger.info("🛑 Manual shutdown requested")
            await self.stop_learning_phase()
        except Exception as e:
            self.logger.error(f"❌ Learning phase error: {e}")
            await self.stop_learning_phase()
            
    async def stop_learning_phase(self):
        """Stop the learning phase and save final report"""
        self.learning_active = False
        self.logger.info("🛑 Stopping learning phase...")
        
        # Generate final session report
        await self._generate_session_report()
        
        self.logger.info("✅ Learning phase stopped successfully")
        
    async def _trading_loop(self):
        """Main trading loop - executes every 30 seconds"""
        while self.learning_active:
            try:
                cycle_start = time.time()
                
                # Perform market analysis
                market_analysis = await self._analyze_market()
                
                # Get bot predictions and scores
                bot_predictions = await self._get_bot_predictions()
                
                # Evaluate trading opportunities
                trade_decision = await self._evaluate_trade_opportunity(market_analysis, bot_predictions)
                
                if trade_decision and trade_decision['execute']:
                    # Execute demo trade
                    trade_result = await self._execute_demo_trade(trade_decision)
                    
                    if trade_result['success']:
                        self.trade_count += 1
                        self.logger.info(f"✅ Demo trade #{self.trade_count} executed: {trade_result['symbol']} | "
                                       f"Return: {trade_result['expected_return']:.2%} | "
                                       f"Confidence: {trade_result['confidence']:.2%}")
                        
                        # Log trade data
                        await self._log_trade_data(trade_result)
                    else:
                        self.logger.warning(f"⚠️ Demo trade failed: {trade_result['reason']}")
                
                # Calculate sleep time to maintain frequency
                cycle_time = time.time() - cycle_start
                sleep_time = max(0, self.trade_frequency - cycle_time)
                
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
                    
            except Exception as e:
                self.logger.error(f"❌ Trading loop error: {e}")
                await asyncio.sleep(self.trade_frequency)
                
    async def _retraining_monitor(self):
        """Monitor for 12-hour retraining intervals"""
        while self.learning_active:
            try:
                current_time = datetime.now()
                time_since_retrain = (current_time - self.last_retrain_time).total_seconds()
                
                if time_since_retrain >= self.retrain_interval:
                    self.logger.info("🔄 Starting 12-hour retraining cycle...")
                    
                    # Trigger retraining
                    retrain_success = await self._trigger_retraining()
                    
                    if retrain_success:
                        self.last_retrain_time = current_time
                        self.logger.info("✅ Retraining completed successfully")
                    else:
                        self.logger.error("❌ Retraining failed")
                
                # Check every 5 minutes
                await asyncio.sleep(300)
                
            except Exception as e:
                self.logger.error(f"❌ Retraining monitor error: {e}")
                await asyncio.sleep(300)
                
    async def _weekly_report_monitor(self):
        """Monitor for weekly report generation"""
        while self.learning_active:
            try:
                current_time = datetime.now()
                time_since_report = (current_time - self.last_weekly_report).total_seconds()
                
                # Generate weekly report (7 days = 604800 seconds)
                if time_since_report >= 604800:
                    self.logger.info("📊 Generating weekly performance report...")
                    
                    report_success = await self._generate_weekly_report()
                    
                    if report_success:
                        self.last_weekly_report = current_time
                        self.logger.info("✅ Weekly report generated successfully")
                    else:
                        self.logger.error("❌ Weekly report generation failed")
                
                # Check every hour
                await asyncio.sleep(3600)
                
            except Exception as e:
                self.logger.error(f"❌ Weekly report monitor error: {e}")
                await asyncio.sleep(3600)
                
    async def _performance_tracker(self):
        """Track performance metrics continuously"""
        while self.learning_active:
            try:
                # Collect performance metrics
                metrics = await self._collect_performance_metrics()
                
                # Update performance data
                self.performance_data['market_data'].append({
                    'timestamp': datetime.now().isoformat(),
                    'metrics': metrics
                })
                
                # Save performance data every 5 minutes
                await self._save_performance_data()
                
                await asyncio.sleep(300)  # 5 minutes
                
            except Exception as e:
                self.logger.error(f"❌ Performance tracker error: {e}")
                await asyncio.sleep(300)
                
    async def _analyze_market(self) -> Dict[str, Any]:
        """Analyze current market conditions"""
        # Mock market analysis for demo
        return {
            'timestamp': datetime.now().isoformat(),
            'volatility': 0.15,
            'trend': 'bullish',
            'volume': 1000000,
            'signals': ['rsi_oversold', 'macd_bullish']
        }
        
    async def _get_bot_predictions(self) -> Dict[str, Any]:
        """Get predictions from all active bots"""
        # Mock bot predictions for demo
        predictions = {
            'strategy_bot': {'confidence': 0.85, 'signal': 'buy', 'expected_return': 0.18},
            'risk_bot': {'risk_level': 'medium', 'max_position': 500},
            'prediction_bot': {'price_target': 45000, 'time_horizon': '1h'},
            'analytics_bot': {'sentiment': 'positive', 'momentum': 'strong'}
        }
        
        # If bot_registry is available, try to get real predictions
        if self.bot_registry:
            try:
                # This would be the integration point for real bot predictions
                real_predictions = {}
                for bot_id in self.bot_registry.get_active_bots():
                    bot = self.bot_registry.get_bot(bot_id)
                    if bot and hasattr(bot, 'get_prediction'):
                        real_predictions[bot_id] = bot.get_prediction()
                
                if real_predictions:
                    predictions.update(real_predictions)
                    
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to get real bot predictions: {e}")
                
        return predictions
        
    async def _evaluate_trade_opportunity(self, market_analysis: Dict, bot_predictions: Dict) -> Optional[Dict]:
        """Evaluate if conditions meet trading thresholds"""
        try:
            # Get strategy bot prediction
            strategy_prediction = bot_predictions.get('strategy_bot', {})
            confidence = strategy_prediction.get('confidence', 0)
            expected_return = strategy_prediction.get('expected_return', 0)
            
            # Check thresholds
            if confidence >= self.confidence_threshold and expected_return >= self.min_return_threshold:
                return {
                    'execute': True,
                    'symbol': 'BTCUSDT',  # Default symbol for demo
                    'signal': strategy_prediction.get('signal', 'buy'),
                    'confidence': confidence,
                    'expected_return': expected_return,
                    'position_size': 500,  # Conservative size for demo
                    'market_analysis': market_analysis,
                    'bot_predictions': bot_predictions
                }
            else:
                self.logger.debug(f"🔍 Trade conditions not met - Confidence: {confidence:.2%}, Return: {expected_return:.2%}")
                return {'execute': False, 'reason': 'Thresholds not met'}
                
        except Exception as e:
            self.logger.error(f"❌ Trade evaluation error: {e}")
            return {'execute': False, 'reason': f'Evaluation error: {e}'}
            
    async def _execute_demo_trade(self, trade_decision: Dict) -> Dict[str, Any]:
        """Execute a demo trade with virtual funds"""
        try:
            # Simulate trade execution
            trade_result = {
                'success': True,
                'trade_id': f"demo_{int(time.time())}",
                'timestamp': datetime.now().isoformat(),
                'symbol': trade_decision['symbol'],
                'signal': trade_decision['signal'],
                'position_size': trade_decision['position_size'],
                'confidence': trade_decision['confidence'],
                'expected_return': trade_decision['expected_return'],
                'entry_price': 43500.0,  # Mock price
                'status': 'executed_demo'
            }
            
            return trade_result
            
        except Exception as e:
            self.logger.error(f"❌ Demo trade execution error: {e}")
            return {'success': False, 'reason': f'Execution error: {e}'}
            
    async def _log_trade_data(self, trade_result: Dict):
        """Log trade data to CSV file"""
        try:
            trade_log_path = self.data_dir / "trade_log.csv"
            
            # Create header if file doesn't exist
            if not trade_log_path.exists():
                with open(trade_log_path, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['timestamp', 'trade_id', 'symbol', 'signal', 'position_size', 
                                   'confidence', 'expected_return', 'entry_price', 'status'])
            
            # Append trade data
            with open(trade_log_path, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    trade_result['timestamp'],
                    trade_result['trade_id'],
                    trade_result['symbol'],
                    trade_result['signal'],
                    trade_result['position_size'],
                    trade_result['confidence'],
                    trade_result['expected_return'],
                    trade_result['entry_price'],
                    trade_result['status']
                ])
                
            # Add to performance data
            self.performance_data['trades'].append(trade_result)
            
        except Exception as e:
            self.logger.error(f"❌ Trade logging error: {e}")
            
    async def _trigger_retraining(self) -> bool:
        """Trigger model retraining"""
        try:
            self.logger.info("🔄 Initiating model retraining...")
            
            # Record retraining event
            retrain_event = {
                'timestamp': datetime.now().isoformat(),
                'trades_since_last': len([t for t in self.performance_data['trades'] 
                                        if datetime.fromisoformat(t['timestamp']) > self.last_retrain_time]),
                'status': 'initiated'
            }
            
            self.performance_data['retraining_history'].append(retrain_event)
            
            # Simulate retraining process
            await asyncio.sleep(2)  # Simulate processing time
            
            retrain_event['status'] = 'completed'
            self.logger.info("✅ Model retraining completed")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Retraining error: {e}")
            return False
            
    async def _generate_weekly_report(self) -> bool:
        """Generate weekly performance report"""
        try:
            week_ago = datetime.now() - timedelta(days=7)
            
            # Filter trades from last week
            weekly_trades = [t for t in self.performance_data['trades'] 
                           if datetime.fromisoformat(t['timestamp']) > week_ago]
            
            if not weekly_trades:
                self.logger.warning("⚠️ No trades in the last week for report generation")
                return True
                
            # Calculate performance metrics
            total_trades = len(weekly_trades)
            avg_confidence = sum(t['confidence'] for t in weekly_trades) / total_trades
            avg_return = sum(t['expected_return'] for t in weekly_trades) / total_trades
            
            # Create report
            report = {
                'report_date': datetime.now().isoformat(),
                'period': '7_days',
                'total_trades': total_trades,
                'average_confidence': avg_confidence,
                'average_expected_return': avg_return,
                'win_rate': 0.75,  # Mock for now
                'sharpe_ratio': 1.2,  # Mock for now
                'top_performing_configs': [
                    {'config_id': 'config_1', 'performance': 0.85},
                    {'config_id': 'config_2', 'performance': 0.82},
                    {'config_id': 'config_3', 'performance': 0.78}
                ]
            }
            
            # Save report
            report_path = self.data_dir / f"weekly_report_{datetime.now().strftime('%Y%m%d')}.json"
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2)
                
            # Export top configs
            await self._export_top_configs(report['top_performing_configs'])
            
            self.logger.info(f"📊 Weekly report saved: {report_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Weekly report error: {e}")
            return False
            
    async def _export_top_configs(self, top_configs):
        """Export top 3 performing configs"""
        try:
            export_path = self.configs_dir / "live_candidates.yaml"
            
            # Create YAML content for top configs
            yaml_content = "# Top 3 Performing Configurations for Live Trading Consideration\n"
            yaml_content += f"# Generated: {datetime.now().isoformat()}\n\n"
            
            for i, config in enumerate(top_configs[:3], 1):
                yaml_content += f"candidate_{i}:\n"
                yaml_content += f"  config_id: {config['config_id']}\n"
                yaml_content += f"  performance_score: {config['performance']}\n"
                yaml_content += f"  status: 'demo_validated'\n"
                yaml_content += f"  ready_for_live: false  # Manual review required\n\n"
                
            with open(export_path, 'w') as f:
                f.write(yaml_content)
                
            self.logger.info(f"🎯 Top configs exported: {export_path}")
            
        except Exception as e:
            self.logger.error(f"❌ Config export error: {e}")
            
    async def _collect_performance_metrics(self) -> Dict[str, Any]:
        """Collect current performance metrics"""
        return {
            'total_trades': self.trade_count,
            'session_duration': (datetime.now() - self.session_start_time).total_seconds() if self.session_start_time else 0,
            'trades_per_hour': self.trade_count / max(1, (datetime.now() - self.session_start_time).total_seconds() / 3600) if self.session_start_time else 0,
            'safety_status': 'DEMO_MODE_ACTIVE',
            'virtual_balance': 10000.0  # Mock virtual balance
        }
        
    async def _save_performance_data(self):
        """Save performance data to file"""
        try:
            performance_path = self.data_dir / "performance_data.json"
            
            with open(performance_path, 'w') as f:
                json.dump(self.performance_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"❌ Performance save error: {e}")
            
    async def _generate_session_report(self):
        """Generate final session report"""
        try:
            session_duration = (datetime.now() - self.session_start_time).total_seconds() if self.session_start_time else 0
            
            report = {
                'session_start': self.session_start_time.isoformat() if self.session_start_time else None,
                'session_end': datetime.now().isoformat(),
                'duration_seconds': session_duration,
                'duration_hours': session_duration / 3600,
                'total_trades': self.trade_count,
                'trades_per_hour': self.trade_count / max(1, session_duration / 3600),
                'safety_violations': 0,
                'demo_mode_maintained': True
            }
            
            session_path = self.data_dir / f"session_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(session_path, 'w') as f:
                json.dump(report, f, indent=2)
                
            self.logger.info(f"📋 Session report saved: {session_path}")
            
        except Exception as e:
            self.logger.error(f"❌ Session report error: {e}")
            
    def get_status(self) -> Dict[str, Any]:
        """Get current learning phase status"""
        return {
            'learning_active': self.learning_active,
            'demo_mode': True,
            'trade_count': self.trade_count,
            'session_start': self.session_start_time.isoformat() if self.session_start_time else None,
            'last_retrain': self.last_retrain_time.isoformat() if self.last_retrain_time else None,
            'next_retrain_in': max(0, self.retrain_interval - (datetime.now() - self.last_retrain_time).total_seconds()) if self.last_retrain_time else 0,
            'safety_status': 'ACTIVE'
        }
