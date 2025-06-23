#!/usr/bin/env python3
"""
TradeMasterX 2.0 - Phase 11 Demo
Demonstration of the complete Phase 11 Intelligent Optimization system
"""

import asyncio
import json
import random
from datetime import datetime, timedelta
from pathlib import Path
import sys
import os

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from trademasterx.optimizers.phase_11 import Phase11Controller

def generate_mock_trade_data(trade_id: int) -> dict:
    """Generate mock trade data for demonstration"""
    symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'SOLUSDT', 'DOTUSDT']
    bot_ids = ['technical_analysis_bot', 'sentiment_bot', 'pattern_recognition_bot', 'ml_predictor_bot']
    strategy_ids = ['conservative', 'aggressive', 'balanced', 'momentum']
    
    # Simulate some realistic trading scenarios
    confidence = random.uniform(0.3, 0.95)
    expected_return = random.uniform(-0.05, 0.08)
    
    # Create correlation between confidence and success rate
    success_probability = 0.4 + (confidence * 0.4)  # Higher confidence = higher success rate
    actual_return = expected_return * random.uniform(0.5, 1.5) if random.random() < success_probability else expected_return * random.uniform(-2.0, -0.5)
    
    return {
        'trade_id': f"demo_trade_{trade_id}",
        'timestamp': datetime.now().isoformat(),
        'symbol': random.choice(symbols),
        'signal': random.choice(['buy', 'sell']),
        'confidence': confidence,
        'expected_return': expected_return,
        'actual_return': actual_return,
        'position_size': random.uniform(1000, 10000),
        'bot_id': random.choice(bot_ids),
        'strategy_id': random.choice(strategy_ids)
    }

async def run_phase11_demo():
    """Run comprehensive Phase 11 demonstration"""
    print("=" * 80)
    print("🧠 TradeMasterX 2.0 - Phase 11: Intelligent Optimization Demo")
    print("=" * 80)
    print()
    
    # Initialize Phase 11 Controller
    print(" Initializing Phase 11 Controller...")
    controller = Phase11Controller()
    
    # Display initial system status
    print("\n📊 Initial System Status:")
    initial_status = controller.get_system_status()
    print(f"   Components Active: {len([k for k, v in initial_status['component_status'].items() if v == 'active'])}/5")
    print(f"   Configuration: {initial_status['configuration']['optimization_interval_seconds']}s intervals")
    print()
    
    # Simulate processing multiple trades
    print("📈 Processing Mock Trades...")
    trade_results = []
    
    for i in range(1, 26):  # Process 25 trades
        trade_data = generate_mock_trade_data(i)
        
        print(f"   Trade {i:2d}: {trade_data['symbol']} {trade_data['signal'].upper()} "
              f"| Conf: {trade_data['confidence']:.2f} | Expected: {trade_data['expected_return']:+.2%} "
              f"| Actual: {trade_data['actual_return']:+.2%}")
        
        # Process trade through Phase 11
        result = await controller.process_trade_result(trade_data)
        trade_results.append(result)
        
        # Small delay to simulate real trading
        await asyncio.sleep(0.1)
    
    print(f"\n✅ Processed {len(trade_results)} trades")
    
    # Run optimization cycle
    print("\n🔄 Running Optimization Cycle...")
    optimization_result = await controller.run_optimization_cycle()
    
    print(f"   Cycle #{optimization_result['cycle_number']} completed in {optimization_result['cycle_time_seconds']:.2f}s")
    print(f"   Efficiency Score: {optimization_result['cycle_efficiency']:.1f}/100")
    
    # Display component results
    component_results = optimization_result['component_results']
    print("\n📋 Component Results:")
    
    # Bot Rankings
    bot_rankings = component_results.get('bot_rankings', {})
    if bot_rankings.get('top_bots'):
        print(f"   🤖 Top Performing Bots ({bot_rankings['total_bots']} total):")
        for i, bot in enumerate(bot_rankings['top_bots'], 1):
            print(f"      {i}. {bot.get('bot_id', 'Unknown')}: {bot.get('reliability_score', 0):.3f}")
    
    # Strategy Evaluation
    strategy_eval = component_results.get('strategy_evaluation', {})
    if strategy_eval and not strategy_eval.get('error'):
        print(f"   📊 Strategy Analysis:")
        print(f"      Strategies Evaluated: {strategy_eval.get('strategies_evaluated', 0)}")
        print(f"      Switches Recommended: {len(strategy_eval.get('recommended_switches', []))}")
    
    # Anomaly Patterns
    anomaly_patterns = component_results.get('anomaly_patterns', {})
    if anomaly_patterns and not anomaly_patterns.get('error'):
        print(f"   🚨 Anomaly Analysis:")
        print(f"      Patterns Detected: {anomaly_patterns.get('patterns_found', 0)}")
        print(f"      Severity Distribution: {anomaly_patterns.get('severity_distribution', {})}")
    
    # Dashboard Update
    dashboard_update = component_results.get('dashboard_update', {})
    if dashboard_update.get('updated'):
        metrics = dashboard_update['metrics_summary']
        print(f"   📱 Dashboard Metrics:")
        print(f"      System Health: {metrics.get('system_health', 0):.1f}%")
        print(f"      Optimization Efficiency: {metrics.get('optimization_efficiency', 0):.1f}%")
        print(f"      Active Alerts: {metrics.get('active_alerts', 0)}")
    
    # Generate comprehensive report
    print("\n📋 Generating Optimization Report...")
    report = controller.get_optimization_report()
    
    if not report.get('error'):
        print(f"   Report Generated: {report['report_timestamp']}")
        
        # System Overview
        overview = report.get('system_overview', {})
        print(f"   📊 System Overview:")
        print(f"      Optimization Cycles: {overview.get('optimization_cycles', 0)}")
        
        system_health = overview.get('system_health', {})
        if system_health:
            print(f"      System Health: {system_health.get('score', 0):.1f}% ({system_health.get('status', 'unknown')})")
        
        # Recommendations
        recommendations = report.get('recommendations', [])
        if recommendations:
            print(f"   💡 Recommendations ({len(recommendations)}):")
            for i, rec in enumerate(recommendations[:3], 1):  # Show top 3
                print(f"      {i}. {rec}")
    
    # Display final system status
    print("\n📊 Final System Status:")
    final_status = controller.get_system_status()
    dashboard_summary = final_status.get('dashboard_summary')
    
    if dashboard_summary:
        print(f"   System Health: {dashboard_summary['system_health']['score']:.1f}% ({dashboard_summary['system_health']['status']})")
        print(f"   Performance Trend: {dashboard_summary['performance']['trend']}")
        print(f"   Active Bots: {dashboard_summary['bots']['active']}/{dashboard_summary['bots']['total']}")
        print(f"   Active Strategies: {dashboard_summary['strategies']['active']}/{dashboard_summary['strategies']['total']}")
        print(f"   Anomalies (24h): {dashboard_summary['anomalies']['total_24h']} ({dashboard_summary['anomalies']['critical']} critical)")
        print(f"   Active Alerts: {dashboard_summary['alerts']['total']}")
    
    # Demonstrate dashboard export
    print("\n💾 Exporting Dashboard Data...")
    export_file = controller.dashboard.export_dashboard_data()
    if export_file:
        print(f"   Dashboard data exported to: {export_file}")
    
    # Show alert statistics
    alert_stats = controller.dashboard.get_alert_statistics()
    if alert_stats['total'] > 0:
        print(f"\n🚨 Alert Statistics:")
        print(f"   Total Alerts: {alert_stats['total']}")
        print(f"   By Severity: {alert_stats['by_severity']}")
        print(f"   By Category: {alert_stats['by_category']}")
        print(f"   Active Alerts: {alert_stats['active_alerts']}")
    
    print("\n" + "=" * 80)
    print("✅ Phase 11 Intelligent Optimization Demo Completed Successfully!")
    print("=" * 80)
    
    print("\n📁 Generated Files:")
    print("   📊 reports/bot_reliability_scores.json - Bot performance metrics")
    print("   📈 reports/strategy_metrics.json - Strategy performance data")
    print("   🚨 logs/anomalies.json - Anomaly detection logs")
    print("   📱 reports/dashboard/ - Dashboard data and exports")
    
    print("\n🔗 Integration Points:")
    print("   • Phase 10 Optimizer: controller.integrate_with_phase10()")
    print("   • Real-time Monitoring: controller.start_continuous_optimization()")
    print("   • Trade Processing: controller.process_trade_result(trade_data)")
    print("   • System Status: controller.get_system_status()")
    
    print(f"\n🎯 Phase 11 Benefits Demonstrated:")
    print(f"   ✅ Self-improving intelligence through adaptive learning")
    print(f"   ✅ Real-time performance monitoring and optimization")
    print(f"   ✅ Automated strategy switching and bot performance scoring")
    print(f"   ✅ Anomaly detection and pattern recognition")
    print(f"   ✅ Comprehensive alerting and reporting system")
    print(f"   ✅ Integration-ready for existing TradeMasterX systems")
    
    return controller

async def demonstrate_continuous_optimization():
    """Demonstrate continuous optimization capabilities"""
    print("\n" + "=" * 80)
    print("🔄 Continuous Optimization Demonstration (30 seconds)")
    print("=" * 80)
    
    controller = Phase11Controller()
    
    # Configure for demo (shorter intervals)
    controller.update_configuration({
        'optimization_interval_seconds': 10,
        'max_optimization_cycles': 3
    })
    
    print(" Starting continuous optimization...")
    
    # Start continuous optimization in background
    optimization_task = asyncio.create_task(controller.start_continuous_optimization())
    
    # Simulate incoming trades during optimization
    trade_simulation_task = asyncio.create_task(simulate_live_trading(controller))
    
    # Wait for demonstration period
    await asyncio.sleep(35)
    
    # Stop optimization
    controller.stop_optimization()
    
    # Wait for tasks to complete
    await asyncio.gather(optimization_task, trade_simulation_task, return_exceptions=True)
    
    print("\n✅ Continuous optimization demonstration completed")
    
    # Show final results
    final_status = controller.get_system_status()
    print(f"📊 Final Results:")
    print(f"   Total Optimization Cycles: {final_status['optimization_cycles_completed']}")
    print(f"   Last Optimization: {final_status['last_optimization_time']}")

async def simulate_live_trading(controller):
    """Simulate live trading during continuous optimization"""
    trade_count = 0
    
    try:
        while controller.is_running:
            trade_count += 1
            trade_data = generate_mock_trade_data(trade_count)
            
            # Process trade
            await controller.process_trade_result(trade_data)
            
            print(f"   📈 Live Trade {trade_count}: {trade_data['symbol']} "
                  f"{trade_data['signal'].upper()} | Return: {trade_data['actual_return']:+.2%}")
            
            # Random interval between trades (1-5 seconds)
            await asyncio.sleep(random.uniform(1, 5))
            
    except Exception as e:
        print(f"   Error in trade simulation: {e}")

if __name__ == "__main__":
    print("Select Phase 11 demonstration mode:")
    print("1. Complete System Demo (default)")
    print("2. Continuous Optimization Demo")
    print("3. Both demonstrations")
    
    choice = input("\nEnter choice (1-3) or press Enter for default: ").strip()
    
    if choice == "2":
        asyncio.run(demonstrate_continuous_optimization())
    elif choice == "3":
        asyncio.run(run_phase11_demo())
        asyncio.run(demonstrate_continuous_optimization())
    else:
        asyncio.run(run_phase11_demo())
