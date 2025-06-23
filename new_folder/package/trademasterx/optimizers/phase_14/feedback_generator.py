"""
TradeMasterX 2.0 - Phase 14: Feedback Generator
Natural language response generation system with human-like feedback
"""

import asyncio
import json
import logging
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import sqlite3

from ...core.bot_registry import BaseBot


@dataclass
class FeedbackTemplate:
    """Feedback template data structure"""
    template_id: str
    category: str  # 'alert', 'insight', 'query', 'status', 'recommendation'
    tone: str  # 'professional', 'casual', 'urgent', 'encouraging', 'analytical'
    template: str
    variables: List[str]
    context_tags: List[str]


@dataclass
class GeneratedFeedback:
    """Generated feedback data structure"""
    feedback_id: str
    timestamp: str
    category: str
    tone: str
    message: str
    context: Dict[str, Any]
    template_used: str
    personalization_score: float


class FeedbackGenerator(BaseBot):
    """
    Feedback Generator - Natural language response generation system
    
    Capabilities:
    - Human-like alert and insight commentary
    - Context-aware response generation
    - Personalized communication style    - Multi-tone feedback (professional, casual, urgent, etc.)
    - Interactive query responses
    - Adaptive language patterns
    - Intelligent recommendation phrasing
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize Feedback Generator"""
        super().__init__(
            name="Feedback Generator",
            config=config or {}
        )
        
        self.config = config or {}
        self.logger = self._setup_logging()
        
        # Communication settings
        self.default_tone = config.get('default_tone', 'professional')
        self.personalization_enabled = config.get('personalization', True)
        self.context_awareness = config.get('context_awareness', True)
        self.response_length = config.get('response_length', 'medium')  # short, medium, long
        
        # Language patterns
        self.language_patterns = {
            'professional': {
                'greetings': ['I notice', 'The analysis indicates', 'Based on current data', 'According to my assessment'],
                'connectors': ['Additionally', 'Furthermore', 'Moreover', 'However'],
                'conclusions': ['I recommend', 'The suggested action is', 'My analysis suggests', 'The optimal approach would be']
            },
            'casual': {
                'greetings': ['Hey there!', 'Just a heads up', 'Quick update', 'FYI'],
                'connectors': ['Also', 'Plus', 'Oh, and', 'By the way'],
                'conclusions': ['You might want to', 'I\'d suggest', 'Maybe try', 'How about']
            },
            'urgent': {
                'greetings': ['ALERT:', 'Urgent:', 'Critical notice:', 'Immediate attention required:'],
                'connectors': ['More importantly', 'Critically', 'Most urgently', 'Immediately'],
                'conclusions': ['Take immediate action:', 'Act now:', 'Urgent recommendation:', 'Critical next step:']
            },
            'encouraging': {
                'greetings': ['Great news!', 'Looking good!', 'Positive update:', 'Things are improving!'],
                'connectors': ['Even better', 'What\'s more', 'Additionally', 'Another positive sign'],
                'conclusions': ['Keep it up!', 'You\'re on the right track', 'Continue this approach', 'Excellent progress']
            },
            'analytical': {
                'greetings': ['Data analysis reveals', 'Statistical evidence shows', 'The metrics indicate', 'Quantitative analysis suggests'],
                'connectors': ['Correlating with this', 'The data further shows', 'Additional metrics confirm', 'Cross-referencing indicates'],
                'conclusions': ['The data-driven recommendation is', 'Statistical analysis suggests', 'Based on quantitative evidence', 'The optimal data-backed approach']
            }
        }
        
        # Data storage
        self.data_dir = Path(config.get('data_dir', 'data/feedback_generator'))
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.data_dir / 'feedback_data.db'
        
        # Feedback tracking
        self.generated_feedback = {}
        self.feedback_templates = {}
        self.user_preferences = {}
        
        # Performance metrics
        self.generation_stats = {
            'total_generated': 0,
            'by_category': {},
            'by_tone': {},
            'average_personalization_score': 0.0
        }
        
        # Initialize database and templates
        self._init_database()
        self._load_feedback_templates()
        
        self.logger.info("💬 Feedback Generator initialized successfully")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for Feedback Generator"""
        logger = logging.getLogger(f"{self.__class__.__name__}")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _init_database(self):
        """Initialize feedback generator database"""
        with sqlite3.connect(self.db_path) as conn:
            # Feedback templates table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS feedback_templates (
                    template_id TEXT PRIMARY KEY,
                    category TEXT NOT NULL,
                    tone TEXT NOT NULL,
                    template TEXT NOT NULL,
                    variables TEXT,
                    context_tags TEXT,
                    created_timestamp TEXT NOT NULL
                )
            """)
            
            # Generated feedback table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS generated_feedback (
                    feedback_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    category TEXT NOT NULL,
                    tone TEXT NOT NULL,
                    message TEXT NOT NULL,
                    context TEXT,
                    template_used TEXT,
                    personalization_score REAL
                )
            """)
            
            # User preferences table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_preferences (
                    user_id TEXT PRIMARY KEY,
                    preferred_tone TEXT,
                    communication_style TEXT,
                    verbosity_level TEXT,
                    preferences TEXT,
                    updated_timestamp TEXT NOT NULL
                )
            """)
    
    def _load_feedback_templates(self):
        """Load predefined feedback templates"""
        try:
            # Alert feedback templates
            alert_templates = {
                'critical_performance': {
                    'professional': "I've detected a critical performance issue with win rate dropping to {win_rate}. This requires immediate attention to prevent further losses. {recommendations}",
                    'urgent': "CRITICAL ALERT: Performance has dropped to {win_rate}! Immediate action required to prevent catastrophic losses. {recommendations}",
                    'analytical': "Statistical analysis reveals critical performance degradation: win rate = {win_rate} (σ = {sigma}). Quantitative recommendations: {recommendations}"
                },
                'system_instability': {
                    'professional': "System stability concerns detected with {failure_rate} bot failure rate. I recommend investigating the root causes and implementing stability measures.",
                    'casual': "Hey, we've got some bots acting up - {failure_rate} failure rate. Might want to check what's going on there.",
                    'urgent': "SYSTEM INSTABILITY: {failure_rate} bot failure rate detected! Take immediate action to prevent system-wide issues."
                },
                'resource_exhaustion': {
                    'professional': "Resource usage has reached critical levels (Memory: {memory_usage}, CPU: {cpu_usage}). System scaling or load reduction is recommended.",
                    'urgent': "RESOURCE CRISIS: Memory at {memory_usage}, CPU at {cpu_usage}! Immediate intervention required!",
                    'analytical': "Resource utilization metrics indicate critical threshold breach: Memory={memory_usage}, CPU={cpu_usage}. Recommend immediate capacity management."
                }
            }
            
            # Insight feedback templates
            insight_templates = {
                'pattern_detection': {
                    'professional': "I've identified an interesting pattern: {pattern_name} with {confidence} confidence. This could impact performance by {impact_score}%.",
                    'casual': "Found something cool! There's a {pattern_name} pattern happening with {confidence} confidence. Could be worth {impact_score}% improvement.",
                    'analytical': "Pattern recognition algorithm detected: {pattern_name} (confidence={confidence}, impact_coefficient={impact_score})."
                },
                'optimization_opportunity': {
                    'professional': "I've discovered an optimization opportunity: {opportunity_name}. Potential improvement: {improvement}%. Implementation difficulty: {difficulty}.",
                    'encouraging': "Great news! I found a way to improve things: {opportunity_name}. We could see {improvement}% better performance!",
                    'analytical': "Optimization analysis reveals: {opportunity_name} (improvement_potential={improvement}%, complexity_rating={difficulty})."
                }
            }
            
            # Query response templates
            query_templates = {
                'status_request': {
                    'professional': "Current system status: {overall_health} health with {health_score}% score. Active alerts: {active_alerts}. Performance: {win_rate} win rate.",
                    'casual': "Everything's looking {overall_health}! Health score is {health_score}%, {active_alerts} alerts active, and we're winning {win_rate} of trades.",
                    'analytical': "System metrics: health_score={health_score}%, alert_count={active_alerts}, win_rate={win_rate}, status={overall_health}."
                },
                'general_inquiry': {
                    'professional': "Based on current system analysis, {main_point}. {supporting_evidence} {recommendation}",
                    'casual': "So here's the deal: {main_point}. {supporting_evidence} {recommendation}",
                    'analytical': "Data analysis indicates: {main_point}. Supporting metrics: {supporting_evidence}. Recommended action: {recommendation}"
                }
            }
            
            # Store all templates
            all_templates = {
                'alert': alert_templates,
                'insight': insight_templates,
                'query': query_templates
            }
            
            # Save to database
            with sqlite3.connect(self.db_path) as conn:
                for category, category_templates in all_templates.items():
                    for template_name, tone_templates in category_templates.items():
                        for tone, template in tone_templates.items():
                            template_id = f"{category}_{template_name}_{tone}"
                            variables = self._extract_template_variables(template)
                            
                            conn.execute("""
                                INSERT OR REPLACE INTO feedback_templates
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                            """, (
                                template_id,
                                category,
                                tone,
                                template,
                                json.dumps(variables),
                                json.dumps([template_name]),
                                datetime.now().isoformat()
                            ))
            
            self.logger.info("📝 Feedback templates loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Error loading feedback templates: {e}")
    
    def _extract_template_variables(self, template: str) -> List[str]:
        """Extract variable names from template string"""
        import re
        variables = re.findall(r'\{(\w+)\}', template)
        return list(set(variables))
    
    async def generate_alert_feedback(self, alert) -> str:
        """Generate human-like feedback for an alert"""
        try:
            # Determine tone based on alert severity
            tone_mapping = {
                'low': 'casual',
                'medium': 'professional',
                'high': 'urgent',
                'critical': 'urgent'
            }
            
            tone = tone_mapping.get(alert.severity, 'professional')
            
            # Select appropriate template based on alert type
            template_map = {
                'performance': 'critical_performance',
                'system': 'system_instability',
                'resource': 'resource_exhaustion',
                'anomaly': 'system_instability'
            }
            
            template_name = template_map.get(alert.alert_type, 'system_instability')
            
            # Get template
            template = await self._get_template('alert', template_name, tone)
            
            if not template:
                # Fallback to generic feedback
                return await self._generate_generic_alert_feedback(alert, tone)
            
            # Prepare context variables
            context_vars = {
                'alert_type': alert.alert_type,
                'severity': alert.severity,
                'title': alert.title,
                'description': alert.description,
                **alert.data,
                'recommendations': '. '.join(alert.recommendations[:2])  # First 2 recommendations
            }
            
            # Format template
            try:
                feedback_message = template.format(**context_vars)
            except KeyError as e:
                # Handle missing variables
                feedback_message = await self._generate_generic_alert_feedback(alert, tone)
            
            # Add personality elements
            feedback_message = await self._add_personality_elements(feedback_message, tone, 'alert')
            
            # Save generated feedback
            await self._save_generated_feedback('alert', tone, feedback_message, context_vars, template_name)
            
            return feedback_message
            
        except Exception as e:
            self.logger.error(f"Error generating alert feedback: {e}")
            return f"Alert detected: {alert.title}. Please review the details and take appropriate action."
    
    async def generate_insight_feedback(self, insight) -> str:
        """Generate human-like feedback for an insight"""
        try:
            # Determine tone based on insight impact
            if insight.impact_score > 80:
                tone = 'encouraging'
            elif insight.impact_score > 60:
                tone = 'professional'
            else:
                tone = 'analytical'
            
            # Select template based on insight type
            template_map = {
                'pattern': 'pattern_detection',
                'optimization': 'optimization_opportunity',
                'risk': 'pattern_detection',
                'opportunity': 'optimization_opportunity'
            }
            
            template_name = template_map.get(insight.insight_type, 'pattern_detection')
            
            # Get template
            template = await self._get_template('insight', template_name, tone)
            
            if not template:
                return await self._generate_generic_insight_feedback(insight, tone)
            
            # Prepare context variables
            context_vars = {
                'insight_type': insight.insight_type,
                'confidence': f"{insight.confidence:.1%}",
                'title': insight.title,
                'description': insight.description,
                'impact_score': f"{insight.impact_score:.0f}",
                'pattern_name': insight.title.replace('Pattern Detected: ', '').replace('Optimization Opportunity: ', ''),
                'opportunity_name': insight.title.replace('Optimization Opportunity: ', ''),
                'improvement': f"{insight.impact_score:.0f}",
                'difficulty': 'medium',  # Default difficulty
                **insight.supporting_data
            }
            
            # Format template
            try:
                feedback_message = template.format(**context_vars)
            except KeyError:
                feedback_message = await self._generate_generic_insight_feedback(insight, tone)
            
            # Add personality elements
            feedback_message = await self._add_personality_elements(feedback_message, tone, 'insight')
            
            # Save generated feedback
            await self._save_generated_feedback('insight', tone, feedback_message, context_vars, template_name)
            
            return feedback_message
            
        except Exception as e:
            self.logger.error(f"Error generating insight feedback: {e}")
            return f"New insight discovered: {insight.title} (confidence: {insight.confidence:.1%})"
    
    async def generate_query_response(self, context: Dict[str, Any]) -> str:
        """Generate response to user query"""
        try:
            query = context.get('query', '').lower()
            
            # Determine response type and tone
            if any(word in query for word in ['status', 'health', 'how', 'doing']):
                template_name = 'status_request'
                tone = 'professional'
            else:
                template_name = 'general_inquiry'
                tone = 'professional'
            
            # Get template
            template = await self._get_template('query', template_name, tone)
            
            if not template:
                return await self._generate_generic_query_response(context, tone)
            
            # Prepare context for status request
            if template_name == 'status_request':
                system_status = context.get('system_status', {}).get('system_health', {})
                context_vars = {
                    'overall_health': system_status.get('overall_health', 'unknown'),
                    'health_score': f"{system_status.get('health_score', 0):.0f}",
                    'active_alerts': len(context.get('active_alerts', [])),
                    'win_rate': f"{system_status.get('win_rate_24h', 0.5):.1%}"
                }
            else:
                # General inquiry response
                insights = context.get('recent_insights', [])
                main_insight = insights[0] if insights else {}
                
                context_vars = {
                    'main_point': main_insight.get('title', 'System is operating normally'),
                    'supporting_evidence': f"Confidence level: {main_insight.get('confidence', 0.5):.1%}" if main_insight else "All systems operational",
                    'recommendation': 'Continue monitoring for optimal performance'
                }
            
            # Format template
            try:
                feedback_message = template.format(**context_vars)
            except KeyError:
                feedback_message = await self._generate_generic_query_response(context, tone)
            
            # Add personality elements
            feedback_message = await self._add_personality_elements(feedback_message, tone, 'query')
            
            # Save generated feedback
            await self._save_generated_feedback('query', tone, feedback_message, context_vars, template_name)
            
            return feedback_message
            
        except Exception as e:
            self.logger.error(f"Error generating query response: {e}")
            return "I'm here to help! Could you please provide more details about what you'd like to know?"
    
    async def generate_status_update(self, system_status: Dict[str, Any]) -> str:
        """Generate human-like status update"""
        try:
            health_data = system_status.get('system_health', {})
            health_score = health_data.get('health_score', 0)
            overall_health = health_data.get('overall_health', 'unknown')
            
            # Determine tone based on health
            if health_score >= 80:
                tone = 'encouraging'
            elif health_score >= 60:
                tone = 'professional'
            elif health_score >= 40:
                tone = 'analytical'
            else:
                tone = 'urgent'
            
            # Generate contextual status message
            if overall_health == 'excellent':
                messages = [
                    f"System is performing excellently with a {health_score:.0f}% health score! All indicators are green.",
                    f"Outstanding performance detected! Health at {health_score:.0f}% - everything's running smoothly.",
                    f"Excellent system status confirmed. {health_score:.0f}% health score indicates optimal operation."
                ]
            elif overall_health == 'good':
                messages = [
                    f"System health is good at {health_score:.0f}%. Minor optimizations available but overall stable.",
                    f"Solid performance with {health_score:.0f}% health. System operating within normal parameters.",
                    f"Good system status maintained. {health_score:.0f}% health score shows reliable operation."
                ]
            elif overall_health == 'fair':
                messages = [
                    f"System health is fair at {health_score:.0f}%. Some attention needed for optimization.",
                    f"Moderate performance detected. {health_score:.0f}% health - consider reviewing current strategies.",
                    f"Fair system status with {health_score:.0f}% health. Room for improvement identified."
                ]
            elif overall_health == 'poor':
                messages = [
                    f"System health is concerning at {health_score:.0f}%. Immediate review recommended.",
                    f"Poor performance detected with {health_score:.0f}% health. Action required to improve stability.",
                    f"System requires attention - {health_score:.0f}% health score indicates issues need addressing."
                ]
            else:  # critical
                messages = [
                    f"CRITICAL: System health at {health_score:.0f}%! Immediate intervention required.",
                    f"System in critical state with {health_score:.0f}% health! Take immediate action.",
                    f"URGENT: Critical system status detected at {health_score:.0f}% health!"
                ]
            
            # Select message based on tone
            if tone == 'encouraging':
                base_message = messages[0]
            elif tone == 'professional':
                base_message = messages[1] if len(messages) > 1 else messages[0]
            else:
                base_message = messages[-1]
            
            # Add personality elements
            status_message = await self._add_personality_elements(base_message, tone, 'status')
            
            # Save generated feedback
            await self._save_generated_feedback('status', tone, status_message, health_data, 'status_update')
            
            return status_message
            
        except Exception as e:
            self.logger.error(f"Error generating status update: {e}")
            return "System status update available. Please check the dashboard for current metrics."
    
    async def _get_template(self, category: str, template_name: str, tone: str) -> Optional[str]:
        """Get feedback template from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT template FROM feedback_templates 
                    WHERE category = ? AND tone = ? AND context_tags LIKE ?
                """, (category, tone, f'%{template_name}%'))
                
                result = cursor.fetchone()
                return result[0] if result else None
                
        except Exception as e:
            self.logger.error(f"Error getting template: {e}")
            return None
    
    async def _add_personality_elements(self, message: str, tone: str, category: str) -> str:
        """Add personality elements to make feedback more human-like"""
        try:
            patterns = self.language_patterns.get(tone, self.language_patterns['professional'])
            
            # Add random connector for longer messages
            if len(message) > 100 and category in ['insight', 'query']:
                connector = random.choice(patterns['connectors'])
                # Insert connector in middle of message if there's a period
                if '. ' in message:
                    parts = message.split('. ', 1)
                    if len(parts) == 2:
                        message = f"{parts[0]}. {connector}, {parts[1].lower()}"
            
            # Add appropriate emojis for different tones
            emoji_map = {
                'encouraging': ['🎉', '✨', '💪', ''],
                'urgent': ['🚨', '⚠️', '🔥'],
                'analytical': ['📊', '📈', '🔍'],
                'professional': ['✅', '📋', '💼'],
                'casual': ['👍', '😊', '🔥']
            }
            
            if tone in emoji_map and random.random() < 0.3:  # 30% chance of emoji
                emoji = random.choice(emoji_map[tone])
                message = f"{emoji} {message}"
            
            return message
            
        except Exception as e:
            self.logger.error(f"Error adding personality elements: {e}")
            return message
    
    async def _generate_generic_alert_feedback(self, alert, tone: str) -> str:
        """Generate generic alert feedback as fallback"""
        patterns = self.language_patterns.get(tone, self.language_patterns['professional'])
        greeting = random.choice(patterns['greetings'])
        conclusion = random.choice(patterns['conclusions'])
        
        return f"{greeting} {alert.title}. Severity: {alert.severity}. {conclusion} {alert.recommendations[0] if alert.recommendations else 'Please review and take appropriate action.'}"
    
    async def _generate_generic_insight_feedback(self, insight, tone: str) -> str:
        """Generate generic insight feedback as fallback"""
        patterns = self.language_patterns.get(tone, self.language_patterns['professional'])
        greeting = random.choice(patterns['greetings'])
        
        return f"{greeting} {insight.title} (confidence: {insight.confidence:.1%}, impact: {insight.impact_score:.0f}%). {insight.description}"
    
    async def _generate_generic_query_response(self, context: Dict[str, Any], tone: str) -> str:
        """Generate generic query response as fallback"""
        patterns = self.language_patterns.get(tone, self.language_patterns['professional'])
        greeting = random.choice(patterns['greetings'])
        
        query = context.get('query', 'your question')
        return f"{greeting} I understand you're asking about {query}. Let me analyze the current system state and provide you with relevant information."
    
    async def _save_generated_feedback(self, category: str, tone: str, message: str, 
                                     context: Dict[str, Any], template_used: str):
        """Save generated feedback to database"""
        try:
            feedback_id = f"feedback_{int(datetime.now().timestamp() * 1000)}"
            
            # Calculate personalization score (simplified)
            personalization_score = self._calculate_personalization_score(message, tone, category)
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO generated_feedback
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    feedback_id,
                    datetime.now().isoformat(),
                    category,
                    tone,
                    message,
                    json.dumps(context),
                    template_used,
                    personalization_score
                ))
            
            # Update statistics
            self.generation_stats['total_generated'] += 1
            self.generation_stats['by_category'][category] = self.generation_stats['by_category'].get(category, 0) + 1
            self.generation_stats['by_tone'][tone] = self.generation_stats['by_tone'].get(tone, 0) + 1
            
        except Exception as e:
            self.logger.error(f"Error saving generated feedback: {e}")
    
    def _calculate_personalization_score(self, message: str, tone: str, category: str) -> float:
        """Calculate personalization score for generated feedback"""
        try:
            score = 0.5  # Base score
            
            # Tone appropriateness
            if tone in ['encouraging', 'casual'] and any(word in message.lower() for word in ['great', 'excellent', 'good']):
                score += 0.2
            
            # Message length appropriateness
            if self.response_length == 'short' and len(message) < 100:
                score += 0.1
            elif self.response_length == 'medium' and 100 <= len(message) <= 300:
                score += 0.1
            elif self.response_length == 'long' and len(message) > 300:
                score += 0.1
            
            # Context relevance
            if category == 'alert' and any(word in message.lower() for word in ['immediate', 'action', 'recommend']):
                score += 0.1
            
            # Personality elements
            if any(emoji in message for emoji in ['🎉', '✨', '🚨', '📊', '✅']):
                score += 0.1
            
            return min(1.0, score)
            
        except Exception as e:
            self.logger.error(f"Error calculating personalization score: {e}")
            return 0.5
    
    # Public API methods
    
    async def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]):
        """Update user communication preferences"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO user_preferences
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    user_id,
                    preferences.get('tone', self.default_tone),
                    preferences.get('communication_style', 'balanced'),
                    preferences.get('verbosity', self.response_length),
                    json.dumps(preferences),
                    datetime.now().isoformat()
                ))
            
            self.user_preferences[user_id] = preferences
            self.logger.info(f"Updated preferences for user {user_id}")
            
        except Exception as e:
            self.logger.error(f"Error updating user preferences: {e}")
    
    async def get_feedback_analytics(self, hours: int = 24) -> Dict[str, Any]:
        """Get feedback generation analytics"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            with sqlite3.connect(self.db_path) as conn:
                # Get feedback count by category
                cursor = conn.execute("""
                    SELECT category, COUNT(*) as count 
                    FROM generated_feedback 
                    WHERE timestamp >= ?
                    GROUP BY category
                """, (cutoff_time.isoformat(),))
                
                category_stats = dict(cursor.fetchall())
                
                # Get feedback count by tone
                cursor = conn.execute("""
                    SELECT tone, COUNT(*) as count 
                    FROM generated_feedback 
                    WHERE timestamp >= ?
                    GROUP BY tone
                """, (cutoff_time.isoformat(),))
                
                tone_stats = dict(cursor.fetchall())
                
                # Get average personalization score
                cursor = conn.execute("""
                    SELECT AVG(personalization_score) as avg_score
                    FROM generated_feedback 
                    WHERE timestamp >= ?
                """, (cutoff_time.isoformat(),))
                
                avg_personalization = cursor.fetchone()[0] or 0.0
                
                return {
                    'time_period_hours': hours,
                    'total_feedback_generated': sum(category_stats.values()),
                    'by_category': category_stats,
                    'by_tone': tone_stats,
                    'average_personalization_score': avg_personalization,
                    'generation_stats': self.generation_stats,
                    'generated_timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"Error getting feedback analytics: {e}")
            return {
                'time_period_hours': hours,
                'total_feedback_generated': 0,
                'by_category': {},
                'by_tone': {},
                'average_personalization_score': 0.0,
                'error': str(e)
            }
    
    async def get_recent_feedback(self, limit: int = 10, category: str = None) -> List[Dict[str, Any]]:
        """Get recent generated feedback"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                if category:
                    cursor = conn.execute("""
                        SELECT * FROM generated_feedback 
                        WHERE category = ?
                        ORDER BY timestamp DESC 
                        LIMIT ?
                    """, (category, limit))
                else:
                    cursor = conn.execute("""
                        SELECT * FROM generated_feedback 
                        ORDER BY timestamp DESC 
                        LIMIT ?
                    """, (limit,))
                
                feedback_list = []
                for row in cursor.fetchall():
                    feedback_list.append({
                        'feedback_id': row[0],
                        'timestamp': row[1],
                        'category': row[2],
                        'tone': row[3],
                        'message': row[4],
                        'context': json.loads(row[5]) if row[5] else {},
                        'template_used': row[6],
                        'personalization_score': row[7]
                    })
                
                return feedback_list
                
        except Exception as e:
            self.logger.error(f"Error getting recent feedback: {e}")
            return []
    
    async def generate_recommendation_text(self, recommendations: List[str], tone: str = None) -> str:
        """Generate human-like text for recommendations"""
        try:
            if not recommendations:
                return "No specific recommendations available at this time."
            
            tone = tone or self.default_tone
            patterns = self.language_patterns.get(tone, self.language_patterns['professional'])
            
            if len(recommendations) == 1:
                conclusion = random.choice(patterns['conclusions'])
                return f"{conclusion} {recommendations[0]}"
            
            # Multiple recommendations
            connector = random.choice(patterns['connectors'])
            conclusion = random.choice(patterns['conclusions'])
            
            if len(recommendations) == 2:
                return f"{conclusion} {recommendations[0]}. {connector}, {recommendations[1]}"
            
            # More than 2 recommendations
            main_recs = recommendations[:2]
            additional = len(recommendations) - 2
            
            text = f"{conclusion} {main_recs[0]}. {connector}, {main_recs[1]}"
            if additional > 0:
                text += f" and {additional} additional optimization{'s' if additional > 1 else ''}"
            
            return text
            
        except Exception as e:
            self.logger.error(f"Error generating recommendation text: {e}")
            return "Please review the available recommendations and take appropriate action."
    
    # Bot lifecycle methods
    
    async def start(self) -> bool:
        """Start Feedback Generator"""
        try:
            self.status = "running"
            self.logger.info("💬 Feedback Generator started successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error starting Feedback Generator: {e}")
            self.status = "error"
            return False
    
    async def stop(self) -> bool:
        """Stop Feedback Generator"""
        try:
            self.status = "stopped"
            self.logger.info("💬 Feedback Generator stopped successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error stopping Feedback Generator: {e}")
            return False
    
    async def get_status(self) -> Dict[str, Any]:
        """Get Feedback Generator status"""
        try:
            return {
                'bot_id': self.bot_id,
                'name': self.name,
                'status': self.status,
                'total_feedback_generated': self.generation_stats['total_generated'],
                'templates_loaded': len(self.feedback_templates),
                'user_preferences': len(self.user_preferences),
                'default_tone': self.default_tone,
                'personalization_enabled': self.personalization_enabled,
                'last_updated': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error getting Feedback Generator status: {e}")
            return {
                'bot_id': self.bot_id,
                'name': self.name,
                'status': 'error',
                'error': str(e)
            }
        
    async def generate_feedback_with_tone(self, context: Dict[str, Any], tone: str) -> str:
        """Generate feedback with specific tone for any context type"""
        try:
            # Determine context type from the provided context
            if 'alert_type' in context or 'severity' in context:
                # This is an alert context
                return await self._generate_alert_feedback_with_tone(context, tone)
            elif 'insight_type' in context or 'confidence' in context:
                # This is an insight context
                return await self._generate_insight_feedback_with_tone(context, tone)
            elif 'query' in context:
                # This is a query context
                return await self._generate_query_feedback_with_tone(context, tone)
            else:
                # Generic context - treat as status update
                return await self._generate_generic_feedback_with_tone(context, tone)
                
        except Exception as e:
            self.logger.error(f"Error generating feedback with tone: {e}")
            return f"I understand you need information with a {tone} tone. Let me provide you with the best assistance I can."
    
    async def _generate_alert_feedback_with_tone(self, alert_context: Dict[str, Any], tone: str) -> str:
        """Generate alert feedback with specific tone"""
        try:
            # Get appropriate template for alert type and tone
            alert_type = alert_context.get('alert_type', 'system')
            severity = alert_context.get('severity', 'medium')
            
            template_map = {
                'performance': 'critical_performance',
                'system': 'system_instability',
                'resource': 'resource_exhaustion',
                'anomaly': 'system_instability'
            }
            
            template_name = template_map.get(alert_type, 'system_instability')
            template = await self._get_template('alert', template_name, tone)
            
            if not template:
                # Generate generic alert feedback with tone
                patterns = self.language_patterns.get(tone, self.language_patterns['professional'])
                greeting = random.choice(patterns['greetings'])
                conclusion = random.choice(patterns['conclusions'])
                
                title = alert_context.get('title', 'Alert detected')
                return f"{greeting} {title}. Severity: {severity}. {conclusion} Review and take appropriate action."
            
            # Prepare context variables
            context_vars = {
                'alert_type': alert_type,
                'severity': severity,
                'title': alert_context.get('title', 'System Alert'),
                'description': alert_context.get('description', 'No description provided'),
                'win_rate': f"{alert_context.get('data', {}).get('drop_percentage', 0.1):.1%}",
                'failure_rate': f"{alert_context.get('data', {}).get('failure_rate', 0.05):.1%}",
                'memory_usage': f"{alert_context.get('data', {}).get('memory_usage', 75)}%",
                'cpu_usage': f"{alert_context.get('data', {}).get('cpu_usage', 80)}%",
                'sigma': '2.1',  # Default statistical value
                'recommendations': '. '.join(alert_context.get('recommendations', ['Please review and take action'])[:2])
            }
            
            # Format template
            try:
                feedback_message = template.format(**context_vars)
            except KeyError:
                # Handle missing variables gracefully
                feedback_message = f"Alert: {context_vars['title']}. {context_vars['recommendations']}"
            
            # Add personality elements
            feedback_message = await self._add_personality_elements(feedback_message, tone, 'alert')
            
            # Save generated feedback
            await self._save_generated_feedback('alert', tone, feedback_message, context_vars, template_name)
            
            return feedback_message
            
        except Exception as e:
            self.logger.error(f"Error generating alert feedback with tone: {e}")
            return f"Alert detected with {tone} priority. Please review the situation and take appropriate action."
    
    async def _generate_insight_feedback_with_tone(self, insight_context: Dict[str, Any], tone: str) -> str:
        """Generate insight feedback with specific tone"""
        try:
            insight_type = insight_context.get('insight_type', 'pattern')
            confidence = insight_context.get('confidence', 0.75)
            impact_score = insight_context.get('impact_score', 50)
            
            template_map = {
                'pattern': 'pattern_detection',
                'optimization': 'optimization_opportunity',
                'risk': 'pattern_detection',
                'opportunity': 'optimization_opportunity'
            }
            
            template_name = template_map.get(insight_type, 'pattern_detection')
            template = await self._get_template('insight', template_name, tone)
            
            if not template:
                # Generate generic insight feedback with tone
                patterns = self.language_patterns.get(tone, self.language_patterns['professional'])
                greeting = random.choice(patterns['greetings'])
                
                title = insight_context.get('title', 'New insight discovered')
                return f"{greeting} {title} (confidence: {confidence:.1%}, impact: {impact_score:.0f}%)."
            
            # Prepare context variables
            context_vars = {
                'insight_type': insight_type,
                'confidence': f"{confidence:.1%}",
                'title': insight_context.get('title', 'System Insight'),
                'description': insight_context.get('description', 'Analysis complete'),
                'impact_score': f"{impact_score:.0f}",
                'pattern_name': insight_context.get('title', 'Analysis Pattern').replace('Pattern Detected: ', '').replace('Optimization Opportunity: ', ''),
                'opportunity_name': insight_context.get('title', 'Optimization').replace('Optimization Opportunity: ', ''),
                'improvement': f"{impact_score:.0f}",
                'difficulty': 'medium'
            }
            
            # Format template
            try:
                feedback_message = template.format(**context_vars)
            except KeyError:
                feedback_message = f"Insight: {context_vars['title']} (confidence: {context_vars['confidence']}, impact: {context_vars['impact_score']}%)"
            
            # Add personality elements
            feedback_message = await self._add_personality_elements(feedback_message, tone, 'insight')
            
            # Save generated feedback
            await self._save_generated_feedback('insight', tone, feedback_message, context_vars, template_name)
            
            return feedback_message
            
        except Exception as e:
            self.logger.error(f"Error generating insight feedback with tone: {e}")
            return f"New insight available with {tone} analysis. Please review the findings."
    
    async def _generate_query_feedback_with_tone(self, query_context: Dict[str, Any], tone: str) -> str:
        """Generate query response with specific tone"""
        try:
            query = query_context.get('query', '').lower()
            
            # Determine response type
            if any(word in query for word in ['status', 'health', 'how', 'doing']):
                template_name = 'status_request'
            else:
                template_name = 'general_inquiry'
            
            template = await self._get_template('query', template_name, tone)
            
            if not template:
                # Generate generic query response with tone
                patterns = self.language_patterns.get(tone, self.language_patterns['professional'])
                greeting = random.choice(patterns['greetings'])
                return f"{greeting} I understand you're asking about {query_context.get('query', 'system information')}. Let me provide you with the relevant details."
            
            # Prepare context variables
            if template_name == 'status_request':
                system_status = query_context.get('system_status', {}).get('system_health', {})
                context_vars = {
                    'overall_health': system_status.get('overall_health', 'unknown'),
                    'health_score': f"{system_status.get('health_score', 0):.0f}",
                    'active_alerts': len(query_context.get('active_alerts', [])),
                    'win_rate': f"{system_status.get('win_rate_24h', 0.5):.1%}"
                }
            else:
                insights = query_context.get('recent_insights', [])
                main_insight = insights[0] if insights else {}
                context_vars = {
                    'main_point': main_insight.get('title', 'System is operating normally'),
                    'supporting_evidence': f"Confidence level: {main_insight.get('confidence', 0.5):.1%}" if main_insight else "All systems operational",
                    'recommendation': 'Continue monitoring for optimal performance'
                }
            
            # Format template
            try:
                feedback_message = template.format(**context_vars)
            except KeyError:
                feedback_message = f"Based on current analysis, the system is functioning properly. Please let me know if you need specific details."
            
            # Add personality elements
            feedback_message = await self._add_personality_elements(feedback_message, tone, 'query')
            
            # Save generated feedback
            await self._save_generated_feedback('query', tone, feedback_message, context_vars, template_name)
            
            return feedback_message
            
        except Exception as e:
            self.logger.error(f"Error generating query feedback with tone: {e}")
            return f"I'm here to help with your question using a {tone} approach. Please provide more details if needed."
    
    async def _generate_generic_feedback_with_tone(self, context: Dict[str, Any], tone: str) -> str:
        """Generate generic feedback with specific tone"""
        try:
            patterns = self.language_patterns.get(tone, self.language_patterns['professional'])
            greeting = random.choice(patterns['greetings'])
            conclusion = random.choice(patterns['conclusions'])
            
            # Try to extract meaningful information from context
            if 'title' in context:
                message = f"{greeting} {context['title']}."
            elif 'message' in context:
                message = f"{greeting} {context['message']}."
            else:
                message = f"{greeting} I've analyzed the current situation."
            
            # Add recommendation if available
            if 'recommendations' in context and context['recommendations']:
                message += f" {conclusion} {context['recommendations'][0] if isinstance(context['recommendations'], list) else context['recommendations']}"

            # Add personality elements
            message = await self._add_personality_elements(message, tone, 'generic')
            
            return message
            
        except Exception as e:
            self.logger.error(f"Error generating generic feedback with tone: {e}")
            return f"Analysis complete. Using {tone} communication style to provide you with the best information available."
    
    # Required abstract methods from BaseBot
    async def initialize(self) -> bool:
        """Initialize FeedbackGenerator resources"""
        try:
            # Initialize database
            await self._init_database()
            
            # Initialize language templates
            await self._init_language_templates()
            
            self.logger.info("🎯 Feedback Generator initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error initializing FeedbackGenerator: {e}")
            return False
    
    async def execute_cycle(self) -> Dict[str, Any]:
        """Execute one FeedbackGenerator cycle"""
        try:
            # This component is reactive - no active cycle needed
            return {
                'status': 'ready',
                'timestamp': datetime.now().isoformat(),
                'templates_loaded': len(self.response_templates),
                'database_status': 'connected'
            }
            
        except Exception as e:
            self.logger.error(f"Error in FeedbackGenerator cycle: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def cleanup(self):
        """Cleanup FeedbackGenerator resources"""
        try:
            # Close database connections if any
            if hasattr(self, 'db_connection') and self.db_connection:
                self.db_connection.close()
                
            self.logger.info("🎯 Feedback Generator cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during FeedbackGenerator cleanup: {e}")
