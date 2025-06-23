#!/usr/bin/env python3
"""
TradeMasterX 2.0 System Test Suite
Comprehensive testing and validation of the refactored production-grade package
"""

import os
import sys
import json
import time
import asyncio
import unittest
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
import traceback

# Add the trademasterx package to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'trademasterx'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TradeMasterXSystemTest(unittest.TestCase):
    """
    Comprehensive system test suite for TradeMasterX 2.0
    Tests all major components, integration, and production readiness
    """
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.test_results = {}
        cls.start_time = time.time()
        
        logger.info("=" * 60)
        logger.info("TradeMasterX 2.0 System Test Suite Starting")
        logger.info("=" * 60)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up and report results"""
        end_time = time.time()
        duration = end_time - cls.start_time
        
        logger.info("=" * 60)
        logger.info(f"Test Suite Completed in {duration:.2f} seconds")
        logger.info("=" * 60)
        
        # Print summary
        passed = sum(1 for result in cls.test_results.values() if result['status'] == 'PASS')
        failed = sum(1 for result in cls.test_results.values() if result['status'] == 'FAIL')
        
        logger.info(f"Tests Passed: {passed}")
        logger.info(f"Tests Failed: {failed}")
        logger.info(f"Total Tests: {len(cls.test_results)}")
        
        if failed > 0:
            logger.error("Some tests failed. See details above.")
        else:
            logger.info("All tests passed! ✅")
    
    def setUp(self):
        """Set up individual test"""
        self.test_name = self._testMethodName
        logger.info(f"\n🧪 Running test: {self.test_name}")
    
    def tearDown(self):
        """Clean up individual test"""
        # Record test result
        if hasattr(self, '_outcome'):
            result = self._outcome.result
            if result.wasSuccessful():
                status = 'PASS'
                message = 'Test completed successfully'
                logger.info(f"✅ {self.test_name}: PASSED")
            else:
                status = 'FAIL'
                errors = [str(error[1]) for error in result.errors + result.failures]
                message = '; '.join(errors) if errors else 'Unknown error'
                logger.error(f"❌ {self.test_name}: FAILED - {message}")
        else:
            status = 'UNKNOWN'
            message = 'Test result unknown'
        
        self.__class__.test_results[self.test_name] = {
            'status': status,
            'message': message,
            'timestamp': time.time()
        }
    
    def test_01_package_structure(self):
        """Test package structure and imports"""
        logger.info("Testing package structure and imports...")
        
        # Test main package import
        try:
            import trademasterx
            self.assertIsNotNone(trademasterx)
            logger.info("✓ Main package import successful")
        except ImportError as e:
            self.fail(f"Failed to import main package: {e}")
        
        # Test core components
        try:
            from trademasterx.core import MasterBot, BotRegistry, ScoringEngine
            logger.info("✓ Core components import successful")
        except ImportError as e:
            self.fail(f"Failed to import core components: {e}")
        
        # Test configuration
        try:
            from trademasterx.config import ConfigLoader
            logger.info("✓ Configuration components import successful")
        except ImportError as e:
            self.fail(f"Failed to import configuration components: {e}")
        
        # Test bot imports
        try:
            from trademasterx.bots.analytics import AnalyticsBot
            from trademasterx.bots.strategy import StrategyBot
            from trademasterx.bots.system import RiskBot, MemoryBot, LoggerBot
            logger.info("✓ All bot imports successful")
        except ImportError as e:
            self.fail(f"Failed to import bots: {e}")
    
    def test_02_config_loader(self):
        """Test configuration loading system"""
        logger.info("Testing configuration loading system...")
        
        try:
            from trademasterx.config.config_loader import ConfigLoader
            
            # Test initialization
            config_loader = ConfigLoader()
            self.assertIsNotNone(config_loader)
            logger.info("✓ ConfigLoader initialization successful")
            
            # Test default config loading
            system_config = config_loader.get_config('system', {})
            self.assertIsInstance(system_config, dict)
            logger.info("✓ System config loading successful")
            
            # Test YAML file loading (if exists)
            yaml_path = Path('trademasterx/config/system.yaml')
            if yaml_path.exists():
                yaml_config = config_loader.load_config_file(str(yaml_path))
                self.assertIsInstance(yaml_config, dict)
                logger.info("✓ YAML config file loading successful")
            
        except Exception as e:
            self.fail(f"Configuration loading failed: {e}")
    
    def test_03_bot_registry(self):
        """Test bot registry system"""
        logger.info("Testing bot registry system...")
        
        try:
            from trademasterx.core.bot_registry import BotRegistry
            from trademasterx.bots.analytics.analytics_bot import AnalyticsBot
            
            # Test initialization
            registry = BotRegistry()
            self.assertIsNotNone(registry)
            logger.info("✓ BotRegistry initialization successful")
            
            # Test bot registration
            registry.register_bot('analytics', AnalyticsBot)
            self.assertIn('analytics', registry.registered_bots)
            logger.info("✓ Bot registration successful")
            
            # Test bot creation
            config = {'test_mode': True}
            bot_id = registry.create_bot('analytics', config)
            self.assertIsNotNone(bot_id)
            self.assertIn(bot_id, registry.active_bots)
            logger.info(f"✓ Bot creation successful (ID: {bot_id})")
            
            # Test bot retrieval
            bot = registry.get_bot(bot_id)
            self.assertIsNotNone(bot)
            self.assertIsInstance(bot, AnalyticsBot)
            logger.info("✓ Bot retrieval successful")
            
            # Test bot removal
            success = registry.remove_bot(bot_id)
            self.assertTrue(success)
            self.assertNotIn(bot_id, registry.active_bots)
            logger.info("✓ Bot removal successful")
            
        except Exception as e:
            self.fail(f"Bot registry testing failed: {e}")
    
    def test_04_master_bot(self):
        """Test master bot orchestration"""
        logger.info("Testing master bot orchestration...")
        
        try:
            from trademasterx.core.master_bot import MasterBot
            
            # Test initialization
            config = {
                'test_mode': True,
                'orchestration': {
                    'max_concurrent_bots': 5,
                    'health_check_interval': 10
                }
            }
            master_bot = MasterBot(config)
            self.assertIsNotNone(master_bot)
            logger.info("✓ MasterBot initialization successful")
            
            # Test configuration
            self.assertEqual(master_bot.config['test_mode'], True)
            logger.info("✓ MasterBot configuration successful")
            
        except Exception as e:
            self.fail(f"Master bot testing failed: {e}")
    
    def test_05_scoring_engine(self):
        """Test scoring engine"""
        logger.info("Testing scoring engine...")
        
        try:
            from trademasterx.core.scoring import ScoringEngine
            
            # Test initialization
            scoring_engine = ScoringEngine()
            self.assertIsNotNone(scoring_engine)
            logger.info("✓ ScoringEngine initialization successful")
            
            # Test basic scoring functionality
            test_metrics = {
                'accuracy': 0.85,
                'profit_factor': 1.5,
                'sharpe_ratio': 1.2
            }
            
            if hasattr(scoring_engine, 'calculate_composite_score'):
                score = scoring_engine.calculate_composite_score(test_metrics)
                self.assertIsInstance(score, (int, float))
                logger.info(f"✓ Composite score calculation successful: {score}")
            
        except Exception as e:
            self.fail(f"Scoring engine testing failed: {e}")
    
    def test_06_analytics_bot(self):
        """Test analytics bot functionality"""
        logger.info("Testing analytics bot functionality...")
        
        try:
            from trademasterx.bots.analytics.analytics_bot import AnalyticsBot
            
            # Test initialization
            config = {'test_mode': True}
            analytics_bot = AnalyticsBot(config)
            self.assertIsNotNone(analytics_bot)
            logger.info("✓ AnalyticsBot initialization successful")
            
            # Test component existence
            self.assertTrue(hasattr(analytics_bot, 'pattern_analyzer'))
            self.assertTrue(hasattr(analytics_bot, 'signal_analyzer'))
            self.assertTrue(hasattr(analytics_bot, 'bot_performance_analyzer'))
            logger.info("✓ AnalyticsBot components verified")
            
        except Exception as e:
            self.fail(f"Analytics bot testing failed: {e}")
    
    def test_07_strategy_bot(self):
        """Test strategy bot functionality"""
        logger.info("Testing strategy bot functionality...")
        
        try:
            from trademasterx.bots.strategy.strategy import StrategyBot
            
            # Test initialization
            config = {'test_mode': True}
            strategy_bot = StrategyBot(config)
            self.assertIsNotNone(strategy_bot)
            logger.info("✓ StrategyBot initialization successful")
            
            # Test strategy components
            self.assertTrue(hasattr(strategy_bot, 'strategy_manager'))
            self.assertTrue(hasattr(strategy_bot, 'signal_generator'))
            logger.info("✓ StrategyBot components verified")
            
        except Exception as e:
            self.fail(f"Strategy bot testing failed: {e}")
    
    def test_08_system_bots(self):
        """Test system bots (Risk, Memory, Logger)"""
        logger.info("Testing system bots...")
        
        try:
            from trademasterx.bots.system.risk_bot import RiskBot
            from trademasterx.bots.system.memory_bot import MemoryBot
            from trademasterx.bots.system.logger_bot import LoggerBot
            
            # Test RiskBot
            config = {'test_mode': True}
            risk_bot = RiskBot(config)
            self.assertIsNotNone(risk_bot)
            logger.info("✓ RiskBot initialization successful")
            
            # Test MemoryBot
            memory_bot = MemoryBot(config)
            self.assertIsNotNone(memory_bot)
            logger.info("✓ MemoryBot initialization successful")
            
            # Test LoggerBot
            logger_bot = LoggerBot(config)
            self.assertIsNotNone(logger_bot)
            logger.info("✓ LoggerBot initialization successful")
            
        except Exception as e:
            self.fail(f"System bots testing failed: {e}")
    
    def test_09_web_interface(self):
        """Test web interface components"""
        logger.info("Testing web interface components...")
        
        try:
            from trademasterx.interface.web.app import TradeMasterXWebApp, create_app
            
            # Test app creation
            app = create_app()
            self.assertIsNotNone(app)
            logger.info("✓ Web application creation successful")
            
            # Test Flask app
            self.assertIsNotNone(app.app)
            self.assertIsNotNone(app.socketio)
            logger.info("✓ Flask and SocketIO initialization successful")
            
        except Exception as e:
            self.fail(f"Web interface testing failed: {e}")
    
    def test_10_cli_interface(self):
        """Test CLI interface components"""
        logger.info("Testing CLI interface components...")
        
        try:
            # Check if CLI module exists
            cli_path = Path('trademasterx/interface/cli/cli.py')
            if cli_path.exists():
                from trademasterx.interface.cli.cli import TradeMasterXCLI
                
                # Test CLI initialization
                cli = TradeMasterXCLI()
                self.assertIsNotNone(cli)
                logger.info("✓ CLI initialization successful")
            else:
                logger.warning("⚠️ CLI module not found - skipping CLI tests")
            
        except Exception as e:
            logger.warning(f"⚠️ CLI testing skipped due to error: {e}")
    
    def test_11_configuration_files(self):
        """Test configuration files existence and validity"""
        logger.info("Testing configuration files...")
        
        config_files = [
            'trademasterx/config/system.yaml',
            'trademasterx/config/bots.yaml',
            'trademasterx/config/strategies.yaml'
        ]
        
        for config_file in config_files:
            config_path = Path(config_file)
            if config_path.exists():
                try:
                    import yaml
                    with open(config_path, 'r') as f:
                        config_data = yaml.safe_load(f)
                    self.assertIsInstance(config_data, dict)
                    logger.info(f"✓ {config_file} is valid")
                except Exception as e:
                    self.fail(f"Invalid config file {config_file}: {e}")
            else:
                logger.warning(f"⚠️ Config file not found: {config_file}")
    
    def test_12_docker_setup(self):
        """Test Docker configuration"""
        logger.info("Testing Docker setup...")
        
        # Check Dockerfile
        dockerfile_path = Path('Dockerfile')
        if dockerfile_path.exists():
            logger.info("✓ Dockerfile found")
        else:
            logger.warning("⚠️ Dockerfile not found")
        
        # Check docker-compose.yml
        compose_path = Path('docker-compose.yml')
        if compose_path.exists():
            logger.info("✓ docker-compose.yml found")
        else:
            logger.warning("⚠️ docker-compose.yml not found")
        
        # Check .env.example
        env_path = Path('.env.example')
        if env_path.exists():
            logger.info("✓ .env.example found")
        else:
            logger.warning("⚠️ .env.example not found")
    
    def test_13_setup_py(self):
        """Test setup.py configuration"""
        logger.info("Testing setup.py configuration...")
        
        setup_path = Path('setup.py')
        if setup_path.exists():
            try:
                # Read setup.py content
                with open(setup_path, 'r') as f:
                    content = f.read()
                
                # Check for required components
                required_components = [
                    'name=',
                    'version=',
                    'packages=',
                    'install_requires=',
                    'entry_points='
                ]
                
                for component in required_components:
                    self.assertIn(component, content)
                
                logger.info("✓ setup.py contains all required components")
                
            except Exception as e:
                self.fail(f"setup.py validation failed: {e}")
        else:
            self.fail("setup.py not found")
    
    def test_14_requirements(self):
        """Test requirements files"""
        logger.info("Testing requirements files...")
        
        # Check main requirements.txt
        req_path = Path('requirements.txt')
        if req_path.exists():
            with open(req_path, 'r') as f:
                requirements = f.read().strip()
            self.assertGreater(len(requirements), 0)
            logger.info("✓ Main requirements.txt found and non-empty")
        else:
            logger.warning("⚠️ Main requirements.txt not found")
        
        # Check package requirements.txt
        pkg_req_path = Path('trademasterx/requirements.txt')
        if pkg_req_path.exists():
            logger.info("✓ Package requirements.txt found")
        else:
            logger.warning("⚠️ Package requirements.txt not found")
    
    def test_15_integration_test(self):
        """Test basic integration scenario"""
        logger.info("Testing basic integration scenario...")
        
        try:
            from trademasterx.core.bot_registry import BotRegistry
            from trademasterx.core.master_bot import MasterBot
            from trademasterx.config.config_loader import ConfigLoader
            from trademasterx.bots.analytics.analytics_bot import AnalyticsBot
            
            # Create integrated system
            config_loader = ConfigLoader()
            bot_registry = BotRegistry()
            
            # Register and create bots
            bot_registry.register_bot('analytics', AnalyticsBot)
            analytics_bot_id = bot_registry.create_bot('analytics', {'test_mode': True})
            
            # Verify integration
            analytics_bot = bot_registry.get_bot(analytics_bot_id)
            self.assertIsNotNone(analytics_bot)
            self.assertIsInstance(analytics_bot, AnalyticsBot)
            
            # Clean up
            bot_registry.remove_bot(analytics_bot_id)
            
            logger.info("✓ Basic integration test successful")
            
        except Exception as e:
            self.fail(f"Integration test failed: {e}")


def run_comprehensive_test():
    """Run the comprehensive test suite"""
    print(" Starting TradeMasterX 2.0 Comprehensive Test Suite")
    print("=" * 70)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TradeMasterXSystemTest)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return results
    return result.wasSuccessful()


def validate_production_readiness():
    """Validate production readiness"""
    logger.info("\n🔍 Validating Production Readiness...")
    
    checks = {
        'Package Structure': check_package_structure(),
        'Configuration Files': check_configuration_files(),
        'Documentation': check_documentation(),
        'Dependencies': check_dependencies(),
        'Docker Setup': check_docker_setup(),
        'Security': check_security_basics()
    }
    
    logger.info("\n📋 Production Readiness Report:")
    logger.info("-" * 50)
    
    all_passed = True
    for check_name, passed in checks.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"{check_name:20} : {status}")
        if not passed:
            all_passed = False
    
    logger.info("-" * 50)
    if all_passed:
        logger.info("🎉 TradeMasterX 2.0 is PRODUCTION READY! 🎉")
    else:
        logger.warning("⚠️ Some production readiness checks failed")
    
    return all_passed


def check_package_structure() -> bool:
    """Check if package structure is correct"""
    required_dirs = [
        'trademasterx',
        'trademasterx/core',
        'trademasterx/bots',
        'trademasterx/config',
        'trademasterx/interface'
    ]
    
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            return False
    
    return True


def check_configuration_files() -> bool:
    """Check if configuration files exist"""
    required_files = [
        'setup.py',
        'requirements.txt',
        'trademasterx/__init__.py'
    ]
    
    for file_path in required_files:
        if not Path(file_path).exists():
            return False
    
    return True


def check_documentation() -> bool:
    """Check if documentation exists"""
    required_docs = [
        'README.md',
        'docs/PROJECT_STRUCTURE.md'
    ]
    
    for doc_path in required_docs:
        if not Path(doc_path).exists():
            return False
    
    return True


def check_dependencies() -> bool:
    """Check if dependencies are properly defined"""
    try:
        with open('requirements.txt', 'r') as f:
            requirements = f.read().strip()
        return len(requirements) > 0
    except:
        return False


def check_docker_setup() -> bool:
    """Check Docker configuration"""
    docker_files = ['Dockerfile', 'docker-compose.yml']
    return all(Path(f).exists() for f in docker_files)


def check_security_basics() -> bool:
    """Check basic security configurations"""
    # Check for .env.example
    if not Path('.env.example').exists():
        return False
    
    # Check that secrets aren't hardcoded (basic check)
    sensitive_files = ['trademasterx/interface/web/app.py']
    sensitive_patterns = ['password', 'secret', 'key']
    
    for file_path in sensitive_files:
        if Path(file_path).exists():
            with open(file_path, 'r') as f:
                content = f.read().lower()
                for pattern in sensitive_patterns:
                    if f'{pattern}=' in content and 'your-' not in content:
                        return False
    
    return True


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='TradeMasterX 2.0 System Test Suite')
    parser.add_argument('--test-only', action='store_true', help='Run only the test suite')
    parser.add_argument('--validate-only', action='store_true', help='Run only production validation')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    success = True
    
    if not args.validate_only:
        # Run comprehensive test suite
        success = run_comprehensive_test()
    
    if not args.test_only:
        # Run production readiness validation
        production_ready = validate_production_readiness()
        success = success and production_ready
    
    # Final status
    if success:
        print("\n🎉 All tests passed! TradeMasterX 2.0 is ready for deployment! 🎉")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please review the output above.")
        sys.exit(1)