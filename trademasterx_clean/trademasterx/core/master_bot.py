"""
TradeMasterX 2.0 - Master Bot Orchestration System
Unified controller for all trading bots, execution cycles, and system coordination.
Consolidates functionality from the original testnet_controller.py with optimizations.
"""

import asyncio
import json
import logging
import signal
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import threading
import time

from trademasterx.config.config_loader import ConfigLoader
from trademasterx.core.bot_registry import BotRegistry
from trademasterx.core.scoring import ScoringEngine
from trademasterx.core.safety_controller import SafetyController
from trademasterx.core.learning_phase_controller import LearningPhaseController


class MasterBot:
    """
    Master orchestration system for TradeMasterX 2.0
    
    Coordinates:
    - Trading bot execution cycles
        - Model retraining and validation
    - Real-time monitoring and reporting
    - Session management and assessment
    - Risk management and emergency controls
    """
    
    def __init__(self, config_path: Union[str, Dict[str, Any]] = "config/system.yaml", trade_callback=None):
        """Initialize master bot with configuration"""
        self.config_loader = ConfigLoader()
        
        # Handle both string path and dict config
        if isinstance(config_path, dict):
            self.config = config_path
        else:
            self.config = self.config_loader.load_system_config(config_path)
        
        # Setup logging
        self.logger = self._setup_logging()
          # Initialize core components
        self.bot_registry = BotRegistry(self.config)
        self.scoring_engine = ScoringEngine(self.config)
        self.safety_controller = SafetyController(self.config)
        self.learning_phase_controller = LearningPhaseController(self.config)
        
        # Phase 10: Check if we're in mainnet demo mode
        self.mainnet_demo_mode = self.config.get('trading_mode', {}).get('mainnet_demo', False)
        self.demo_mode = self.config.get('trading_mode', {}).get('DEMO_MODE', True)
        
        # Session management
        self.session_start_time = datetime.now()
        self.session_duration = timedelta(hours=self.config.get('session_duration_hours', 168))
        self.is_running = False
        self.shutdown_requested = False
        
        # Background tasks
        self.tasks: List[asyncio.Task] = []
        
        # Setup signal handlers
        self._setup_signal_handlers()
        
        self.trade_callback = trade_callback
        
        self.logger.info("MasterBot initialized successfully")

    def _setup_logging(self) -> logging.Logger:
        """Setup master bot logging"""
        logger = logging.getLogger("MasterBot")
        logger.setLevel(logging.INFO)
        
        # Create logs directory
        log_dir = Path(self.config.get('paths', {}).get('logs', 'logs'))
        log_dir.mkdir(exist_ok=True)
        
        # File handler
        log_file = log_dir / f"master_bot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
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
        try:
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
        except (AttributeError, OSError):
            # Windows compatibility
            pass

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}. Initiating graceful shutdown...")
        self.shutdown_requested = True

    async def start_session(self, session_type: str = "testnet"):
        """
        Start trading session
        
        Args:
            session_type: 'testnet' or 'live'
        """
        self.logger.info("=" * 80)
        self.logger.info(f" STARTING TRADEMASTERX 2.0 - {session_type.upper()} SESSION")
        self.logger.info("=" * 80)
        self.logger.info(f"Session Start: {self.session_start_time}")
        self.logger.info(f"Session End: {self.session_start_time + self.session_duration}")
        self.logger.info("=" * 80)
        
        try:
            # Initialize all bots
            await self.bot_registry.initialize_all_bots()
            
            # Start background tasks
            await self._start_background_tasks()
            
            # Run main session loop
            await self._run_session_loop()
            
        except Exception as e:
            self.logger.error(f"❌ Session failed: {e}")
            raise
        finally:
            await self._cleanup_session()

    async def _start_background_tasks(self):
        """Start all background monitoring and execution tasks"""
        self.logger.info("🔄 Starting background tasks...")
        
        # Get configured intervals
        intervals = self.config.get('intervals', {})
        
        # Task 1: Trading execution loop
        if intervals.get('trade_seconds'):
            trade_task = asyncio.create_task(self._trading_loop())
            self.tasks.append(trade_task)
        
        # Task 2: Analytics loop
        if intervals.get('analytics_minutes'):
            analytics_task = asyncio.create_task(self._analytics_loop())
            self.tasks.append(analytics_task)
        
        # Task 3: Strategy optimization loop
        if intervals.get('strategy_minutes'):
            strategy_task = asyncio.create_task(self._strategy_loop())
            self.tasks.append(strategy_task)
        
        # Task 4: System monitoring loop
        if intervals.get('monitoring_minutes'):
            monitoring_task = asyncio.create_task(self._monitoring_loop())
            self.tasks.append(monitoring_task)
        
        # Task 5: Reporting loop
        if intervals.get('reporting_hours'):
            reporting_task = asyncio.create_task(self._reporting_loop())
            self.tasks.append(reporting_task)
        
        self.logger.info(f"✅ Started {len(self.tasks)} background tasks")

    async def _trading_loop(self):
        """Main trading execution loop"""
        self.logger.info("📈 Trading loop started")
        interval = self.config.get('intervals', {}).get('trade_seconds', 30)
        
        while not self.shutdown_requested and self._session_active():
            try:
                # Execute strategy bot
                strategy_bot = self.bot_registry.get_bot('strategy')
                if strategy_bot:
                    await strategy_bot.execute_cycle()
                
                await asyncio.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"Trading loop error: {e}")
                await asyncio.sleep(interval)

    async def _analytics_loop(self):
        """Market analysis loop"""
        self.logger.info("📊 Analytics loop started")
        interval = self.config.get('intervals', {}).get('analytics_minutes', 5) * 60
        
        while not self.shutdown_requested and self._session_active():
            try:
                # Execute analytics bots
                market_bot = self.bot_registry.get_bot('market_analysis')
                sentiment_bot = self.bot_registry.get_bot('sentiment')
                
                if market_bot:
                    await market_bot.execute_cycle()
                if sentiment_bot:
                    await sentiment_bot.execute_cycle()
                
                await asyncio.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"Analytics loop error: {e}")
                await asyncio.sleep(interval)

    async def _strategy_loop(self):
        """Strategy optimization loop"""
        self.logger.info("🧠 Strategy loop started")
        interval = self.config.get('intervals', {}).get('strategy_minutes', 60) * 60
        
        while not self.shutdown_requested and self._session_active():
            try:
                # Update scoring and strategy optimization
                await self.scoring_engine.update_scores()
                
                await asyncio.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"Strategy loop error: {e}")
                await asyncio.sleep(interval)

    async def _monitoring_loop(self):
        """System monitoring loop"""
        self.logger.info("👁️ Monitoring loop started")
        interval = self.config.get('intervals', {}).get('monitoring_minutes', 10) * 60
        
        while not self.shutdown_requested and self._session_active():
            try:
                # Execute system monitoring bots
                risk_bot = self.bot_registry.get_bot('risk')
                memory_bot = self.bot_registry.get_bot('memory')
                
                if risk_bot:
                    await risk_bot.execute_cycle()
                if memory_bot:
                    await memory_bot.execute_cycle()
                
                # Log session progress
                self._log_session_progress()
                
                await asyncio.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(interval)

    async def _reporting_loop(self):
        """Reporting and assessment loop"""
        self.logger.info("📄 Reporting loop started")
        interval = self.config.get('intervals', {}).get('reporting_hours', 24) * 3600
        
        while not self.shutdown_requested and self._session_active():
            try:
                # Generate reports and assessments
                await self.scoring_engine.generate_reports()
                
                await asyncio.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"Reporting loop error: {e}")
                await asyncio.sleep(interval)

    async def _run_session_loop(self):
        """Main session monitoring loop"""
        self.is_running = True
        
        while self.is_running and not self.shutdown_requested:
            # Check if session is complete
            if not self._session_active():
                self.logger.info("⏰ Session completed - initiating final assessment")
                break
            
            # Session monitoring interval
            await asyncio.sleep(60)  # Check every minute
        
        # Session completed - run final assessment
        await self.scoring_engine.run_final_assessment()

    def _session_active(self) -> bool:
        """Check if session is still active"""
        elapsed = datetime.now() - self.session_start_time
        return elapsed < self.session_duration

    def _log_session_progress(self):
        """Log session progress"""
        elapsed = datetime.now() - self.session_start_time
        remaining = self.session_duration - elapsed
        progress_percent = (elapsed.total_seconds() / self.session_duration.total_seconds()) * 100
        
        hours_elapsed = elapsed.total_seconds() / 3600
        hours_remaining = remaining.total_seconds() / 3600
        
        self.logger.info(
            f"📊 Session Progress: {progress_percent:.1f}% | "
            f"Elapsed: {hours_elapsed:.1f}h | "
            f"Remaining: {hours_remaining:.1f}h"
        )

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
        
        # Cleanup bots
        await self.bot_registry.cleanup_all_bots()
        
        self.logger.info("✅ Session cleanup completed")

    async def emergency_stop(self):
        """Emergency stop for manual intervention"""
        self.logger.warning("🚨 EMERGENCY STOP INITIATED")
        self.shutdown_requested = True
        self.is_running = False
        
        # Stop all bots immediately
        await self.bot_registry.emergency_stop_all()
        
        await self._cleanup_session()
        self.logger.warning("🛑 Emergency stop completed")

    async def start_learning_phase(self):
        """
        Start Phase 10: Mainnet Demo Learning Loop
        """
        if not self.mainnet_demo_mode or not self.demo_mode:
            self.logger.error("❌ Learning phase requires mainnet_demo and DEMO_MODE to be enabled")
            return False
            
        self.logger.info("=" * 80)
        self.logger.info("🎯 STARTING PHASE 10: MAINNET DEMO LEARNING LOOP")
        self.logger.info("=" * 80)
        self.logger.info(f"🛡️ DEMO_MODE: {self.demo_mode}")
        self.logger.info(f"🌐 Mainnet Demo: {self.mainnet_demo_mode}")
        self.logger.info(f"⚡ Trade Frequency: {self.config.get('learning', {}).get('trade_frequency', 30)}s")
        self.logger.info(f"🔄 Retrain Interval: {self.config.get('learning', {}).get('retrain_interval', 43200)}s")
        self.logger.info("=" * 80)
        
        try:
            # Safety validation before starting
            if not self.safety_controller.validate_trading_request("START_LEARNING_PHASE"):
                self.logger.error("❌ Safety validation failed - cannot start learning phase")
                return False
                
            # Initialize all bots
            await self.bot_registry.initialize_all_bots()
            
            # Start the learning phase controller
            await self.learning_phase_controller.start_learning_phase()
            
        except Exception as e:
            self.logger.error(f"❌ Learning phase failed: {e}")
            return False
        finally:
            await self._cleanup_session()
            
        return True

    def get_session_status(self) -> Dict[str, Any]:
        """Get current session status"""
        elapsed = datetime.now() - self.session_start_time
        
        return {
            "session_start": self.session_start_time.isoformat(),
            "elapsed_hours": elapsed.total_seconds() / 3600,
            "is_running": self.is_running,
            "shutdown_requested": self.shutdown_requested,
            "active_tasks": len([t for t in self.tasks if not t.done()]),
            "bot_count": self.bot_registry.get_bot_count(),
            "config_loaded": bool(self.config)
        }


# CLI Interface for backward compatibility
async def main():
    """Main CLI interface for launching MasterBot"""
    master_bot = MasterBot()
    
    print("🎯 TradeMasterX 2.0 - Master Bot Controller")
    print("=" * 60)
    print("Starting optimized trading session...")
    print("=" * 60)
    
    try:
        await master_bot.start_session("testnet")
        print("✅ Session completed successfully!")
        
    except KeyboardInterrupt:
        print("\n🛑 Manual shutdown requested...")
        await master_bot.emergency_stop()
        
    except Exception as e:
        print(f"❌ Session failed: {e}")
        await master_bot.emergency_stop()


if __name__ == "__main__":
    asyncio.run(main())
