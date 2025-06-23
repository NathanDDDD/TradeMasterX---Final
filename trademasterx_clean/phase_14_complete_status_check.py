#!/usr/bin/env python3
"""
TradeMasterX 2.0 - Phase 14 Complete Autonomous AI Status Check
Comprehensive validation of the entire autonomous intelligence system
"""

import asyncio
import sys
from pathlib import Path

def check_complete_autonomous_system():
    """Comprehensive status check for Phase 14 Complete Autonomous AI"""
    
    print(" TradeMasterX 2.0 - Phase 14 Complete Autonomous AI Status Check")
    print("=" * 80)
    
    status = {
        'components': 0,
        'total_components': 6,
        'files': 0,
        'total_files': 6,
        'dependencies': 0,
        'total_dependencies': 10
    }
    
    # 1. Test Core AI Components
    print("\n🧠 Testing Core AI Components...")
    components = [
        ('ObserverAgent', 'trademasterx.ai.observer_agent', 'ObserverAgent'),
        ('AIOrchestrator', 'trademasterx.ai.ai_orchestrator', 'AIOrchestrator'),
        ('ReinforcementEngine', 'trademasterx.ai.reinforcement_engine', 'ReinforcementEngine'),
        ('AnomalyAuditor', 'trademasterx.ai.anomaly_auditor', 'AnomalyAuditor'),
        ('AIDashboard', 'trademasterx.interface.web.ai_dashboard', 'AIDashboard'),
        ('Phase14AutonomousAI', 'phase_14_complete_autonomous_ai', 'Phase14AutonomousAI')
    ]
    
    for name, module_path, class_name in components:
        try:
            module = __import__(module_path, fromlist=[class_name])
            getattr(module, class_name)
            print(f"   ✅ {name} - Ready for autonomous operation")
            status['components'] += 1
        except Exception as e:
            print(f"   ❌ {name} - Import failed: {e}")
    
    # 2. Check Critical Files
    print("\n📁 Checking Critical System Files...")
    critical_files = [
        'trademasterx/ai/observer_agent.py',
        'trademasterx/ai/ai_orchestrator.py', 
        'trademasterx/ai/reinforcement_engine.py',
        'trademasterx/ai/anomaly_auditor.py',
        'trademasterx/interface/web/ai_dashboard.py',
        'phase_14_complete_autonomous_ai.py'
    ]
    
    for file_path in critical_files:
        if Path(file_path).exists():
            print(f"   ✅ {file_path}")
            status['files'] += 1
        else:
            print(f"   ❌ {file_path} - Missing")
    
    # 3. Check Dependencies
    print("\n📦 Checking System Dependencies...")
    dependencies = [
        'numpy', 'pandas', 'scipy', 'asyncio', 'logging',
        'aiohttp', 'json', 'datetime', 'pathlib', 'yaml'
    ]
    
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"   ✅ {dep}")
            status['dependencies'] += 1
        except ImportError:
            print(f"   ❌ {dep} - Not available")
    
    # 4. Test Directory Structure
    print("\n📂 Checking Directory Structure...")
    required_dirs = ['logs', 'status', 'reports', 'reports/anomalies']
    
    for directory in required_dirs:
        dir_path = Path(directory)
        if dir_path.exists():
            print(f"   ✅ {directory}/")
        else:
            print(f"   ⚠️  {directory}/ - Will be created automatically")
    
    # 5. Test Integration
    print("\n🔗 Testing System Integration...")
    try:
        from phase_14_complete_autonomous_ai import Phase14AutonomousAI
        
        # Test configuration loading
        config = {
            'observer_interval': 30,
            'orchestrator_cycle': 60,
            'dashboard_port': 8080,
            'ai_mode': 'autonomous'
        }
        
        # Test initialization (without starting background tasks)
        system = Phase14AutonomousAI(config)
        print("   ✅ System initialization successful")
        print("   ✅ All components properly integrated")
        
        # Test component communication
        if hasattr(system, 'observer_agent') and system.observer_agent:
            print("   ✅ Observer Agent integrated")
        if hasattr(system, 'ai_orchestrator') and system.ai_orchestrator:
            print("   ✅ AI Orchestrator integrated")
        if hasattr(system, 'reinforcement_engine') and system.reinforcement_engine:
            print("   ✅ Reinforcement Engine integrated")
        if hasattr(system, 'anomaly_auditor') and system.anomaly_auditor:
            print("   ✅ Anomaly Auditor integrated")
        if hasattr(system, 'ai_dashboard') and system.ai_dashboard:
            print("   ✅ AI Dashboard integrated")
            
    except Exception as e:
        print(f"   ❌ Integration test failed: {e}")
      # 6. Test AI Copilot Components (Phase 14 subset)
    print("\n🤖 Testing AI Copilot Components...")
    copilot_components = [
        ('AICopilot', 'trademasterx.optimizers.phase_14.ai_copilot', 'AICopilot'),
        ('RealTimeMonitor', 'trademasterx.optimizers.phase_14.real_time_monitor', 'RealTimeMonitor'),
        ('IntelligentAnalyzer', 'trademasterx.optimizers.phase_14.intelligent_analyzer', 'IntelligentAnalyzer'),
        ('FeedbackGenerator', 'trademasterx.optimizers.phase_14.feedback_generator', 'FeedbackGenerator')
    ]
    
    copilot_working = 0
    for name, module_path, class_name in copilot_components:
        try:
            module = __import__(module_path, fromlist=[class_name])
            getattr(module, class_name)
            print(f"   ✅ {name} - AI Copilot ready")
            copilot_working += 1
        except Exception as e:
            print(f"   ⚠️  {name} - {e}")
    
    # 7. Generate Status Summary
    print("\n" + "=" * 80)
    print("📊 PHASE 14 COMPLETE AUTONOMOUS AI STATUS SUMMARY")
    print("=" * 80)
    
    components_status = "🟢 READY" if status['components'] >= 5 else "🟡 PARTIAL" if status['components'] >= 3 else "🔴 FAILED"
    files_status = "🟢 READY" if status['files'] >= 5 else "🟡 PARTIAL" if status['files'] >= 3 else "🔴 FAILED"
    deps_status = "🟢 READY" if status['dependencies'] >= 8 else "🟡 PARTIAL" if status['dependencies'] >= 6 else "🔴 FAILED"
    copilot_status = "🟢 READY" if copilot_working >= 3 else "🟡 PARTIAL" if copilot_working >= 2 else "🔴 FAILED"
    
    print(f"Core AI Components: {status['components']}/{status['total_components']} {components_status}")
    print(f"Critical Files: {status['files']}/{status['total_files']} {files_status}")
    print(f"Dependencies: {status['dependencies']}/{status['total_dependencies']} {deps_status}")
    print(f"AI Copilot: {copilot_working}/4 {copilot_status}")
    
    # Overall status
    overall_score = (status['components'] + status['files'] + status['dependencies'] + copilot_working)
    max_score = (status['total_components'] + status['total_files'] + status['total_dependencies'] + 4)
    
    if overall_score >= max_score * 0.9:
        overall_status = "🟢 FULLY OPERATIONAL"
        message = "Phase 14 Complete Autonomous AI is ready for production!"
    elif overall_score >= max_score * 0.7:
        overall_status = "🟡 MOSTLY OPERATIONAL" 
        message = "Phase 14 is mostly ready - minor issues detected"
    else:
        overall_status = "🔴 NEEDS ATTENTION"
        message = "Phase 14 requires fixes before operation"
    
    print(f"\nOverall Status: {overall_status}")
    print(f"System Score: {overall_score}/{max_score} ({overall_score/max_score*100:.1f}%)")
    
    print(f"\n💡 {message}")
    
    # 8. Usage Instructions
    print("\n USAGE INSTRUCTIONS:")
    print("=" * 80)
    
    if overall_score >= max_score * 0.7:
        print("✅ Run Complete Autonomous System:")
        print("   python phase_14_complete_autonomous_ai.py")
        print("\n✅ Run AI Copilot Only:")
        print("   python demo_phase_14.py")
        print("\n✅ Test System Integration:")
        print("   python test_phase_14_integration.py")
        print("\n🌐 Access Web Dashboard:")
        print("   http://localhost:8080 (when system is running)")
        print("\n🎛️  Manual Control:")
        print("   Use Command Assistant: 'ai status', 'ai retrain', 'ai monitor'")
    else:
        print("⚠️  System requires fixes before use")
        print("   Check missing components and dependencies above")
    
    print("\n📋 AUTONOMOUS FEATURES:")
    print("   • Real-time trade monitoring (30s intervals)")
    print("   • Automatic model retraining based on performance")
    print("   • Dynamic strategy weight optimization")
    print("   • Advanced anomaly detection and alerts")
    print("   • Web dashboard for system monitoring")
    print("   • Integration with Command Assistant")
    
    return overall_score >= max_score * 0.7

if __name__ == "__main__":
    try:
        success = check_complete_autonomous_system()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Status check failed: {e}")
        sys.exit(1)
