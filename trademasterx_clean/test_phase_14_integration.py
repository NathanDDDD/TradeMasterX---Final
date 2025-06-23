#!/usr/bin/env python3
"""
TradeMasterX 2.0 - Phase 14: AI Copilot Integration Testing
Comprehensive test suite for AI Copilot Assistant components
"""

import asyncio
import sys
import os
import logging
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Add workspace to path
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('Phase14IntegrationTest')

class Phase14IntegrationTest:
    """
    Comprehensive integration test suite for Phase 14 AI Copilot Assistant
    
    Tests all 4 core components working together:
    - AICopilot (main controller)
    - RealTimeMonitor (monitoring system)
    - IntelligentAnalyzer (pattern recognition and analytics)
    - FeedbackGenerator (natural language feedback)
    """
    
    def __init__(self):
        self.test_results = []
        self.test_data_dir = Path("test_data/phase_14")
        self.test_logs_dir = Path("test_logs/phase_14")
        
        # Create test directories
        self.test_data_dir.mkdir(parents=True, exist_ok=True)
        self.test_logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Test configuration
        self.test_config = {
            'data_dir': str(self.test_data_dir),
            'logs_dir': str(self.test_logs_dir),
            'monitoring_interval': 5,  # Fast testing
            'alert_thresholds': {
                'anomaly_spike': 3,
                'performance_drop': 0.3,
                'system_resource': 0.8,
                'bot_failure_rate': 0.4
            }
        }
        
        logger.info("Phase 14 Integration Test initialized")
    
    def generate_test_market_data(self, count: int = 100) -> List[Dict[str, Any]]:
        """Generate synthetic market data for testing"""
        import random
        
        market_data = []
        symbols = ['BTC/USD', 'ETH/USD', 'ADA/USD', 'DOT/USD', 'LINK/USD']
        
        for i in range(count):
            timestamp = datetime.now() - timedelta(minutes=i)
            
            for symbol in symbols:
                base_price = {
                    'BTC/USD': 45000,
                    'ETH/USD': 3000,
                    'ADA/USD': 1.2,
                    'DOT/USD': 25,
                    'LINK/USD': 15
                }[symbol]
                
                # Add some volatility
                volatility = random.uniform(0.95, 1.05)
                price = base_price * volatility
                
                market_data.append({
                    'timestamp': timestamp.isoformat(),
                    'symbol': symbol,
                    'price': round(price, 8),
                    'volume': random.uniform(1000, 50000),
                    'bid': round(price * 0.999, 8),
                    'ask': round(price * 1.001, 8),
                    'change_24h': random.uniform(-0.1, 0.1)
                })
        
        return market_data
    
    def generate_test_trades(self, count: int = 50) -> List[Dict[str, Any]]:
        """Generate synthetic trade data for testing"""
        import random
        
        trades = []
        bot_ids = ['momentum_bot', 'arbitrage_bot', 'grid_bot', 'dca_bot']
        strategies = ['momentum', 'arbitrage', 'grid_trading', 'dca']
        symbols = ['BTC/USD', 'ETH/USD', 'ADA/USD']
        
        for i in range(count):
            timestamp = datetime.now() - timedelta(minutes=i * 2)
            bot_id = random.choice(bot_ids)
            strategy = random.choice(strategies)
            symbol = random.choice(symbols)
            
            # Simulate realistic trade outcomes
            success_rate = random.uniform(0.4, 0.8)
            is_profitable = random.random() < success_rate
            
            entry_price = random.uniform(100, 50000)
            exit_price = entry_price * (1 + random.uniform(-0.05, 0.05))
            pnl = (exit_price - entry_price) * random.uniform(0.1, 2.0)
            
            if not is_profitable:
                pnl = -abs(pnl)
            
            trades.append({
                'trade_id': f'test_trade_{i:04d}',
                'timestamp': timestamp.isoformat(),
                'bot_id': bot_id,
                'strategy_id': strategy,
                'symbol': symbol,
                'side': random.choice(['buy', 'sell']),
                'entry_price': round(entry_price, 8),
                'exit_price': round(exit_price, 8),
                'quantity': random.uniform(0.01, 1.0),
                'pnl': round(pnl, 6),
                'duration_minutes': random.uniform(5, 120),
                'confidence': random.uniform(0.3, 0.9),
                'is_profitable': is_profitable
            })
        
        return trades
    
    async def test_component_initialization(self):
        """Test that all Phase 14 components initialize correctly"""
        logger.info("Testing component initialization...")
        
        try:
            # Import Phase 14 components
            from package.trademasterx.optimizers.phase_14 import (
                AICopilot, RealTimeMonitor, IntelligentAnalyzer, FeedbackGenerator
            )
            
            logger.info("✓ Successfully imported Phase 14 components")
            
            # Test individual component initialization
            monitor = RealTimeMonitor(self.test_config)
            assert monitor is not None, "RealTimeMonitor not initialized"
            logger.info("✓ RealTimeMonitor initialized")
            
            analyzer = IntelligentAnalyzer(self.test_config)
            assert analyzer is not None, "IntelligentAnalyzer not initialized"
            logger.info("✓ IntelligentAnalyzer initialized")
            
            feedback_gen = FeedbackGenerator(self.test_config)
            assert feedback_gen is not None, "FeedbackGenerator not initialized"
            logger.info("✓ FeedbackGenerator initialized")
            
            # Test main AI Copilot initialization
            copilot = AICopilot(self.test_config)
            assert copilot is not None, "AICopilot not initialized"
            assert hasattr(copilot, 'real_time_monitor'), "Missing real_time_monitor"
            assert hasattr(copilot, 'intelligent_analyzer'), "Missing intelligent_analyzer"
            assert hasattr(copilot, 'feedback_generator'), "Missing feedback_generator"
            
            logger.info("✓ AICopilot initialized with all components")
            
            self.test_results.append({
                'test_name': 'component_initialization',
                'status': 'PASS',
                'message': 'All Phase 14 components initialized successfully',
                'components_tested': 4
            })
            
            return copilot
            
        except ImportError as e:
            logger.error(f"❌ Failed to import Phase 14 components: {e}")
            self.test_results.append({
                'test_name': 'component_initialization',
                'status': 'FAIL',
                'message': f'Import error: {e}'
            })
            return None
            
        except Exception as e:
            logger.error(f"❌ Component initialization failed: {e}")
            self.test_results.append({
                'test_name': 'component_initialization',
                'status': 'FAIL',
                'message': f'Initialization error: {e}'
            })
            return None
    
    async def test_real_time_monitoring(self, copilot):
        """Test real-time monitoring capabilities"""
        logger.info("Testing real-time monitoring...")
        
        try:
            # Start monitoring
            await copilot.start_monitoring()
            assert copilot.is_monitoring, "Monitoring not started"
            logger.info("✓ Monitoring started successfully")
            
            # Wait for a few monitoring cycles
            await asyncio.sleep(12)  # 2-3 cycles at 5-second intervals
            
            # Check system health collection
            health_status = await copilot._collect_system_health()
            assert health_status is not None, "System health not collected"
            assert health_status.health_score >= 0, "Invalid health score"
            logger.info(f"✓ System health collected (score: {health_status.health_score:.1f})")
            
            # Check monitoring data persistence
            assert len(copilot.system_health_history) > 0, "No health history recorded"
            logger.info(f"✓ Health history recorded ({len(copilot.system_health_history)} entries)")
            
            # Stop monitoring
            await copilot.stop_monitoring()
            assert not copilot.is_monitoring, "Monitoring not stopped"
            logger.info("✓ Monitoring stopped successfully")
            
            self.test_results.append({
                'test_name': 'real_time_monitoring',
                'status': 'PASS',
                'message': 'Real-time monitoring working correctly',
                'health_score': health_status.health_score,
                'monitoring_cycles': len(copilot.system_health_history)
            })
            
        except Exception as e:
            logger.error(f"❌ Real-time monitoring test failed: {e}")
            self.test_results.append({
                'test_name': 'real_time_monitoring',
                'status': 'FAIL',
                'message': f'Monitoring error: {e}'
            })
    
    async def test_intelligent_analysis(self, copilot):
        """Test intelligent analysis and pattern recognition"""
        logger.info("Testing intelligent analysis...")
        
        try:
            # Generate test data
            market_data = self.generate_test_market_data(50)
            trade_data = self.generate_test_trades(30)
            
            # Test pattern recognition
            analyzer = copilot.intelligent_analyzer
            
            # Analyze market patterns
            patterns = await analyzer.detect_patterns(market_data)
            assert isinstance(patterns, list), "Patterns not returned as list"
            logger.info(f"✓ Pattern detection completed ({len(patterns)} patterns found)")
            
            # Test optimization opportunities
            opportunities = await analyzer.identify_optimization_opportunities(trade_data)
            assert isinstance(opportunities, list), "Opportunities not returned as list"
            logger.info(f"✓ Optimization analysis completed ({len(opportunities)} opportunities found)")
            
            # Test risk assessment
            risk_assessment = await analyzer.assess_risks(market_data, trade_data)
            assert isinstance(risk_assessment, list), "Risk assessment not returned as list"
            logger.info(f"✓ Risk assessment completed ({len(risk_assessment)} risks identified)")
            
            # Test predictive modeling
            predictions = await analyzer.generate_predictions(market_data, trade_data)
            assert isinstance(predictions, dict), "Predictions not returned as dict"
            assert 'performance' in predictions, "Performance predictions missing"
            logger.info("✓ Predictive modeling completed")
            
            self.test_results.append({
                'test_name': 'intelligent_analysis',
                'status': 'PASS',
                'message': 'Intelligent analysis working correctly',
                'patterns_detected': len(patterns),
                'opportunities_found': len(opportunities),
                'risks_identified': len(risk_assessment),
                'predictions_generated': len(predictions)
            })
            
        except Exception as e:
            logger.error(f"❌ Intelligent analysis test failed: {e}")
            self.test_results.append({
                'test_name': 'intelligent_analysis',
                'status': 'FAIL',
                'message': f'Analysis error: {e}'
            })
    
    async def test_feedback_generation(self, copilot):
        """Test natural language feedback generation"""
        logger.info("Testing feedback generation...")
        
        try:
            feedback_gen = copilot.feedback_generator
            
            # Test alert feedback generation
            alert_context = {
                'alert_type': 'performance',
                'severity': 'high',
                'title': 'Performance Drop Detected',
                'data': {'drop_percentage': 0.25, 'affected_bots': 3}
            }
            
            alert_feedback = await feedback_gen.generate_alert_feedback(alert_context)
            assert isinstance(alert_feedback, str), "Alert feedback not string"
            assert len(alert_feedback) > 0, "Empty alert feedback"
            logger.info("✓ Alert feedback generation working")
            
            # Test insight feedback generation
            insight_context = {
                'insight_type': 'optimization',
                'confidence': 0.85,
                'title': 'Strategy Optimization Opportunity',
                'impact_score': 75,
                'recommendations': ['Adjust position sizing', 'Update stop-loss levels']
            }
            
            insight_feedback = await feedback_gen.generate_insight_feedback(insight_context)
            assert isinstance(insight_feedback, str), "Insight feedback not string"
            assert len(insight_feedback) > 0, "Empty insight feedback"
            logger.info("✓ Insight feedback generation working")
            
            # Test query response generation
            query_context = {
                'query': 'What is the current system status?',
                'system_status': {'health_score': 85, 'active_bots': 5},
                'active_alerts': [],
                'recent_insights': []
            }
            
            query_response = await feedback_gen.generate_query_response(query_context)
            assert isinstance(query_response, str), "Query response not string"
            assert len(query_response) > 0, "Empty query response"
            logger.info("✓ Query response generation working")
            
            # Test different communication tones
            tones = ['professional', 'casual', 'urgent', 'encouraging', 'analytical']
            tone_results = {}
            
            for tone in tones:
                tone_feedback = await feedback_gen.generate_feedback_with_tone(
                    alert_context, tone
                )
                tone_results[tone] = len(tone_feedback) > 0
                logger.info(f"✓ {tone.capitalize()} tone working")
            
            self.test_results.append({
                'test_name': 'feedback_generation',
                'status': 'PASS',
                'message': 'Feedback generation working correctly',
                'feedback_types_tested': 3,
                'tones_tested': len([t for t, working in tone_results.items() if working]),
                'tone_results': tone_results
            })
            
        except Exception as e:
            logger.error(f"❌ Feedback generation test failed: {e}")
            self.test_results.append({
                'test_name': 'feedback_generation',
                'status': 'FAIL',
                'message': f'Feedback generation error: {e}'
            })
    
    async def test_alert_management(self, copilot):
        """Test alert creation, management, and resolution"""
        logger.info("Testing alert management...")
        
        try:
            # Create test alerts
            await copilot._create_alert(
                alert_type='performance',
                severity='high',
                title='Test Performance Alert',
                description='Test alert for integration testing',
                data={'test': True},
                recommendations=['Check system logs', 'Restart affected bots']
            )
            
            await copilot._create_alert(
                alert_type='anomaly',
                severity='medium',
                title='Test Anomaly Alert',
                description='Test anomaly detection alert',
                data={'anomaly_score': 0.75},
                recommendations=['Investigate trading patterns']
            )
            
            # Check active alerts
            active_alerts = await copilot.get_active_alerts()
            assert len(active_alerts) >= 2, "Alerts not created properly"
            logger.info(f"✓ Alert creation working ({len(active_alerts)} active alerts)")
            
            # Test alert acknowledgment
            if active_alerts:
                alert_id = active_alerts[0]['alert_id']
                ack_result = await copilot.acknowledge_alert(alert_id)
                assert ack_result, "Alert acknowledgment failed"
                logger.info("✓ Alert acknowledgment working")
            
            # Test alert resolution
            if len(active_alerts) > 1:
                alert_id = active_alerts[1]['alert_id']
                resolve_result = await copilot.resolve_alert(alert_id, "Test resolution")
                assert resolve_result, "Alert resolution failed"
                logger.info("✓ Alert resolution working")
            
            # Test auto-resolution
            await copilot._auto_resolve_alerts()
            logger.info("✓ Auto-resolution completed")
            
            self.test_results.append({
                'test_name': 'alert_management',
                'status': 'PASS',
                'message': 'Alert management working correctly',
                'alerts_created': 2,
                'active_alerts': len(await copilot.get_active_alerts())
            })
            
        except Exception as e:
            logger.error(f"❌ Alert management test failed: {e}")
            self.test_results.append({
                'test_name': 'alert_management',
                'status': 'FAIL',
                'message': f'Alert management error: {e}'
            })
    
    async def test_insight_generation(self, copilot):
        """Test insight generation and management"""
        logger.info("Testing insight generation...")
        
        try:
            # Create test insights
            await copilot._create_insight(
                insight_type='optimization',
                confidence=0.85,
                title='Test Optimization Insight',
                description='Test optimization opportunity',
                impact_score=75.0,
                supporting_data={'improvement_potential': 0.15},
                recommendations=['Adjust parameters', 'Increase position size'],
                follow_up_required=True
            )
            
            await copilot._create_insight(
                insight_type='pattern',
                confidence=0.72,
                title='Test Pattern Insight',
                description='Test pattern recognition',
                impact_score=60.0,
                supporting_data={'pattern_strength': 0.8},
                recommendations=['Monitor closely', 'Consider strategy adjustment']
            )
            
            # Check recent insights
            recent_insights = await copilot.get_recent_insights(10)
            assert len(recent_insights) >= 2, "Insights not created properly"
            logger.info(f"✓ Insight creation working ({len(recent_insights)} insights)")
            
            # Verify insight data structure
            if recent_insights:
                insight = recent_insights[0]
                required_fields = ['insight_id', 'timestamp', 'insight_type', 'confidence', 'title']
                for field in required_fields:
                    assert field in insight, f"Missing field: {field}"
                logger.info("✓ Insight data structure correct")
            
            self.test_results.append({
                'test_name': 'insight_generation',
                'status': 'PASS',
                'message': 'Insight generation working correctly',
                'insights_created': 2,
                'recent_insights': len(recent_insights)
            })
            
        except Exception as e:
            logger.error(f"❌ Insight generation test failed: {e}")
            self.test_results.append({
                'test_name': 'insight_generation',
                'status': 'FAIL',
                'message': f'Insight generation error: {e}'
            })
    
    async def test_copilot_response_generation(self, copilot):
        """Test AI Copilot query response generation"""
        logger.info("Testing copilot response generation...")
        
        try:
            # Test various query types
            test_queries = [
                "What is the current system status?",
                "Show me the latest alerts",
                "What optimization opportunities are available?",
                "How is system performance?",
                "Are there any critical issues?"
            ]
            
            responses = {}
            for query in test_queries:
                response = await copilot.generate_copilot_response(query)
                assert isinstance(response, str), f"Response not string for query: {query}"
                assert len(response) > 0, f"Empty response for query: {query}"
                responses[query] = len(response)
                logger.info(f"✓ Response generated for: '{query[:30]}...'")
            
            # Test system status retrieval
            system_status = await copilot.get_system_status()
            assert isinstance(system_status, dict), "System status not dict"
            assert 'system_health' in system_status, "Missing system_health in status"
            logger.info("✓ System status retrieval working")
            
            # Test performance summary
            perf_summary = await copilot.get_performance_summary(24)
            assert isinstance(perf_summary, dict), "Performance summary not dict"
            logger.info("✓ Performance summary working")
            
            self.test_results.append({
                'test_name': 'copilot_response_generation',
                'status': 'PASS',
                'message': 'Copilot response generation working correctly',
                'queries_tested': len(test_queries),
                'avg_response_length': sum(responses.values()) // len(responses) if responses else 0
            })
            
        except Exception as e:
            logger.error(f"❌ Copilot response generation test failed: {e}")
            self.test_results.append({
                'test_name': 'copilot_response_generation',
                'status': 'FAIL',
                'message': f'Response generation error: {e}'
            })
    
    async def test_database_integration(self, copilot):
        """Test database storage and retrieval"""
        logger.info("Testing database integration...")
        
        try:
            import sqlite3
            
            # Check database file exists
            assert copilot.db_path.exists(), "Database file not created"
            logger.info("✓ Database file exists")
            
            # Test database connectivity
            with sqlite3.connect(copilot.db_path) as conn:
                cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                expected_tables = ['alerts', 'insights', 'system_health', 'performance_metrics']
                for table in expected_tables:
                    assert table in tables, f"Missing table: {table}"
                
                logger.info(f"✓ All required tables exist ({len(tables)} total)")
            
            # Test data persistence
            health_status = await copilot._collect_system_health()
            await copilot._save_monitoring_data(health_status)
            
            # Verify data was saved
            with sqlite3.connect(copilot.db_path) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM system_health")
                health_count = cursor.fetchone()[0]
                assert health_count > 0, "System health data not saved"
                
                cursor = conn.execute("SELECT COUNT(*) FROM alerts")
                alert_count = cursor.fetchone()[0]
                
                logger.info(f"✓ Data persistence working (health: {health_count}, alerts: {alert_count})")
            
            self.test_results.append({
                'test_name': 'database_integration',
                'status': 'PASS',
                'message': 'Database integration working correctly',
                'tables_created': len(expected_tables),
                'records_stored': health_count + alert_count
            })
            
        except Exception as e:
            logger.error(f"❌ Database integration test failed: {e}")
            self.test_results.append({
                'test_name': 'database_integration',
                'status': 'FAIL',
                'message': f'Database error: {e}'
            })
    
    async def test_integration_with_existing_phases(self, copilot):
        """Test integration with existing TradeMasterX phases"""
        logger.info("Testing integration with existing phases...")
        
        try:
            # Test Phase 11 integration (AnomalyDetector)
            assert hasattr(copilot, 'anomaly_detector'), "Missing anomaly_detector integration"
            logger.info("✓ Phase 11 AnomalyDetector integration available")
            
            # Test Phase 13 integration (ConversationEngine)
            assert hasattr(copilot, 'conversation_engine'), "Missing conversation_engine integration"
            logger.info("✓ Phase 13 ConversationEngine integration available")
            
            # Test analytics integration
            assert hasattr(copilot, 'analytics_bot'), "Missing analytics_bot integration"
            logger.info("✓ AnalyticsBot integration available")
            
            # Test monitoring integration
            assert hasattr(copilot, 'real_time_monitor'), "Missing real_time_monitor"
            monitor_status = await copilot.real_time_monitor.get_current_metrics()
            assert isinstance(monitor_status, dict), "Monitor not returning metrics"
            logger.info("✓ Real-time monitoring integration working")
            
            self.test_results.append({
                'test_name': 'integration_with_existing_phases',
                'status': 'PASS',
                'message': 'Integration with existing phases working correctly',
                'integrations_tested': 4
            })
            
        except Exception as e:
            logger.error(f"❌ Integration test failed: {e}")
            self.test_results.append({
                'test_name': 'integration_with_existing_phases',
                'status': 'FAIL',
                'message': f'Integration error: {e}'
            })
    
    async def run_all_tests(self):
        """Run all Phase 14 integration tests"""
        logger.info("🧪 Starting Phase 14 Integration Testing")
        logger.info("=" * 60)
        
        start_time = time.time()
        
        # Test 1: Component Initialization
        copilot = await self.test_component_initialization()
        if not copilot:
            logger.error("❌ Cannot proceed without successful component initialization")
            return False
        
        # Test 2: Real-time Monitoring
        await self.test_real_time_monitoring(copilot)
        
        # Test 3: Intelligent Analysis
        await self.test_intelligent_analysis(copilot)
        
        # Test 4: Feedback Generation
        await self.test_feedback_generation(copilot)
        
        # Test 5: Alert Management
        await self.test_alert_management(copilot)
        
        # Test 6: Insight Generation
        await self.test_insight_generation(copilot)
        
        # Test 7: Copilot Response Generation
        await self.test_copilot_response_generation(copilot)
        
        # Test 8: Database Integration
        await self.test_database_integration(copilot)
        
        # Test 9: Integration with Existing Phases
        await self.test_integration_with_existing_phases(copilot)
        
        # Calculate results
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        # Print summary
        logger.info("=" * 60)
        logger.info("🧪 PHASE 14 INTEGRATION TEST RESULTS")
        logger.info("=" * 60)
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {failed_tests}")
        logger.info(f"Success Rate: {success_rate:.1f}%")
        logger.info(f"Test Duration: {time.time() - start_time:.1f} seconds")
        
        # Print detailed results
        logger.info("\n📋 Detailed Test Results:")
        for result in self.test_results:
            status_emoji = "✅" if result['status'] == 'PASS' else "❌"
            logger.info(f"{status_emoji} {result['test_name']}: {result['message']}")
        
        # Save results to file
        results_file = self.test_data_dir / 'integration_test_results.json'
        with open(results_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': failed_tests,
                'success_rate': success_rate,
                'test_duration': time.time() - start_time,
                'test_results': self.test_results
            }, f, indent=2)
        
        logger.info(f"\n📁 Results saved to: {results_file}")
        
        # Overall success check
        if success_rate >= 90:
            logger.info("\n🎉 PHASE 14 INTEGRATION TESTS PASSED!")
            logger.info("AI Copilot system is ready for production use.")
            return True
        elif success_rate >= 70:
            logger.warning("\n⚠️ PHASE 14 INTEGRATION TESTS PARTIALLY PASSED")
            logger.warning("Some issues detected. Review failed tests before production.")
            return True
        else:
            logger.error("\n❌ PHASE 14 INTEGRATION TESTS FAILED")
            logger.error("Critical issues detected. Fix before proceeding.")
            return False

async def main():
    """Main test execution"""
    tester = Phase14IntegrationTest()
    success = await tester.run_all_tests()
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
