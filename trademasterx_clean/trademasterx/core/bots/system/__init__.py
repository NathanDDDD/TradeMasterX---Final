"""
System Bots Package

Contains system management and utility bots.
"""

from typing import Dict, Type, Any
import logging

logger = logging.getLogger(__name__)

# System bot registry
SYSTEM_BOTS = {}

def register_system_bot(name: str, bot_class: Type[Any]) -> None:
    """Register a system bot."""
    SYSTEM_BOTS[name] = bot_class
    logger.info(f"Registered system bot: {name}")

def get_system_bot(name: str) -> Type[Any]:
    """Get a system bot class by name."""
    if name not in SYSTEM_BOTS:
        raise ValueError(f"System bot '{name}' not found")
    return SYSTEM_BOTS[name]

def list_system_bots() -> Dict[str, Type[Any]]:
    """List all available system bots."""
    return SYSTEM_BOTS.copy()

# Import and register system bots
try:
    from .risk_bot import RiskBot
    register_system_bot('risk', RiskBot)
except ImportError as e:
    logger.warning(f"Failed to import RiskBot: {e}")

try:
    from .memory_bot import MemoryBot
    register_system_bot('memory', MemoryBot)
except ImportError as e:
    logger.warning(f"Failed to import MemoryBot: {e}")

try:
    from .logger_bot import LoggerBot
    register_system_bot('logger', LoggerBot)
except ImportError as e:
    logger.warning(f"Failed to import LoggerBot: {e}")

__all__ = [
    'SYSTEM_BOTS',
    'register_system_bot',
    'get_system_bot', 
    'list_system_bots',
    'RiskBot',
    'MemoryBot',
    'LoggerBot'
]