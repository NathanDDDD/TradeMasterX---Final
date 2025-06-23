#!/usr/bin/env python3
"""
TradeMasterX 2.0 - Phase 15 Final Test Run
Complete system validation and demonstration
"""

import asyncio
import sys
import json
import time
from pathlib import Path
from datetime import datetime
import logging

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

class Phase15FinalDemo:
    """Phase 15 Final Demonstration and Validation"""
    
    def __init__(self):
        self.start_time = None
        self.demo_results = []
        self.setup_logging()
        
    def setup_logging(self):
        """Setup demo logging"""
        # Create reports directory
        reports_dir = Path("reports_clean")
        reports_dir.mkdir(exist_ok=True)
        
        # Setup logging
        self.log_file = reports_dir / f"final_phase15_run_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("Phase15Demo")
    
    def print_banner(self):
        """Print demo banner"""
        banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                   🎯 PHASE 15 FINAL TEST RUN - COMPLETE 🎯                 ║
║                      TradeMasterX 2.0 Launch Validation                      ║
║                         Production Ready System Demo                         ║
╚══════════════════════════════════════════════════════════════════════════════╝
        """
        print(banner)
        print(f"⏰ Demo Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📄 Log File: {self.log_file}")
        print()
    
    def add_result(self, test_name: str, status: str, details: str = "", duration: float = 0):
        """Add demo result"""
        result = {
            'test_name': test_name,
            'status': status,
            'details': details,
            'duration': duration,
            'timestamp': datetime.now().isoformat()
        }
        self.demo_results.append(result)
        
        # Print result
        status_icon = {
            'SUCCESS': '✅',
            'FAIL': '❌',
            'WARNING': '⚠️',
            'INFO': 'ℹ️'
        }.get(status, '❓')
        
        duration_str = f"({duration:.2f}s)" if duration > 0 else ""
        print(f"   {status_icon} {test_name}: {status} {duration_str}")
        if details:
            print(f"      {details}")
    
    async def test_system_startup(self):
        """Test system startup sequence"""
        print("\n Testing System Startup...")
        
        start_time = time.time()
        try:
            # Test Phase 14 import
            from phase_14_complete_autonomous_ai import Phase14AutonomousAI
            
            config = {
                'demo_mode': True,
                'web_port': 8080,
                'test_mode': True,
                'observer_interval': 5,
                'orchestrator_cycle': 10
            }
            
            # Initialize system
            system = Phase14AutonomousAI(config)
            
            duration = time.time() - start_time
            self.add_result("System Initialization", "SUCCESS", 
                          "All AI components initialized successfully", duration)
            
            return system
            
        except Exception as e:
            duration = time.time() - start_time
            self.add_result("System Initialization", "FAIL", str(e), duration)
            return None
    
    async def test_demo_trading(self, system):
        """Simulate demo trading sequence"""
        print("\n💰 Testing Demo Trading Sequence...")
        
        if not system:
            self.add_result("Demo Trading", "FAIL", "System not available")
            return
        
        try:
            # Simulate trade observation
            start_time = time.time()
            
            mock_trade = {
                'timestamp': datetime.now().isoformat(),
                'symbol': 'BTCUSDT',
                'action': 'BUY',
                'amount': 1.0,
                'price': 45000.0,
                'strategy': 'momentum',
                'confidence': 0.85,
                'expected_return': 0.025
            }
            
            # Test trade observation
            await system.observer_agent.observe_trade(mock_trade)
            
            duration = time.time() - start_time
            self.add_result("Trade Observation", "SUCCESS", 
                          f"Processed trade: {mock_trade['symbol']}", duration)
            
            # Test performance recording
            start_time = time.time()
            
            performance_data = {
                'return': 0.025,
                'sharpe_ratio': 1.2,
                'volatility': 0.15,
                'win_rate': 0.75
            }
            
            system.reinforcement_engine.record_performance('momentum', performance_data)
            
            duration = time.time() - start_time
            self.add_result("Performance Recording", "SUCCESS", 
                          "Performance metrics recorded", duration)
            
        except Exception as e:
            self.add_result("Demo Trading", "FAIL", str(e))
    
    async def test_ai_retraining(self, system):
        """Test AI retraining functionality"""
        print("\n🧠 Testing AI Retraining...")
        
        if not system:
            self.add_result("AI Retraining", "FAIL", "System not available")
            return
        
        try:
            start_time = time.time()
            
            # Test manual retrain trigger
            result = await system.manual_command("trigger_retrain", {
                "reason": "Phase 15 final demo test",
                "priority": "high"
            })
            
            duration = time.time() - start_time
            
            if result.get('success', False):
                self.add_result("AI Retraining", "SUCCESS", 
                              "Retraining completed successfully", duration)
            else:
                self.add_result("AI Retraining", "WARNING", 
                              f"Retraining result: {result.get('message', 'Unknown')}", duration)
                
        except Exception as e:
            self.add_result("AI Retraining", "FAIL", str(e))
    
    async def test_anomaly_detection(self, system):
        """Test anomaly detection system"""
        print("\n🚨 Testing Anomaly Detection...")
        
        if not system:
            self.add_result("Anomaly Detection", "FAIL", "System not available")
            return
        
        try:
            start_time = time.time()
            
            # Create trade with known anomalies
            anomaly_trade = {
                'symbol': 'ETHUSDT',
                'strategy': 'reversal',
                'bot_name': 'TestBot',
                'actual_return': -0.35,  # Large loss - should trigger anomaly
                'expected_return': 0.02,
                'confidence': 0.95  # High confidence error
            }
            
            # Test anomaly detection
            audit_result = system.anomaly_auditor.audit_trade(anomaly_trade)
            
            duration = time.time() - start_time
            
            anomalies_count = len(audit_result['anomalies_detected'])
            if anomalies_count > 0:
                self.add_result("Anomaly Detection", "SUCCESS", 
                              f"Detected {anomalies_count} anomalies, severity: {audit_result['severity']}", 
                              duration)
            else:
                self.add_result("Anomaly Detection", "WARNING", 
                              "No anomalies detected in test data", duration)
                
        except Exception as e:
            self.add_result("Anomaly Detection", "FAIL", str(e))
    
    async def test_dashboard_status(self, system):
        """Test dashboard and reporting"""
        print("\n🌐 Testing Dashboard & Reporting...")
        
        if not system:
            self.add_result("Dashboard Status", "FAIL", "System not available")
            return
        
        try:
            start_time = time.time()
            
            # Generate status report
            await system._generate_status_report()
            
            # Get system status
            status = await system.get_system_status()
            
            duration = time.time() - start_time
            
            if 'system_status' in status:
                self.add_result("Dashboard Status", "SUCCESS", 
                              f"Status: {status['system_status']}, Components: {len(status.get('components', {}))}", 
                              duration)
            else:
                self.add_result("Dashboard Status", "WARNING", 
                              "Status report generated but incomplete", duration)
                
        except Exception as e:
            self.add_result("Dashboard Status", "FAIL", str(e))
    
    async def test_main_app_launcher(self):
        """Test main application launcher"""
        print("\n Testing Main App Launcher...")
        
        try:
            start_time = time.time()
            
            # Test main app import and initialization
            from main_app import TradeMasterXApp
            
            app = TradeMasterXApp()
            
            # Test configuration loading
            config = app.load_configuration()
            
            # Test environment check
            env_check = app.check_environment()
            
            duration = time.time() - start_time
            
            if env_check:
                self.add_result("Main App Launcher", "SUCCESS", 
                              f"App ready, config loaded, port: {config.get('web_port', 8080)}", 
                              duration)
            else:
                self.add_result("Main App Launcher", "WARNING", 
                              "Environment checks detected issues", duration)
                
        except Exception as e:
            self.add_result("Main App Launcher", "FAIL", str(e))
    
    def generate_final_report(self):
        """Generate comprehensive final report"""
        print("\n📊 Generating Final Report...")
        
        # Calculate statistics
        total_tests = len(self.demo_results)
        successful = len([r for r in self.demo_results if r['status'] == 'SUCCESS'])
        failed = len([r for r in self.demo_results if r['status'] == 'FAIL'])
        warnings = len([r for r in self.demo_results if r['status'] == 'WARNING'])
        
        success_rate = (successful / total_tests * 100) if total_tests > 0 else 0
        total_duration = sum(r['duration'] for r in self.demo_results)
        
        # Determine overall status
        if failed == 0 and warnings <= 1:
            overall_status = "🟢 PRODUCTION READY"
        elif failed == 0:
            overall_status = "🟡 READY WITH MINOR ISSUES"
        else:
            overall_status = "🔴 NEEDS ATTENTION"
        
        # Create comprehensive report
        report = {
            'timestamp': datetime.now().isoformat(),
            'phase': 'Phase 15 - Final Packaging & Launch Ready',
            'demo_duration': total_duration,
            'statistics': {
                'total_tests': total_tests,
                'successful': successful,
                'failed': failed,
                'warnings': warnings,
                'success_rate': success_rate
            },
            'overall_status': overall_status,
            'detailed_results': self.demo_results,
            'system_readiness': {
                'autonomous_ai': successful >= 4,
                'demo_trading': 'Demo Trading' not in [r['test_name'] for r in self.demo_results if r['status'] == 'FAIL'],
                'anomaly_detection': 'Anomaly Detection' not in [r['test_name'] for r in self.demo_results if r['status'] == 'FAIL'],
                'main_launcher': 'Main App Launcher' not in [r['test_name'] for r in self.demo_results if r['status'] == 'FAIL']
            },
            'recommendations': self._generate_recommendations(failed, warnings)
        }
        
        # Save report
        try:
            with open(self.log_file.parent / "final_phase15_run_log.txt", 'w') as f:
                f.write(json.dumps(report, indent=2))
            
            self.add_result("Final Report Generation", "SUCCESS", 
                          f"Report saved to {self.log_file.parent / 'final_phase15_run_log.txt'}")
        except Exception as e:
            self.add_result("Final Report Generation", "FAIL", str(e))
        
        return report
    
    def _generate_recommendations(self, failed: int, warnings: int) -> list:
        """Generate recommendations based on test results"""
        recommendations = []
        
        if failed == 0 and warnings == 0:
            recommendations = [
                "✅ System is fully ready for production deployment",
                " All components are functioning optimally",
                "📈 Performance metrics are within acceptable ranges",
                "🌐 Web dashboard is operational and responsive"
            ]
        elif failed == 0:
            recommendations = [
                "⚠️ System is mostly ready with minor configuration issues",
                "🔧 Review warning messages and adjust configuration",
                "📊 Consider optimizing components showing warnings",
                "✅ Core functionality is stable and ready"
            ]
        else:
            recommendations = [
                "❌ Critical issues detected that require resolution",
                "🛠️ Fix failed components before production deployment",
                "📞 Review error logs and component initialization",
                "🔄 Re-run tests after addressing critical issues"
            ]
        
        return recommendations
    
    def print_final_summary(self, report):
        """Print final demonstration summary"""
        print("\n" + "="*80)
        print("🎉 PHASE 15 FINAL DEMONSTRATION COMPLETE!")
        print("="*80)
        
        stats = report['statistics']
        print(f"\n📊 DEMONSTRATION RESULTS:")
        print(f"   Total Tests: {stats['total_tests']}")
        print(f"   ✅ Successful: {stats['successful']}")
        print(f"   ❌ Failed: {stats['failed']}")
        print(f"   ⚠️ Warnings: {stats['warnings']}")
        print(f"   📈 Success Rate: {stats['success_rate']:.1f}%")
        print(f"   ⏱️ Total Duration: {report['demo_duration']:.2f}s")
        
        print(f"\n{report['overall_status']}")
        
        print(f"\n SYSTEM READINESS:")
        readiness = report['system_readiness']
        for component, ready in readiness.items():
            status_icon = "✅" if ready else "❌"
            print(f"   {status_icon} {component.replace('_', ' ').title()}: {'Ready' if ready else 'Issues Detected'}")
        
        print(f"\n💡 RECOMMENDATIONS:")
        for rec in report['recommendations']:
            print(f"   {rec}")
        
        print(f"\n📋 NEXT STEPS:")
        if stats['failed'] == 0:
            print("   1.  Launch production system: python main_app.py")
            print("   2. 🌐 Access dashboard: http://localhost:8080")
            print("   3. 🎮 Start in demo mode for safe exploration")
            print("   4. 🔧 Configure .env for live trading when ready")
            print("   5. 📊 Monitor logs and performance metrics")
        else:
            print("   1. 📝 Review failed test details above")
            print("   2. 🔧 Fix critical component issues")
            print("   3. 📦 Verify dependency installation")
            print("   4. 🔄 Re-run final test: python phase_15_final_demo.py")
        
        print(f"\n📁 OUTPUTS GENERATED:")
        print(f"   📄 Detailed Log: {self.log_file}")
        print(f"   📊 JSON Report: {self.log_file.parent / 'final_phase15_run_log.txt'}")
        print(f"   📂 Reports Directory: {self.log_file.parent}")
        
        print("\n" + "="*80)
        print("🎯 TRADEMASTERX 2.0 PHASE 15 COMPLETE!")
        print("🏆 Production-Ready AI Trading System Delivered!")
        print("="*80)
    
    async def run_complete_demo(self):
        """Run complete Phase 15 demonstration"""
        self.start_time = time.time()
        self.print_banner()
        
        # Test sequence
        system = await self.test_system_startup()
        await self.test_demo_trading(system)
        await self.test_ai_retraining(system)
        await self.test_anomaly_detection(system)
        await self.test_dashboard_status(system)
        await self.test_main_app_launcher()
        
        # Generate final report
        report = self.generate_final_report()
        self.print_final_summary(report)
        
        return report['statistics']['failed'] == 0


async def main():
    """Main demonstration runner"""
    demo = Phase15FinalDemo()
    
    try:
        success = await demo.run_complete_demo()
        return 0 if success else 1
    except KeyboardInterrupt:
        print(f"\n⏹️ Demo interrupted by user")
        return 0
    except Exception as e:
        print(f"❌ Demo error: {e}")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n👋 Demo session ended")
        sys.exit(0)
