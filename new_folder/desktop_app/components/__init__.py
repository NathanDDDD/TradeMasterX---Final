"""
Desktop App Components
"""

from .system_control import SystemControlPanel
from .ai_chat import AIChatInterface
from .status_dashboard import StatusDashboard
from .trade_history import TradeHistoryViewer

__all__ = [
    'SystemControlPanel',
    'AIChatInterface', 
    'StatusDashboard',
    'TradeHistoryViewer'
]
