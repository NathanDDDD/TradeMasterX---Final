#!/usr/bin/env python3
"""
TradeMasterX 2.0 - Phase 14: Quick Status Checker
Quick verification of AI Copilot Assistant components
"""

import sys
import os
from pathlib import Path

# Add workspace to path
sys.path.insert(0, str(Path(__file__).parent))

def check_phase14_status():
    """Quick check of Phase 14 AI Copilot components"""
    print("TradeMasterX 2.0 - Phase 14: AI Copilot Status Check")
    print("=" * 60)
    
    results = {
        'components': {},
        'files': {},
        'dependencies': {},
        'overall_status': 'UNKNOWN'
    }
    
    # Check component imports
    print("\n🧪 Testing Component Imports...")
    
    try:
        from package.trademasterx.optimizers.phase_14 import AICopilot
        results['components']['AICopilot'] = 'PASS'
        print("✅ AICopilot - Main controller")
    except ImportError as e:
        results['components']['AICopilot'] = f'FAIL: {e}'
        print(f"❌ AICopilot - {e}")
    
    try:
        from package.trademasterx.optimizers.phase_14 import RealTimeMonitor
        results['components']['RealTimeMonitor'] = 'PASS'
        print("✅ RealTimeMonitor - Monitoring system")
    except ImportError as e:
        results['components']['RealTimeMonitor'] = f'FAIL: {e}'
        print(f"❌ RealTimeMonitor - {e}")
    
    try:
        from package.trademasterx.optimizers.phase_14 import IntelligentAnalyzer
        results['components']['IntelligentAnalyzer'] = 'PASS'
        print("✅ IntelligentAnalyzer - Pattern recognition")
    except ImportError as e:
        results['components']['IntelligentAnalyzer'] = f'FAIL: {e}'
        print(f"❌ IntelligentAnalyzer - {e}")
    
    try:
        from package.trademasterx.optimizers.phase_14 import FeedbackGenerator
        results['components']['FeedbackGenerator'] = 'PASS'
        print("✅ FeedbackGenerator - Natural language feedback")
    except ImportError as e:
        results['components']['FeedbackGenerator'] = f'FAIL: {e}'
        print(f"❌ FeedbackGenerator - {e}")
    
    # Check file existence
    print("\n📁 Checking Phase 14 Files...")
    
    phase14_dir = Path("package/trademasterx/optimizers/phase_14")
    required_files = [
        'ai_copilot.py',
        'real_time_monitor.py',
        'intelligent_analyzer.py',
        'feedback_generator.py',
        '__init__.py'
    ]
    
    for file_name in required_files:
        file_path = phase14_dir / file_name
        if file_path.exists():
            results['files'][file_name] = 'EXISTS'
            print(f"✅ {file_name}")
        else:
            results['files'][file_name] = 'MISSING'
            print(f"❌ {file_name} - File not found")
    
    # Check dependencies
    print("\n📦 Checking Dependencies...")
    
    dependencies = [
        ('numpy', 'np'),
        ('pandas', 'pd'),
        ('sqlite3', None),
        ('asyncio', None),
        ('logging', None),
        ('datetime', None)
    ]
    
    for dep_name, import_alias in dependencies:
        try:
            if import_alias:
                exec(f"import {dep_name} as {import_alias}")
            else:
                exec(f"import {dep_name}")
            results['dependencies'][dep_name] = 'AVAILABLE'
            print(f"✅ {dep_name}")
        except ImportError:
            results['dependencies'][dep_name] = 'MISSING'
            print(f"❌ {dep_name} - Not available")
    
    # Check integration dependencies
    print("\n🔗 Checking Integration Dependencies...")
    
    integrations = [
        ('trademasterx.core.bot_registry', 'BaseBot'),
        ('trademasterx.optimizers.phase_11.anomaly_detector', 'AnomalyDetector'),
        ('trademasterx.interface.assistant.conversation_engine', 'ConversationEngine'),
        ('trademasterx.bots.analytics.analytics_bot', 'AnalyticsBot')
    ]
    
    integration_results = {}
    for module_path, class_name in integrations:
        try:
            module = __import__(module_path, fromlist=[class_name])
            getattr(module, class_name)
            integration_results[module_path] = 'AVAILABLE'
            print(f"✅ {class_name} ({module_path})")
        except (ImportError, AttributeError) as e:
            integration_results[module_path] = f'UNAVAILABLE: {e}'
            print(f"⚠️ {class_name} - {e}")
    
    results['integrations'] = integration_results
    
    # Calculate overall status
    component_passes = len([v for v in results['components'].values() if v == 'PASS'])
    file_exists = len([v for v in results['files'].values() if v == 'EXISTS'])
    dep_available = len([v for v in results['dependencies'].values() if v == 'AVAILABLE'])
    
    total_components = len(results['components'])
    total_files = len(results['files'])
    total_deps = len(results['dependencies'])
    
    # Status calculation
    if component_passes == total_components and file_exists == total_files:
        if dep_available >= total_deps * 0.8:  # 80% of dependencies
            results['overall_status'] = 'READY'
        else:
            results['overall_status'] = 'PARTIAL'
    elif component_passes >= total_components * 0.5:  # 50% of components
        results['overall_status'] = 'PARTIAL'
    else:
        results['overall_status'] = 'NOT_READY'
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 PHASE 14 STATUS SUMMARY")
    print("=" * 60)
    
    print(f"Components: {component_passes}/{total_components} working")
    print(f"Files: {file_exists}/{total_files} present")
    print(f"Dependencies: {dep_available}/{total_deps} available")
    
    # Overall status
    status_emoji = {
        'READY': '🟢',
        'PARTIAL': '🟡',
        'NOT_READY': '🔴',
        'UNKNOWN': '⚪'
    }
    
    print(f"\nOverall Status: {status_emoji.get(results['overall_status'], '⚪')} {results['overall_status']}")
    
    if results['overall_status'] == 'READY':
        print("\n✅ Phase 14 AI Copilot is ready for use!")
        print("You can run:")
        print("  • python test_phase_14_integration.py - Full integration tests")
        print("  • python demo_phase_14.py - Interactive demonstration")
        
    elif results['overall_status'] == 'PARTIAL':
        print("\n⚠️ Phase 14 AI Copilot is partially ready")
        print("Some components may not work correctly.")
        print("Check the failed imports above.")
        
    else:
        print("\n❌ Phase 14 AI Copilot is not ready")
        print("Critical components are missing or not working.")
        print("Please check the installation and dependencies.")
    
    # Recommendations
    print(f"\n💡 Recommendations:")
    
    if results['overall_status'] != 'READY':
        if any('FAIL' in v or 'MISSING' in v for v in results['files'].values()):
            print("  • Ensure all Phase 14 files are present")
        
        if any('FAIL' in str(v) for v in results['components'].values()):
            print("  • Check Python import paths and module structure")
        
        if any('MISSING' in v for v in results['dependencies'].values()):
            print("  • Install missing dependencies with pip")
        
        print("  • Run the full integration test for detailed diagnostics")
    
    else:
        print("  • Phase 14 is ready - run the demo to explore features")
        print("  • Consider running integration tests before production use")
    
    return results['overall_status'] == 'READY'

def main():
    """Main status check execution"""
    try:
        success = check_phase14_status()
        return success
    except Exception as e:
        print(f"\n❌ Status check failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
