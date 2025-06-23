"""
TradeMasterX 2.0 - System Validation Script
Quick validation of all components before launch
"""

import sys
import traceback
from pathlib import Path

def validate_imports():
    """Validate all core module imports"""
    print("Validating module imports...")
    
    try:
        # Test core imports
        from core.assessment.readiness_estimator import LiveReadinessEstimator
        from core.execution.trade_executor import TestnetTradeExecutor
        from core.monitoring.real_time_monitor import RealTimeMonitor
        from core.training.continuous_retrainer import ContinuousRetrainer
        from core.tuning.dynamic_tuner import DynamicSystemTuner
        from core.reporting.daily_reporter import DailyReporter
        from trademasterx.core.validation.retraining_validator import RetrainingValidator
        
        print("All core modules imported successfully")
        return True
        
    except ImportError as e:
        print(f"Import error: {e}")
        traceback.print_exc()
        return False

def validate_config():
    """Validate configuration files"""
    print("Validating configuration...")
    
    config_file = Path("config/master_config.json")
    if not config_file.exists():
        print("Missing: config/master_config.json")
        return False
    
    try:
        import json
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        required_keys = ['bybit_testnet', 'trading', 'paths']
        for key in required_keys:
            if key not in config:
                print(f"Missing config key: {key}")
                return False
        
        print("Configuration valid")
        return True
        
    except Exception as e:
        print(f"Config validation error: {e}")
        return False

def validate_directories():
    """Validate required directories exist"""
    print("Validating directory structure...")
    
    required_dirs = [
        "core/assessment",
        "core/execution", 
        "core/monitoring",
        "core/training",
        "core/tuning",
        "core/reporting",
        "trademasterx/core/validation",
        "launch",
        "config"
    ]
    
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            print(f"Missing directory: {dir_path}")
            return False
    
    print("Directory structure valid")
    return True

def main():
    """Main validation function"""
    print("TradeMasterX 2.0 - System Validation")
    print("=" * 50)
    
    all_valid = True
    
    # Validate directories
    if not validate_directories():
        all_valid = False
    
    # Validate configuration
    if not validate_config():
        all_valid = False
    
    # Validate imports
    if not validate_imports():
        all_valid = False
    
    print("=" * 50)
    if all_valid:
        print("SYSTEM VALIDATION PASSED")
        print(" Ready to launch TradeMasterX 2.0!")
        print("\nNext steps:")
        print("1. Configure Bybit testnet API credentials")
        print("2. Run: python launch_trademasterx.py")
    else:
        print("SYSTEM VALIDATION FAILED")
        print("Please fix the issues above before launching.")
    
    return all_valid

if __name__ == "__main__":
    main()
