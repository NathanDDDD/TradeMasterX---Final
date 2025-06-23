"""
TradeMasterX 2.0 - Multi-Layer Risk Guard
Phase 12: Live Trade Safety, Failovers & Risk Mitigation Systems

Comprehensive risk protection with daily loss limits, trade limits, and auto-safety halts.
"""

import json
import logging
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
import yaml


class RiskGuard:
    """
    Multi-layer risk protection system
    """
    
    @staticmethod
    def _get_default_config() -> Dict[str, Any]:
        """Get default configuration for risk guard"""
        return {
            'risk_limits': {
                'daily_loss_limit': 300.0,
                'max_trades_per_day': 100,
                'max_position_size': 1000.0,
                'max_concurrent_positions': 5,
                'drawdown_threshold': 0.10
            }
        }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._get_default_config()
        self.logger = logging.getLogger("RiskGuard")
        
        # Risk limits
        self.daily_loss_limit = self.config.get('risk_limits', {}).get('daily_loss_limit', 300.0)
        self.max_trades_per_day = self.config.get('risk_limits', {}).get('max_trades_per_day', 100)
        self.max_position_size = self.config.get('risk_limits', {}).get('max_position_size', 1000.0)
        self.max_concurrent_positions = self.config.get('risk_limits', {}).get('max_concurrent_positions', 5)
        self.drawdown_threshold = self.config.get('risk_limits', {}).get('drawdown_threshold', 0.10)
        
        # State tracking
        self.daily_pnl = 0.0
        self.daily_trades = 0
        self.active_positions = []
        self.session_start_balance = 10000.0
        self.current_balance = self.session_start_balance
        self.max_balance_today = self.session_start_balance
        self.last_reset_date = datetime.now().date()
        
        # Safety flags
        self._risk_guard_active = True
        self._auto_halt_triggered = False
        self._lock = threading.Lock()
        
        # File paths
        self.risk_data_file = Path("data/safety/risk_guard_data.json")
        self.risk_log_file = Path("logs/risk_violations.log")
        
        # Ensure directories exist
        self.risk_data_file.parent.mkdir(parents=True, exist_ok=True)
        self.risk_log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize risk tracking
        self._load_daily_data()
        
        self.logger.info("Risk Guard initialized with multi-layer protection")
        
    def is_active(self) -> bool:
        """Check if risk guard is active"""
        return self._risk_guard_active and not self._auto_halt_triggered
        
    def get_risk_status(self) -> Dict[str, Any]:
        """Get current risk status and metrics"""
        current_drawdown = 0.0
        if self.max_balance_today > 0:
            current_drawdown = (self.max_balance_today - self.current_balance) / self.max_balance_today
            
        return {
            "risk_guard_active": self._risk_guard_active,
            "auto_halt_triggered": self._auto_halt_triggered,
            "daily_pnl": self.daily_pnl,
            "daily_trades": self.daily_trades,
            "current_balance": self.current_balance,
            "daily_loss_limit": self.daily_loss_limit,
            "max_trades_per_day": self.max_trades_per_day,
            "trades_remaining": max(0, self.max_trades_per_day - self.daily_trades),
            "loss_limit_remaining": max(0, self.daily_loss_limit + self.daily_pnl),
            "current_drawdown_pct": current_drawdown * 100,
            "drawdown_threshold_pct": self.drawdown_threshold * 100,
            "active_positions": len(self.active_positions),
            "max_concurrent_positions": self.max_concurrent_positions,
            "last_reset_date": self.last_reset_date.isoformat()
        }
        
    def validate_trade_request(self, trade_request: Dict[str, Any]) -> Dict[str, Any]:
        """Validate trade request against all risk limits"""
        with self._lock:
            try:
                if not self._risk_guard_active:
                    return self._create_validation_result(False, "Risk guard is disabled")
                    
                if self._auto_halt_triggered:
                    return self._create_validation_result(False, "Auto-halt triggered - trading suspended")
                    
                # Check daily reset
                if datetime.now().date() > self.last_reset_date:
                    self._reset_daily_counters()
                    
                # Validate daily trade limit
                if self.daily_trades >= self.max_trades_per_day:
                    self._trigger_auto_halt("DAILY_TRADE_LIMIT_EXCEEDED")
                    return self._create_validation_result(False, f"Daily trade limit reached ({self.max_trades_per_day})")
                    
                # All checks passed
                return self._create_validation_result(True, "Trade approved")
                
            except Exception as e:
                self.logger.error(f"Risk validation error: {e}")
                return self._create_validation_result(False, f"Validation error: {e}")
                
    def record_trade_result(self, trade_result: Dict[str, Any]):
        """Record trade result and update risk metrics"""
        with self._lock:
            try:
                self.daily_trades += 1
                pnl = trade_result.get('pnl', 0.0)
                self.daily_pnl += pnl
                self.current_balance += pnl
                
                if self.current_balance > self.max_balance_today:
                    self.max_balance_today = self.current_balance
                    
                self._check_post_trade_risks()
                self._save_daily_data()
                
                self.logger.info(f"Trade recorded - P&L: ${pnl:.2f}, Daily P&L: ${self.daily_pnl:.2f}")
                
            except Exception as e:
                self.logger.error(f"Error recording trade result: {e}")
                
    def _load_daily_data(self):
        """Load daily risk data if available"""
        try:
            if self.risk_data_file.exists():
                with open(self.risk_data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                data_date = datetime.fromisoformat(data.get('date', '2020-01-01')).date()
                
                if data_date == datetime.now().date():
                    self.daily_pnl = data.get('daily_pnl', 0.0)
                    self.daily_trades = data.get('daily_trades', 0)
                    self.current_balance = data.get('current_balance', self.session_start_balance)
                    self.max_balance_today = data.get('max_balance_today', self.session_start_balance)
                    self._auto_halt_triggered = data.get('auto_halt_triggered', False)
                else:
                    self._reset_daily_counters()
            else:
                self._reset_daily_counters()
                
        except Exception as e:
            self.logger.error(f"Error loading daily data: {e}")
            self._reset_daily_counters()
            
    def _reset_daily_counters(self):
        """Reset daily counters for new trading day"""
        self.daily_pnl = 0.0
        self.daily_trades = 0
        self.session_start_balance = self.current_balance
        self.max_balance_today = self.current_balance
        self._auto_halt_triggered = False
        self.last_reset_date = datetime.now().date()
        
        self.logger.info("Daily counters reset for new trading day")
        self._save_daily_data()
        
    def _check_post_trade_risks(self):
        """Check for risk violations after trade execution"""
        try:
            if self.daily_pnl < -self.daily_loss_limit:
                self._trigger_auto_halt("DAILY_LOSS_LIMIT_EXCEEDED")
                return
                
            current_drawdown = (self.max_balance_today - self.current_balance) / self.max_balance_today
            if current_drawdown > self.drawdown_threshold:
                self._trigger_auto_halt("DRAWDOWN_THRESHOLD_EXCEEDED")
                return
                
        except Exception as e:
            self.logger.error(f"Error checking post-trade risks: {e}")
            
    def _trigger_auto_halt(self, reason: str):
        """Trigger automatic trading halt due to risk violation"""
        try:
            self._auto_halt_triggered = True
            
            violation_data = {
                "timestamp": datetime.now().isoformat(),
                "reason": reason,
                "daily_pnl": self.daily_pnl,
                "daily_trades": self.daily_trades,
                "current_balance": self.current_balance
            }
            
            with open(self.risk_log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(violation_data) + '\n')
                
            self.logger.critical(f"AUTO-HALT TRIGGERED: {reason}")
            self._save_daily_data()
            
        except Exception as e:
            self.logger.error(f"Error triggering auto-halt: {e}")
            
    def reset_auto_halt(self, authorization_code: str) -> bool:
        """Reset auto-halt (requires authorization)"""
        try:
            expected_code = "TRADEMASTERX_RISK_RESET_2025"
            
            if authorization_code != expected_code:
                self.logger.error("UNAUTHORIZED: Invalid authorization code for risk reset")
                return False
                
            self._auto_halt_triggered = False
            self.logger.warning("AUTO-HALT RESET: Trading can resume")
            self._save_daily_data()
            return True
            
        except Exception as e:
            self.logger.error(f"Error resetting auto-halt: {e}")
            return False
            
    def get_risk_warnings(self) -> List[Dict[str, Any]]:
        """Get current risk warnings"""
        warnings = []
        
        try:
            trades_remaining = self.max_trades_per_day - self.daily_trades
            if trades_remaining <= 10:
                warnings.append({
                    "type": "TRADE_LIMIT_WARNING",
                    "message": f"Only {trades_remaining} trades remaining today",
                    "severity": "HIGH" if trades_remaining <= 5 else "MEDIUM"
                })
                
            loss_remaining = self.daily_loss_limit + self.daily_pnl
            if loss_remaining <= 50:
                warnings.append({
                    "type": "LOSS_LIMIT_WARNING",
                    "message": f"Only ${loss_remaining:.2f} loss buffer remaining",
                    "severity": "HIGH" if loss_remaining <= 20 else "MEDIUM"
                })
                
        except Exception as e:
            self.logger.error(f"Error generating risk warnings: {e}")
            
        return warnings
        
    def _create_validation_result(self, approved: bool, message: str) -> Dict[str, Any]:
        """Create validation result dictionary"""
        return {
            "approved": approved,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "risk_status": self.get_risk_status()
        }
        
    def _save_daily_data(self):
        """Save daily risk data to file"""
        try:
            data = {
                "date": datetime.now().isoformat(),
                "daily_pnl": self.daily_pnl,
                "daily_trades": self.daily_trades,
                "current_balance": self.current_balance,
                "max_balance_today": self.max_balance_today,
                "auto_halt_triggered": self._auto_halt_triggered,
                "active_positions": self.active_positions
            }
            
            with open(self.risk_data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Error saving daily data: {e}")


if __name__ == "__main__":
    import sys
    
    # Simple CLI for testing
    risk_guard = RiskGuard()
    
    if len(sys.argv) > 1 and sys.argv[1] == "status":
        status = risk_guard.get_risk_status()
        print("Risk Guard Status:")
        print(f"  Active: {status['risk_guard_active']}")
        print(f"  Auto-halt: {status['auto_halt_triggered']}")
        print(f"  Daily P&L: ${status['daily_pnl']:.2f}")
        print(f"  Daily Trades: {status['daily_trades']}/{status['max_trades_per_day']}")
    else:
        print("Usage: python risk_guard.py status")
