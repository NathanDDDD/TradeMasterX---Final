#!/usr/bin/env python3
"""
TradeMasterX 2.0 - Production Package Validator
Validates the complete production package for deployment
"""

import sys
import os
import logging
import importlib.util
from pathlib import Path
from typing import Dict, List, Any, Tuple

class PackageValidator:
    """Validates the production package integrity and functionality"""
    
    def __init__(self):
        self.package_root = Path(__file__).parent
        self.results = {}
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging for validation"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('PackageValidator')
    
    def validate_structure(self) -> bool:
        """Validate package directory structure"""
        self.logger.info("🔍 Validating package structure...")
        
        required_files = [
            'launcher.py',
            'requirements.txt',
            'PRODUCTION_README.md',
            'trademasterx/__init__.py',
            'trademasterx/core/__init__.py',
            'trademasterx/core/kill_switch.py',
            'trademasterx/core/safety_dashboard.py',
            'trademasterx/interface/assistant/command_assistant.py',
            'trademasterx/interface/cli/cli.py'
        ]
        
        missing_files = []
        for file_path in required_files:
            full_path = self.package_root / file_path
            if not full_path.exists():
                missing_files.append(file_path)
        
        if missing_files:
            self.logger.error(f"❌ Missing files: {missing_files}")
            return False
        
        self.logger.info("✅ Package structure validation passed")
        return True
    
    def validate_imports(self) -> bool:
        """Validate that all critical imports work"""
        self.logger.info("🔍 Validating critical imports...")
        
        # Add package to path
        sys.path.insert(0, str(self.package_root))
        
        critical_imports = [
            'trademasterx.core.kill_switch',
            'trademasterx.core.safety_dashboard',
            'trademasterx.core.risk_guard',
            'trademasterx.interface.assistant.command_assistant',
            'trademasterx.interface.cli.cli'
        ]
        
        failed_imports = []
        for module_name in critical_imports:
            try:
                spec = importlib.util.find_spec(module_name)
                if spec is None:
                    failed_imports.append(f"{module_name} (not found)")
                    continue
                    
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                self.logger.info(f"✅ Successfully imported: {module_name}")
                
            except Exception as e:
                failed_imports.append(f"{module_name} ({str(e)})")
                self.logger.error(f"❌ Failed to import {module_name}: {e}")
        
        if failed_imports:
            self.logger.error(f"❌ Failed imports: {failed_imports}")
            return False
        
        self.logger.info("✅ Import validation passed")
        return True
    
    def validate_launcher(self) -> bool:
        """Validate launcher script functionality"""
        self.logger.info("🔍 Validating launcher script...")
        
        launcher_path = self.package_root / 'launcher.py'
        
        try:
            # Check if launcher can be loaded
            spec = importlib.util.spec_from_file_location("launcher", launcher_path)
            launcher_module = importlib.util.module_from_spec(spec)
            
            # Add to sys.modules to prevent import issues
            sys.modules["launcher"] = launcher_module
            spec.loader.exec_module(launcher_module)
            
            # Check if main functions exist
            required_functions = ['main', 'show_help']
            missing_functions = []
            
            for func_name in required_functions:
                if not hasattr(launcher_module, func_name):
                    missing_functions.append(func_name)
            
            if missing_functions:
                self.logger.error(f"❌ Missing launcher functions: {missing_functions}")
                return False
            
            self.logger.info("✅ Launcher validation passed")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Launcher validation failed: {e}")
            return False
    
    def validate_configuration(self) -> bool:
        """Validate configuration files and defaults"""
        self.logger.info("🔍 Validating configuration...")
        
        try:
            # Add package to path
            sys.path.insert(0, str(self.package_root))
            
            from trademasterx.config.config_loader import ConfigLoader
            config_loader = ConfigLoader()
            
            # Test configuration loading
            config = config_loader.get_system_config()
            
            required_sections = ['kill_switch', 'risk_guard', 'safety']
            missing_sections = []
            
            for section in required_sections:
                if section not in config:
                    missing_sections.append(section)
            
            if missing_sections:
                self.logger.warning(f"⚠️ Missing config sections (using defaults): {missing_sections}")
            
            self.logger.info("✅ Configuration validation passed")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Configuration validation failed: {e}")
            return False
    
    def validate_safety_systems(self) -> bool:
        """Validate core safety systems functionality"""
        self.logger.info("🔍 Validating safety systems...")
        
        try:
            # Add package to path
            sys.path.insert(0, str(self.package_root))
            
            from trademasterx.core.kill_switch import KillSwitch
            from trademasterx.core.safety_dashboard import SafetyDashboard
            from trademasterx.core.risk_guard import RiskGuard
            
            # Test kill switch
            kill_switch = KillSwitch()
            kill_switch_status = kill_switch.get_status()
            
            if 'kill_switch_active' not in kill_switch_status:
                self.logger.error("❌ Kill switch status invalid")
                return False
            
            # Test safety dashboard
            safety_dashboard = SafetyDashboard()
            
            # Test risk guard
            risk_guard = RiskGuard()
            
            self.logger.info("✅ Safety systems validation passed")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Safety systems validation failed: {e}")
            return False
    
    def run_validation(self) -> Dict[str, Any]:
        """Run complete package validation"""
        self.logger.info(" Starting TradeMasterX 2.0 Production Package Validation")
        self.logger.info("=" * 70)
        
        validation_tests = [
            ('Structure', self.validate_structure),
            ('Imports', self.validate_imports),
            ('Launcher', self.validate_launcher),
            ('Configuration', self.validate_configuration),
            ('Safety Systems', self.validate_safety_systems)
        ]
        
        results = {}
        total_tests = len(validation_tests)
        passed_tests = 0
        
        for test_name, test_func in validation_tests:
            self.logger.info(f"\n🧪 Running {test_name} validation...")
            try:
                result = test_func()
                results[test_name] = {
                    'status': 'PASS' if result else 'FAIL',
                    'success': result
                }
                if result:
                    passed_tests += 1
                    self.logger.info(f"✅ {test_name}: PASS")
                else:
                    self.logger.error(f"❌ {test_name}: FAIL")
                    
            except Exception as e:
                results[test_name] = {
                    'status': 'ERROR',
                    'success': False,
                    'error': str(e)
                }
                self.logger.error(f"💥 {test_name}: ERROR - {e}")
        
        # Calculate success rate
        success_rate = (passed_tests / total_tests) * 100
        
        # Final summary
        self.logger.info("\n" + "=" * 70)
        self.logger.info("VALIDATION SUMMARY")
        self.logger.info("=" * 70)
        
        for test_name, result in results.items():
            status_emoji = "✅" if result['success'] else "❌"
            self.logger.info(f"{status_emoji} {test_name}: {result['status']}")
        
        self.logger.info(f"\nTotal Tests: {total_tests}")
        self.logger.info(f"Passed: {passed_tests}")
        self.logger.info(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            self.logger.info("\n🎉 PACKAGE VALIDATION: SUCCESS")
            self.logger.info("TradeMasterX 2.0 is ready for deployment!")
        else:
            self.logger.error("\n❌ PACKAGE VALIDATION: FAILED")
            self.logger.error("Please fix the issues before deployment.")
        
        return {
            'success_rate': success_rate,
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'results': results,
            'ready_for_deployment': success_rate >= 80
        }

def main():
    """Main entry point for package validation"""
    validator = PackageValidator()
    results = validator.run_validation()
    
    # Exit with appropriate code
    sys.exit(0 if results['ready_for_deployment'] else 1)

if __name__ == "__main__":
    main()
