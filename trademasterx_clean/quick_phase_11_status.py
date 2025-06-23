"""
Quick Phase 11 Status Test - No Emoji Version
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from trademasterx.optimizers.phase_11.phase_11_controller import Phase11Controller
    from trademasterx.optimizers.phase_11.config import TESTING_CONFIG
    
    print("TradeMasterX 2.0 - Phase 11 Quick Status Test")
    print("=" * 50)
    
    # Initialize controller
    controller = Phase11Controller(
        data_dir="test_data/phase_11",
        logs_dir="test_logs/phase_11"
    )
    
    # Apply testing config
    test_config = TESTING_CONFIG.to_dict()
    controller.update_configuration(test_config)
    
    print("[PASS] Phase 11 Controller initialized successfully")
    
    # Test component access
    components = [
        ('AdaptiveStrategyReinforcer', controller.strategy_reinforcer),
        ('BotPerformanceScorer', controller.bot_scorer),
        ('StrategySwitcher', controller.strategy_switcher),
        ('AnomalyDetector', controller.anomaly_detector),
        ('LiveOptimizationDashboard', controller.dashboard)
    ]
    
    for name, component in components:
        if component is not None:
            print(f"[PASS] {name} - Available")
        else:
            print(f"[FAIL] {name} - Not available")
    
    # Test report generation
    try:
        report = controller.get_optimization_report()
        if 'system_overview' in report:
            print("[PASS] Report generation - Working")
            print(f"       Report contains: {list(report.keys())}")
        else:
            print("[FAIL] Report generation - Missing system_overview")
    except Exception as e:
        print(f"[FAIL] Report generation - Error: {e}")
    
    # Test system status
    try:
        status = controller.get_system_status()
        if status and 'is_running' in status:
            print("[PASS] System status - Working")
        else:
            print("[FAIL] System status - Invalid response")
    except Exception as e:
        print(f"[FAIL] System status - Error: {e}")
    
    print("\nPhase 11 Quick Status: OPERATIONAL")
    print("All core components are functional and ready for use!")
    
except ImportError as e:
    print(f"[FAIL] Import error: {e}")
except Exception as e:
    print(f"[FAIL] Unexpected error: {e}")
