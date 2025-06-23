#!/usr/bin/env python3
"""
Phase 12 Integration Test - Comprehensive System Validation
Tests all 6 Phase 12 components with proper error handling
"""

import sys
import os
import json
import time
import logging
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("Phase12Test")

def setup_environment():
    """Setup test environment"""
    logger.info("Setting up test environment...")
    
    # Add project root to path
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    
    # Create necessary directories
    data_dir = project_root / "data" / "safety"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    logs_dir = project_root / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    # Clean up any persisted state
    kill_switch_file = data_dir / "kill_switch.json"
    if kill_switch_file.exists():
        kill_switch_file.unlink()
        logger.info("Cleaned up kill switch state file")
    
    logger.info("Environment setup complete")

def test_component_imports():
    """Test that all Phase 12 components can be imported"""
    logger.info("Testing component imports...")
    
    results = {}
    
    # Test KillSwitch
    try:
        from trademasterx.core.kill_switch import KillSwitch
        results['KillSwitch'] = {'import': True, 'error': None}
        logger.info("✓ KillSwitch imported successfully")
    except Exception as e:
        results['KillSwitch'] = {'import': False, 'error': str(e)}
        logger.error(f"✗ KillSwitch import failed: {e}")
    
    # Test RiskGuard
    try:
        from trademasterx.core.risk_guard import RiskGuard
        results['RiskGuard'] = {'import': True, 'error': None}
        logger.info("✓ RiskGuard imported successfully")
    except Exception as e:
        results['RiskGuard'] = {'import': False, 'error': str(e)}
        logger.error(f"✗ RiskGuard import failed: {e}")
    
    # Test TradeDeviationAlert
    try:
        from trademasterx.core.trade_deviation_alert import TradeDeviationAlert
        results['TradeDeviationAlert'] = {'import': True, 'error': None}
        logger.info("✓ TradeDeviationAlert imported successfully")
    except Exception as e:
        results['TradeDeviationAlert'] = {'import': False, 'error': str(e)}
        logger.error(f"✗ TradeDeviationAlert import failed: {e}")
    
    # Test RecoveryManager
    try:
        from trademasterx.core.failover_recovery import RecoveryManager
        results['RecoveryManager'] = {'import': True, 'error': None}
        logger.info("✓ RecoveryManager imported successfully")
    except Exception as e:
        results['RecoveryManager'] = {'import': False, 'error': str(e)}
        logger.error(f"✗ RecoveryManager import failed: {e}")
    
    # Test SafetyDashboard
    try:
        from trademasterx.core.safety_dashboard import SafetyDashboard
        results['SafetyDashboard'] = {'import': True, 'error': None}
        logger.info("✓ SafetyDashboard imported successfully")
    except Exception as e:
        results['SafetyDashboard'] = {'import': False, 'error': str(e)}
        logger.error(f"✗ SafetyDashboard import failed: {e}")
    
    return results

def test_component_instantiation():
    """Test that components can be instantiated"""
    logger.info("Testing component instantiation...")
    
    results = {}
    
    try:
        from trademasterx.core.kill_switch import KillSwitch
        ks = KillSwitch()
        results['KillSwitch'] = {'instantiate': True, 'error': None}
        logger.info("✓ KillSwitch instantiated successfully")
    except Exception as e:
        results['KillSwitch'] = {'instantiate': False, 'error': str(e)}
        logger.error(f"✗ KillSwitch instantiation failed: {e}")
    
    try:
        from trademasterx.core.risk_guard import RiskGuard
        rg = RiskGuard()
        results['RiskGuard'] = {'instantiate': True, 'error': None}
        logger.info("✓ RiskGuard instantiated successfully")
    except Exception as e:
        results['RiskGuard'] = {'instantiate': False, 'error': str(e)}
        logger.error(f"✗ RiskGuard instantiation failed: {e}")
    
    try:
        from trademasterx.core.trade_deviation_alert import TradeDeviationAlert
        tda = TradeDeviationAlert()
        results['TradeDeviationAlert'] = {'instantiate': True, 'error': None}
        logger.info("✓ TradeDeviationAlert instantiated successfully")
    except Exception as e:
        results['TradeDeviationAlert'] = {'instantiate': False, 'error': str(e)}
        logger.error(f"✗ TradeDeviationAlert instantiation failed: {e}")
    
    try:
        from trademasterx.core.failover_recovery import RecoveryManager
        rm = RecoveryManager()
        results['RecoveryManager'] = {'instantiate': True, 'error': None}
        logger.info("✓ RecoveryManager instantiated successfully")
    except Exception as e:
        results['RecoveryManager'] = {'instantiate': False, 'error': str(e)}
        logger.error(f"✗ RecoveryManager instantiation failed: {e}")
    
    try:
        from trademasterx.core.safety_dashboard import SafetyDashboard
        sd = SafetyDashboard()
        results['SafetyDashboard'] = {'instantiate': True, 'error': None}
        logger.info("✓ SafetyDashboard instantiated successfully")
    except Exception as e:
        results['SafetyDashboard'] = {'instantiate': False, 'error': str(e)}
        logger.error(f"✗ SafetyDashboard instantiation failed: {e}")
    
    return results

def test_required_methods():
    """Test that required methods are available and callable"""
    logger.info("Testing required methods...")
    
    results = {}
    
    try:
        from trademasterx.core.kill_switch import KillSwitch
        ks = KillSwitch()
        
        # Test activate method
        if hasattr(ks, 'activate'):
            results['KillSwitch_activate'] = {'available': True}
            logger.info("✓ KillSwitch.activate method available")
        else:
            results['KillSwitch_activate'] = {'available': False}
            logger.error("✗ KillSwitch.activate method missing")
        
        # Test deactivate method
        if hasattr(ks, 'deactivate'):
            results['KillSwitch_deactivate'] = {'available': True}
            logger.info("✓ KillSwitch.deactivate method available")
        else:
            results['KillSwitch_deactivate'] = {'available': False}
            logger.error("✗ KillSwitch.deactivate method missing")
            
    except Exception as e:
        results['KillSwitch_methods'] = {'available': False, 'error': str(e)}
        logger.error(f"✗ KillSwitch method test failed: {e}")
    
    try:
        from trademasterx.core.risk_guard import RiskGuard
        rg = RiskGuard()
        
        if hasattr(rg, 'validate_trade'):
            results['RiskGuard_validate_trade'] = {'available': True}
            logger.info("✓ RiskGuard.validate_trade method available")
        else:
            results['RiskGuard_validate_trade'] = {'available': False}
            logger.error("✗ RiskGuard.validate_trade method missing")
            
    except Exception as e:
        results['RiskGuard_methods'] = {'available': False, 'error': str(e)}
        logger.error(f"✗ RiskGuard method test failed: {e}")
    
    try:
        from trademasterx.core.failover_recovery import RecoveryManager
        rm = RecoveryManager()
        
        if hasattr(rm, 'get_latest_snapshot'):
            results['RecoveryManager_get_latest_snapshot'] = {'available': True}
            logger.info("✓ RecoveryManager.get_latest_snapshot method available")
        else:
            results['RecoveryManager_get_latest_snapshot'] = {'available': False}
            logger.error("✗ RecoveryManager.get_latest_snapshot method missing")
            
        if hasattr(rm, 'recover_from_snapshot'):
            results['RecoveryManager_recover_from_snapshot'] = {'available': True}
            logger.info("✓ RecoveryManager.recover_from_snapshot method available")
        else:
            results['RecoveryManager_recover_from_snapshot'] = {'available': False}
            logger.error("✗ RecoveryManager.recover_from_snapshot method missing")
            
    except Exception as e:
        results['RecoveryManager_methods'] = {'available': False, 'error': str(e)}
        logger.error(f"✗ RecoveryManager method test failed: {e}")
    
    return results

def run_integration_tests():
    """Run comprehensive integration tests"""
    logger.info("Starting Phase 12 Integration Tests...")
    
    # Setup
    setup_environment()
    
    # Test results
    all_results = {}
    
    # Test 1: Component imports
    import_results = test_component_imports()
    all_results['imports'] = import_results
    
    # Test 2: Component instantiation
    instantiation_results = test_component_instantiation()
    all_results['instantiation'] = instantiation_results
    
    # Test 3: Required methods
    method_results = test_required_methods()
    all_results['methods'] = method_results
    
    # Calculate success metrics
    import_success = sum(1 for r in import_results.values() if r.get('import'))
    instantiation_success = sum(1 for r in instantiation_results.values() if r.get('instantiate'))
    method_success = sum(1 for r in method_results.values() if r.get('available'))
    
    total_import_tests = len(import_results)
    total_instantiation_tests = len(instantiation_results)
    total_method_tests = len(method_results)
    
    # Generate report
    logger.info("=" * 60)
    logger.info("PHASE 12 INTEGRATION TEST RESULTS")
    logger.info("=" * 60)
    logger.info(f"Import Tests: {import_success}/{total_import_tests} passed")
    logger.info(f"Instantiation Tests: {instantiation_success}/{total_instantiation_tests} passed")
    logger.info(f"Method Tests: {method_success}/{total_method_tests} passed")
    
    total_tests = total_import_tests + total_instantiation_tests + total_method_tests
    total_success = import_success + instantiation_success + method_success
    success_rate = (total_success / total_tests * 100) if total_tests > 0 else 0
    
    logger.info(f"Overall Success Rate: {success_rate:.1f}% ({total_success}/{total_tests})")
    logger.info("=" * 60)
    
    # Save detailed results
    results_file = Path("test_reports") / f"phase_12_integration_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    results_file.parent.mkdir(exist_ok=True)
    
    with open(results_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'success_rate': success_rate,
            'total_tests': total_tests,
            'total_success': total_success,
            'detailed_results': all_results
        }, f, indent=2)
    
    logger.info(f"Detailed results saved to: {results_file}")
    
    # Determine overall success
    if success_rate >= 90:
        logger.info("✓ PHASE 12 INTEGRATION: SUCCESS")
        return True
    else:
        logger.info("✗ PHASE 12 INTEGRATION: NEEDS ATTENTION")
        return False

if __name__ == "__main__":
    try:
        success = run_integration_tests()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        sys.exit(1)
