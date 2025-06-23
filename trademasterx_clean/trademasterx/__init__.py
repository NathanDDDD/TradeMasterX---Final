"""
TradeMasterX 2.0 - Production Grade Trading System
A comprehensive cryptocurrency trading automation platform with real-time analysis,
adaptive strategies, and live trading readiness assessment.

Version: 2.0.0
Author: TradeMasterX Team
License: MIT

Core Components:
- Master Bot Orchestration System
- Multi-Strategy Trading Bots
- Real-time Market Analysis
- Risk Management & Memory Systems
- Web & CLI Interfaces
- Comprehensive Configuration Management
"""

__version__ = "2.0.0"
__author__ = "TradeMasterX Team"
__license__ = "MIT"

# Core exports
# from .core.master_bot import MasterBot  # Temporarily commented out due to import issues
from .core.bot_registry import BotRegistry
from .core.scoring import ScoringEngine

# Configuration
from .config.config_loader import ConfigLoader

__all__ = [
    # 'MasterBot',  # Temporarily commented out
    'BotRegistry', 
    'ScoringEngine',
    'ConfigLoader',
    '__version__',
    '__author__',
    '__license__'
]
