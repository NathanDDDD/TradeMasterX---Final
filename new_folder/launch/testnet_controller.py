"""
TradeMasterX 2.0 - Master Launch Controller
Complete orchestration system for 7-day Bybit Testnet Training
Phase 9A & 9B Integration
"""

import asyncio
import json
import logging
import signal
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional
import threading
import time

# Import all core components
from core.execution.trade_executor import TestnetTradeExecutor
from core.training.continuous_retrainer import ContinuousRetrainer
from core.monitoring.real_time_monitor import RealTimeMonitor
from core.tuning.dynamic_tuner import DynamicSystemTuner
from core.reporting.daily_reporter import DailyReporter
from core.validation.retraining_validator import RetrainingValidator
from core.assessment.readiness_estimator import LiveReadinessEstimator

class MasterLaunchController:
    """
    Master orchestration system for TradeMasterX 2.0 Phase 9A & 9B
    
    Coordinates:
    - 30-second trade execution cycles
    - 12-hour model retraining cycles  
    - 10-minute monitoring cycles
    - 7-day session management
    - Final live trading readiness assessment
    """
    
    def __init__(self, config_path: str = "config/master_config.json"):
        self.config = self._load_config(config_path)
        self.logger = self._setup_logging()
        
        # Session management
        self.session_start_time = datetime.now()
        self.session_duration = timedelta(days=7)
        self.is_running = False
        self.shutdown_requested = False
        
        # Component instances
        self.trade_executor = None
        self.retrainer = None
        self.monitor = None
        self.tuner = None
        self.reporter = None
        self.validator = None
        self.readiness_estimator = None
        
        # Background tasks
        self.tasks = []
        
        # Setup signal handlers for graceful shutdown
        self._setup_signal_handlers()

    def _load_config(self, config_path: str) -> Dict:
        """Load master configuration"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Return default configuration
            return {
                "session_duration_hours": 168,  # 7 days
                "trade_interval_seconds": 30,
                "retraining_interval_hours": 12,
                "monitoring_interval_minutes": 10,
                "reporting_time": "00:00",  # Midnight
                "bybit_testnet": {
                    "api_key": "your_testnet_api_key",
                    "api_secret": "your_testnet_api_secret",
                    "base_url": "https://api-testnet.bybit.com"
                },
                "trading": {
                    "symbols": ["BTCUSDT", "ETHUSDT"],
                    "position_size": 0.01,
                    "initial_confidence_threshold": 0.75
                },
                "paths": {
                    "data": "data",
                    "models": "models", 
                    "reports": "reports",
                    "logs": "logs"
                }
            }

    def _setup_logging(self) -> logging.Logger:
        """Setup master controller logging"""
        logger = logging.getLogger("MasterController")
        logger.setLevel(logging.INFO)
        
        # Create logs directory
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # File handler
        log_file = log_dir / f"master_controller_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        file_handler = logging.FileHandler(log_file)
        
        # Console handler
        console_handler = logging.StreamHandler()
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger

    def _setup_signal_handlers(self):
        """Setup graceful shutdown signal handlers"""
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}. Initiating graceful shutdown...")
        self.shutdown_requested = True

    async def initialize_components(self):
        """Initialize all system components"""
        self.logger.info(" Initializing TradeMasterX 2.0 Components...")
        
        try:
            # Initialize trade executor
            self.trade_executor = TestnetTradeExecutor(
                api_key=self.config["bybit_testnet"]["api_key"],
                api_secret=self.config["bybit_testnet"]["api_secret"],
                symbols=self.config["trading"]["symbols"]
            )
            
            # Initialize continuous retrainer
            self.retrainer = ContinuousRetrainer(
                model_path=self.config["paths"]["models"],
                data_path=self.config["paths"]["data"]
            )
            
            # Initialize real-time monitor
            self.monitor = RealTimeMonitor(
                data_path=self.config["paths"]["data"]
            )
            
            # Initialize dynamic tuner
            self.tuner = DynamicSystemTuner(
                initial_confidence=self.config["trading"]["initial_confidence_threshold"]
            )
            
            # Initialize daily reporter
            self.reporter = DailyReporter(
                reports_path=self.config["paths"]["reports"]
            )
            
            # Initialize retraining validator
            self.validator = RetrainingValidator(
                model_path=self.config["paths"]["models"],
                data_path=self.config["paths"]["data"]
            )
            
            # Initialize readiness estimator
            self.readiness_estimator = LiveReadinessEstimator(
                data_path=self.config["paths"]["data"],
                reports_path=self.config["paths"]["reports"]
            )
            
            self.logger.info("✅ All components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Component initialization failed: {e}")
            raise

    async def start_session(self):
        """Start complete 7-day testnet training session"""
        self.logger.info("=" * 80)
        self.logger.info("🎯 STARTING TRADEMASTERX 2.0 - 7-DAY BYBIT TESTNET TRAINING")
        self.logger.info("=" * 80)
        self.logger.info(f"Session Start: {self.session_start_time}")
        self.logger.info(f"Session End: {self.session_start_time + self.session_duration}")
        self.logger.info(f"Expected Trades: ~20,160 (30-second intervals)")
        self.logger.info(f"Retraining Cycles: 14 (every 12 hours)")
        self.logger.info("=" * 80)
        
        try:
            # Initialize all components
            await self.initialize_components()
            
            # Start all background tasks
            await self._start_background_tasks()
            
            # Main session loop
            await self._run_session_loop()
            
        except Exception as e:
            self.logger.error(f"❌ Session failed: {e}")
            raise
        finally:
            await self._cleanup_session()

    async def _start_background_tasks(self):
        """Start all background monitoring and execution tasks"""
        self.logger.info("🔄 Starting background tasks...")
        
        # Task 1: Trade execution loop (30-second intervals)
        trade_task = asyncio.create_task(self._trade_execution_loop())
        self.tasks.append(trade_task)
        
        # Task 2: Model retraining loop (12-hour intervals)
        retraining_task = asyncio.create_task(self._retraining_loop())
        self.tasks.append(retraining_task)
        
        # Task 3: Real-time monitoring loop (10-minute intervals)
        monitoring_task = asyncio.create_task(self._monitoring_loop())
        self.tasks.append(monitoring_task)
        
        # Task 4: Daily reporting task (midnight)
        reporting_task = asyncio.create_task(self._daily_reporting_loop())
        self.tasks.append(reporting_task)
        
        # Task 5: System status logger (10-minute intervals)
        status_task = asyncio.create_task(self._system_status_loop())
        self.tasks.append(status_task)
        
        self.logger.info(f"✅ Started {len(self.tasks)} background tasks")

    async def _trade_execution_loop(self):
        """Main trade execution loop - 30-second intervals"""
        self.logger.info("📈 Trade execution loop started")
        
        while not self.shutdown_requested and self._session_active():
            try:
                # Get current confidence threshold from tuner
                confidence_threshold = self.tuner.get_current_confidence_threshold()
                
                # Execute trades for all symbols
                for symbol in self.config["trading"]["symbols"]:
                    await self.trade_executor.execute_trade_cycle(
                        symbol=symbol,
                        confidence_threshold=confidence_threshold
                    )
                
                # Wait for next cycle
                await asyncio.sleep(self.config["trade_interval_seconds"])
                
            except Exception as e:
                self.logger.error(f"Trade execution error: {e}")
                await asyncio.sleep(30)  # Wait before retrying

    async def _retraining_loop(self):
        """Model retraining loop - 12-hour intervals"""
        self.logger.info("🧠 Retraining loop started")
        
        retraining_interval = self.config["retraining_interval_hours"] * 3600
        
        while not self.shutdown_requested and self._session_active():
            try:
                # Wait for retraining interval
                await asyncio.sleep(retraining_interval)
                
                if self.shutdown_requested:
                    break
                
                self.logger.info("🔄 Starting scheduled model retraining...")
                
                # Start retraining process
                success = await self.retrainer.retrain_models()
                
                if success:
                    # Validate new models
                    validation_result = await self.validator.validate_retraining(
                        self.retrainer.get_latest_model_version()
                    )
                    
                    # Update tuner with retraining results
                    self.tuner.update_retraining_status(validation_result)
                    
                else:
                    self.logger.warning("⚠️ Retraining failed - continuing with current models")
                
            except Exception as e:
                self.logger.error(f"Retraining loop error: {e}")

    async def _monitoring_loop(self):
        """Real-time monitoring loop - 10-minute intervals"""
        self.logger.info("👁️ Monitoring loop started")
        
        monitoring_interval = self.config["monitoring_interval_minutes"] * 60
        
        while not self.shutdown_requested and self._session_active():
            try:
                # Run monitoring cycle
                metrics = await self.monitor.run_monitoring_cycle()
                
                # Update dynamic tuner with latest metrics
                self.tuner.update_performance_metrics(metrics)
                
                # Check for adaptive adjustments
                adjustments = self.tuner.check_adaptive_adjustments()
                if adjustments:
                    self.logger.info(f"🎛️ Applied adaptive adjustments: {adjustments}")
                
                # Wait for next monitoring cycle
                await asyncio.sleep(monitoring_interval)
                
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(60)  # Wait before retrying

    async def _daily_reporting_loop(self):
        """Daily reporting loop - midnight execution"""
        self.logger.info("📊 Daily reporting loop started")
        
        while not self.shutdown_requested and self._session_active():
            try:
                # Calculate time until next midnight
                now = datetime.now()
                next_midnight = (now + timedelta(days=1)).replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
                sleep_seconds = (next_midnight - now).total_seconds()
                
                # Wait until midnight
                await asyncio.sleep(sleep_seconds)
                
                if self.shutdown_requested:
                    break
                
                # Generate daily report
                await self.reporter.generate_daily_report()
                
            except Exception as e:
                self.logger.error(f"Daily reporting error: {e}")
                await asyncio.sleep(3600)  # Wait 1 hour before retrying

    async def _system_status_loop(self):
        """System status logging loop - 10-minute intervals"""
        status_interval = 600  # 10 minutes
        
        while not self.shutdown_requested and self._session_active():
            try:
                elapsed = datetime.now() - self.session_start_time
                remaining = self.session_duration - elapsed
                
                # Log session progress
                hours_elapsed = elapsed.total_seconds() / 3600
                hours_remaining = remaining.total_seconds() / 3600
                progress_percent = (elapsed.total_seconds() / self.session_duration.total_seconds()) * 100
                
                self.logger.info(
                    f"📊 Session Progress: {progress_percent:.1f}% | "
                    f"Elapsed: {hours_elapsed:.1f}h | "
                    f"Remaining: {hours_remaining:.1f}h"
                )
                
                await asyncio.sleep(status_interval)
                
            except Exception as e:
                self.logger.error(f"Status logging error: {e}")
                await asyncio.sleep(status_interval)

    async def _run_session_loop(self):
        """Main session monitoring loop"""
        self.is_running = True
        
        while self.is_running and not self.shutdown_requested:
            # Check if 7-day session is complete
            if not self._session_active():
                self.logger.info("⏰ 7-day session completed - initiating final assessment")
                break
            
            # Session monitoring interval
            await asyncio.sleep(60)  # Check every minute
        
        # Session completed - run final assessment
        await self._run_final_assessment()

    def _session_active(self) -> bool:
        """Check if 7-day session is still active"""
        elapsed = datetime.now() - self.session_start_time
        return elapsed < self.session_duration

    async def _run_final_assessment(self):
        """Run final live trading readiness assessment"""
        self.logger.info("🎯 Starting Final Live Trading Readiness Assessment...")
        
        try:
            # Run complete assessment
            assessment_results = self.readiness_estimator.run_final_assessment()
            
            # Log final results
            score = assessment_results.get('live_trading_readiness_score', 0)
            status = assessment_results.get('approval_status', 'UNKNOWN')
            
            self.logger.info("=" * 80)
            self.logger.info("🏁 FINAL ASSESSMENT COMPLETE")
            self.logger.info("=" * 80)
            self.logger.info(f"Live Trading Readiness Score: {score}/100")
            self.logger.info(f"Approval Status: {status}")
            
            if status == "APPROVED_FOR_LIVE_TRADING":
                self.logger.info(" CONGRATULATIONS! System approved for live trading!")
            else:
                self.logger.warning("⚠️ System requires improvements before live deployment")
            
            self.logger.info("📄 Detailed assessment saved to: reports/final/final_testnet_evaluation.json")
            self.logger.info("=" * 80)
            
        except Exception as e:
            self.logger.error(f"❌ Final assessment failed: {e}")

    async def _cleanup_session(self):
        """Cleanup and shutdown all components"""
        self.logger.info("🧹 Cleaning up session...")
        
        # Cancel all background tasks
        for task in self.tasks:
            if not task.done():
                task.cancel()
        
        # Wait for tasks to complete
        if self.tasks:
            await asyncio.gather(*self.tasks, return_exceptions=True)
        
        # Cleanup components
        if self.trade_executor:
            await self.trade_executor.cleanup()
        
        if self.monitor:
            await self.monitor.cleanup()
        
        self.logger.info("✅ Session cleanup completed")

    async def emergency_stop(self):
        """Emergency stop for manual intervention"""
        self.logger.warning("🚨 EMERGENCY STOP INITIATED")
        self.shutdown_requested = True
        self.is_running = False
        
        # Stop all trading immediately
        if self.trade_executor:
            await self.trade_executor.emergency_stop()
        
        await self._cleanup_session()
        self.logger.warning("🛑 Emergency stop completed")


# CLI Interface
async def main():
    """Main CLI interface"""
    controller = MasterLaunchController()
    
    print("🎯 TradeMasterX 2.0 - Master Launch Controller")
    print("=" * 60)
    print("Starting 7-day Bybit Testnet Training Session...")
    print("=" * 60)
    
    try:
        await controller.start_session()
        print("✅ Session completed successfully!")
        
    except KeyboardInterrupt:
        print("\n🛑 Manual shutdown requested...")
        await controller.emergency_stop()
        
    except Exception as e:
        print(f"❌ Session failed: {e}")
        await controller.emergency_stop()


if __name__ == "__main__":
    asyncio.run(main())
