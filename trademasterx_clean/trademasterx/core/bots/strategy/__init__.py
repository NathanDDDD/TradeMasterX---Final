"""
Strategy Bots Package

Contains trading strategy and signal generation bots.
"""

from typing import Dict, Type, Any
import logging

logger = logging.getLogger(__name__)

# Strategy bot registry
STRATEGY_BOTS = {}

def register_strategy_bot(name: str, bot_class: Type[Any]) -> None:
    """Register a strategy bot."""
    STRATEGY_BOTS[name] = bot_class
    logger.info(f"Registered strategy bot: {name}")

def get_strategy_bot(name: str) -> Type[Any]:
    """Get a strategy bot class by name."""
    if name not in STRATEGY_BOTS:
        raise ValueError(f"Strategy bot '{name}' not found")
    return STRATEGY_BOTS[name]

def list_strategy_bots() -> Dict[str, Type[Any]]:
    """List all available strategy bots."""
    return STRATEGY_BOTS.copy()

# Import and register strategy bots
try:
    from .strategy import StrategyBot
    register_strategy_bot('strategy', StrategyBot)
except ImportError as e:
    logger.warning(f"Failed to import StrategyBot: {e}")

__all__ = [
    'STRATEGY_BOTS',
    'register_strategy_bot',
    'get_strategy_bot', 
    'list_strategy_bots',
    'StrategyBot'
]