"""
TradeMasterX 2.0 - Phase 11: Intelligent Optimization Configuration
Centralized configuration for all Phase 11 components
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
import json
from pathlib import Path

@dataclass
class Phase11Config:
    """
    Phase 11 Intelligent Optimization Configuration
    
    Centralizes all configuration settings for the self-improving intelligence layer
    """
    
    # Controller Settings
    optimization_interval_seconds: int = 300  # 5 minutes
    dashboard_update_interval_seconds: int = 60  # 1 minute
    anomaly_check_interval_seconds: int = 30  # 30 seconds
    strategy_evaluation_interval_seconds: int = 600  # 10 minutes
    bot_scoring_interval_seconds: int = 180  # 3 minutes
    max_optimization_cycles: Optional[int] = None  # No limit
    
    # Component Toggles
    enable_auto_switching: bool = True
    enable_anomaly_detection: bool = True
    enable_dashboard: bool = True
    enable_strategy_reinforcement: bool = True
    enable_bot_scoring: bool = True
    
    # AdaptiveStrategyReinforcer Settings
    reinforcement_learning_rate: float = 0.1
    reinforcement_decay_rate: float = 0.95
    reinforcement_min_trades: int = 10
    reinforcement_max_weight_change: float = 0.2
    reinforcement_confidence_threshold: float = 0.6
    
    # BotPerformanceScorer Settings
    bot_scoring_window_hours: int = 24
    bot_min_predictions: int = 5
    bot_reliability_threshold: float = 0.7
    bot_performance_weights: Dict[str, float] = None
    
    # StrategySwitcher Settings
    strategy_switch_threshold: float = 0.6
    strategy_cooldown_minutes: int = 30
    strategy_min_performance_window: int = 20
    strategy_max_switches_per_day: int = 10
    strategy_performance_lookback_hours: int = 6
    
    # AnomalyDetector Settings
    anomaly_sensitivity: float = 2.0  # Standard deviations
    anomaly_min_samples: int = 30
    anomaly_pattern_window_hours: int = 24
    anomaly_auto_adjust_baseline: bool = True
    anomaly_alert_threshold: int = 3  # Consecutive anomalies
    
    # LiveOptimizationDashboard Settings
    dashboard_port: int = 8765
    dashboard_host: str = "localhost"
    dashboard_max_connections: int = 10
    dashboard_data_retention_hours: int = 168  # 1 week
    dashboard_alert_levels: Dict[str, str] = None
    
    # Integration Settings
    phase10_integration: bool = True
    web_dashboard_integration: bool = True
    export_metrics_enabled: bool = True
    export_format: str = "json"  # json, csv, both
    
    # Performance Settings
    max_concurrent_trades: int = 100
    memory_limit_mb: int = 512
    log_level: str = "INFO"
    enable_profiling: bool = False
    
    def __post_init__(self):
        """Initialize default values for complex fields"""
        if self.bot_performance_weights is None:
            self.bot_performance_weights = {
                'accuracy': 0.4,
                'confidence_calibration': 0.3,
                'consistency': 0.2,
                'responsiveness': 0.1
            }
        
        if self.dashboard_alert_levels is None:
            self.dashboard_alert_levels = {
                'info': '#17a2b8',
                'warning': '#ffc107',
                'error': '#dc3545',
                'critical': '#6f42c1'
            }
    
    @classmethod
    def from_file(cls, config_path: str) -> 'Phase11Config':
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)
            return cls(**config_data)
        except FileNotFoundError:
            # Return default config if file doesn't exist
            return cls()
        except Exception as e:
            raise ValueError(f"Error loading config from {config_path}: {e}")
    
    def to_file(self, config_path: str):
        """Save configuration to JSON file"""
        config_dict = self.to_dict()
        Path(config_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(config_dict, f, indent=2)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'optimization_interval_seconds': self.optimization_interval_seconds,
            'dashboard_update_interval_seconds': self.dashboard_update_interval_seconds,
            'anomaly_check_interval_seconds': self.anomaly_check_interval_seconds,
            'strategy_evaluation_interval_seconds': self.strategy_evaluation_interval_seconds,
            'bot_scoring_interval_seconds': self.bot_scoring_interval_seconds,
            'max_optimization_cycles': self.max_optimization_cycles,
            'enable_auto_switching': self.enable_auto_switching,
            'enable_anomaly_detection': self.enable_anomaly_detection,
            'enable_dashboard': self.enable_dashboard,
            'enable_strategy_reinforcement': self.enable_strategy_reinforcement,
            'enable_bot_scoring': self.enable_bot_scoring,
            'reinforcement_learning_rate': self.reinforcement_learning_rate,
            'reinforcement_decay_rate': self.reinforcement_decay_rate,
            'reinforcement_min_trades': self.reinforcement_min_trades,
            'reinforcement_max_weight_change': self.reinforcement_max_weight_change,
            'reinforcement_confidence_threshold': self.reinforcement_confidence_threshold,
            'bot_scoring_window_hours': self.bot_scoring_window_hours,
            'bot_min_predictions': self.bot_min_predictions,
            'bot_reliability_threshold': self.bot_reliability_threshold,
            'bot_performance_weights': self.bot_performance_weights,
            'strategy_switch_threshold': self.strategy_switch_threshold,
            'strategy_cooldown_minutes': self.strategy_cooldown_minutes,
            'strategy_min_performance_window': self.strategy_min_performance_window,
            'strategy_max_switches_per_day': self.strategy_max_switches_per_day,
            'strategy_performance_lookback_hours': self.strategy_performance_lookback_hours,
            'anomaly_sensitivity': self.anomaly_sensitivity,
            'anomaly_min_samples': self.anomaly_min_samples,
            'anomaly_pattern_window_hours': self.anomaly_pattern_window_hours,
            'anomaly_auto_adjust_baseline': self.anomaly_auto_adjust_baseline,
            'anomaly_alert_threshold': self.anomaly_alert_threshold,
            'dashboard_port': self.dashboard_port,
            'dashboard_host': self.dashboard_host,
            'dashboard_max_connections': self.dashboard_max_connections,
            'dashboard_data_retention_hours': self.dashboard_data_retention_hours,
            'dashboard_alert_levels': self.dashboard_alert_levels,
            'phase10_integration': self.phase10_integration,
            'web_dashboard_integration': self.web_dashboard_integration,
            'export_metrics_enabled': self.export_metrics_enabled,
            'export_format': self.export_format,
            'max_concurrent_trades': self.max_concurrent_trades,
            'memory_limit_mb': self.memory_limit_mb,
            'log_level': self.log_level,
            'enable_profiling': self.enable_profiling
        }
    
    def update(self, **kwargs):
        """Update configuration with new values"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise ValueError(f"Unknown configuration parameter: {key}")
    
    def validate(self) -> bool:
        """Validate configuration values"""
        errors = []
        
        # Validate intervals
        if self.optimization_interval_seconds < 60:
            errors.append("optimization_interval_seconds must be at least 60")
        
        if self.dashboard_update_interval_seconds < 10:
            errors.append("dashboard_update_interval_seconds must be at least 10")
        
        # Validate thresholds
        if not 0 <= self.reinforcement_learning_rate <= 1:
            errors.append("reinforcement_learning_rate must be between 0 and 1")
        
        if not 0 <= self.bot_reliability_threshold <= 1:
            errors.append("bot_reliability_threshold must be between 0 and 1")
        
        if not 0 <= self.strategy_switch_threshold <= 1:
            errors.append("strategy_switch_threshold must be between 0 and 1")
        
        if self.anomaly_sensitivity < 0.5:
            errors.append("anomaly_sensitivity must be at least 0.5")
        
        # Validate weights
        if abs(sum(self.bot_performance_weights.values()) - 1.0) > 0.01:
            errors.append("bot_performance_weights must sum to 1.0")
        
        if errors:
            raise ValueError(f"Configuration validation errors: {'; '.join(errors)}")
        
        return True

# Default configuration instances for different environments
DEVELOPMENT_CONFIG = Phase11Config(
    optimization_interval_seconds=60,  # Faster for testing
    dashboard_update_interval_seconds=30,
    anomaly_check_interval_seconds=15,
    log_level="DEBUG",
    enable_profiling=True
)

PRODUCTION_CONFIG = Phase11Config(
    optimization_interval_seconds=300,  # Standard 5 minutes
    dashboard_update_interval_seconds=60,
    anomaly_check_interval_seconds=30,
    log_level="INFO",
    enable_profiling=False,
    memory_limit_mb=1024
)

TESTING_CONFIG = Phase11Config(
    optimization_interval_seconds=10,  # Very fast for unit tests
    dashboard_update_interval_seconds=5,
    anomaly_check_interval_seconds=2,
    max_optimization_cycles=5,  # Limited cycles for testing
    log_level="DEBUG",
    enable_profiling=True
)
