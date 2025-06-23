#!/usr/bin/env python3
"""
TradeMasterX 2.0 - API Integration Framework
Phase 13: Smart Command Interface API Integration

Provides integration with Claude API (primary) and OpenAI API (fallback)
for enhanced natural language processing and intelligent responses.
"""

import json
import logging
import os
import time
from typing import Dict, Any, List, Optional, Union
import asyncio
import aiohttp
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class APIIntegration:
    """
    API integration framework supporting Claude (primary) and OpenAI (fallback)
    """
    
    def __init__(self, api_manager=None):
        self.api_manager = api_manager
        self.session = None
        
        # API endpoints
        self.claude_base_url = "https://api.anthropic.com/v1"
        self.openai_base_url = "https://api.openai.com/v1"
        
        # Rate limiting
        self.last_claude_call = 0
        self.last_openai_call = 0
        self.claude_rate_limit = 1.0  # seconds between calls
        self.openai_rate_limit = 1.0  # seconds between calls
        
        # Request tracking
        self.request_count = 0
        self.failed_requests = 0
        
        # Initialize session
        self._init_session()
    
    def _init_session(self):
        """Initialize HTTP session"""
        connector = aiohttp.TCPConnector(limit=10, limit_per_host=5)
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={'User-Agent': 'TradeMasterX/2.0'}
        )
    
    async def close(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def enhance_command_understanding(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Enhance command understanding using AI APIs
        
        Args:
            user_input: Raw user input text
            context: Additional context (system status, history, etc.)
        
        Returns:
            Enhanced understanding with confidence scores and suggestions
        """
        context = context or {}
        
        # Prepare system context
        system_context = self._prepare_system_context(context)
        
        # Try Claude first, then OpenAI as fallback
        result = await self._try_claude_enhancement(user_input, system_context)
        
        if not result or result.get('confidence', 0) < 0.5:
            logger.info("Claude API unavailable or low confidence, trying OpenAI fallback")
            result = await self._try_openai_enhancement(user_input, system_context)
        
        # Add metadata
        result = result or {}
        result.update({
            'timestamp': datetime.now().isoformat(),
            'original_input': user_input,
            'api_used': result.get('api_used', 'none'),
            'request_id': f"req_{self.request_count}"
        })
        
        self.request_count += 1
        return result
    
    async def _try_claude_enhancement(self, user_input: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Try to enhance command using Claude API"""
        if not self.api_manager.has_claude_key():
            logger.debug("Claude API key not available")
            return None
        
        # Rate limiting
        time_since_last = time.time() - self.last_claude_call
        if time_since_last < self.claude_rate_limit:
            await asyncio.sleep(self.claude_rate_limit - time_since_last)
        
        try:
            headers = {
                'x-api-key': self.api_manager.get_claude_key(),
                'Content-Type': 'application/json',
                'anthropic-version': '2023-06-01'
            }
            
            prompt = self._build_claude_prompt(user_input, context)
            
            payload = {
                'model': 'claude-3-sonnet-20240229',
                'max_tokens': 500,
                'messages': [
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ]
            }
            
            async with self.session.post(
                f"{self.claude_base_url}/messages",
                headers=headers,
                json=payload
            ) as response:
                self.last_claude_call = time.time()
                
                if response.status == 200:
                    data = await response.json()
                    result = self._parse_claude_response(data)
                    result['api_used'] = 'claude'
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"Claude API error {response.status}: {error_text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error calling Claude API: {e}")
            self.failed_requests += 1
            return None
    
    async def _try_openai_enhancement(self, user_input: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Try to enhance command using OpenAI API"""
        if not self.api_manager.has_openai_key():
            logger.debug("OpenAI API key not available")
            return None
        
        # Rate limiting
        time_since_last = time.time() - self.last_openai_call
        if time_since_last < self.openai_rate_limit:
            await asyncio.sleep(self.openai_rate_limit - time_since_last)
        
        try:
            headers = {
                'Authorization': f'Bearer {self.api_manager.get_openai_key()}',
                'Content-Type': 'application/json'
            }
            
            prompt = self._build_openai_prompt(user_input, context)
            
            payload = {
                'model': 'gpt-3.5-turbo',
                'messages': [
                    {
                        'role': 'system',
                        'content': 'You are a trading bot command interpreter. Parse user commands and respond with JSON.'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'max_tokens': 300,
                'temperature': 0.3
            }
            
            async with self.session.post(
                f"{self.openai_base_url}/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                self.last_openai_call = time.time()
                
                if response.status == 200:
                    data = await response.json()
                    result = self._parse_openai_response(data)
                    result['api_used'] = 'openai'
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"OpenAI API error {response.status}: {error_text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
            self.failed_requests += 1
            return None
    
    def _prepare_system_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare system context for API calls"""
        return {
            'system_status': context.get('system_status', 'unknown'),
            'active_bots': context.get('active_bots', []),
            'recent_performance': context.get('recent_performance', {}),
            'safety_level': context.get('safety_level', 'unknown'),
            'available_commands': [
                'pause', 'resume', 'status', 'performance', 'retrain',
                'diagnostics', 'logs', 'risk', 'shutdown', 'help', 'config'
            ]
        }
    
    def _build_claude_prompt(self, user_input: str, context: Dict[str, Any]) -> str:
        """Build prompt for Claude API"""
        return f"""
You are TradeMasterX, an intelligent trading bot command interpreter. 

Current system context:
- System Status: {context.get('system_status', 'unknown')}
- Safety Level: {context.get('safety_level', 'unknown')}
- Active Bots: {len(context.get('active_bots', []))}

User Input: "{user_input}"

Available Commands: {', '.join(context.get('available_commands', []))}

Please analyze this command and respond with JSON containing:
1. "command" - the most likely intended command
2. "confidence" - confidence score 0-1
3. "parameters" - extracted parameters
4. "explanation" - brief explanation of interpretation
5. "suggestions" - alternative interpretations if confidence < 0.8

Response must be valid JSON only.
"""
    
    def _build_openai_prompt(self, user_input: str, context: Dict[str, Any]) -> str:
        """Build prompt for OpenAI API"""
        return f"""
Parse this trading bot command: "{user_input}"

System Context:
- Status: {context.get('system_status', 'unknown')}
- Safety: {context.get('safety_level', 'unknown')}
- Bots: {len(context.get('active_bots', []))}

Available commands: {', '.join(context.get('available_commands', []))}

Return JSON with: command, confidence (0-1), parameters, explanation, suggestions
"""
    
    def _parse_claude_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Claude API response"""
        try:
            content = response_data['content'][0]['text']
            
            # Extract JSON from response
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_content = content[json_start:json_end]
                parsed = json.loads(json_content)
                
                # Validate required fields
                required_fields = ['command', 'confidence']
                if all(field in parsed for field in required_fields):
                    return parsed
            
            # Fallback if JSON parsing fails
            return {
                'command': 'unknown',
                'confidence': 0.3,
                'explanation': 'Could not parse AI response',
                'raw_response': content
            }
            
        except Exception as e:
            logger.error(f"Error parsing Claude response: {e}")
            return {
                'command': 'unknown',
                'confidence': 0.0,
                'explanation': f'Parse error: {str(e)}'
            }
    
    def _parse_openai_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse OpenAI API response"""
        try:
            content = response_data['choices'][0]['message']['content']
            
            # Try to parse as JSON
            try:
                parsed = json.loads(content)
                return parsed
            except json.JSONDecodeError:
                # Try to extract JSON from text
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                
                if json_start >= 0 and json_end > json_start:
                    json_content = content[json_start:json_end]
                    parsed = json.loads(json_content)
                    return parsed
                
                # Fallback
                return {
                    'command': 'unknown',
                    'confidence': 0.3,
                    'explanation': 'Could not parse AI response',
                    'raw_response': content
                }
                
        except Exception as e:
            logger.error(f"Error parsing OpenAI response: {e}")
            return {
                'command': 'unknown',
                'confidence': 0.0,
                'explanation': f'Parse error: {str(e)}'
            }
    
    async def generate_response(self, command: str, result: Dict[str, Any], personality: str = 'professional') -> str:
        """
        Generate contextual response using AI APIs
        
        Args:
            command: Executed command
            result: Command execution result
            personality: Response personality style
        
        Returns:
            AI-generated response text
        """
        if not (self.api_manager.has_claude_key() or self.api_manager.has_openai_key()):
            return self._generate_fallback_response(command, result, personality)
        
        context = {
            'command': command,
            'result': result,
            'personality': personality,
            'timestamp': datetime.now().isoformat()
        }
        
        # Try Claude first
        response = await self._generate_claude_response(context)
        
        if not response:
            # Fallback to OpenAI
            response = await self._generate_openai_response(context)
        
        if not response:
            # Final fallback
            response = self._generate_fallback_response(command, result, personality)
        
        return response
    
    async def _generate_claude_response(self, context: Dict[str, Any]) -> Optional[str]:
        """Generate response using Claude"""
        if not self.api_manager.has_claude_key():
            return None
        
        try:
            prompt = f"""
Generate a {context['personality']} response for this trading bot interaction:

Command: {context['command']}
Result: {context['result']}

Style Guidelines:
- Professional: Formal, informative, focused on facts
- Friendly: Warm, encouraging, uses emojis appropriately  
- Technical: Detailed, system-focused, includes metrics

Keep response under 100 words. Be helpful and contextual.
"""
            
            headers = {
                'x-api-key': self.api_manager.get_claude_key(),
                'Content-Type': 'application/json',
                'anthropic-version': '2023-06-01'
            }
            
            payload = {
                'model': 'claude-3-haiku-20240307',  # Faster model for responses
                'max_tokens': 200,
                'messages': [{'role': 'user', 'content': prompt}]
            }
            
            async with self.session.post(
                f"{self.claude_base_url}/messages",
                headers=headers,
                json=payload
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    return data['content'][0]['text'].strip()
                    
        except Exception as e:
            logger.error(f"Error generating Claude response: {e}")
        
        return None
    
    async def _generate_openai_response(self, context: Dict[str, Any]) -> Optional[str]:
        """Generate response using OpenAI"""
        if not self.api_manager.has_openai_key():
            return None
        
        try:
            prompt = f"""
Command: {context['command']}
Result: {context['result']}
Style: {context['personality']}

Generate a brief, helpful response (under 100 words).
"""
            
            headers = {
                'Authorization': f'Bearer {self.api_manager.get_openai_key()}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': 'gpt-3.5-turbo',
                'messages': [
                    {
                        'role': 'system',
                        'content': f'You are a {context["personality"]} trading bot assistant. Be helpful and concise.'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'max_tokens': 150,
                'temperature': 0.7
            }
            
            async with self.session.post(
                f"{self.openai_base_url}/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    return data['choices'][0]['message']['content'].strip()
                    
        except Exception as e:
            logger.error(f"Error generating OpenAI response: {e}")
        
        return None
    
    def _generate_fallback_response(self, command: str, result: Dict[str, Any], personality: str) -> str:
        """Generate fallback response without AI APIs"""
        success = result.get('success', False)
        
        responses = {
            'professional': {
                'success': f"Command '{command}' executed successfully.",
                'error': f"Command '{command}' encountered an error."
            },
            'friendly': {
                'success': f"Great! ✅ The '{command}' command worked perfectly!",
                'error': f"Oops! ❌ Something went wrong with the '{command}' command."
            },
            'technical': {
                'success': f"[SYSTEM] Command '{command}' completed with status: SUCCESS",
                'error': f"[SYSTEM] Command '{command}' completed with status: ERROR"
            }
        }
        
        style = responses.get(personality, responses['professional'])
        base_response = style['success'] if success else style['error']
        
        # Add details if available
        if 'message' in result:
            base_response += f" {result['message']}"
        
        return base_response
    
    def get_stats(self) -> Dict[str, Any]:
        """Get API usage statistics"""
        return {
            'total_requests': self.request_count,
            'failed_requests': self.failed_requests,
            'success_rate': (self.request_count - self.failed_requests) / max(self.request_count, 1),
            'claude_available': self.api_manager.has_claude_key(),
            'openai_available': self.api_manager.has_openai_key()
        }


# Mock API classes for testing without actual API keys
class MockAPIIntegration(APIIntegration):
    """Mock API integration for testing"""
    
    def __init__(self, api_manager):
        super().__init__(api_manager)
        self.mock_responses = True
    
    async def enhance_command_understanding(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Mock enhancement with simulated AI understanding"""
        await asyncio.sleep(0.1)  # Simulate API delay
        
        # Simple keyword-based mock enhancement
        user_lower = user_input.lower()
        
        if any(word in user_lower for word in ['pause', 'stop', 'halt']):
            command = 'pause'
            confidence = 0.9
        elif any(word in user_lower for word in ['resume', 'start', 'continue']):
            command = 'resume'  
            confidence = 0.9
        elif any(word in user_lower for word in ['status', 'state', 'how']):
            command = 'status'
            confidence = 0.8
        elif any(word in user_lower for word in ['performance', 'profit', 'results']):
            command = 'performance'
            confidence = 0.8
        else:
            command = 'unknown'
            confidence = 0.3
        
        return {
            'command': command,
            'confidence': confidence,
            'parameters': {},
            'explanation': f'Mock interpretation of: {user_input}',
            'api_used': 'mock',
            'timestamp': datetime.now().isoformat(),
            'original_input': user_input,
            'request_id': f"mock_{self.request_count}"
        }
    
    async def generate_response(self, command: str, result: Dict[str, Any], personality: str = 'professional') -> str:
        """Mock response generation"""
        await asyncio.sleep(0.1)  # Simulate API delay
        
        return self._generate_fallback_response(command, result, personality) + " (Mock AI)"
