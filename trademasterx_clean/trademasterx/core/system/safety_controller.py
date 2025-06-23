"""
TradeMasterX 2.0 - Safety Controller
Phase 10: Mainnet Demo Learning Loop

This module enforces DEMO_MODE safety and prevents accidental live trading.
"""

import logging
import os
from typing import Dict, Any, Optional
from datetime import datetime
import json
from pathlib import Path


class SafetyController:
    """
    Enforces safety controls for demo trading on mainnet API
    Prevents accidental real fund usage and unauthorized live trading
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger("SafetyController")
        
        # Load safety settings
        self.demo_mode = config.get('trading_mode', {}).get('DEMO_MODE', True)
        self.live_mode = config.get('trading_mode', {}).get('LIVE_MODE', False)
        self.mainnet_demo = config.get('trading_mode', {}).get('mainnet_demo', True)
        self.manual_override_required = config.get('trading_mode', {}).get('manual_override_required', True)
        
        # Safety controls
        self.withdrawal_disabled = config.get('safety', {}).get('withdrawal_disabled', True)
        self.wallet_protection = config.get('safety', {}).get('wallet_protection', True)
        self.max_virtual_balance = config.get('safety', {}).get('max_virtual_balance', 10000)
        self.max_position_size = config.get('safety', {}).get('max_position_size', 1000)
        
        # Initialize safety state
        self._initialize_safety_state()
        
        self.logger.info("🛡️ SafetyController initialized for DEMO_MODE on mainnet")
        
    def _initialize_safety_state(self):
        """Initialize safety state and validation"""
        # Ensure DEMO_MODE is always active
        if not self.demo_mode:
            self.logger.critical("🚨 CRITICAL: DEMO_MODE is disabled! Forcing activation...")
            self.demo_mode = True
            
        # Ensure LIVE_MODE is disabled
        if self.live_mode:
            self.logger.critical("🚨 CRITICAL: LIVE_MODE is enabled! Forcing deactivation...")
            self.live_mode = False
            
        # Create safety lock file
        self._create_safety_lock()
        
        self.logger.info(f"✅ Safety State: DEMO={self.demo_mode}, LIVE={self.live_mode}, MAINNET_DEMO={self.mainnet_demo}")
        
    def _create_safety_lock(self):
        """Create a safety lock file to prevent accidental activation"""
        lock_file = Path("data/safety_lock.json")
        lock_file.parent.mkdir(exist_ok=True)
        
        lock_data = {
            "demo_mode": self.demo_mode,
            "live_mode": self.live_mode,
            "mainnet_demo": self.mainnet_demo,
            "created_at": datetime.now().isoformat(),
            "warning": "This file prevents accidental live trading activation"
        }
        
        with open(lock_file, 'w') as f:
            json.dump(lock_data, f, indent=2)
            
        self.logger.info(f"🔒 Safety lock created: {lock_file}")
        
    def validate_trading_request(self, operation: str, amount: float = 0) -> bool:
        """
        Validate if a trading operation is allowed under current safety settings
        
        Args:
            operation: Type of operation (buy, sell, withdraw, transfer, etc.)
            amount: Amount involved in USD
            
        Returns:
            bool: True if operation is allowed, False otherwise
        """
        # Check if DEMO_MODE is active
        if not self.demo_mode:
            self.logger.error(f"🚨 Operation '{operation}' blocked: DEMO_MODE is not active")
            return False
            
        # Block withdrawal operations
        if operation in ['withdraw', 'withdrawal'] and self.withdrawal_disabled:
            self.logger.error(f"🚨 Operation '{operation}' blocked: Withdrawals disabled in DEMO_MODE")
            return False
            
        # Block wallet modification operations
        if operation in ['transfer', 'deposit', 'wallet_modify'] and self.wallet_protection:
            self.logger.error(f"🚨 Operation '{operation}' blocked: Wallet protection active")
            return False
            
        # Check position size limits
        if operation in ['buy', 'sell', 'open_position'] and amount > self.max_position_size:
            self.logger.error(f"🚨 Operation '{operation}' blocked: Amount ${amount} exceeds limit ${self.max_position_size}")
            return False
            
        # Log approved operation
        self.logger.info(f"✅ Operation '{operation}' approved: Amount=${amount}, DEMO_MODE active")
        return True
        
    def get_demo_balance_limit(self) -> float:
        """Get the maximum virtual balance allowed in demo mode"""
        return self.max_virtual_balance
        
    def get_position_size_limit(self) -> float:
        """Get the maximum position size allowed in demo mode"""
        return self.max_position_size
        
    def is_demo_mode_active(self) -> bool:
        """Check if demo mode is currently active"""
        return self.demo_mode
        
    def is_live_mode_blocked(self) -> bool:
        """Check if live mode is properly blocked"""
        return not self.live_mode
        
    def get_safety_status(self) -> Dict[str, Any]:
        """Get current safety status for monitoring"""
        return {
            "demo_mode": self.demo_mode,
            "live_mode": self.live_mode,
            "mainnet_demo": self.mainnet_demo,
            "withdrawal_disabled": self.withdrawal_disabled,
            "wallet_protection": self.wallet_protection,
            "max_virtual_balance": self.max_virtual_balance,
            "max_position_size": self.max_position_size,
            "manual_override_required": self.manual_override_required,
            "safety_level": "MAXIMUM" if self.demo_mode and not self.live_mode else "COMPROMISED"
        }
        
    def manual_override_go_live(self, authorization_code: str) -> bool:
        """
        Manual override to activate live trading (REQUIRES EXPLICIT AUTHORIZATION)
        
        Args:
            authorization_code: Required authorization code for live trading
            
        Returns:
            bool: True if successfully activated, False otherwise
        """
        # This is intentionally difficult to activate
        expected_code = "TRADEMASTERX_LIVE_AUTHORIZATION_2025"
        
        if authorization_code != expected_code:
            self.logger.error("🚨 UNAUTHORIZED: Invalid authorization code for live trading")
            return False
            
        if not self.manual_override_required:
            self.logger.error("🚨 BLOCKED: Manual override not enabled in configuration")
            return False
            
        # Log the activation attempt
        self.logger.critical("⚠️ MANUAL OVERRIDE: Attempting to activate LIVE_MODE")
        self.logger.critical("⚠️ WARNING: This will use REAL FUNDS")
        self.logger.critical("⚠️ Ensure you understand the risks before proceeding")
        
        # This would require additional confirmation steps in a real implementation
        self.logger.info("🔐 Live trading activation requires additional manual steps")
        self.logger.info("🔐 For safety, automatic activation is disabled")
        
        return False  # Always return False for safety in this demo phase
        
    def emergency_shutdown(self):
        """Emergency shutdown - force back to demo mode"""
        self.demo_mode = True
        self.live_mode = False
        self._create_safety_lock()
        
        self.logger.critical("🚨 EMERGENCY SHUTDOWN: Forced back to DEMO_MODE")
        self.logger.critical("🚨 All trading operations suspended")
        
    def log_safety_violation(self, violation_type: str, details: Dict[str, Any]):
        """Log safety violations for audit trail"""
        violation = {
            "timestamp": datetime.now().isoformat(),
            "type": violation_type,
            "details": details,
            "safety_state": self.get_safety_status()
        }
        
        # Log to file
        violations_file = Path("logs/safety_violations.json")
        violations_file.parent.mkdir(exist_ok=True)
        
        violations = []
        if violations_file.exists():
            try:
                with open(violations_file, 'r') as f:
                    violations = json.load(f)
            except Exception as e:
                self.logger.error(f"Error reading violations file: {e}")
                
        violations.append(violation)
        
        # Keep only last 1000 violations
        if len(violations) > 1000:
            violations = violations[-1000:]
            
        with open(violations_file, 'w') as f:
            json.dump(violations, f, indent=2)
            
        self.logger.error(f"🚨 SAFETY VIOLATION: {violation_type} - {details}")


class DemoModeIndicator:
    """
    UI indicator for demo mode status
    """
    
    @staticmethod
    def get_ui_status() -> Dict[str, Any]:
        """Get status for UI display"""
        return {
            "mode": "DEMO MODE ACTIVE",
            "status": "Using Virtual Funds Only",
            "color": "green",
            "warning": "No Real Money at Risk",
            "api": "Bybit Mainnet (Demo Account)",
            "funds": "Virtual USD $10,000"
        }
        
    @staticmethod
    def get_banner_text() -> str:
        """Get banner text for console/web display"""
        return """
🛡️ ═══════════════════════════════════════════════════════════ 🛡️
🎯 TRADEMASTERX 2.0 - DEMO MODE ACTIVE - MAINNET API LEARNING 🎯
🛡️ ═══════════════════════════════════════════════════════════ 🛡️
   ✅ Using Bybit Mainnet API with DEMO ACCOUNT
   ✅ Virtual Funds Only - No Real Money at Risk  
   ✅ Real Market Data for Learning
   🚫 Live Trading DISABLED
   🚫 Withdrawals BLOCKED
   🚫 Real Fund Access LOCKED
🛡️ ═══════════════════════════════════════════════════════════ 🛡️
"""
