"""
TradeMasterX 2.0 - Risk Management Bot
Comprehensive risk monitoring and management system.
"""

import json
import logging
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np

from ...core.bot_registry import BaseBot


class RiskLevel(Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class RiskType(Enum):
    MARKET = "market"
    POSITION = "position"
    LIQUIDITY = "liquidity"
    CORRELATION = "correlation"
    CONCENTRATION = "concentration"
    LEVERAGE = "leverage"


@dataclass
class RiskAlert:
    """Risk alert notification"""
    risk_type: RiskType
    risk_level: RiskLevel
    symbol: Optional[str]
    description: str
    current_value: float
    threshold: float
    recommended_action: str
    timestamp: datetime
    metadata: Dict[str, Any]


@dataclass
class PortfolioRisk:
    """Portfolio risk assessment"""
    total_exposure: float
    portfolio_var: float
    max_drawdown: float
    correlation_risk: float
    concentration_risk: float
    leverage_ratio: float
    risk_score: float
    risk_level: RiskLevel


@dataclass
class PositionRisk:
    """Individual position risk assessment"""
    symbol: str
    position_size: float
    market_value: float
    unrealized_pnl: float
    risk_percentage: float
    stop_loss_distance: float
    leverage: float
    risk_score: float


class RiskBot(BaseBot):
    """
    Comprehensive Risk Management Bot for TradeMasterX 2.0
    
    Provides:
    - Real-time portfolio risk monitoring
    - Position-level risk assessment    - Risk alerts and notifications
    - Automated risk management actions
    - Risk reporting and analytics
    """
    
    def __init__(self, name: str, config: Dict[str, Any]):
        # If no config is provided, load default configuration
        if config is None:
            from ...config.config_loader import ConfigLoader
            config_loader = ConfigLoader()
            config = config_loader.get_config('system', {}).get('risk', {})
        
        super().__init__(name, config)
        
        # Risk configuration
        self.max_portfolio_risk = config.get('max_portfolio_risk', 0.15)  # 15%
        self.max_position_risk = config.get('max_position_risk', 0.05)   # 5%
        self.max_correlation = config.get('max_correlation', 0.7)         # 70%
        self.max_concentration = config.get('max_concentration', 0.3)     # 30%
        self.max_leverage = config.get('max_leverage', 3.0)               # 3x
        
        # Alert thresholds
        self.alert_thresholds = config.get('alert_thresholds', {
            'portfolio_risk': [0.8, 0.9, 0.95],  # 80%, 90%, 95% of max
            'position_risk': [0.8, 0.9, 0.95],
            'correlation': [0.6, 0.7, 0.8],
            'concentration': [0.25, 0.3, 0.35],
            'leverage': [2.0, 2.5, 3.0]
        })
        
        # Risk monitoring settings
        self.monitoring_interval = config.get('monitoring_interval', 60)  # 60 seconds
        self.var_confidence = config.get('var_confidence', 0.95)           # 95%
        self.lookback_days = config.get('lookback_days', 30)               # 30 days
        
        # Data storage
        self.portfolio_risk: Optional[PortfolioRisk] = None
        self.position_risks: Dict[str, PositionRisk] = {}
        self.active_alerts: List[RiskAlert] = []
        self.risk_history: List[Dict[str, Any]] = []
        
        # Risk state
        self.emergency_mode = False
        self.last_risk_check = None
        self.risk_actions_taken = []
        
        self.logger.info(f"RiskBot {name} configured with {self.max_portfolio_risk:.1%} max portfolio risk")

    async def initialize(self) -> bool:
        """Initialize risk management bot"""
        try:
            # Validate risk parameters
            if await self._validate_risk_config():
                self.is_initialized = True
                self.logger.info("RiskBot initialized successfully")
                return True
            else:
                self.logger.error("Risk configuration validation failed")
                return False
                
        except Exception as e:
            self.logger.error(f"RiskBot initialization failed: {e}")
            return False

    async def execute_cycle(self) -> Dict[str, Any]:
        """Execute risk management cycle"""
        try:
            self.logger.info("⚠️ Starting risk management cycle...")
            
            # Calculate portfolio risk
            portfolio_risk_result = await self.calculate_portfolio_risk()
            
            # Assess position risks
            position_risk_result = await self.assess_position_risks()
            
            # Generate risk alerts
            alerts_result = await self.generate_risk_alerts()
            
            # Check for emergency situations
            emergency_check = await self.check_emergency_conditions()
            
            # Take automated risk actions if needed
            actions_result = await self.execute_risk_actions()
            
            cycle_result = {
                "timestamp": datetime.now().isoformat(),
                "portfolio_risk": portfolio_risk_result,
                "position_risks": position_risk_result,
                "risk_alerts": alerts_result,
                "emergency_status": emergency_check,
                "actions_taken": actions_result,
                "overall_risk_level": self._get_overall_risk_level(),
                "status": "success"
            }
            
            # Save risk assessment
            await self._save_risk_assessment(cycle_result)
            
            # Update last check time
            self.last_risk_check = datetime.now()
            
            self.logger.info(f"✅ Risk cycle completed - Risk Level: {cycle_result['overall_risk_level']}")
            return cycle_result
            
        except Exception as e:
            self.logger.error(f"Risk management cycle error: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "status": "error",
                "error": str(e)
            }

    async def calculate_portfolio_risk(self) -> Dict[str, Any]:
        """
        Calculate comprehensive portfolio risk metrics
        
        Returns:
            Dict containing portfolio risk assessment
        """
        try:
            self.logger.info("📊 Calculating portfolio risk...")
            
            # Get current portfolio data
            portfolio_data = await self._get_portfolio_data()
            
            if not portfolio_data:
                return {"status": "no_data", "risk": {}}
            
            # Calculate total exposure
            total_exposure = sum(pos.get('market_value', 0) for pos in portfolio_data.values())
            
            # Calculate Value at Risk (VaR)
            portfolio_var = await self._calculate_portfolio_var(portfolio_data)
            
            # Calculate maximum drawdown
            max_drawdown = await self._calculate_max_drawdown(portfolio_data)
            
            # Calculate correlation risk
            correlation_risk = await self._calculate_correlation_risk(portfolio_data)
            
            # Calculate concentration risk
            concentration_risk = await self._calculate_concentration_risk(portfolio_data)
            
            # Calculate leverage ratio
            leverage_ratio = await self._calculate_leverage_ratio(portfolio_data)
            
            # Calculate overall risk score
            risk_score = self._calculate_risk_score(
                portfolio_var, max_drawdown, correlation_risk,
                concentration_risk, leverage_ratio
            )
            
            # Determine risk level
            risk_level = self._determine_risk_level(risk_score)
            
            # Create portfolio risk object
            portfolio_risk = PortfolioRisk(
                total_exposure=total_exposure,
                portfolio_var=portfolio_var,
                max_drawdown=max_drawdown,
                correlation_risk=correlation_risk,
                concentration_risk=concentration_risk,
                leverage_ratio=leverage_ratio,
                risk_score=risk_score,
                risk_level=risk_level
            )
            
            self.portfolio_risk = portfolio_risk
            
            result = {
                "status": "success",
                "total_positions": len(portfolio_data),
                "risk_assessment": asdict(portfolio_risk),
                "risk_breakdown": {
                    "market_risk": portfolio_var / total_exposure if total_exposure > 0 else 0,
                    "concentration_risk": concentration_risk,
                    "correlation_risk": correlation_risk,
                    "leverage_risk": min(1.0, leverage_ratio / self.max_leverage)
                },
                "risk_limits": {
                    "max_portfolio_risk": self.max_portfolio_risk,
                    "max_correlation": self.max_correlation,
                    "max_concentration": self.max_concentration,
                    "max_leverage": self.max_leverage
                }
            }
            
            self.logger.info(f"Portfolio risk calculated - Level: {risk_level.value}, Score: {risk_score:.2f}")
            return result
            
        except Exception as e:
            self.logger.error(f"Portfolio risk calculation error: {e}")
            return {"status": "error", "error": str(e)}

    async def assess_position_risks(self) -> Dict[str, Any]:
        """
        Assess risk for individual positions
        
        Returns:
            Dict containing position risk assessments
        """
        try:
            self.logger.info("🎯 Assessing position risks...")
            
            # Get current positions
            positions_data = await self._get_positions_data()
            
            if not positions_data:
                return {"status": "no_data", "positions": {}}
            
            position_assessments = {}
            high_risk_positions = []
            
            for symbol, position_data in positions_data.items():
                # Calculate position-specific risks
                position_risk = await self._calculate_position_risk(symbol, position_data)
                
                position_assessments[symbol] = asdict(position_risk)
                self.position_risks[symbol] = position_risk
                
                # Track high-risk positions
                if position_risk.risk_score > 0.8:
                    high_risk_positions.append(symbol)
            
            # Calculate position risk summary
            risk_scores = [p.risk_score for p in self.position_risks.values()]
            avg_position_risk = np.mean(risk_scores) if risk_scores else 0
            max_position_risk = max(risk_scores) if risk_scores else 0
            
            result = {
                "status": "success",
                "total_positions": len(positions_data),
                "position_assessments": position_assessments,
                "risk_summary": {
                    "average_position_risk": round(avg_position_risk, 3),
                    "maximum_position_risk": round(max_position_risk, 3),
                    "high_risk_positions": high_risk_positions,
                    "positions_at_risk": len(high_risk_positions)
                },
                "position_limits": {
                    "max_position_risk": self.max_position_risk,
                    "risk_threshold": 0.8
                }
            }
            
            self.logger.info(f"Position risks assessed - {len(high_risk_positions)} high-risk positions")
            return result
            
        except Exception as e:
            self.logger.error(f"Position risk assessment error: {e}")
            return {"status": "error", "error": str(e)}

    async def generate_risk_alerts(self) -> Dict[str, Any]:
        """
        Generate risk alerts based on current conditions
        
        Returns:
            Dict containing generated risk alerts
        """
        try:
            self.logger.info("🚨 Generating risk alerts...")
            
            new_alerts = []
            
            # Portfolio-level alerts
            if self.portfolio_risk:
                portfolio_alerts = self._check_portfolio_alerts(self.portfolio_risk)
                new_alerts.extend(portfolio_alerts)
            
            # Position-level alerts
            for symbol, position_risk in self.position_risks.items():
                position_alerts = self._check_position_alerts(symbol, position_risk)
                new_alerts.extend(position_alerts)
            
            # Market condition alerts
            market_alerts = await self._check_market_alerts()
            new_alerts.extend(market_alerts)
            
            # Update active alerts
            self.active_alerts = new_alerts
            
            # Categorize alerts by severity
            alert_categories = {
                'critical': [a for a in new_alerts if a.risk_level == RiskLevel.CRITICAL],
                'high': [a for a in new_alerts if a.risk_level == RiskLevel.HIGH],
                'moderate': [a for a in new_alerts if a.risk_level == RiskLevel.MODERATE],
                'low': [a for a in new_alerts if a.risk_level == RiskLevel.LOW]
            }
            
            result = {
                "status": "success",
                "total_alerts": len(new_alerts),
                "alerts": [asdict(alert) for alert in new_alerts],
                "alert_summary": {
                    "critical_alerts": len(alert_categories['critical']),
                    "high_alerts": len(alert_categories['high']),
                    "moderate_alerts": len(alert_categories['moderate']),
                    "low_alerts": len(alert_categories['low'])
                },
                "alert_categories": {
                    level: [asdict(alert) for alert in alerts]
                    for level, alerts in alert_categories.items()
                }
            }
            
            self.logger.info(f"Generated {len(new_alerts)} risk alerts")
            return result
            
        except Exception as e:
            self.logger.error(f"Risk alert generation error: {e}")
            return {"status": "error", "error": str(e)}

    async def check_emergency_conditions(self) -> Dict[str, Any]:
        """
        Check for emergency risk conditions
        
        Returns:
            Dict containing emergency status and conditions
        """
        try:
            self.logger.info("🆘 Checking emergency conditions...")
            
            emergency_conditions = []
            previous_emergency_mode = self.emergency_mode
            
            # Check portfolio-level emergencies
            if self.portfolio_risk:
                if self.portfolio_risk.risk_score > 0.95:
                    emergency_conditions.append("Portfolio risk score critically high")
                
                if self.portfolio_risk.portfolio_var > self.max_portfolio_risk * 1.2:
                    emergency_conditions.append("Portfolio VaR exceeds emergency threshold")
                
                if self.portfolio_risk.leverage_ratio > self.max_leverage * 1.5:
                    emergency_conditions.append("Leverage ratio in danger zone")
            
            # Check position-level emergencies
            for symbol, position_risk in self.position_risks.items():
                if position_risk.risk_score > 0.95:
                    emergency_conditions.append(f"Position {symbol} in critical risk state")
                
                if position_risk.unrealized_pnl < -position_risk.market_value * 0.2:
                    emergency_conditions.append(f"Position {symbol} down >20%")
            
            # Check market condition emergencies
            market_emergencies = await self._check_market_emergencies()
            emergency_conditions.extend(market_emergencies)
            
            # Update emergency mode
            self.emergency_mode = len(emergency_conditions) > 0
            
            # Emergency mode change notification
            if self.emergency_mode != previous_emergency_mode:
                if self.emergency_mode:
                    self.logger.warning("🆘 EMERGENCY MODE ACTIVATED")
                else:
                    self.logger.info("✅ Emergency mode deactivated")
            
            result = {
                "emergency_mode": self.emergency_mode,
                "emergency_conditions": emergency_conditions,
                "emergency_count": len(emergency_conditions),
                "mode_changed": self.emergency_mode != previous_emergency_mode,
                "recommended_actions": self._get_emergency_actions(emergency_conditions) if emergency_conditions else []
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Emergency check error: {e}")
            return {"error": str(e)}

    async def execute_risk_actions(self) -> Dict[str, Any]:
        """
        Execute automated risk management actions
        
        Returns:
            Dict containing actions taken
        """
        try:
            self.logger.info("⚡ Executing risk management actions...")
            
            actions_taken = []
            
            # Emergency actions
            if self.emergency_mode:
                emergency_actions = await self._execute_emergency_actions()
                actions_taken.extend(emergency_actions)
            
            # Portfolio rebalancing
            rebalancing_actions = await self._execute_rebalancing_actions()
            actions_taken.extend(rebalancing_actions)
            
            # Position adjustments
            position_actions = await self._execute_position_actions()
            actions_taken.extend(position_actions)
            
            # Update action history
            self.risk_actions_taken.extend(actions_taken)
            
            # Keep only recent actions
            cutoff_time = datetime.now() - timedelta(hours=24)
            self.risk_actions_taken = [
                action for action in self.risk_actions_taken 
                if action.get('timestamp', datetime.min) > cutoff_time
            ]
            
            result = {
                "actions_taken": actions_taken,
                "total_actions": len(actions_taken),
                "emergency_actions": [a for a in actions_taken if a.get('type') == 'emergency'],
                "rebalancing_actions": [a for a in actions_taken if a.get('type') == 'rebalancing'],
                "position_actions": [a for a in actions_taken if a.get('type') == 'position'],
                "recent_actions_24h": len(self.risk_actions_taken)
            }
            
            if actions_taken:
                self.logger.info(f"Executed {len(actions_taken)} risk management actions")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Risk action execution error: {e}")
            return {"error": str(e)}

    async def cleanup(self):
        """Cleanup risk management bot resources"""
        try:
            # Clear cached data
            self.portfolio_risk = None
            self.position_risks.clear()
            self.active_alerts.clear()
            
            # Reset state
            self.emergency_mode = False
            self.last_risk_check = None
            
            self.logger.info("RiskBot cleaned up")
            
        except Exception as e:
            self.logger.error(f"RiskBot cleanup error: {e}")

    # Private helper methods
    
    async def _validate_risk_config(self) -> bool:
        """Validate risk management configuration"""
        try:
            # Check risk limits are reasonable
            if not (0 < self.max_portfolio_risk <= 0.5):
                self.logger.error("Max portfolio risk must be between 0 and 50%")
                return False
            
            if not (0 < self.max_position_risk <= 0.2):
                self.logger.error("Max position risk must be between 0 and 20%")
                return False
            
            if not (0 < self.max_correlation <= 1.0):
                self.logger.error("Max correlation must be between 0 and 100%")
                return False
            
            if not (1.0 <= self.max_leverage <= 10.0):
                self.logger.error("Max leverage must be between 1x and 10x")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Risk config validation error: {e}")
            return False

    async def _get_portfolio_data(self) -> Dict[str, Dict[str, Any]]:
        """Get current portfolio data"""
        # This would typically fetch from a real portfolio API
        # For now, return simulated data
        
        symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'DOTUSDT']
        portfolio_data = {}
        
        for symbol in symbols:
            portfolio_data[symbol] = {
                'symbol': symbol,
                'position_size': np.random.uniform(0.1, 2.0),
                'market_value': np.random.uniform(1000, 10000),
                'unrealized_pnl': np.random.uniform(-500, 1000),
                'entry_price': np.random.uniform(10, 50000),
                'current_price': np.random.uniform(10, 55000),
                'leverage': np.random.uniform(1.0, 3.0)
            }
        
        return portfolio_data

    async def _get_positions_data(self) -> Dict[str, Dict[str, Any]]:
        """Get current positions data"""
        return await self._get_portfolio_data()  # Same data structure for now

    async def _calculate_portfolio_var(self, portfolio_data: Dict[str, Any]) -> float:
        """Calculate portfolio Value at Risk"""
        try:
            total_value = sum(pos.get('market_value', 0) for pos in portfolio_data.values())
            
            # Simplified VaR calculation
            # In practice, this would use historical returns and correlations
            portfolio_volatility = 0.03  # 3% daily volatility assumption
            confidence_multiplier = 1.645  # 95% confidence level
            
            var = total_value * portfolio_volatility * confidence_multiplier
            return var
            
        except Exception as e:
            self.logger.error(f"Portfolio VaR calculation error: {e}")
            return 0.0

    async def _calculate_max_drawdown(self, portfolio_data: Dict[str, Any]) -> float:
        """Calculate maximum drawdown"""
        try:
            # Simplified calculation based on current unrealized P&L
            total_unrealized = sum(pos.get('unrealized_pnl', 0) for pos in portfolio_data.values())
            total_value = sum(pos.get('market_value', 0) for pos in portfolio_data.values())
            
            if total_value > 0:
                current_drawdown = abs(min(0, total_unrealized)) / total_value
                return current_drawdown
            
            return 0.0
            
        except Exception as e:
            self.logger.error(f"Max drawdown calculation error: {e}")
            return 0.0

    async def _calculate_correlation_risk(self, portfolio_data: Dict[str, Any]) -> float:
        """Calculate correlation risk between positions"""
        try:
            symbols = list(portfolio_data.keys())
            
            if len(symbols) < 2:
                return 0.0
            
            # Simplified correlation calculation
            # In practice, this would use historical price correlations
            crypto_symbols = [s for s in symbols if 'USDT' in s]
            if len(crypto_symbols) > 1:
                return 0.6  # Assume 60% correlation for crypto pairs
            
            return 0.3  # Lower correlation for diverse assets
            
        except Exception as e:
            self.logger.error(f"Correlation risk calculation error: {e}")
            return 0.0

    async def _calculate_concentration_risk(self, portfolio_data: Dict[str, Any]) -> float:
        """Calculate concentration risk"""
        try:
            total_value = sum(pos.get('market_value', 0) for pos in portfolio_data.values())
            
            if total_value == 0:
                return 0.0
            
            # Calculate Herfindahl index for concentration
            weights = [pos.get('market_value', 0) / total_value for pos in portfolio_data.values()]
            herfindahl_index = sum(w**2 for w in weights)
            
            return herfindahl_index
            
        except Exception as e:
            self.logger.error(f"Concentration risk calculation error: {e}")
            return 0.0

    async def _calculate_leverage_ratio(self, portfolio_data: Dict[str, Any]) -> float:
        """Calculate average leverage ratio"""
        try:
            leverages = [pos.get('leverage', 1.0) for pos in portfolio_data.values()]
            weights = [pos.get('market_value', 0) for pos in portfolio_data.values()]
            
            if sum(weights) == 0:
                return 1.0
            
            # Calculate weighted average leverage
            weighted_leverage = sum(l * w for l, w in zip(leverages, weights)) / sum(weights)
            return weighted_leverage
            
        except Exception as e:
            self.logger.error(f"Leverage ratio calculation error: {e}")
            return 1.0

    def _calculate_risk_score(self, var: float, drawdown: float, 
                            correlation: float, concentration: float, leverage: float) -> float:
        """Calculate overall risk score"""
        try:
            # Normalize each component to 0-1 scale
            var_score = min(1.0, var / (10000 * self.max_portfolio_risk))
            drawdown_score = min(1.0, drawdown / self.max_portfolio_risk)
            correlation_score = correlation
            concentration_score = min(1.0, concentration / self.max_concentration)
            leverage_score = min(1.0, (leverage - 1) / (self.max_leverage - 1))
            
            # Weighted risk score
            risk_score = (
                var_score * 0.3 +
                drawdown_score * 0.25 +
                correlation_score * 0.2 +
                concentration_score * 0.15 +
                leverage_score * 0.1
            )
            
            return min(1.0, risk_score)
            
        except Exception as e:
            self.logger.error(f"Risk score calculation error: {e}")
            return 0.0

    def _determine_risk_level(self, risk_score: float) -> RiskLevel:
        """Determine risk level from risk score"""
        if risk_score >= 0.9:
            return RiskLevel.CRITICAL
        elif risk_score >= 0.7:
            return RiskLevel.HIGH
        elif risk_score >= 0.4:
            return RiskLevel.MODERATE
        else:
            return RiskLevel.LOW

    async def _calculate_position_risk(self, symbol: str, position_data: Dict[str, Any]) -> PositionRisk:
        """Calculate risk for an individual position"""
        try:
            position_size = position_data.get('position_size', 0)
            market_value = position_data.get('market_value', 0)
            unrealized_pnl = position_data.get('unrealized_pnl', 0)
            entry_price = position_data.get('entry_price', 0)
            current_price = position_data.get('current_price', 0)
            leverage = position_data.get('leverage', 1.0)
            
            # Calculate risk percentage
            risk_percentage = abs(unrealized_pnl) / market_value if market_value > 0 else 0
            
            # Calculate stop loss distance
            if entry_price > 0:
                stop_loss_distance = abs(current_price - entry_price) / entry_price
            else:
                stop_loss_distance = 0
            
            # Calculate position risk score
            risk_factors = [
                min(1.0, risk_percentage / self.max_position_risk),
                min(1.0, stop_loss_distance / 0.1),  # 10% max distance
                min(1.0, (leverage - 1) / (self.max_leverage - 1)),
                min(1.0, market_value / 50000)  # Position size factor
            ]
            
            risk_score = np.mean(risk_factors)
            
            return PositionRisk(
                symbol=symbol,
                position_size=position_size,
                market_value=market_value,
                unrealized_pnl=unrealized_pnl,
                risk_percentage=risk_percentage,
                stop_loss_distance=stop_loss_distance,
                leverage=leverage,
                risk_score=risk_score
            )
            
        except Exception as e:
            self.logger.error(f"Position risk calculation error for {symbol}: {e}")
            return PositionRisk(
                symbol=symbol, position_size=0, market_value=0,
                unrealized_pnl=0, risk_percentage=0, stop_loss_distance=0,
                leverage=1.0, risk_score=0
            )

    def _check_portfolio_alerts(self, portfolio_risk: PortfolioRisk) -> List[RiskAlert]:
        """Check for portfolio-level risk alerts"""
        alerts = []
        
        try:
            # Portfolio risk alert
            if portfolio_risk.risk_score > 0.8:
                alerts.append(RiskAlert(
                    risk_type=RiskType.MARKET,
                    risk_level=RiskLevel.HIGH if portfolio_risk.risk_score < 0.9 else RiskLevel.CRITICAL,
                    symbol=None,
                    description=f"Portfolio risk score high: {portfolio_risk.risk_score:.2%}",
                    current_value=portfolio_risk.risk_score,
                    threshold=0.8,
                    recommended_action="Reduce position sizes or hedge exposure",
                    timestamp=datetime.now(),
                    metadata={"component": "portfolio", "metric": "risk_score"}
                ))
            
            # Concentration alert
            if portfolio_risk.concentration_risk > self.max_concentration * 0.8:
                alerts.append(RiskAlert(
                    risk_type=RiskType.CONCENTRATION,
                    risk_level=RiskLevel.MODERATE,
                    symbol=None,
                    description=f"High concentration risk: {portfolio_risk.concentration_risk:.2%}",
                    current_value=portfolio_risk.concentration_risk,
                    threshold=self.max_concentration * 0.8,
                    recommended_action="Diversify portfolio holdings",
                    timestamp=datetime.now(),
                    metadata={"component": "portfolio", "metric": "concentration"}
                ))
            
            # Correlation alert
            if portfolio_risk.correlation_risk > self.max_correlation * 0.8:
                alerts.append(RiskAlert(
                    risk_type=RiskType.CORRELATION,
                    risk_level=RiskLevel.MODERATE,
                    symbol=None,
                    description=f"High correlation risk: {portfolio_risk.correlation_risk:.2%}",
                    current_value=portfolio_risk.correlation_risk,
                    threshold=self.max_correlation * 0.8,
                    recommended_action="Add uncorrelated assets",
                    timestamp=datetime.now(),
                    metadata={"component": "portfolio", "metric": "correlation"}
                ))
                
        except Exception as e:
            self.logger.error(f"Portfolio alerts check error: {e}")
        
        return alerts

    def _check_position_alerts(self, symbol: str, position_risk: PositionRisk) -> List[RiskAlert]:
        """Check for position-level risk alerts"""
        alerts = []
        
        try:
            # High position risk
            if position_risk.risk_score > 0.8:
                alerts.append(RiskAlert(
                    risk_type=RiskType.POSITION,
                    risk_level=RiskLevel.HIGH if position_risk.risk_score < 0.9 else RiskLevel.CRITICAL,
                    symbol=symbol,
                    description=f"Position {symbol} high risk: {position_risk.risk_score:.2%}",
                    current_value=position_risk.risk_score,
                    threshold=0.8,
                    recommended_action="Consider reducing position size",
                    timestamp=datetime.now(),
                    metadata={"position": symbol, "metric": "risk_score"}
                ))
            
            # High leverage
            if position_risk.leverage > self.max_leverage * 0.8:
                alerts.append(RiskAlert(
                    risk_type=RiskType.LEVERAGE,
                    risk_level=RiskLevel.MODERATE,
                    symbol=symbol,
                    description=f"Position {symbol} high leverage: {position_risk.leverage:.1f}x",
                    current_value=position_risk.leverage,
                    threshold=self.max_leverage * 0.8,
                    recommended_action="Reduce leverage",
                    timestamp=datetime.now(),
                    metadata={"position": symbol, "metric": "leverage"}
                ))
                
        except Exception as e:
            self.logger.error(f"Position alerts check error for {symbol}: {e}")
        
        return alerts

    async def _check_market_alerts(self) -> List[RiskAlert]:
        """Check for market condition alerts"""
        alerts = []
        
        try:
            # Simulated market volatility check
            market_volatility = np.random.uniform(0.02, 0.08)  # 2-8% volatility
            
            if market_volatility > 0.05:  # High volatility
                alerts.append(RiskAlert(
                    risk_type=RiskType.MARKET,
                    risk_level=RiskLevel.MODERATE if market_volatility < 0.07 else RiskLevel.HIGH,
                    symbol=None,
                    description=f"High market volatility detected: {market_volatility:.2%}",
                    current_value=market_volatility,
                    threshold=0.05,
                    recommended_action="Reduce risk exposure",
                    timestamp=datetime.now(),
                    metadata={"component": "market", "metric": "volatility"}
                ))
                
        except Exception as e:
            self.logger.error(f"Market alerts check error: {e}")
        
        return alerts

    async def _check_market_emergencies(self) -> List[str]:
        """Check for market emergency conditions"""
        emergencies = []
        
        try:
            # Simulated market crash detection
            market_drop = np.random.uniform(0, 0.15)  # 0-15% market drop
            
            if market_drop > 0.1:  # 10% market drop
                emergencies.append(f"Market crash detected: {market_drop:.1%} drop")
            
            # Simulated liquidity crisis
            liquidity_ratio = np.random.uniform(0.5, 1.0)
            
            if liquidity_ratio < 0.7:  # Low liquidity
                emergencies.append("Low market liquidity detected")
                
        except Exception as e:
            self.logger.error(f"Market emergencies check error: {e}")
        
        return emergencies

    def _get_overall_risk_level(self) -> str:
        """Get overall risk level for the portfolio"""
        if self.emergency_mode:
            return "CRITICAL"
        elif self.portfolio_risk:
            return self.portfolio_risk.risk_level.value.upper()
        else:
            return "UNKNOWN"

    def _get_emergency_actions(self, emergency_conditions: List[str]) -> List[str]:
        """Get recommended emergency actions"""
        actions = []
        
        for condition in emergency_conditions:
            if "portfolio risk" in condition.lower():
                actions.append("Immediately reduce portfolio exposure")
            elif "leverage" in condition.lower():
                actions.append("Reduce leverage across all positions")
            elif "position" in condition.lower():
                actions.append("Close or reduce high-risk positions")
            elif "market crash" in condition.lower():
                actions.append("Activate emergency stops")
            elif "liquidity" in condition.lower():
                actions.append("Maintain cash reserves")
        
        return list(set(actions))  # Remove duplicates

    async def _execute_emergency_actions(self) -> List[Dict[str, Any]]:
        """Execute emergency risk management actions"""
        actions = []
        
        try:
            if self.emergency_mode and self.portfolio_risk:
                # Emergency position reduction
                if self.portfolio_risk.risk_score > 0.95:
                    actions.append({
                        "type": "emergency",
                        "action": "position_reduction",
                        "description": "Emergency 50% position reduction",
                        "timestamp": datetime.now(),
                        "reason": "Critical risk level reached"
                    })
                
                # Emergency leverage reduction
                if self.portfolio_risk.leverage_ratio > self.max_leverage:
                    actions.append({
                        "type": "emergency",
                        "action": "leverage_reduction",
                        "description": "Emergency leverage reduction to 1x",
                        "timestamp": datetime.now(),
                        "reason": "Leverage limit exceeded"
                    })
                    
        except Exception as e:
            self.logger.error(f"Emergency actions execution error: {e}")
        
        return actions

    async def _execute_rebalancing_actions(self) -> List[Dict[str, Any]]:
        """Execute portfolio rebalancing actions"""
        actions = []
        
        try:
            if self.portfolio_risk and self.portfolio_risk.concentration_risk > self.max_concentration:
                actions.append({
                    "type": "rebalancing",
                    "action": "portfolio_rebalancing",
                    "description": "Rebalance to reduce concentration",
                    "timestamp": datetime.now(),
                    "reason": "Concentration limit exceeded"
                })
                
        except Exception as e:
            self.logger.error(f"Rebalancing actions execution error: {e}")
        
        return actions

    async def _execute_position_actions(self) -> List[Dict[str, Any]]:
        """Execute position-level risk actions"""
        actions = []
        
        try:
            for symbol, position_risk in self.position_risks.items():
                if position_risk.risk_score > 0.9:
                    actions.append({
                        "type": "position",
                        "action": "position_reduction",
                        "symbol": symbol,
                        "description": f"Reduce {symbol} position by 25%",
                        "timestamp": datetime.now(),
                        "reason": "High position risk"
                    })
                    
        except Exception as e:
            self.logger.error(f"Position actions execution error: {e}")
        
        return actions

    async def _save_risk_assessment(self, assessment: Dict[str, Any]):
        """Save risk assessment to file"""
        try:
            results_dir = Path("data/risk")
            results_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_file = results_dir / f"risk_assessment_{timestamp}.json"
            
            with open(results_file, 'w') as f:
                json.dump(assessment, f, indent=2, default=str)
            
            # Add to history
            self.risk_history.append(assessment)
            
            # Keep only recent history
            if len(self.risk_history) > 100:
                self.risk_history = self.risk_history[-100:]
            
            self.logger.info(f"Risk assessment saved: {results_file}")
            
        except Exception as e:
            self.logger.error(f"Risk assessment saving error: {e}")


# Register the risk bot
from . import register_system_bot
register_system_bot("risk", RiskBot)
