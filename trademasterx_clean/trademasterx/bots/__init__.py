"""
TradeMasterX Bots Package

This package contains all trading bots organized by category:
- analytics: Market analysis and data processing bots
- strategy: Trading strategy implementation bots
- system: System management and utility bots
"""

from typing import Dict, Type, Any
import logging

logger = logging.getLogger(__name__)

# Bot category registry
BOT_CATEGORIES = {
    'analytics': 'Analytics and market analysis bots',
    'strategy': 'Trading strategy implementation bots', 
    'system': 'System management and utility bots'
}

def get_available_bot_categories() -> Dict[str, str]:
    """Get all available bot categories."""
    return BOT_CATEGORIES.copy()

def validate_bot_category(category: str) -> bool:
    """Validate if a bot category exists."""
    return category in BOT_CATEGORIES

__all__ = [
    'BOT_CATEGORIES',
    'get_available_bot_categories',
    'validate_bot_category'
]
