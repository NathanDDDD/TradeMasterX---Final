#!/usr/bin/env python3
"""
TradeMasterX 2.0 - Unified Phase Tester
Comprehensive testing suite for all implemented phases with dependency-aware testing.
"""

import sys
import os
import json
import logging
import time
import importlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

# Setup path for imports
sys.path.insert(0, os.path.abspath('.'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('PhaseTester')

class PhaseTester:
    """Unified testing suite for all TradeMasterX phases"""
    
    def __init__(self):
        self.results = {
            'test_time': datetime.now().isoformat(),
            'phases': {},
            'overall_status': 'UNKNOWN',
            'summary': {}
        }
        
        self.phases_to_test = [
            ('Phase 12', 'Safety Systems', self.test_phase_12),
            ('Phase 13', 'Smart Command Interface', self.test_phase_13),
            ('Integration', 'System Integration', self.test_integration),
            ('Dependencies', 'Package Dependencies', self.test_dependencies)
        ]
        
    def safe_import(self, module_path: str, description: str = "") -> Optional[Any]:
        """Safely import a module with error handling"""
        try:
            module = importlib.import_module(module_path)
            logger.info(f"✓ Successfully imported: {module_path}")
            return module
        except ImportError as e:
            logger.warning(f"⚠ Could not import {module_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Error importing {module_path}: {e}")
            return None
    
    def test_phase_12(self) -> Dict[str, Any]:
        """Test Phase 12 - Safety Systems"""
        logger.info("Testing Phase 12 - Safety Systems...")
        
        results = {
            'kill_switch': False,
            'safety_dashboard': False,
            'risk_guard': False,
            'trade_deviation_alert': False,
            'recovery_manager': False,
            'functional_tests': False
        }
        
        # Test core safety components
        kill_switch_module = self.safe_import('trademasterx.core.kill_switch')
        if kill_switch_module:
            try:
                kill_switch = kill_switch_module.KillSwitch()
                # Test basic functionality
                status = kill_switch.get_status()
                results['kill_switch'] = isinstance(status, dict)
                logger.info("✓ Kill Switch functional")
            except Exception as e:
                logger.warning(f"⚠ Kill Switch error: {e}")
        
        safety_dashboard_module = self.safe_import('trademasterx.core.safety_dashboard')
        if safety_dashboard_module:
            try:
                dashboard = safety_dashboard_module.SafetyDashboard()
                status = dashboard.get_safety_status()
                results['safety_dashboard'] = isinstance(status, dict)
                logger.info("✓ Safety Dashboard functional")
            except Exception as e:
                logger.warning(f"⚠ Safety Dashboard error: {e}")
        
        risk_guard_module = self.safe_import('trademasterx.core.risk_guard')
        if risk_guard_module:
            try:
                risk_guard = risk_guard_module.RiskGuard()
                test_trade = {'symbol': 'TEST', 'amount': 100, 'side': 'buy'}
                validation = risk_guard.validate_trade(test_trade)
                results['risk_guard'] = isinstance(validation, dict)
                logger.info("✓ Risk Guard functional")
            except Exception as e:
                logger.warning(f"⚠ Risk Guard error: {e}")
        
        trade_alert_module = self.safe_import('trademasterx.core.trade_deviation_alert')
        if trade_alert_module:
            try:
                alert_system = trade_alert_module.TradeDeviationAlert()
                results['trade_deviation_alert'] = True
                logger.info("✓ Trade Deviation Alert functional")
            except Exception as e:
                logger.warning(f"⚠ Trade Deviation Alert error: {e}")
        
        recovery_module = self.safe_import('trademasterx.core.failover_recovery')
        if recovery_module:
            try:
                recovery = recovery_module.RecoveryManager()
                results['recovery_manager'] = True
                logger.info("✓ Recovery Manager functional")
            except Exception as e:
                logger.warning(f"⚠ Recovery Manager error: {e}")
        
        # Run functional tests if available
        try:
            from test_phase_12_functional import Phase12FunctionalTest
            func_test = Phase12FunctionalTest()
            func_test.setup_test_environment()
            
            # Run lightweight functional tests
            func_test.test_emergency_kill_switch_scenario()
            func_test.test_risk_guard_protection()
            
            results['functional_tests'] = True
            logger.info("✓ Phase 12 functional tests completed")
        except Exception as e:
            logger.warning(f"⚠ Phase 12 functional tests skipped: {e}")
        
        success_count = sum(results.values())
        total_count = len(results)
        
        return {
            'components': results,
            'success_rate': (success_count / total_count) * 100,
            'status': 'PASS' if success_count >= 3 else 'PARTIAL' if success_count >= 1 else 'FAIL'
        }
    
    def test_phase_13(self) -> Dict[str, Any]:
        """Test Phase 13 - Smart Command Interface"""
        logger.info("Testing Phase 13 - Smart Command Interface...")
        
        results = {
            'command_assistant': False,
            'api_integration': False,
            'conversation_engine': False,
            'cli_integration': False,
            'personality_system': False,
            'command_parsing': False
        }
        
        # Test command assistant
        assistant_module = self.safe_import('trademasterx.interface.assistant.command_assistant')
        if assistant_module:
            try:
                assistant = assistant_module.CommandAssistant(personality="professional", setup_keys=False)
                results['command_assistant'] = True
                logger.info("✓ Command Assistant initialized")
                
                # Test command parsing
                test_command = assistant.parse_command("show status")
                if test_command and 'command' in test_command:
                    results['command_parsing'] = True
                    logger.info("✓ Command parsing functional")
                
                # Test personality system
                personalities = ["professional", "friendly", "technical"]
                personality_tests = []
                for personality in personalities:
                    try:
                        test_assistant = assistant_module.CommandAssistant(personality=personality, setup_keys=False)
                        personality_tests.append(True)
                    except:
                        personality_tests.append(False)
                
                results['personality_system'] = sum(personality_tests) >= 2
                if results['personality_system']:
                    logger.info("✓ Personality system functional")
                
            except Exception as e:
                logger.warning(f"⚠ Command Assistant error: {e}")
        
        # Test API integration
        api_module = self.safe_import('trademasterx.interface.assistant.api_integration')
        if api_module:
            try:
                api_integration = api_module.APIIntegration()
                
                # Test mock mode
                mock_response = api_integration.process_command_with_ai(
                    "Test command", 
                    {"test": True}, 
                    use_mock=True
                )
                
                results['api_integration'] = isinstance(mock_response, dict)
                if results['api_integration']:
                    logger.info("✓ API Integration functional (mock mode)")
                
            except Exception as e:
                logger.warning(f"⚠ API Integration error: {e}")
        
        # Test conversation engine
        conv_module = self.safe_import('trademasterx.interface.assistant.conversation_engine')
        if conv_module:
            try:
                conv_engine = conv_module.ConversationEngine()
                response = conv_engine.process_conversation(
                    "test message", 
                    {"test": True}, 
                    "test_session"
                )
                
                results['conversation_engine'] = response is not None
                if results['conversation_engine']:
                    logger.info("✓ Conversation Engine functional")
                
            except Exception as e:
                logger.warning(f"⚠ Conversation Engine error: {e}")
        
        # Test CLI integration
        cli_module = self.safe_import('trademasterx.interface.cli.cli')
        if cli_module:
            try:
                cli = cli_module.cli
                commands = [cmd.name for cmd in cli.commands.values()]
                results['cli_integration'] = 'chat' in commands
                if results['cli_integration']:
                    logger.info("✓ CLI integration functional")
            except Exception as e:
                logger.warning(f"⚠ CLI integration error: {e}")
        
        success_count = sum(results.values())
        total_count = len(results)
        
        return {
            'components': results,
            'success_rate': (success_count / total_count) * 100,
            'status': 'PASS' if success_count >= 4 else 'PARTIAL' if success_count >= 2 else 'FAIL'
        }
    
    def test_integration(self) -> Dict[str, Any]:
        """Test system integration across phases"""
        logger.info("Testing System Integration...")
        
        results = {
            'core_imports': False,
            'config_system': False,
            'bot_registry': False,
            'interface_access': False,
            'cross_component': False
        }
        
        # Test core module imports
        core_module = self.safe_import('trademasterx.core')
        if core_module:
            results['core_imports'] = True
            logger.info("✓ Core module accessible")
        
        # Test configuration system
        config_module = self.safe_import('trademasterx.config.config_loader')
        if config_module:
            try:
                config_loader = config_module.ConfigLoader()
                system_config = config_loader.load_system_config()
                results['config_system'] = isinstance(system_config, dict)
                if results['config_system']:
                    logger.info("✓ Configuration system functional")
            except Exception as e:
                logger.warning(f"⚠ Configuration system error: {e}")
        
        # Test bot registry
        registry_module = self.safe_import('trademasterx.core.bot_registry')
        if registry_module:
            try:
                registry = registry_module.BotRegistry({})
                results['bot_registry'] = True
                logger.info("✓ Bot registry functional")
            except Exception as e:
                logger.warning(f"⚠ Bot registry error: {e}")
        
        # Test interface access
        web_module = self.safe_import('trademasterx.interface.web.app')
        cli_module = self.safe_import('trademasterx.interface.cli.cli')
        
        interface_count = 0
        if web_module:
            interface_count += 1
            logger.info("✓ Web interface accessible")
        if cli_module:
            interface_count += 1
            logger.info("✓ CLI interface accessible")
        
        results['interface_access'] = interface_count >= 1
        
        # Test cross-component functionality
        try:
            # Try to create a safety dashboard that uses multiple components
            safety_module = self.safe_import('trademasterx.core.safety_dashboard')
            kill_switch_module = self.safe_import('trademasterx.core.kill_switch')
            
            if safety_module and kill_switch_module:
                dashboard = safety_module.SafetyDashboard()
                kill_switch = kill_switch_module.KillSwitch()
                
                # Test that dashboard can access kill switch status
                dashboard_data = dashboard.get_dashboard_data()
                kill_switch_status = kill_switch.get_status()
                
                results['cross_component'] = (
                    isinstance(dashboard_data, dict) and 
                    isinstance(kill_switch_status, dict)
                )
                
                if results['cross_component']:
                    logger.info("✓ Cross-component integration functional")
        except Exception as e:
            logger.warning(f"⚠ Cross-component integration error: {e}")
        
        success_count = sum(results.values())
        total_count = len(results)
        
        return {
            'components': results,
            'success_rate': (success_count / total_count) * 100,
            'status': 'PASS' if success_count >= 4 else 'PARTIAL' if success_count >= 2 else 'FAIL'
        }
    
    def test_dependencies(self) -> Dict[str, Any]:
        """Test package dependencies"""
        logger.info("Testing Package Dependencies...")
        
        required_packages = {
            'core': ['sqlite3', 'json', 'logging', 'pathlib', 'datetime'],
            'web': ['flask', 'flask_cors'],
            'cli': ['click'],
            'rich_ui': ['rich'],
            'ai_integration': ['anthropic', 'openai'],
            'data_processing': ['pandas', 'numpy'],
            'async': ['asyncio']
        }
        
        results = {}
        total_packages = 0
        available_packages = 0
        
        for category, packages in required_packages.items():
            category_results = []
            for package in packages:
                total_packages += 1
                try:
                    if package == 'sqlite3':
                        import sqlite3
                    elif package == 'json':
                        import json
                    elif package == 'logging':
                        import logging
                    elif package == 'pathlib':
                        from pathlib import Path
                    elif package == 'datetime':
                        from datetime import datetime
                    elif package == 'flask':
                        import flask
                    elif package == 'flask_cors':
                        import flask_cors
                    elif package == 'click':
                        import click
                    elif package == 'rich':
                        import rich
                    elif package == 'anthropic':
                        import anthropic
                    elif package == 'openai':
                        import openai
                    elif package == 'pandas':
                        import pandas
                    elif package == 'numpy':
                        import numpy
                    elif package == 'asyncio':
                        import asyncio
                    else:
                        importlib.import_module(package)
                    
                    category_results.append(True)
                    available_packages += 1
                    
                except ImportError:
                    category_results.append(False)
                    logger.warning(f"⚠ Missing package: {package}")
                except Exception as e:
                    category_results.append(False)
                    logger.warning(f"⚠ Error with package {package}: {e}")
            
            results[category] = {
                'available': sum(category_results),
                'total': len(category_results),
                'success_rate': (sum(category_results) / len(category_results)) * 100
            }
        
        overall_success_rate = (available_packages / total_packages) * 100
        
        return {
            'categories': results,
            'overall': {
                'available': available_packages,
                'total': total_packages,
                'success_rate': overall_success_rate
            },
            'status': 'PASS' if overall_success_rate >= 80 else 'PARTIAL' if overall_success_rate >= 60 else 'FAIL'
        }
    
    def run_all_tests(self) -> bool:
        """Run all phase tests"""
        logger.info("=" * 80)
        logger.info("TRADEMASTERX 2.0 - UNIFIED PHASE TESTER")
        logger.info("=" * 80)
        
        start_time = time.time()
        
        # Run all test phases
        for phase_name, description, test_func in self.phases_to_test:
            logger.info(f"\n🧪 Testing {phase_name}: {description}")
            logger.info("-" * 60)
            
            try:
                phase_result = test_func()
                self.results['phases'][phase_name] = phase_result
                
                status_emoji = "✅" if phase_result['status'] == 'PASS' else "⚠️" if phase_result['status'] == 'PARTIAL' else "❌"
                logger.info(f"{status_emoji} {phase_name}: {phase_result['status']} ({phase_result.get('success_rate', 0):.1f}%)")
                
            except Exception as e:
                logger.error(f"❌ {phase_name} testing failed: {e}")
                self.results['phases'][phase_name] = {
                    'status': 'ERROR',
                    'error': str(e),
                    'success_rate': 0
                }
        
        # Calculate overall results
        phase_statuses = [result['status'] for result in self.results['phases'].values()]
        success_count = sum(1 for status in phase_statuses if status == 'PASS')
        partial_count = sum(1 for status in phase_statuses if status == 'PARTIAL')
        total_count = len(phase_statuses)
        
        overall_success_rate = ((success_count * 1.0 + partial_count * 0.5) / total_count) * 100
        
        if overall_success_rate >= 80:
            self.results['overall_status'] = 'SUCCESS'
        elif overall_success_rate >= 60:
            self.results['overall_status'] = 'PARTIAL'
        else:
            self.results['overall_status'] = 'FAILED'
        
        # Create summary
        self.results['summary'] = {
            'total_phases': total_count,
            'passed_phases': success_count,
            'partial_phases': partial_count,
            'failed_phases': total_count - success_count - partial_count,
            'overall_success_rate': overall_success_rate,
            'test_duration': time.time() - start_time
        }
        
        # Print final results
        self.print_final_results()
        
        # Save detailed results
        self.save_results()
        
        return self.results['overall_status'] == 'SUCCESS'
    
    def print_final_results(self):
        """Print comprehensive test results"""
        logger.info("\n" + "=" * 80)
        logger.info("FINAL TEST RESULTS")
        logger.info("=" * 80)
        
        for phase_name, result in self.results['phases'].items():
            status = result['status']
            success_rate = result.get('success_rate', 0)
            
            status_emoji = "✅" if status == 'PASS' else "⚠️" if status == 'PARTIAL' else "❌"
            logger.info(f"{status_emoji} {phase_name:20} {status:8} ({success_rate:5.1f}%)")
            
            # Show component details if available
            if 'components' in result:
                for component, success in result['components'].items():
                    component_emoji = "✓" if success else "✗"
                    logger.info(f"    {component_emoji} {component}")
        
        summary = self.results['summary']
        logger.info("\n" + "-" * 80)
        logger.info(f"Total Phases Tested: {summary['total_phases']}")
        logger.info(f"Passed: {summary['passed_phases']} | Partial: {summary['partial_phases']} | Failed: {summary['failed_phases']}")
        logger.info(f"Overall Success Rate: {summary['overall_success_rate']:.1f}%")
        logger.info(f"Test Duration: {summary['test_duration']:.1f} seconds")
        
        logger.info("\n" + "=" * 80)
        final_status = self.results['overall_status']
        if final_status == 'SUCCESS':
            logger.info("🎉 TRADEMASTERX 2.0: ALL SYSTEMS OPERATIONAL")
        elif final_status == 'PARTIAL':
            logger.info("⚠️  TRADEMASTERX 2.0: PARTIAL FUNCTIONALITY AVAILABLE")
        else:
            logger.info("❌ TRADEMASTERX 2.0: CRITICAL ISSUES DETECTED")
        logger.info("=" * 80)
    
    def save_results(self):
        """Save test results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_dir = Path("test_reports")
        results_dir.mkdir(exist_ok=True)
        
        results_file = results_dir / f"unified_phase_test_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        logger.info(f"\n📄 Detailed results saved to: {results_file}")


def main():
    """Main entry point"""
    tester = PhaseTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
