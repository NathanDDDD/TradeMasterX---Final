"""
TradeMasterX 2.0 - Phase 11: Intelligent Optimization Demo
Complete demonstration of the self-improving intelligence layer
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
import sys
import random

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from trademasterx.optimizers.phase_11.phase_11_controller import Phase11Controller
from trademasterx.optimizers.phase_11.config import Phase11Config, DEVELOPMENT_CONFIG

class Phase11Demo:
    """
    Interactive demonstration of Phase 11 Intelligent Optimization
    
    Showcases all 5 components:
    1. AdaptiveStrategyReinforcer - Learns from trade outcomes
    2. BotPerformanceScorer - Tracks bot reliability
    3. StrategySwitcher - Auto-switches failing strategies
    4. AnomalyDetector - Catches unusual patterns
    5. LiveOptimizationDashboard - Real-time monitoring
    """
    
    def __init__(self):
        self.demo_data_dir = Path("demo_data/phase_11")
        self.demo_logs_dir = Path("demo_logs/phase_11")
        
        # Create demo directories
        self.demo_data_dir.mkdir(parents=True, exist_ok=True)
        self.demo_logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Phase 11 controller
        self.controller = Phase11Controller(
            data_dir=str(self.demo_data_dir),
            logs_dir=str(self.demo_logs_dir)
        )
        
        # Configure for demo (faster intervals)
        demo_config = DEVELOPMENT_CONFIG.to_dict()
        demo_config.update({
            'optimization_interval_seconds': 30,
            'dashboard_update_interval_seconds': 15,
            'anomaly_check_interval_seconds': 10
        })
        self.controller.update_configuration(demo_config)
        
        self.demo_step = 0
        self.total_trades_processed = 0
    
    def print_header(self, title: str):
        """Print formatted section header"""
        print("\n" + "=" * 80)
        print(f"  {title}")
        print("=" * 80)
    
    def print_step(self, step_title: str):
        """Print formatted step"""
        self.demo_step += 1
        print(f"\n[STEP {self.demo_step}] {step_title}")
        print("-" * 60)
    
    def generate_realistic_trade_sequence(self, strategy: str, bot: str, count: int = 10):
        """Generate realistic trade sequence for a specific strategy/bot"""
        trades = []
        base_time = datetime.now()
        
        # Strategy characteristics
        strategy_profiles = {
            'momentum': {'base_confidence': 0.75, 'volatility': 0.02, 'win_rate': 0.65},
            'mean_reversion': {'base_confidence': 0.70, 'volatility': 0.015, 'win_rate': 0.70},
            'breakout': {'base_confidence': 0.80, 'volatility': 0.03, 'win_rate': 0.60},
            'scalping': {'base_confidence': 0.85, 'volatility': 0.008, 'win_rate': 0.72},
            'swing': {'base_confidence': 0.65, 'volatility': 0.025, 'win_rate': 0.68}
        }
        
        profile = strategy_profiles.get(strategy, strategy_profiles['momentum'])
        symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'SOLUSDT']
        
        for i in range(count):
            confidence = profile['base_confidence'] + random.uniform(-0.15, 0.15)
            confidence = max(0.3, min(0.95, confidence))
            
            expected_return = random.uniform(-0.02, 0.04)
            
            # Simulate realistic performance based on strategy and confidence
            if random.random() < profile['win_rate']:
                # Winning trade
                actual_return = expected_return + random.uniform(0, profile['volatility'])
            else:
                # Losing trade
                actual_return = expected_return - random.uniform(0, profile['volatility'] * 2)
            
            trade = {
                'trade_id': f"{strategy}_{bot}_{i:03d}",
                'bot_id': bot,
                'strategy_id': strategy,
                'symbol': random.choice(symbols),
                'signal': random.choice(['buy', 'sell']),
                'confidence': confidence,
                'expected_return': expected_return,
                'actual_return': actual_return,
                'position_size': random.uniform(100, 1000),
                'timestamp': (base_time + timedelta(minutes=i*3)).isoformat(),
                'market_conditions': {
                    'volatility': random.uniform(0.01, 0.04),
                    'volume': random.uniform(1000000, 8000000),
                    'trend': random.choice(['bullish', 'bearish', 'sideways'])
                }
            }
            trades.append(trade)
        
        return trades
    
    async def demo_initialization(self):
        """Demonstrate Phase 11 initialization"""
        self.print_header("PHASE 11: INTELLIGENT OPTIMIZATION DEMO")
        
        print(" TradeMasterX 2.0 - Self-Improving Intelligence Layer")
        print("\nThis demo showcases how Phase 11 automatically:")
        print("• Learns from trade outcomes to improve strategies")
        print("• Tracks and scores bot performance in real-time")
        print("• Switches underperforming strategies automatically")
        print("• Detects anomalies and unusual trading patterns")
        print("• Provides live optimization dashboard with alerts")
        
        self.print_step("Initialize Phase 11 Controller")
        
        # Show system status
        status = self.controller.get_system_status()
        print(f"✅ Phase 11 Controller initialized")
        print(f"📊 Components active: {len([k for k, v in status['component_status'].items() if v == 'active'])}/5")
        print(f"⚙️  Configuration: {status['configuration']['optimization_interval_seconds']}s optimization cycles")
        
        # Show components
        print("\n📋 Active Components:")
        for component, state in status['component_status'].items():
            emoji = "✅" if state == "active" else "⏸️"
            print(f"   {emoji} {component.replace('_', ' ').title()}: {state}")
        
        input("\nPress Enter to continue...")
    
    async def demo_trade_processing(self):
        """Demonstrate individual trade processing"""
        self.print_step("Process Individual Trades")
        
        print("🔄 Processing sample trades through all Phase 11 components...")
        
        # Generate sample trades from different strategies
        strategies = ['momentum', 'mean_reversion', 'breakout']
        bots = ['alpha_bot', 'beta_bot', 'gamma_bot']
        
        for strategy in strategies:
            for bot in bots:
                print(f"\n📈 Processing {strategy} trade from {bot}...")
                
                # Generate single trade
                trade = self.generate_realistic_trade_sequence(strategy, bot, 1)[0]
                
                # Process through Phase 11
                start_time = time.time()
                result = await self.controller.process_trade_result(trade)
                processing_time = time.time() - start_time
                
                # Show results
                print(f"   ⚡ Processed in {processing_time:.3f}s")
                print(f"   💰 Expected: {trade['expected_return']:.3f}, Actual: {trade['actual_return']:.3f}")
                print(f"   🎯 Confidence: {trade['confidence']:.2f}")
                
                # Show component results
                opt_results = result['optimization_results']
                
                if 'strategy_reinforcement' in opt_results and not opt_results['strategy_reinforcement'].get('error'):
                    sr_result = opt_results['strategy_reinforcement']
                    if sr_result.get('weight_adjusted'):
                        print(f"   🧠 Strategy weight adjusted")
                
                if 'bot_scoring' in opt_results and not opt_results['bot_scoring'].get('error'):
                    bs_result = opt_results['bot_scoring']
                    print(f"   🤖 Bot score updated: {bs_result.get('new_score', 'N/A')}")
                
                if 'anomaly_detection' in opt_results and not opt_results['anomaly_detection'].get('error'):
                    ad_result = opt_results['anomaly_detection']
                    if ad_result.get('is_anomaly'):
                        print(f"   🚨 Anomaly detected: {ad_result.get('anomaly_type', 'unknown')}")
                    else:
                        print(f"   ✅ Normal trade pattern")
                
                self.total_trades_processed += 1
                await asyncio.sleep(0.5)  # Small delay for demo effect
        
        print(f"\n📊 Total trades processed: {self.total_trades_processed}")
        input("\nPress Enter to continue...")
    
    async def demo_bulk_processing(self):
        """Demonstrate bulk trade processing"""
        self.print_step("Bulk Trade Processing & Learning")
        
        print("📦 Processing larger batch of trades to demonstrate learning...")
        
        # Generate bulk trades with some patterns
        all_trades = []
        
        # Good performing strategy
        good_trades = self.generate_realistic_trade_sequence('scalping', 'alpha_bot', 15)
        all_trades.extend(good_trades)
        
        # Poor performing strategy  
        poor_trades = self.generate_realistic_trade_sequence('breakout', 'beta_bot', 15)
        # Make some trades deliberately poor
        for trade in poor_trades[-8:]:
            trade['actual_return'] = trade['expected_return'] - 0.05
        all_trades.extend(poor_trades)
        
        # Normal mixed performance
        mixed_trades = self.generate_realistic_trade_sequence('momentum', 'gamma_bot', 10)
        all_trades.extend(mixed_trades)
        
        print(f"🔄 Processing {len(all_trades)} trades...")
        
        processed = 0
        for trade in all_trades:
            result = await self.controller.process_trade_result(trade)
            processed += 1
            
            if processed % 10 == 0:
                print(f"   ✅ Processed {processed}/{len(all_trades)} trades")
        
        self.total_trades_processed += len(all_trades)
        
        print(f"\n📈 Bulk processing complete!")
        print(f"   • Total processed: {len(all_trades)}")
        print(f"   • Alpha Bot (scalping): Expected good performance")
        print(f"   • Beta Bot (breakout): Included poor trades")
        print(f"   • Gamma Bot (momentum): Mixed performance")
        
        input("\nPress Enter to continue...")
    
    async def demo_optimization_cycle(self):
        """Demonstrate optimization cycle"""
        self.print_step("Run Optimization Cycle")
        
        print("🔄 Running complete optimization cycle across all components...")
        
        start_time = time.time()
        cycle_result = await self.controller.run_optimization_cycle()
        cycle_time = time.time() - start_time
        
        print(f"✅ Optimization cycle completed in {cycle_time:.2f}s")
        print(f"🔢 Cycle #{cycle_result['cycle_number']}")
        
        # Show component results
        comp_results = cycle_result['component_results']
        
        print("\n📊 Component Results:")
        
        # Bot rankings
        if 'bot_rankings' in comp_results and not comp_results['bot_rankings'].get('error'):
            br = comp_results['bot_rankings']
            print(f"   🤖 Bot Rankings: Updated {br.get('total_bots', 0)} bots")
            if br.get('top_bots'):
                print(f"      Top performers: {[bot.get('bot_id', 'unknown') for bot in br['top_bots'][:3]]}")
        
        # Strategy evaluation
        if 'strategy_evaluation' in comp_results and not comp_results['strategy_evaluation'].get('error'):
            se = comp_results['strategy_evaluation']
            print(f"   📈 Strategy Evaluation: Completed")
            if se.get('recommendations'):
                print(f"      Recommendations available: {len(se['recommendations'])}")
        
        # Anomaly patterns
        if 'anomaly_patterns' in comp_results and not comp_results['anomaly_patterns'].get('error'):
            ap = comp_results['anomaly_patterns']
            print(f"   🔍 Anomaly Analysis: Completed")
            if ap.get('patterns_found'):
                print(f"      Patterns detected: {ap.get('pattern_count', 0)}")
        
        # Dashboard update
        if 'dashboard_update' in comp_results and not comp_results['dashboard_update'].get('error'):
            du = comp_results['dashboard_update']
            if du.get('updated'):
                metrics = du.get('metrics_summary', {})
                print(f"   📊 Dashboard: Updated")
                print(f"      System Health: {metrics.get('system_health', 'N/A')}")
                print(f"      Optimization Efficiency: {metrics.get('optimization_efficiency', 'N/A')}")
        
        input("\nPress Enter to continue...")
    
    async def demo_anomaly_detection(self):
        """Demonstrate anomaly detection"""
        self.print_step("Anomaly Detection Demo")
        
        print("🔍 Demonstrating anomaly detection with intentional anomalies...")
        
        # First, establish normal baseline
        print("\n1️⃣ Establishing normal trading baseline...")
        normal_trades = self.generate_realistic_trade_sequence('momentum', 'delta_bot', 15)
        
        for trade in normal_trades:
            await self.controller.process_trade_result(trade)
        
        print(f"   ✅ Processed {len(normal_trades)} normal trades")
        
        # Now introduce anomalies
        print("\n2️⃣ Introducing anomalous trades...")
        
        anomaly_scenarios = [
            {
                'name': 'Extreme Loss',
                'description': 'High confidence trade with massive loss',
                'trade': {
                    'trade_id': 'anomaly_extreme_loss',
                    'bot_id': 'delta_bot',
                    'strategy_id': 'momentum',
                    'symbol': 'BTCUSDT',
                    'confidence': 0.95,
                    'expected_return': 0.02,
                    'actual_return': -0.25,  # Massive loss
                    'timestamp': datetime.now().isoformat()
                }
            },
            {
                'name': 'Confidence Mismatch',
                'description': 'Low confidence with unexpected high return',
                'trade': {
                    'trade_id': 'anomaly_confidence_mismatch',
                    'bot_id': 'delta_bot',
                    'strategy_id': 'momentum',
                    'symbol': 'ETHUSDT',
                    'confidence': 0.25,
                    'expected_return': 0.01,
                    'actual_return': 0.15,  # Unexpected high return
                    'timestamp': datetime.now().isoformat()
                }
            },
            {
                'name': 'Impossible Return',
                'description': 'Return far beyond market norms',
                'trade': {
                    'trade_id': 'anomaly_impossible_return',
                    'bot_id': 'delta_bot',
                    'strategy_id': 'momentum',
                    'symbol': 'ADAUSDT',
                    'confidence': 0.70,
                    'expected_return': 0.02,
                    'actual_return': 0.50,  # 50% return - impossible
                    'timestamp': datetime.now().isoformat()
                }
            }
        ]
        
        for scenario in anomaly_scenarios:
            print(f"\n   🚨 Testing: {scenario['name']}")
            print(f"      {scenario['description']}")
            
            result = await self.controller.process_trade_result(scenario['trade'])
            anomaly_result = result['optimization_results']['anomaly_detection']
            
            if anomaly_result.get('is_anomaly'):
                print(f"      ✅ DETECTED as anomaly!")
                print(f"      Type: {anomaly_result.get('anomaly_type', 'unknown')}")
                if anomaly_result.get('severity'):
                    print(f"      Severity: {anomaly_result['severity']}")
            else:
                print(f"      ❌ Not detected as anomaly")
            
            await asyncio.sleep(1)
        
        input("\nPress Enter to continue...")
    
    async def demo_strategy_switching(self):
        """Demonstrate strategy switching"""
        self.print_step("Strategy Switching Demo")
        
        print("🔄 Demonstrating automatic strategy switching...")
        
        # Simulate a failing strategy
        print("\n1️⃣ Simulating failing strategy performance...")
        
        failing_trades = []
        for i in range(8):
            trade = {
                'trade_id': f'failing_strategy_{i}',
                'bot_id': 'epsilon_bot',
                'strategy_id': 'failing_strategy',
                'symbol': 'BTCUSDT',
                'confidence': 0.80,
                'expected_return': 0.03,
                'actual_return': -0.02 - (i * 0.005),  # Getting worse
                'timestamp': (datetime.now() + timedelta(minutes=i)).isoformat()
            }
            failing_trades.append(trade)
        
        switch_detected = False
        for trade in failing_trades:
            result = await self.controller.process_trade_result(trade)
            
            switch_result = result['optimization_results'].get('strategy_switching', {})
            if switch_result.get('switch_recommended') or switch_result.get('switched'):
                print(f"   🔄 Strategy switch recommended!")
                print(f"      Reason: {switch_result.get('reason', 'performance decline')}")
                switch_detected = True
                break
            else:
                print(f"   📊 Trade {trade['trade_id']}: Return {trade['actual_return']:.3f}")
        
        if not switch_detected:
            print("   ℹ️  Strategy switching requires more data or specific conditions")
        
        # Test strategy evaluation
        print("\n2️⃣ Running strategy evaluation...")
        strategy_eval = self.controller.strategy_switcher.evaluate_all_strategies()
        
        if strategy_eval.get('strategies_evaluated'):
            print(f"   ✅ Evaluated {strategy_eval['strategies_evaluated']} strategies")
            if strategy_eval.get('recommendations'):
                print(f"   💡 {len(strategy_eval['recommendations'])} recommendations generated")
        
        input("\nPress Enter to continue...")
    
    async def demo_dashboard_and_reports(self):
        """Demonstrate dashboard and reporting"""
        self.print_step("Dashboard & Reporting Demo")
        
        print("📊 Demonstrating dashboard and comprehensive reporting...")
        
        # Get dashboard summary
        print("\n1️⃣ Dashboard Summary:")
        dashboard_summary = self.controller.dashboard.get_dashboard_summary()
        
        if dashboard_summary:
            print(f"   📈 System Health Score: {dashboard_summary.get('system_health', {}).get('score', 'N/A')}")
            print(f"   ⚡ Optimization Efficiency: {dashboard_summary.get('optimization', {}).get('efficiency_score', 'N/A')}")
            print(f"   🚨 Active Alerts: {dashboard_summary.get('alerts', {}).get('total_active', 0)}")
            print(f"   🤖 Active Bots: {dashboard_summary.get('bots', {}).get('active_count', 0)}")
        else:
            print("   ℹ️  Dashboard summary not available yet")
        
        # Generate comprehensive report
        print("\n2️⃣ Generating Comprehensive Report...")
        report = self.controller.get_optimization_report()
        
        print(f"   ✅ Report generated for {report.get('report_period', 'unknown')} period")
        print(f"   📊 Optimization cycles: {report.get('system_overview', {}).get('optimization_cycles', 0)}")
        
        # Show recommendations
        recommendations = report.get('recommendations', [])
        if recommendations:
            print(f"\n   💡 Top Recommendations:")
            for i, rec in enumerate(recommendations[:3], 1):
                print(f"      {i}. {rec}")
        else:
            print(f"   ✅ No critical recommendations - system performing well")
        
        # Save report
        report_file = self.demo_data_dir / f"demo_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n   💾 Full report saved to: {report_file}")
        
        # Show system status
        print("\n3️⃣ Current System Status:")
        status = self.controller.get_system_status()
        
        print(f"   🔄 Optimization running: {status['is_running']}")
        print(f"   🔢 Cycles completed: {status['optimization_cycles_completed']}")
        print(f"   ⏰ Last optimization: {status.get('last_optimization_time', 'Never')}")
        
        input("\nPress Enter to continue...")
    
    async def demo_continuous_optimization(self):
        """Demonstrate continuous optimization"""
        self.print_step("Continuous Optimization Demo")
        
        print("🔄 Demonstrating continuous optimization mode...")
        print("   This mode runs optimization cycles automatically at regular intervals")
        
        # Configure for demo
        self.controller.update_configuration({
            'optimization_interval_seconds': 15,  # Fast for demo
            'max_optimization_cycles': 3  # Limited for demo
        })
        
        print(f"\n⚙️  Configured for demo:")
        print(f"   • Optimization interval: 15 seconds")
        print(f"   • Maximum cycles: 3")
        
        input("\nPress Enter to start continuous optimization...")
        
        print("\n Starting continuous optimization...")
        
        # Start continuous optimization (non-blocking)
        optimization_task = asyncio.create_task(
            self.controller.start_continuous_optimization()
        )
        
        # Simulate ongoing trading activity
        print("\n📈 Simulating ongoing trading activity...")
        
        trading_task = asyncio.create_task(self._simulate_ongoing_trading())
        
        # Monitor progress
        monitor_task = asyncio.create_task(self._monitor_optimization_progress())
        
        # Wait for optimization to complete
        try:
            await optimization_task
        except Exception as e:
            print(f"Optimization completed or stopped: {e}")
        
        # Clean up tasks
        trading_task.cancel()
        monitor_task.cancel()
        
        print(f"\n✅ Continuous optimization demo completed!")
        print(f"   Final cycle count: {self.controller.optimization_cycle_count}")
        
        input("\nPress Enter to continue...")
    
    async def _simulate_ongoing_trading(self):
        """Simulate ongoing trading during continuous optimization"""
        strategies = ['momentum', 'scalping', 'swing']
        bots = ['live_bot_1', 'live_bot_2', 'live_bot_3']
        
        trade_count = 0
        
        try:
            while True:
                # Generate random trade
                strategy = random.choice(strategies)
                bot = random.choice(bots)
                
                trade = self.generate_realistic_trade_sequence(strategy, bot, 1)[0]
                trade['trade_id'] = f'live_trade_{trade_count:03d}'
                
                await self.controller.process_trade_result(trade)
                trade_count += 1
                
                await asyncio.sleep(5)  # New trade every 5 seconds
                
        except asyncio.CancelledError:
            print(f"\n   📊 Processed {trade_count} live trades during optimization")
    
    async def _monitor_optimization_progress(self):
        """Monitor optimization progress"""
        last_cycle = 0
        
        try:
            while True:
                current_cycle = self.controller.optimization_cycle_count
                if current_cycle > last_cycle:
                    print(f"   🔄 Completed optimization cycle #{current_cycle}")
                    last_cycle = current_cycle
                
                await asyncio.sleep(2)
                
        except asyncio.CancelledError:
            pass
    
    def demo_summary(self):
        """Show demo summary"""
        self.print_header("PHASE 11 DEMO SUMMARY")
        
        print("🎉 Phase 11 Intelligent Optimization Demo Complete!")
        print(f"\n📊 Demo Statistics:")
        print(f"   • Total trades processed: {self.total_trades_processed}")
        print(f"   • Optimization cycles run: {self.controller.optimization_cycle_count}")
        print(f"   • Demo steps completed: {self.demo_step}")
        
        print(f"\n✅ Components Demonstrated:")
        print(f"   🧠 AdaptiveStrategyReinforcer - ✅ Learning from outcomes")
        print(f"   🤖 BotPerformanceScorer - ✅ Tracking bot reliability")
        print(f"   🔄 StrategySwitcher - ✅ Auto-switching strategies")
        print(f"   🔍 AnomalyDetector - ✅ Catching unusual patterns")
        print(f"   📊 LiveOptimizationDashboard - ✅ Real-time monitoring")
        
        print(f"\n🎯 Key Features Showcased:")
        print(f"   • Real-time trade processing and optimization")
        print(f"   • Intelligent anomaly detection")
        print(f"   • Automated strategy switching")
        print(f"   • Comprehensive performance monitoring")
        print(f"   • Self-improving intelligence without manual intervention")
        
        print(f"\n📁 Demo Data Saved To:")
        print(f"   • Data: {self.demo_data_dir}")
        print(f"   • Logs: {self.demo_logs_dir}")
        
        print(f"\n Next Steps:")
        print(f"   • Review generated reports and logs")
        print(f"   • Integrate Phase 11 with your trading system")
        print(f"   • Configure optimization parameters for your needs")
        print(f"   • Monitor real-time dashboard for ongoing optimization")

async def main():
    """Main demo execution"""
    demo = Phase11Demo()
    
    try:
        # Run complete demo
        await demo.demo_initialization()
        await demo.demo_trade_processing()
        await demo.demo_bulk_processing()
        await demo.demo_optimization_cycle()
        await demo.demo_anomaly_detection()
        await demo.demo_strategy_switching()
        await demo.demo_dashboard_and_reports()
        await demo.demo_continuous_optimization()
        
        demo.demo_summary()
        
        print(f"\n🎊 Thank you for trying the Phase 11 Demo!")
        
    except KeyboardInterrupt:
        print(f"\n\n🛑 Demo interrupted by user")
    except Exception as e:
        print(f"\n\n💥 Demo error: {e}")
        
if __name__ == "__main__":
    asyncio.run(main())
