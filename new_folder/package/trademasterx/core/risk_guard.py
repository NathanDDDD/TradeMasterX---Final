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
        self.config = config if config is not None else self._get_default_config()
        self.logger = logging.getLogger("RiskGuard")
        
        # Ensure config has proper structure
        if not isinstance(self.config, dict):
            self.config = self._get_default_config()
        if 'risk_limits' not in self.config:
            self.config['risk_limits'] = self._get_default_config()['risk_limits']
        
        # Risk limits
        self.daily_loss_limit = self.config.get('risk_limits', {}).get('daily_loss_limit', 300.0)
        self.max_trades_per_day = self.config.get('risk_limits', {}).get('max_trades_per_day', 100)
        self.max_position_size = self.config.get('risk_limits', {}).get('max_position_size', 1000.0)
        self.max_concurrent_positions = self.config.get('risk_limits', {}).get('max_concurrent_positions', 5)
        self.drawdown_threshold = self.config.get('risk_limits', {}).get('drawdown_threshold', 0.10)  # 10%
        
        # State tracking
        self.daily_pnl = 0.0
        self.daily_trades = 0
        self.active_positions = []
        self.session_start_balance = 10000.0  # Default demo balance
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
        
        self.logger.info("🛡️ Risk Guard initialized with multi-layer protection")
        self.logger.info(f"[INFO] Daily Loss Limit: ${self.daily_loss_limit}")
        self.logger.info(f"[INFO] Max Trades/Day: {self.max_trades_per_day}")
        
    def _load_daily_data(self):
        """Load daily risk data if available"""
        try:
            if self.risk_data_file.exists():
                with open(self.risk_data_file, 'r') as f:
                    data = json.load(f)
                    
                # Check if data is from today
                data_date = datetime.fromisoformat(data.get('date', '2020-01-01')).date()
                
                if data_date == datetime.now().date():
                    self.daily_pnl = data.get('daily_pnl', 0.0)
                    self.daily_trades = data.get('daily_trades', 0)
                    self.current_balance = data.get('current_balance', self.session_start_balance)
                    self.max_balance_today = data.get('max_balance_today', self.session_start_balance)
                    self._auto_halt_triggered = data.get('auto_halt_triggered', False)
                    
                    self.logger.info(f"[INFO] Loaded daily data - P&L: ${self.daily_pnl:.2f}, Trades: {self.daily_trades}")
                else:
                    # New day - reset counters
                    self._reset_daily_counters()
            else:
                # First run - initialize
                self._reset_daily_counters()
                
        except Exception as e:
            self.logger.error(f"[ERROR] Error loading daily data: {e}")
            self._reset_daily_counters()
            
    def _reset_daily_counters(self):
        """Reset daily counters for new trading day"""
        self.daily_pnl = 0.0
        self.daily_trades = 0
        self.session_start_balance = self.current_balance
        self.max_balance_today = self.current_balance
        self._auto_halt_triggered = False
        self.last_reset_date = datetime.now().date()
        
        self.logger.info("🔄 Daily counters reset for new trading day")
        self._save_daily_data()
        
    def validate_trade_request(self, trade_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate trade request against all risk limits
        
        Args:
            trade_request: Trade request with amount, symbol, etc.
            
        Returns:
            Dict with validation result
        """
        with self._lock:
            try:
                # Check if risk guard is active
                if not self._risk_guard_active:
                    return self._create_validation_result(False, "Risk guard is disabled")
                    
                # Check if auto-halt is triggered
                if self._auto_halt_triggered:
                    return self._create_validation_result(False, "Auto-halt triggered - trading suspended")
                    
                # Check daily reset
                if datetime.now().date() > self.last_reset_date:
                    self._reset_daily_counters()
                    
                # Validate daily trade limit
                if self.daily_trades >= self.max_trades_per_day:
                    self._trigger_auto_halt("DAILY_TRADE_LIMIT_EXCEEDED")
                    return self._create_validation_result(False, f"Daily trade limit reached ({self.max_trades_per_day})")
                      # Validate position size (check both 'position_size' and 'amount' fields)
                position_size = trade_request.get('position_size', trade_request.get('amount', 0))
                if position_size > self.max_position_size:
                    return self._create_validation_result(False, f"Position size ${position_size} exceeds limit ${self.max_position_size}")
                    
                # Validate concurrent positions
                if len(self.active_positions) >= self.max_concurrent_positions:
                    return self._create_validation_result(False, f"Max concurrent positions reached ({self.max_concurrent_positions})")
                    
                # Validate daily loss limit (potential)
                potential_loss = position_size * 0.02  # Assume 2% max loss per trade
                if self.daily_pnl - potential_loss < -self.daily_loss_limit:
                    return self._create_validation_result(False, f"Potential loss would exceed daily limit (${self.daily_loss_limit})")
                      # Validate drawdown threshold
                current_drawdown = (self.max_balance_today - self.current_balance) / self.max_balance_today
                if current_drawdown > self.drawdown_threshold:
                    self._trigger_auto_halt("DRAWDOWN_THRESHOLD_EXCEEDED")
                    return self._create_validation_result(False, f"Drawdown threshold exceeded ({current_drawdown:.1%})")
                    
                # All checks passed
                return self._create_validation_result(True, "Trade approved")
                
            except Exception as e:
                self.logger.error(f"[ERROR] Risk validation error: {e}")
                return self._create_validation_result(False, f"Validation error: {e}")
                
    def validate_trade(self, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simple trade validation method for testing
        
        Args:
            trade_data: Trade data to validate
            
        Returns:
            Dict: Validation result with approved status and details
        """
        try:
            # Call the full validation method
            validation_result = self.validate_trade_request(trade_data)
            return validation_result
        except Exception as e:
            self.logger.error(f"Error validating trade: {e}")
            return {
                "approved": False,
                "reason": f"Validation error: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def record_trade_result(self, trade_result: Dict[str, Any]):
        """
        Record trade result and update risk metrics
        
        Args:
            trade_result: Trade result with P&L, fees, etc.
        """
        with self._lock:
            try:
                # Update trade count
                self.daily_trades += 1
                
                # Update P&L
                pnl = trade_result.get('pnl', 0.0)
                fees = trade_result.get('fees', 0.0)
                net_pnl = pnl - fees
                
                self.daily_pnl += net_pnl
                self.current_balance += net_pnl
                
                # Update max balance if positive
                if self.current_balance > self.max_balance_today:
                    self.max_balance_today = self.current_balance
                    
                # Check for risk violations after trade
                self._check_post_trade_risks()
                
                # Update position tracking
                if trade_result.get('action') == 'open':
                    self.active_positions.append({
                        'id': trade_result.get('trade_id'),
                        'symbol': trade_result.get('symbol'),
                        'size': trade_result.get('position_size'),
                        'timestamp': datetime.now().isoformat()
                    })
                elif trade_result.get('action') == 'close':
                    self._remove_position(trade_result.get('trade_id'))
                    
                # Save updated data
                self._save_daily_data()
                
                # Log risk metrics
                self.logger.info(f"[INFO] Trade recorded - P&L: ${net_pnl:.2f}, Daily P&L: ${self.daily_pnl:.2f}, Trades: {self.daily_trades}")
                
            except Exception as e:
                self.logger.error(f"[ERROR] Error recording trade result: {e}")
                
    def _check_post_trade_risks(self):
        """Check for risk violations after trade execution"""
        try:
            # Check daily loss limit
            if self.daily_pnl < -self.daily_loss_limit:
                self._trigger_auto_halt("DAILY_LOSS_LIMIT_EXCEEDED")
                return
                
            # Check drawdown threshold
            current_drawdown = (self.max_balance_today - self.current_balance) / self.max_balance_today
            if current_drawdown > self.drawdown_threshold:
                self._trigger_auto_halt("DRAWDOWN_THRESHOLD_EXCEEDED")
                return
                
            # Check balance protection (if balance drops below 50% of start)
            balance_loss_pct = (self.session_start_balance - self.current_balance) / self.session_start_balance
            if balance_loss_pct > 0.50:
                self._trigger_auto_halt("BALANCE_PROTECTION_TRIGGERED")
                return
                
        except Exception as e:
            self.logger.error(f"[ERROR] Error checking post-trade risks: {e}")
            
    def _trigger_auto_halt(self, reason: str):
        """Trigger automatic trading halt due to risk violation"""
        try:
            self._auto_halt_triggered = True
            
            # Log violation
            violation_data = {
                "timestamp": datetime.now().isoformat(),
                "reason": reason,
                "daily_pnl": self.daily_pnl,
                "daily_trades": self.daily_trades,
                "current_balance": self.current_balance,
                "drawdown_pct": (self.max_balance_today - self.current_balance) / self.max_balance_today * 100
            }
            
            # Log to file
            with open(self.risk_log_file, 'a') as f:
                f.write(json.dumps(violation_data) + '\n')
                
            self.logger.critical(f"🚨 AUTO-HALT TRIGGERED: {reason}")
            self.logger.critical(f"🚨 Trading suspended due to risk violation")
            self.logger.critical(f"🚨 Daily P&L: ${self.daily_pnl:.2f}")
            
            # Save state
            self._save_daily_data()
            
        except Exception as e:
            self.logger.error(f"[ERROR] Error triggering auto-halt: {e}")
            
    def reset_auto_halt(self, authorization_code: str) -> bool:
        """
        Reset auto-halt (requires authorization)
        
        Args:
            authorization_code: Required authorization code
            
        Returns:
            bool: True if successfully reset
        """
        try:
            expected_code = "TRADEMASTERX_RISK_RESET_2025"
            
            if authorization_code != expected_code:
                self.logger.error("[CRITICAL] UNAUTHORIZED: Invalid authorization code for risk reset")
                return False
                
            self._auto_halt_triggered = False
            
            self.logger.warning("[WARNING] AUTO-HALT RESET: Trading can resume")
            self.logger.warning("[WARNING] WARNING: Risk limits remain in effect")
            
            self._save_daily_data()
            return True
            
        except Exception as e:
            self.logger.error(f"[ERROR] Error resetting auto-halt: {e}")
            return False
            
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
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current risk metrics for monitoring and display"""
        return {
            "daily_loss": abs(min(0, self.daily_pnl)),  # Only show loss as positive
            "daily_trades": self.daily_trades,
            "current_balance": self.current_balance,
            "daily_loss_limit": self.daily_loss_limit,
            "max_trades_per_day": self.max_trades_per_day,
            "trades_remaining": max(0, self.max_trades_per_day - self.daily_trades),
            "loss_limit_remaining": max(0, self.daily_loss_limit + self.daily_pnl),
            "risk_guard_active": self._risk_guard_active,
            "auto_halt_triggered": self._auto_halt_triggered,
            "active_positions": len(self.active_positions),
            "max_concurrent_positions": self.max_concurrent_positions
        }
        
    def get_risk_warnings(self) -> List[Dict[str, Any]]:
        """Get current risk warnings"""
        warnings = []
        
        try:
            # Check daily trade limit
            trades_remaining = self.max_trades_per_day - self.daily_trades
            if trades_remaining <= 10:
                warnings.append({
                    "type": "TRADE_LIMIT_WARNING",
                    "message": f"Only {trades_remaining} trades remaining today",
                    "severity": "HIGH" if trades_remaining <= 5 else "MEDIUM"
                })
                
            # Check daily loss limit
            loss_remaining = self.daily_loss_limit + self.daily_pnl
            if loss_remaining <= 50:
                warnings.append({
                    "type": "LOSS_LIMIT_WARNING",
                    "message": f"Only ${loss_remaining:.2f} loss buffer remaining",
                    "severity": "HIGH" if loss_remaining <= 20 else "MEDIUM"
                })
                
            # Check drawdown
            current_drawdown = (self.max_balance_today - self.current_balance) / self.max_balance_today
            if current_drawdown > 0.05:  # 5% warning threshold
                warnings.append({
                    "type": "DRAWDOWN_WARNING",
                    "message": f"Current drawdown: {current_drawdown:.1%}",
                    "severity": "HIGH" if current_drawdown > 0.08 else "MEDIUM"
                })
                
            # Check position concentration
            if len(self.active_positions) >= self.max_concurrent_positions - 1:                warnings.append({
                    "type": "POSITION_LIMIT_WARNING",
                    "message": f"Near max concurrent positions ({len(self.active_positions)}/{self.max_concurrent_positions})",
                    "severity": "MEDIUM"
                })
                
        except Exception as e:
            self.logger.error(f"[ERROR] Error generating risk warnings: {e}")
            
        return warnings
        
    def _create_validation_result(self, approved: bool, message: str) -> Dict[str, Any]:
        """Create validation result dictionary"""
        return {
            "approved": approved,
            "allowed": approved,  # Added for test compatibility
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "risk_status": self.get_risk_status()
        }
        
    def _remove_position(self, trade_id: str):
        """Remove position from active tracking"""
        self.active_positions = [pos for pos in self.active_positions if pos.get('id') != trade_id]
        
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
                "active_positions": self.active_positions            }
            
            with open(self.risk_data_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"[ERROR] Error saving daily data: {e}")
            
    def get_daily_status(self) -> Dict[str, Any]:
        """
        Get comprehensive daily status for risk management
        
        Returns:
            Dict containing daily status metrics and limits
        """
        try:
            current_drawdown = 0.0
            if self.max_balance_today > 0:
                current_drawdown = (self.max_balance_today - self.current_balance) / self.max_balance_today
                
            balance_loss_pct = 0.0
            if self.session_start_balance > 0:
                balance_loss_pct = (self.session_start_balance - self.current_balance) / self.session_start_balance
                
            return {
                "date": self.last_reset_date.isoformat(),
                "pnl": self.daily_pnl,  # Added for test compatibility
                "trade_count": self.daily_trades,  # Added for test compatibility
                "daily_summary": {
                    "daily_pnl": self.daily_pnl,
                    "daily_trades": self.daily_trades,
                    "trades_remaining": max(0, self.max_trades_per_day - self.daily_trades),
                    "loss_limit_remaining": max(0, self.daily_loss_limit + self.daily_pnl)
                },
                "balance_info": {
                    "current_balance": self.current_balance,
                    "session_start_balance": self.session_start_balance,
                    "max_balance_today": self.max_balance_today,
                    "balance_change": self.current_balance - self.session_start_balance,
                    "balance_loss_pct": balance_loss_pct * 100
                },
                "risk_metrics": {
                    "current_drawdown_pct": current_drawdown * 100,
                    "drawdown_threshold_pct": self.drawdown_threshold * 100,
                    "active_positions": len(self.active_positions),
                    "max_concurrent_positions": self.max_concurrent_positions
                },
                "limits": {
                    "daily_loss_limit": self.daily_loss_limit,
                    "max_trades_per_day": self.max_trades_per_day,
                    "max_position_size": self.max_position_size,
                    "drawdown_threshold": self.drawdown_threshold
                },
                "status_flags": {
                    "risk_guard_active": self._risk_guard_active,
                    "auto_halt_triggered": self._auto_halt_triggered,
                    "within_loss_limits": self.daily_pnl > -self.daily_loss_limit,
                    "within_trade_limits": self.daily_trades < self.max_trades_per_day,
                    "within_drawdown_limits": current_drawdown <= self.drawdown_threshold
                },
                "warnings": self.get_risk_warnings(),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"[ERROR] Error getting daily status: {e}")
            return {
                "error": f"Failed to get daily status: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }


class RiskGuardCLI:
    """
    Command-line interface for risk guard operations
    """
    
    def __init__(self):
        # Load config
        config_file = Path("trademasterx/config/system.yaml")
        if config_file.exists():
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
        else:
            config = {}
            
        self.risk_guard = RiskGuard(config)
        
    def status(self):
        """Display risk guard status"""
        status = self.risk_guard.get_risk_status()
        warnings = self.risk_guard.get_risk_warnings()
        
        print("\n🛡️ RISK GUARD STATUS")
        print("=" * 50)
        print(f"Risk Guard Active: {'YES' if status['risk_guard_active'] else 'NO'}")
        print(f"Auto-Halt Triggered: {'YES' if status['auto_halt_triggered'] else 'NO'}")
        print(f"Daily P&L: ${status['daily_pnl']:.2f}")
        print(f"Daily Trades: {status['daily_trades']}/{status['max_trades_per_day']}")
        print(f"Current Balance: ${status['current_balance']:.2f}")
        print(f"Loss Limit Remaining: ${status['loss_limit_remaining']:.2f}")
        print(f"Current Drawdown: {status['current_drawdown_pct']:.1f}%")
        print(f"Active Positions: {status['active_positions']}/{status['max_concurrent_positions']}")
        
        if warnings:
            print("\n[WARNING] RISK WARNINGS:")
            for warning in warnings:
                print(f"  {warning['severity']}: {warning['message']}")
                
        print("=" * 50)
        
    def reset_halt(self, auth_code: str):
        """Reset auto-halt via CLI"""
        if self.risk_guard.reset_auto_halt(auth_code):            print("[WARNING] Auto-halt reset successfully")
        else:
            print("[ERROR] Failed to reset auto-halt")


if __name__ == "__main__":
    import sys
    
    cli = RiskGuardCLI()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python risk_guard.py status")
        print("  python risk_guard.py reset_halt <auth_code>")
        sys.exit(1)
        
    command = sys.argv[1]
    
    if command == "status":
        cli.status()
    elif command == "reset_halt":
        if len(sys.argv) < 3:
            print("Error: Authorization code required")
            sys.exit(1)
        auth_code = sys.argv[2]
        cli.reset_halt(auth_code)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
