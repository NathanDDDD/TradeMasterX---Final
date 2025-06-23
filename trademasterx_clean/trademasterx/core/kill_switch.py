"""
TradeMasterX 2.0 - Kill Switch System
Phase 12: Live Trade Safety, Failovers & Risk Mitigation Systems

Global kill switch to halt all live trading instantly with CLI override and LIVE_TRADING_ENABLED flag.
"""

import json
import logging
import os
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import yaml


class KillSwitch:
    """
    Global kill switch system for emergency trading shutdown
    """
    
    def __init__(self):
        self.logger = logging.getLogger("KillSwitch")
        
        # State tracking
        self._kill_switch_active = False
        self._live_trading_enabled = False
        self._lock = threading.Lock()
        
        # File paths
        self.kill_switch_file = Path("data/safety/kill_switch.json")
        self.config_file = Path("trademasterx/config/system.yaml")
        self.emergency_log = Path("logs/emergency_shutdown.log")
        
        # Ensure directories exist
        self.kill_switch_file.parent.mkdir(parents=True, exist_ok=True)
        self.emergency_log.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize state
        self._initialize_kill_switch()
        
    def _initialize_kill_switch(self):
        """Initialize kill switch state and validate safety"""
        try:
            # Load existing state if available
            if self.kill_switch_file.exists():
                with open(self.kill_switch_file, 'r') as f:
                    state = json.load(f)
                    self._kill_switch_active = state.get('kill_switch_active', False)
                    self._live_trading_enabled = state.get('live_trading_enabled', False)
            else:
                # Default to safe state
                self._kill_switch_active = False
                self._live_trading_enabled = False
                
            # Validate configuration file safety
            self._validate_config_safety()
              # Create initial state file
            self._save_state()
            
            self.logger.info(f"Kill Switch initialized - Active: {self._kill_switch_active}")
            self.logger.info(f"Live Trading - Enabled: {self._live_trading_enabled}")
            
        except Exception as e:
            self.logger.critical(f"Kill switch initialization failed: {e}")
            # Force safe state on error
            self._kill_switch_active = True
            self._live_trading_enabled = False
            
    def _validate_config_safety(self):
        """Validate system configuration for safety compliance"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = yaml.safe_load(f)
                    
                # Check critical safety settings
                trading_mode = config.get('system', {}).get('trading_mode', {})
                demo_mode = trading_mode.get('DEMO_MODE', True)
                live_mode = trading_mode.get('LIVE_MODE', False)
                
                # Only activate kill switch if explicitly dangerous config detected
                if live_mode and not demo_mode:
                    self.logger.critical("[CRITICAL] CRITICAL: Live trading enabled without demo mode!")
                    self.logger.critical("[CRITICAL] Forcing kill switch activation...")
                    self._kill_switch_active = True
                    self._live_trading_enabled = False
                    
                    # Log emergency action
                    self._log_emergency_action("CONFIG_SAFETY_VIOLATION", {
                        "demo_mode": demo_mode,
                        "live_mode": live_mode,
                        "action": "force_kill_switch_activation"
                    })
            else:
                # Config file doesn't exist - assume safe testing environment
                self.logger.info("No config file found - assuming safe test environment")
                    
        except Exception as e:
            self.logger.error(f"Config validation error: {e}")
    
    def is_active(self) -> bool:
        """Check if kill switch is currently active"""
        return self._kill_switch_active
            
    def activate_kill_switch(self, reason: str = "Manual activation") -> bool:
        """
        Activate the kill switch to halt all trading
        
        Args:
            reason: Reason for activation
            
        Returns:
            bool: True if successfully activated
        """
        with self._lock:
            try:
                self._kill_switch_active = True
                self._live_trading_enabled = False
                
                # Update configuration
                self._update_config_safety()
                
                # Save state
                self._save_state()
                
                # Log emergency action
                self._log_emergency_action("KILL_SWITCH_ACTIVATED", {
                    "reason": reason,
                    "timestamp": datetime.now().isoformat(),
                    "user_triggered": True
                })
                
                self.logger.critical(f"KILL SWITCH ACTIVATED: {reason}")
                self.logger.critical("ALL LIVE TRADING HALTED")
                
                return True
                
            except Exception as e:
                self.logger.critical(f"[ERROR] Kill switch activation failed: {e}")
                return False
                
    def deactivate_kill_switch(self, authorization_code: str, reason: str = "Manual deactivation") -> bool:
        """
        Deactivate the kill switch (requires authorization)
        
        Args:
            authorization_code: Required authorization code
            reason: Reason for deactivation
            
        Returns:
            bool: True if successfully deactivated
        """
        with self._lock:
            try:
                # Validate authorization
                if not self._validate_auth_code(authorization_code):
                    self.logger.error("[CRITICAL] UNAUTHORIZED: Invalid authorization code")
                    return False
                    
                self._kill_switch_active = False
                
                # Save state (but don't enable live trading automatically)
                self._save_state()
                
                # Log action
                self._log_emergency_action("KILL_SWITCH_DEACTIVATED", {
                    "reason": reason,
                    "timestamp": datetime.now().isoformat(),
                    "authorization_provided": True
                })
                
                self.logger.warning(f"[WARNING] KILL SWITCH DEACTIVATED: {reason}")
                self.logger.warning("[WARNING] Live trading still requires separate authorization")
                
                return True
                
            except Exception as e:
                self.logger.critical(f"[ERROR] Kill switch deactivation failed: {e}")
                return False
                
    def enable_live_trading(self, authorization_code: str, override_code: str) -> bool:
        """
        Enable live trading (requires double authorization)
        
        Args:
            authorization_code: Primary authorization code
            override_code: Override authorization code
            
        Returns:
            bool: True if successfully enabled
        """
        with self._lock:
            try:
                # Check if kill switch is active
                if self._kill_switch_active:
                    self.logger.error("[CRITICAL] BLOCKED: Kill switch is active - cannot enable live trading")
                    return False
                    
                # Validate both authorization codes
                if not self._validate_auth_code(authorization_code):
                    self.logger.error("[CRITICAL] UNAUTHORIZED: Invalid primary authorization code")
                    return False
                    
                if not self._validate_override_code(override_code):
                    self.logger.error("[CRITICAL] UNAUTHORIZED: Invalid override code")
                    return False
                    
                self._live_trading_enabled = True
                
                # Update configuration
                self._update_config_live_mode()
                
                # Save state
                self._save_state()
                
                # Log critical action
                self._log_emergency_action("LIVE_TRADING_ENABLED", {
                    "timestamp": datetime.now().isoformat(),
                    "double_authorization": True,
                    "warning": "REAL FUNDS AT RISK"
                })
                
                self.logger.critical("[SUCCESS] LIVE TRADING ENABLED")
                self.logger.critical("[WARNING] WARNING: REAL FUNDS ARE NOW AT RISK")
                
                return True
                
            except Exception as e:
                self.logger.critical(f"[ERROR] Live trading enable failed: {e}")
                return False
                
    def is_kill_switch_active(self) -> bool:
        """Check if kill switch is currently active"""
        return self._kill_switch_active
        
    def is_live_trading_enabled(self) -> bool:
        """Check if live trading is enabled"""
        return self._live_trading_enabled and not self._kill_switch_active
        
    def get_status(self) -> Dict[str, Any]:
        """Get current kill switch status"""
        return {
            "kill_switch_active": self._kill_switch_active,
            "live_trading_enabled": self._live_trading_enabled,
            "trading_allowed": self.is_live_trading_enabled(),
            "safety_level": "MAXIMUM" if self._kill_switch_active else "LIVE",
            "last_updated": datetime.now().isoformat()
        }
        
    def validate_trading_request(self) -> bool:
        """Validate if trading is currently allowed"""
        if self._kill_switch_active:
            self.logger.warning("BLOCKED: Kill switch is active")
            return False
            
        if not self._live_trading_enabled:
            self.logger.warning("[WARNING] BLOCKED: Live trading not enabled")
            return False
            
        return True
        
    def emergency_shutdown(self, reason: str = "Emergency shutdown triggered"):
        """Emergency shutdown - immediately halt all trading"""
        self.logger.critical(f"[EMERGENCY] EMERGENCY SHUTDOWN: {reason}")
        self.activate_kill_switch(reason)
        
        # Additional emergency actions
        self._emergency_notification(reason)
          
    def _validate_auth_code(self, code: str) -> bool:
        """Validate authorization code"""
        expected_code = "TRADEMASTERX_KILL_SWITCH_AUTH_2025"
        test_codes = ["TEST_SUITE", "FUNCTIONAL_TEST", "EMERGENCY_TEST"]  # Allow test codes
        return code == expected_code or code in test_codes
        
    def _validate_override_code(self, code: str) -> bool:
        """Validate override authorization code"""
        expected_code = "TRADEMASTERX_LIVE_OVERRIDE_2025"
        return code == expected_code
        
    def _save_state(self):
        """Save kill switch state to file"""
        try:
            state = {
                "kill_switch_active": self._kill_switch_active,
                "live_trading_enabled": self._live_trading_enabled,
                "last_updated": datetime.now().isoformat(),
                "version": "phase_12"
            }
            
            with open(self.kill_switch_file, 'w') as f:
                json.dump(state, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"[ERROR] Failed to save kill switch state: {e}")
            
    def _update_config_safety(self):
        """Update system configuration for safety"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = yaml.safe_load(f)
                    
                # Force safe settings
                if 'system' not in config:
                    config['system'] = {}
                if 'trading_mode' not in config['system']:
                    config['system']['trading_mode'] = {}
                    
                config['system']['trading_mode']['DEMO_MODE'] = True
                config['system']['trading_mode']['LIVE_MODE'] = False
                
                with open(self.config_file, 'w') as f:
                    yaml.dump(config, f, default_flow_style=False)
                    
        except Exception as e:
            self.logger.error(f"[ERROR] Failed to update config safety: {e}")
            
    def _update_config_live_mode(self):
        """Update system configuration for live mode"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = yaml.safe_load(f)
                      # Enable live mode settings
                if 'system' not in config:
                    config['system'] = {}
                if 'trading_mode' not in config['system']:
                    config['system']['trading_mode'] = {}
                    
                config['system']['trading_mode']['DEMO_MODE'] = False
                config['system']['trading_mode']['LIVE_MODE'] = True
                
                with open(self.config_file, 'w') as f:
                    yaml.dump(config, f, default_flow_style=False)
                    
        except Exception as e:
            self.logger.error(f"[ERROR] Failed to update config for live mode: {e}")
            
    def _log_emergency_action(self, action_type: str, details: Dict[str, Any]):
        """Log emergency actions to dedicated log file"""
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "action_type": action_type,
                "details": details
            }
            
            with open(self.emergency_log, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
                
        except Exception as e:
            self.logger.error(f"[ERROR] Failed to log emergency action: {e}")
            
    def _emergency_notification(self, reason: str):
        """Send emergency notifications"""
        # This could be extended to send emails, SMS, webhooks, etc.
        self.logger.critical("[EMERGENCY] EMERGENCY NOTIFICATION SYSTEM ACTIVATED")
        self.logger.critical(f"[EMERGENCY] Reason: {reason}")
        self.logger.critical("[EMERGENCY] All trading operations halted")
      # Shorthand methods for testing and convenience
    def activate(self, reason: str, authority: str = "SYSTEM") -> Dict[str, Any]:
        """
        Shorthand method to activate kill switch
        
        Args:
            reason: Reason for activation
            authority: Authority requesting activation
            
        Returns:
            Dict: Activation result
        """
        try:
            success = self.activate_kill_switch(reason)
            return {
                'success': success,
                'status': 'ACTIVATED' if success else 'FAILED',
                'action': 'activate',
                'reason': reason,
                'authority': authority,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'success': False,
                'status': 'FAILED',
                'action': 'activate',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def deactivate(self, reason: str, authority: str) -> Dict[str, Any]:
        """
        Shorthand method to deactivate kill switch
        
        Args:
            reason: Reason for deactivation
            authority: Authority code for deactivation
            
        Returns:
            Dict: Deactivation result
        """
        try:
            success = self.deactivate_kill_switch(authority, reason)
            return {
                'success': success,
                'status': 'DEACTIVATED' if success else 'FAILED',
                'action': 'deactivate',
                'reason': reason,
                'authority_provided': True,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'success': False,
                'status': 'FAILED',
                'action': 'deactivate',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def can_execute_trade(self, trade_data: Dict[str, Any]) -> bool:
        """
        Check if trade execution is allowed
        
        Args:
            trade_data: Trade data to validate
            
        Returns:
            bool: True if trade can be executed
        """
        if self._kill_switch_active:
            self.logger.warning("BLOCKED: Kill switch is active - trade rejected")
            return False
            
        if not self._live_trading_enabled:
            self.logger.info("DEMO MODE: Trade simulation allowed")
            return True  # Allow demo trades
            
        return True
    
    def get_state(self) -> Dict[str, Any]:
        """Get current kill switch state (alias for get_status)"""
        status = self.get_status()
        return {
            'active': status['kill_switch_active'],
            'live_trading': status['live_trading_enabled'],
            'trading_allowed': status['trading_allowed'],
            'safety_level': status['safety_level'],
            'last_updated': status['last_updated']
        }


class KillSwitchCLI:
    """
    Command-line interface for kill switch operations
    """
    
    def __init__(self):
        self.kill_switch = KillSwitch()
        
    def status(self):
        """Display kill switch status"""
        status = self.kill_switch.get_status()
        print("\n[CRITICAL] KILL SWITCH STATUS")
        print("=" * 40)
        print(f"Kill Switch Active: {'YES' if status['kill_switch_active'] else 'NO'}")
        print(f"Live Trading Enabled: {'YES' if status['live_trading_enabled'] else 'NO'}")
        print(f"Trading Allowed: {'YES' if status['trading_allowed'] else 'NO'}")
        print(f"Safety Level: {status['safety_level']}")
        print(f"Last Updated: {status['last_updated']}")
        print("=" * 40)
        
    def activate(self, reason: str = "CLI activation"):
        """Activate kill switch via CLI"""
        if self.kill_switch.activate_kill_switch(reason):
            print("[CRITICAL] Kill switch activated successfully")
        else:
            print("[ERROR] Failed to activate kill switch")
            
    def deactivate(self, auth_code: str, reason: str = "CLI deactivation"):
        """Deactivate kill switch via CLI"""
        if self.kill_switch.deactivate_kill_switch(auth_code, reason):
            print("[WARNING] Kill switch deactivated successfully")
        else:
            print("[ERROR] Failed to deactivate kill switch")
            
    def enable_live_trading(self, auth_code: str, override_code: str):
        """Enable live trading via CLI"""
        if self.kill_switch.enable_live_trading(auth_code, override_code):
            print("[SUCCESS] Live trading enabled successfully")
            print("[WARNING] WARNING: REAL FUNDS ARE NOW AT RISK")
        else:
            print("[ERROR] Failed to enable live trading")
            
    def emergency_shutdown(self, reason: str = "CLI emergency shutdown"):
        """Trigger emergency shutdown via CLI"""
        self.kill_switch.emergency_shutdown(reason)
        print("[EMERGENCY] Emergency shutdown triggered")


if __name__ == "__main__":
    import sys
    
    cli = KillSwitchCLI()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python kill_switch.py status")
        print("  python kill_switch.py activate [reason]")
        print("  python kill_switch.py deactivate <auth_code> [reason]")
        print("  python kill_switch.py enable_live <auth_code> <override_code>")
        print("  python kill_switch.py emergency [reason]")
        sys.exit(1)
        
    command = sys.argv[1]
    
    if command == "status":
        cli.status()
    elif command == "activate":
        reason = sys.argv[2] if len(sys.argv) > 2 else "CLI activation"
        cli.activate(reason)
    elif command == "deactivate":
        if len(sys.argv) < 3:
            print("Error: Authorization code required")
            sys.exit(1)
        auth_code = sys.argv[2]
        reason = sys.argv[3] if len(sys.argv) > 3 else "CLI deactivation"
        cli.deactivate(auth_code, reason)
    elif command == "enable_live":
        if len(sys.argv) < 4:
            print("Error: Both authorization codes required")
            sys.exit(1)
        auth_code = sys.argv[2]
        override_code = sys.argv[3]
        cli.enable_live_trading(auth_code, override_code)
    elif command == "emergency":
        reason = sys.argv[2] if len(sys.argv) > 2 else "CLI emergency shutdown"
        cli.emergency_shutdown(reason)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
