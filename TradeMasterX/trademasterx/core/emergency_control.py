import time
from trademasterx.utils.logger import get_logger
from trademasterx.utils.mini_log import log_event

class EmergencyControl:
    """Emergency trading control system for instant halt capability."""
    
    def __init__(self):
        self.logger = get_logger("EmergencyControl")
        self.is_emergency_stop_active = False
        self.emergency_stop_time = None
        self.trading_allowed = True
        
    def emergency_stop(self):
        """Activate emergency stop - immediately halt all trading."""
        self.is_emergency_stop_active = True
        self.emergency_stop_time = time.time()
        self.trading_allowed = False
        
        self.logger.warning("🚨 EMERGENCY STOP ACTIVATED - ALL TRADING HALTED")
        log_event("🚨 EMERGENCY STOP ACTIVATED - ALL TRADING HALTED")
        
        return {
            "status": "emergency_stop_activated",
            "timestamp": self.emergency_stop_time,
            "message": "All trading activities have been immediately halted"
        }
    
    def reset_emergency_stop(self):
        """Reset emergency stop and allow trading to resume."""
        self.is_emergency_stop_active = False
        self.emergency_stop_time = None
        self.trading_allowed = True
        
        self.logger.info("✅ Emergency stop reset - trading can resume")
        log_event("✅ Emergency stop reset - trading can resume")
        
        return {
            "status": "emergency_stop_reset",
            "timestamp": time.time(),
            "message": "Trading can now resume"
        }
    
    def can_trade(self):
        """Check if trading is currently allowed."""
        return self.trading_allowed and not self.is_emergency_stop_active
    
    def get_status(self):
        """Get current emergency control status."""
        return {
            "emergency_stop_active": self.is_emergency_stop_active,
            "trading_allowed": self.trading_allowed,
            "emergency_stop_time": self.emergency_stop_time,
            "uptime_since_reset": time.time() - (self.emergency_stop_time or time.time())
        } 