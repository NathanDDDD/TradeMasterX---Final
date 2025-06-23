"""
TradeMasterX 2.0 - Core Module
Centralized access to all core trading system components.
"""

# from .master_bot import MasterBot  # Temporarily commented out due to import issues
from .bot_registry import BotRegistry
from .scoring import ScoringEngine
from .safety_dashboard import SafetyDashboard
from .kill_switch import KillSwitch
from .risk_guard import RiskGuard
from .trade_deviation_alert import TradeDeviationAlert
from .failover_recovery import RecoveryManager

__all__ = [
    # 'MasterBot',  # Temporarily commented out
    'BotRegistry', 
    'ScoringEngine',
    'SafetyDashboard',
    'KillSwitch',
    'RiskGuard',
    'TradeDeviationAlert',
    'RecoveryManager'
]
