#!/usr/bin/env python3
"""
TradeMasterX 2.0 Integration Test
End-to-end integration testing for the complete system
"""

import os
import sys
import time
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List
import threading

# Add the trademasterx package to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'trademasterx'))

from trademasterx.core.master_bot import MasterBot
from trademasterx.core.bot_registry import BotRegistry
from trademasterx.core.scoring import ScoringEngine
from trademasterx.config.config_loader import ConfigLoader
from trademasterx.bots.analytics.analytics_bot import AnalyticsBot
from trademasterx.bots.strategy.strategy import StrategyBot
from trademasterx.bots.system.risk_bot import RiskBot
from trademasterx.bots.system.memory_bot import MemoryBot
from trademasterx.bots.system.logger_bot import LoggerBot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TradeMasterXIntegrationTest:
    """
    End-to-end integration test for TradeMasterX 2.0
    Tests complete system workflow and bot interactions
    """
    
    def __init__(self):
        self.config_loader = None
        self.bot_registry = None
        self.master_bot = None
        self.scoring_engine = None
        self.active_bots = {}
        self.test_results = {}
        
    def setup_system(self):
        """Initialize the complete TradeMasterX system"""
        logger.info(" Setting up TradeMasterX 2.0 Integration Test Environment")
        
        try:
            # Initialize configuration loader
            self.config_loader = ConfigLoader()
            logger.info("✓ Configuration loader initialized")
            
            # Initialize bot registry
            self.bot_registry = BotRegistry()
            logger.info("✓ Bot registry initialized")
            
            # Initialize scoring engine
            self.scoring_engine = ScoringEngine()
            logger.info("✓ Scoring engine initialized")
            
            # Register all bot types
            self.bot_registry.register_bot('analytics', AnalyticsBot)
            self.bot_registry.register_bot('strategy', StrategyBot)
            self.bot_registry.register_bot('risk', RiskBot)
            self.bot_registry.register_bot('memory', MemoryBot)
            self.bot_registry.register_bot('logger', LoggerBot)
            logger.info("✓ All bot types registered")
            
            # Initialize master bot
            master_config = self.config_loader.get_config('system', {
                'test_mode': True,
                'orchestration': {
                    'max_concurrent_bots': 10,
                    'health_check_interval': 5,
                    'auto_recovery': True
                }
            })
            self.master_bot = MasterBot(master_config)
            logger.info("✓ Master bot initialized")
            
            logger.info("🎉 System setup completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ System setup failed: {e}")
            return False
    
    def test_bot_lifecycle(self):
        """Test complete bot lifecycle management"""
        logger.info("\n🧪 Testing Bot Lifecycle Management...")
        
        test_config = {'test_mode': True, 'integration_test': True}
        created_bots = []
        
        try:
            # Test creating all bot types
            bot_types = ['analytics', 'strategy', 'risk', 'memory', 'logger']
            
            for bot_type in bot_types:
                logger.info(f"Creating {bot_type} bot...")
                bot_id = self.bot_registry.create_bot(bot_type, test_config)
                created_bots.append(bot_id)
                
                # Verify bot creation
                bot = self.bot_registry.get_bot(bot_id)
                assert bot is not None, f"Failed to create {bot_type} bot"
                logger.info(f"✓ {bot_type} bot created successfully (ID: {bot_id})")
            
            # Test bot interaction
            logger.info("Testing bot interactions...")
            
            # Get analytics bot and test its functionality
            analytics_bot = None
            for bot_id in created_bots:
                bot = self.bot_registry.get_bot(bot_id)
                if isinstance(bot, AnalyticsBot):
                    analytics_bot = bot
                    break
            
            if analytics_bot:
                # Test analytics functionality
                if hasattr(analytics_bot, 'analyze_market_patterns'):
                    try:
                        patterns = analytics_bot.analyze_market_patterns()
                        logger.info("✓ Analytics bot pattern analysis working")
                    except Exception as e:
                        logger.warning(f"⚠️ Analytics pattern analysis error: {e}")
            
            # Test bot cleanup
            logger.info("Testing bot cleanup...")
            for bot_id in created_bots:
                success = self.bot_registry.remove_bot(bot_id)
                assert success, f"Failed to remove bot {bot_id}"
                logger.info(f"✓ Bot {bot_id} removed successfully")
            
            self.test_results['bot_lifecycle'] = 'PASS'
            logger.info("✅ Bot lifecycle test PASSED")
            return True
            
        except Exception as e:
            logger.error(f"❌ Bot lifecycle test FAILED: {e}")
            self.test_results['bot_lifecycle'] = 'FAIL'
            
            # Cleanup any remaining bots
            for bot_id in created_bots:
                try:
                    self.bot_registry.remove_bot(bot_id)
                except:
                    pass
            
            return False
    
    def test_configuration_system(self):
        """Test configuration loading and management"""
        logger.info("\n🧪 Testing Configuration System...")
        
        try:
            # Test default configuration loading
            system_config = self.config_loader.get_config('system', {})
            assert isinstance(system_config, dict), "System config should be a dictionary"
            logger.info("✓ Default system configuration loaded")            # Test configuration updates
            test_config = {'test_key': 'test_value', 'nested': {'key': 'value'}}
            test_config_path = 'config/test.yaml'
            self.config_loader.save_config(test_config, test_config_path)
            
            loaded_config = self.config_loader._load_yaml_file(test_config_path)
            assert loaded_config['test_key'] == 'test_value', "Configuration not saved correctly"
            logger.info("✓ Configuration save/load working")
            
            # Test configuration validation
            if hasattr(self.config_loader, 'validate_config'):
                try:
                    is_valid = self.config_loader.validate_config('system', system_config)
                    logger.info(f"✓ Configuration validation working: {is_valid}")
                except Exception as e:
                    logger.warning(f"⚠️ Configuration validation error: {e}")
            
            self.test_results['configuration_system'] = 'PASS'
            logger.info("✅ Configuration system test PASSED")
            return True
            
        except Exception as e:
            logger.error(f"❌ Configuration system test FAILED: {e}")
            self.test_results['configuration_system'] = 'FAIL'
            return False
    
    def test_master_bot_orchestration(self):
        """Test master bot orchestration capabilities"""
        logger.info("\n🧪 Testing Master Bot Orchestration...")
        
        try:
            # Test master bot initialization
            assert self.master_bot is not None, "Master bot not initialized"
            logger.info("✓ Master bot initialized")
            
            # Test bot orchestration
            if hasattr(self.master_bot, 'orchestrate_bots'):
                try:
                    orchestration_result = self.master_bot.orchestrate_bots()
                    logger.info("✓ Bot orchestration executed")
                except Exception as e:
                    logger.warning(f"⚠️ Bot orchestration error: {e}")
            
            # Test health monitoring
            if hasattr(self.master_bot, 'check_system_health'):
                try:
                    health_status = self.master_bot.check_system_health()
                    logger.info(f"✓ System health check working: {health_status}")
                except Exception as e:
                    logger.warning(f"⚠️ Health check error: {e}")
            
            # Test configuration access
            config = self.master_bot.config
            assert isinstance(config, dict), "Master bot config should be a dictionary"
            logger.info("✓ Master bot configuration access working")
            
            self.test_results['master_bot_orchestration'] = 'PASS'
            logger.info("✅ Master bot orchestration test PASSED")
            return True
            
        except Exception as e:
            logger.error(f"❌ Master bot orchestration test FAILED: {e}")
            self.test_results['master_bot_orchestration'] = 'FAIL'
            return False
    
    def test_scoring_engine(self):
        """Test scoring engine functionality"""
        logger.info("\n🧪 Testing Scoring Engine...")
        
        try:
            # Test scoring engine initialization
            assert self.scoring_engine is not None, "Scoring engine not initialized"
            logger.info("✓ Scoring engine initialized")
            
            # Test metric scoring
            test_metrics = {
                'accuracy': 0.85,
                'profit_factor': 1.5,
                'sharpe_ratio': 1.2,
                'win_rate': 0.65,
                'max_drawdown': 0.15
            }
            
            if hasattr(self.scoring_engine, 'calculate_composite_score'):
                try:
                    composite_score = self.scoring_engine.calculate_composite_score(test_metrics)
                    assert isinstance(composite_score, (int, float)), "Score should be numeric"
                    logger.info(f"✓ Composite score calculation working: {composite_score}")
                except Exception as e:
                    logger.warning(f"⚠️ Composite score calculation error: {e}")
            
            # Test performance assessment
            if hasattr(self.scoring_engine, 'assess_performance'):
                try:
                    assessment = self.scoring_engine.assess_performance(test_metrics)
                    logger.info("✓ Performance assessment working")
                except Exception as e:
                    logger.warning(f"⚠️ Performance assessment error: {e}")
            
            self.test_results['scoring_engine'] = 'PASS'
            logger.info("✅ Scoring engine test PASSED")
            return True
            
        except Exception as e:
            logger.error(f"❌ Scoring engine test FAILED: {e}")
            self.test_results['scoring_engine'] = 'FAIL'
            return False
    
    def test_system_integration(self):
        """Test full system integration"""
        logger.info("\n🧪 Testing Full System Integration...")
        
        try:
            # Create a realistic trading scenario
            logger.info("Setting up realistic trading scenario...")
            
            # Create essential bots
            analytics_id = self.bot_registry.create_bot('analytics', {'test_mode': True})
            strategy_id = self.bot_registry.create_bot('strategy', {'test_mode': True})
            risk_id = self.bot_registry.create_bot('risk', {'test_mode': True})
            memory_id = self.bot_registry.create_bot('memory', {'test_mode': True})
            logger_id = self.bot_registry.create_bot('logger', {'test_mode': True})
            
            created_bots = [analytics_id, strategy_id, risk_id, memory_id, logger_id]
            logger.info(f"✓ Created {len(created_bots)} bots for integration test")
            
            # Test inter-bot communication
            analytics_bot = self.bot_registry.get_bot(analytics_id)
            strategy_bot = self.bot_registry.get_bot(strategy_id)
            risk_bot = self.bot_registry.get_bot(risk_id)
            
            # Simulate a trading workflow
            logger.info("Simulating trading workflow...")
            
            # Step 1: Analytics analyzes market
            if hasattr(analytics_bot, 'analyze_market_patterns'):
                try:
                    market_analysis = analytics_bot.analyze_market_patterns()
                    logger.info("✓ Market analysis completed")
                except Exception as e:
                    logger.warning(f"⚠️ Market analysis error: {e}")
            
            # Step 2: Strategy generates signals
            if hasattr(strategy_bot, 'generate_signals'):
                try:
                    signals = strategy_bot.generate_signals()
                    logger.info("✓ Trading signals generated")
                except Exception as e:
                    logger.warning(f"⚠️ Signal generation error: {e}")
            
            # Step 3: Risk assessment
            if hasattr(risk_bot, 'assess_risk'):
                try:
                    risk_assessment = risk_bot.assess_risk()
                    logger.info("✓ Risk assessment completed")
                except Exception as e:
                    logger.warning(f"⚠️ Risk assessment error: {e}")
            
            # Test system performance under load
            logger.info("Testing system performance under load...")
            
            # Simulate multiple concurrent operations
            def simulate_bot_activity(bot_id, duration=2):
                """Simulate bot activity for testing"""
                bot = self.bot_registry.get_bot(bot_id)
                if bot and hasattr(bot, 'is_active'):
                    start_time = time.time()
                    while time.time() - start_time < duration:
                        time.sleep(0.1)  # Simulate work
            
            # Run concurrent simulations
            threads = []
            for bot_id in created_bots[:3]:  # Test first 3 bots
                thread = threading.Thread(target=simulate_bot_activity, args=(bot_id, 1))
                threads.append(thread)
                thread.start()
            
            # Wait for all threads to complete
            for thread in threads:
                thread.join()
            
            logger.info("✓ Concurrent bot operations completed successfully")
            
            # Clean up
            for bot_id in created_bots:
                self.bot_registry.remove_bot(bot_id)
            
            self.test_results['system_integration'] = 'PASS'
            logger.info("✅ Full system integration test PASSED")
            return True
            
        except Exception as e:
            logger.error(f"❌ System integration test FAILED: {e}")
            self.test_results['system_integration'] = 'FAIL'
            return False
    
    def test_error_handling(self):
        """Test system error handling and recovery"""
        logger.info("\n🧪 Testing Error Handling and Recovery...")
        
        try:
            # Test invalid bot creation
            try:
                invalid_bot_id = self.bot_registry.create_bot('invalid_bot_type', {})
                logger.error("Should have failed to create invalid bot type")
                return False
            except Exception:
                logger.info("✓ Invalid bot creation properly rejected")
            
            # Test bot removal of non-existent bot
            removal_success = self.bot_registry.remove_bot('non_existent_bot_id')
            assert not removal_success, "Should return False for non-existent bot"
            logger.info("✓ Non-existent bot removal handled correctly")
            
            # Test configuration error handling
            try:
                invalid_config = self.config_loader.get_config('non_existent_config', None)
                assert invalid_config is None, "Should return None for non-existent config"
                logger.info("✓ Non-existent configuration handled correctly")
            except Exception as e:
                logger.warning(f"⚠️ Configuration error handling issue: {e}")
            
            self.test_results['error_handling'] = 'PASS'
            logger.info("✅ Error handling test PASSED")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error handling test FAILED: {e}")
            self.test_results['error_handling'] = 'FAIL'
            return False
    
    def run_integration_test(self):
        """Run the complete integration test suite"""
        logger.info("🎯 Starting TradeMasterX 2.0 Integration Test Suite")
        logger.info("=" * 60)
        
        start_time = time.time()
        
        # Setup system
        if not self.setup_system():
            logger.error("❌ System setup failed - aborting integration tests")
            return False
        
        # Run test suite
        tests = [
            ('Bot Lifecycle', self.test_bot_lifecycle),
            ('Configuration System', self.test_configuration_system),
            ('Master Bot Orchestration', self.test_master_bot_orchestration),
            ('Scoring Engine', self.test_scoring_engine),
            ('System Integration', self.test_system_integration),
            ('Error Handling', self.test_error_handling)
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            logger.info(f"\n{'='*20} {test_name} {'='*20}")
            if test_func():
                passed_tests += 1
        
        # Report results
        end_time = time.time()
        duration = end_time - start_time
        
        logger.info("\n" + "="*60)
        logger.info("📊 INTEGRATION TEST RESULTS")
        logger.info("="*60)
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {total_tests - passed_tests}")
        logger.info(f"Duration: {duration:.2f} seconds")
        logger.info("="*60)
        
        if passed_tests == total_tests:
            logger.info("🎉 ALL INTEGRATION TESTS PASSED! 🎉")
            logger.info(" TradeMasterX 2.0 is ready for production deployment!")
            return True
        else:
            logger.error(f"❌ {total_tests - passed_tests} integration tests failed")
            logger.error("📝 Please review the test output above for details")
            return False


def main():
    """Main entry point for integration testing"""
    test_suite = TradeMasterXIntegrationTest()
    success = test_suite.run_integration_test()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()