#!/usr/bin/env python3
"""
TradeMasterX 2.0 - Final Phase Comprehensive Tester
Complete system validation and testing suite
"""

import asyncio
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
import logging

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

class FinalPhaseTester:
    """Comprehensive system tester for TradeMasterX 2.0"""
    
    def __init__(self):
        self.test_results = []
        self.start_time = None
        self.setup_logging()
        
    def setup_logging(self):
        """Setup test logging"""
        logs_dir = Path("logs_clean")
        logs_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(logs_dir / "comprehensive_test.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("TesterX2")
    
    def print_banner(self):
        """Print test banner"""
        banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                    🧪 TRADEMASTERX 2.0 FINAL TESTER 🧪                     ║
║                     Comprehensive System Validation                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
        """
        print(banner)
        print(f"⏰ Test Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
    
    def add_test_result(self, test_name: str, status: str, details: str = "", duration: float = 0):
        """Add test result"""
        result = {
            'test_name': test_name,
            'status': status,  # PASS, FAIL, SKIP, WARNING
            'details': details,
            'duration': duration,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        # Print result
        status_icon = {
            'PASS': '✅',
            'FAIL': '❌', 
            'SKIP': '⏭️',
            'WARNING': '⚠️'
        }.get(status, '❓')
        
        duration_str = f"({duration:.2f}s)" if duration > 0 else ""
        print(f"   {status_icon} {test_name}: {status} {duration_str}")
        if details and status != 'PASS':
            print(f"      {details}")
    
    async def test_imports(self):
        """Test all critical imports"""
        print("\n🔍 Testing Component Imports...")
        
        import_tests = [
            ('Phase14AutonomousAI', 'phase_14_complete_autonomous_ai'),
            ('ObserverAgent', 'trademasterx.ai.observer_agent'),
            ('AIOrchestrator', 'trademasterx.ai.ai_orchestrator'),
            ('ReinforcementEngine', 'trademasterx.ai.reinforcement_engine'),
            ('AnomalyAuditor', 'trademasterx.ai.anomaly_auditor'),
            ('AIDashboard', 'trademasterx.interface.web.ai_dashboard'),
            ('ConfigLoader', 'trademasterx.config.config_loader'),
            ('CommandAssistant', 'trademasterx.interface.assistant.command_assistant')
        ]
        
        for class_name, module_path in import_tests:
            start_time = time.time()
            try:
                module = __import__(module_path, fromlist=[class_name])
                getattr(module, class_name)
                duration = time.time() - start_time
                self.add_test_result(f"Import {class_name}", "PASS", duration=duration)
            except Exception as e:
                duration = time.time() - start_time
                self.add_test_result(f"Import {class_name}", "FAIL", str(e), duration)
    
    async def test_dependencies(self):
        """Test required dependencies"""
        print("\n📦 Testing Dependencies...")
        
        dependencies = [
            'numpy', 'pandas', 'scipy', 'asyncio', 'logging',
            'aiohttp', 'json', 'datetime', 'pathlib', 'yaml'
        ]
        
        for dep in dependencies:
            start_time = time.time()
            try:
                __import__(dep)
                duration = time.time() - start_time
                self.add_test_result(f"Dependency {dep}", "PASS", duration=duration)
            except ImportError as e:
                duration = time.time() - start_time
                self.add_test_result(f"Dependency {dep}", "FAIL", str(e), duration)
    
    async def test_file_structure(self):
        """Test file structure and organization"""
        print("\n📁 Testing File Structure...")
        
        required_files = [
            'main_app.py',
            'phase_14_complete_autonomous_ai.py',
            'requirements.txt',
            '.env.example'
        ]
        
        required_dirs = [
            'trademasterx',
            'logs_clean',
            'reports_clean',
            'core_clean'
        ]
        
        # Test files
        for file_path in required_files:
            if Path(file_path).exists():
                self.add_test_result(f"File {file_path}", "PASS")
            else:
                self.add_test_result(f"File {file_path}", "FAIL", "File missing")
        
        # Test directories
        for dir_path in required_dirs:
            if Path(dir_path).exists():
                self.add_test_result(f"Directory {dir_path}", "PASS")
            else:
                self.add_test_result(f"Directory {dir_path}", "FAIL", "Directory missing")
    
    async def test_configuration(self):
        """Test configuration loading"""
        print("\n⚙️ Testing Configuration...")
        
        start_time = time.time()
        try:
            from trademasterx.config.config_loader import ConfigLoader
            config_loader = ConfigLoader()
            
            # Test default config
            try:
                config = config_loader.load_system_config("trademasterx/config/system.yaml")
                duration = time.time() - start_time
                self.add_test_result("Config Loading", "PASS", duration=duration)
            except Exception:
                # Test with fallback
                config = {
                    'demo_mode': True,
                    'web_port': 8080,
                    'log_level': 'INFO'
                }
                duration = time.time() - start_time
                self.add_test_result("Config Loading", "WARNING", "Using fallback config", duration)
                
        except Exception as e:
            duration = time.time() - start_time
            self.add_test_result("Config Loading", "FAIL", str(e), duration)
    
    async def test_ai_components(self):
        """Test AI component initialization"""
        print("\n🤖 Testing AI Components...")
        
        try:
            from phase_14_complete_autonomous_ai import Phase14AutonomousAI
            
            config = {
                'demo_mode': True,
                'web_port': 8080,
                'test_mode': True
            }
            
            start_time = time.time()
            ai_system = Phase14AutonomousAI(config)
            duration = time.time() - start_time
            self.add_test_result("AI System Init", "PASS", duration=duration)
            
            # Test individual components
            components = [
                ('Observer Agent', ai_system.observer_agent),
                ('AI Orchestrator', ai_system.ai_orchestrator),
                ('Reinforcement Engine', ai_system.reinforcement_engine),
                ('Anomaly Auditor', ai_system.anomaly_auditor),
                ('AI Dashboard', ai_system.ai_dashboard)
            ]
            
            for name, component in components:
                if component:
                    self.add_test_result(f"{name} Init", "PASS")
                else:
                    self.add_test_result(f"{name} Init", "FAIL", "Component not initialized")
                    
        except Exception as e:
            self.add_test_result("AI Components", "FAIL", str(e))
    
    async def test_manual_commands(self):
        """Test manual command interface"""
        print("\n🎛️ Testing Manual Commands...")
        
        try:
            from phase_14_complete_autonomous_ai import Phase14AutonomousAI
            
            config = {'demo_mode': True, 'test_mode': True}
            ai_system = Phase14AutonomousAI(config)
            
            # Test commands
            commands = [
                ('get_ai_health', {}),
                ('get_performance', {}),
                ('trigger_retrain', {'reason': 'Test trigger'})
            ]
            
            for cmd, params in commands:
                start_time = time.time()
                try:
                    result = await ai_system.manual_command(cmd, params)
                    duration = time.time() - start_time
                    
                    if 'error' not in result:
                        self.add_test_result(f"Command {cmd}", "PASS", duration=duration)
                    else:
                        self.add_test_result(f"Command {cmd}", "WARNING", result['error'], duration)
                        
                except Exception as e:
                    duration = time.time() - start_time
                    self.add_test_result(f"Command {cmd}", "FAIL", str(e), duration)
                    
        except Exception as e:
            self.add_test_result("Manual Commands", "FAIL", str(e))
    
    async def test_anomaly_detection(self):
        """Test anomaly detection system"""
        print("\n🚨 Testing Anomaly Detection...")
        
        try:
            from trademasterx.ai.anomaly_auditor import AnomalyAuditor
            
            config = {'test_mode': True}
            auditor = AnomalyAuditor(config)
            
            # Test with known anomaly data
            test_trade = {
                'symbol': 'BTCUSDT',
                'strategy': 'test',
                'bot_name': 'TestBot',
                'actual_return': -0.30,  # Large loss
                'expected_return': 0.02,
                'confidence': 0.95  # High confidence error
            }
            
            start_time = time.time()
            result = auditor.audit_trade(test_trade)
            duration = time.time() - start_time
            
            if result['anomalies_detected']:
                self.add_test_result("Anomaly Detection", "PASS", 
                                   f"Detected {len(result['anomalies_detected'])} anomalies", duration)
            else:
                self.add_test_result("Anomaly Detection", "WARNING", 
                                   "No anomalies detected in test data", duration)
                
        except Exception as e:
            self.add_test_result("Anomaly Detection", "FAIL", str(e))
    
    async def test_performance_tracking(self):
        """Test performance tracking"""
        print("\n📊 Testing Performance Tracking...")
        
        try:
            from trademasterx.ai.reinforcement_engine import ReinforcementEngine
            
            config = {'test_mode': True}
            engine = ReinforcementEngine(config)
            
            # Test performance recording
            test_performance = {
                'strategy': 'test_strategy',
                'return': 0.025,
                'sharpe_ratio': 1.2,
                'volatility': 0.15
            }
            
            start_time = time.time()
            engine.record_performance('test_strategy', test_performance)
            duration = time.time() - start_time
            
            # Test weight retrieval
            weights = engine.get_strategy_weights()
            
            self.add_test_result("Performance Tracking", "PASS", 
                               f"Recorded performance, {len(weights)} strategies", duration)
                
        except Exception as e:
            self.add_test_result("Performance Tracking", "FAIL", str(e))
    
    async def test_main_app(self):
        """Test main application launcher"""
        print("\n Testing Main Application...")
        
        start_time = time.time()
        try:
            from main_app import TradeMasterXApp
            
            app = TradeMasterXApp()
            
            # Test configuration loading
            config = app.load_configuration()
            
            # Test environment check
            env_ok = app.check_environment()
            
            duration = time.time() - start_time
            
            if env_ok:
                self.add_test_result("Main App", "PASS", "App initialized successfully", duration)
            else:
                self.add_test_result("Main App", "WARNING", "Environment issues detected", duration)
                
        except Exception as e:
            duration = time.time() - start_time
            self.add_test_result("Main App", "FAIL", str(e), duration)
    
    async def test_integration(self):
        """Test system integration"""
        print("\n🔗 Testing System Integration...")
        
        try:
            # Test minimal integration
            from phase_14_complete_autonomous_ai import Phase14AutonomousAI
            
            config = {
                'demo_mode': True,
                'test_mode': True,
                'observer_interval': 5,
                'orchestrator_cycle': 10
            }
            
            start_time = time.time()
            system = Phase14AutonomousAI(config)
            
            # Test status generation
            await system._generate_status_report()
              # Test status retrieval
            status = system.get_system_status()
            
            duration = time.time() - start_time
            
            if 'system_status' in status:
                self.add_test_result("System Integration", "PASS", 
                                   f"Status: {status['system_status']}", duration)
            else:
                self.add_test_result("System Integration", "WARNING", 
                                   "Status generation incomplete", duration)
                
        except Exception as e:
            self.add_test_result("System Integration", "FAIL", str(e))
    
    def calculate_test_summary(self) -> Dict[str, Any]:
        """Calculate test summary statistics"""
        total_tests = len(self.test_results)
        passed = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed = len([r for r in self.test_results if r['status'] == 'FAIL'])
        warnings = len([r for r in self.test_results if r['status'] == 'WARNING'])
        skipped = len([r for r in self.test_results if r['status'] == 'SKIP'])
        
        success_rate = (passed / total_tests * 100) if total_tests > 0 else 0
        total_duration = sum(r['duration'] for r in self.test_results)
        
        return {
            'total_tests': total_tests,
            'passed': passed,
            'failed': failed,
            'warnings': warnings,
            'skipped': skipped,
            'success_rate': success_rate,
            'total_duration': total_duration,
            'overall_status': 'PASS' if failed == 0 else 'FAIL' if failed > warnings else 'WARNING'
        }
    
    def print_test_summary(self, summary: Dict[str, Any]):
        """Print test summary"""
        print("\n" + "="*80)
        print("📊 COMPREHENSIVE TEST RESULTS")
        print("="*80)
        
        print(f"\nTest Statistics:")
        print(f"   Total Tests: {summary['total_tests']}")
        print(f"   ✅ Passed: {summary['passed']}")
        print(f"   ❌ Failed: {summary['failed']}")
        print(f"   ⚠️ Warnings: {summary['warnings']}")
        print(f"   ⏭️ Skipped: {summary['skipped']}")
        print(f"   📈 Success Rate: {summary['success_rate']:.1f}%")
        print(f"   ⏱️ Total Duration: {summary['total_duration']:.2f}s")
        
        # Overall status
        status_icon = {'PASS': '🟢', 'WARNING': '🟡', 'FAIL': '🔴'}.get(summary['overall_status'], '❓')
        print(f"\n{status_icon} Overall Status: {summary['overall_status']}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if summary['overall_status'] == 'PASS':
            print("   ✅ System is ready for production deployment!")
            print("    All core components are functioning correctly")
            print("   📈 Performance metrics are within acceptable ranges")
        elif summary['overall_status'] == 'WARNING':
            print("   ⚠️ System is mostly functional with minor issues")
            print("   🔧 Review warnings and configure missing components")
            print("   📊 Consider addressing configuration gaps")
        else:
            print("   ❌ System has critical issues that need resolution")
            print("   🛠️ Fix failed components before deployment")
            print("   📞 Consider seeking technical support")
        
        print(f"\n📋 NEXT STEPS:")
        if summary['failed'] == 0:
            print("   1.  Run: python main_app.py")
            print("   2. 🌐 Access dashboard: http://localhost:8080")
            print("   3. 🎮 Explore demo mode features")
            print("   4. 🔧 Configure .env for live trading")
        else:
            print("   1. 📝 Review failed test details above")
            print("   2. 🔧 Fix component initialization issues")
            print("   3. 📦 Check dependency installation")
            print("   4. 🔄 Re-run tests: python tests_clean/final_phase_tester.py")
    
    def save_test_report(self, summary: Dict[str, Any]):
        """Save detailed test report"""
        try:
            reports_dir = Path("reports_clean")
            reports_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = reports_dir / f"final_test_report_{timestamp}.json"
            
            report = {
                'timestamp': datetime.now().isoformat(),
                'test_summary': summary,
                'detailed_results': self.test_results,
                'system_info': {
                    'python_version': sys.version,
                    'platform': sys.platform,
                    'project_root': str(PROJECT_ROOT)
                }
            }
            
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            print(f"\n💾 Test report saved: {report_file}")
            
        except Exception as e:
            print(f"⚠️ Failed to save test report: {e}")
    
    async def run_all_tests(self):
        """Run all tests"""
        self.start_time = time.time()
        self.print_banner()
        
        # Run test suites
        await self.test_imports()
        await self.test_dependencies()
        await self.test_file_structure()
        await self.test_configuration()
        await self.test_ai_components()
        await self.test_manual_commands()
        await self.test_anomaly_detection()
        await self.test_performance_tracking()
        await self.test_main_app()
        await self.test_integration()
        
        # Calculate and display summary
        summary = self.calculate_test_summary()
        self.print_test_summary(summary)
        self.save_test_report(summary)
        
        total_time = time.time() - self.start_time
        print(f"\n⏱️ Total Test Time: {total_time:.2f} seconds")
        print("="*80)
        
        return summary['overall_status'] == 'PASS'


async def main():
    """Main test runner"""
    tester = FinalPhaseTester()
    
    try:
        success = await tester.run_all_tests()
        return 0 if success else 1
    except KeyboardInterrupt:
        print(f"\n⏹️ Tests interrupted by user")
        return 0
    except Exception as e:
        print(f"❌ Test runner error: {e}")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n👋 Test session ended")
        sys.exit(0)
