import os
import requests
from trademasterx.utils.logger import get_logger

class AIAssistant:
    """AI trading assistant using Claude AI and OpenAI for analysis and advice."""
    
    def __init__(self):
        self.logger = get_logger("AIAssistant")
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        
    def get_trading_advice(self, market_data, question):
        """Get AI trading advice based on market data and user question."""
        try:
            # Try Claude AI first
            if self.anthropic_api_key:
                return self._ask_claude(market_data, question)
            # Fallback to OpenAI
            elif self.openai_api_key:
                return self._ask_openai(market_data, question)
            else:
                return "No AI API keys configured. Please set ANTHROPIC_API_KEY or OPENAI_API_KEY."
        except Exception as e:
            self.logger.error(f"AI assistant error: {e}")
            return f"Error getting AI advice: {e}"
    
    def _ask_claude(self, market_data, question):
        """Ask Claude AI for trading advice."""
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.anthropic_api_key,
            "content-type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        prompt = f"""
        Market Data: {market_data}
        Question: {question}
        
        Provide trading advice based on the market data. Be concise and actionable.
        """
        
        data = {
            "model": "claude-3-sonnet-20240229",
            "max_tokens": 500,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()["content"][0]["text"]
        else:
            raise Exception(f"Claude API error: {response.status_code}")
    
    def _ask_openai(self, market_data, question):
        """Ask OpenAI for trading advice."""
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json"
        }
        
        prompt = f"""
        Market Data: {market_data}
        Question: {question}
        
        Provide trading advice based on the market data. Be concise and actionable.
        """
        
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 500
        }
        
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            raise Exception(f"OpenAI API error: {response.status_code}") 