"""
Analytics Bots Package

Contains bots for market analysis, data processing, and trading intelligence.
"""

from typing import Dict, Type, Any
import logging

logger = logging.getLogger(__name__)

# Analytics bot registry
ANALYTICS_BOTS = {}

def register_analytics_bot(name: str, bot_class: Type[Any]) -> None:
    """Register an analytics bot."""
    ANALYTICS_BOTS[name] = bot_class
    logger.info(f"Registered analytics bot: {name}")
    
# Import at the end to avoid circular imports
from .analytics_bot import AnalyticsBot

# Auto-register the AnalyticsBot
register_analytics_bot("analytics", AnalyticsBot)

def get_analytics_bot(name: str) -> Type[Any]:
    """Get an analytics bot class by name."""
    if name not in ANALYTICS_BOTS:
        raise ValueError(f"Analytics bot '{name}' not found")
    return ANALYTICS_BOTS[name]

def list_analytics_bots() -> Dict[str, Type[Any]]:
    """List all available analytics bots."""
    return ANALYTICS_BOTS.copy()

__all__ = [
    'ANALYTICS_BOTS',
    'register_analytics_bot', 
    'get_analytics_bot',
    'list_analytics_bots'
]
