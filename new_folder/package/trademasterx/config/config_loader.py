"""
TradeMasterX 2.0 - Configuration Management
Centralized configuration loading with YAML support and environment variable integration.
"""

import os
import yaml
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union, Tuple, List
from dataclasses import dataclass
from dotenv import load_dotenv


@dataclass
class DatabaseConfig:
    """Database configuration"""
    trades_db: str
    models_db: str
    monitoring_db: str
    
    
@dataclass
class APIConfig:
    """API configuration"""
    api_key: str
    api_secret: str
    base_url: str
    testnet: bool = True


@dataclass
class TradingConfig:
    """Trading configuration"""
    symbols: list
    position_size: float
    max_position_size: float
    stop_loss_percentage: float
    take_profit_percentage: float
    initial_confidence_threshold: float


@dataclass
class PathsConfig:
    """Paths configuration"""
    data: str
    models: str
    reports: str
    logs: str


class ConfigLoader:
    """
    Centralized configuration loader with support for:
    - YAML configuration files
    - Environment variable override
    - Configuration validation
    - Default fallbacks
    """
    
    def __init__(self):
        self.logger = logging.getLogger("ConfigLoader")
        
        # Load environment variables
        load_dotenv()
        
        # Configuration cache
        self._config_cache: Dict[str, Any] = {}
        
        self.logger.info("ConfigLoader initialized")

    def get_config(self, config_type: str, default: Any = None) -> Any:
        """
        Generic config getter for tests and general use
        
        Args:
            config_type: Type of config ('system', 'bots', 'strategies', 'api')
            default: Default value if config not found
            
        Returns:
            Configuration data or default value
        """
        try:
            if config_type == 'system':
                return self.load_system_config()
            elif config_type == 'bots':
                return self.load_bot_config()
            elif config_type == 'strategies':
                return self.load_strategy_config()
            elif config_type == 'api':
                return self.get_api_config()
            else:
                self.logger.warning(f"Unknown config type: {config_type}")
                return default
        except Exception as e:
            self.logger.error(f"Failed to get config {config_type}: {e}")
            return default

    def load_system_config(self, config_path: str = "config/system.yaml") -> Dict[str, Any]:
        """Load main system configuration"""
        if config_path in self._config_cache:
            return self._config_cache[config_path]
        
        try:
            config = self._load_yaml_file(config_path)
            
            if not config:
                self.logger.warning(f"Config file not found: {config_path}, using defaults")
                config = self._get_default_system_config()
            
            # Apply environment variable overrides
            config = self._apply_env_overrides(config)
            
            # Validate configuration
            self._validate_system_config(config)
            
            # Cache configuration
            self._config_cache[config_path] = config
            
            self.logger.info(f"System configuration loaded: {config_path}")
            return config
            
        except Exception as e:
            self.logger.error(f"Failed to load system config: {e}")
            return self._get_default_system_config()

    def load_bot_config(self, config_path: str = "config/bots.yaml") -> Dict[str, Any]:
        """Load bot-specific configuration"""
        if config_path in self._config_cache:
            return self._config_cache[config_path]
        
        try:
            config = self._load_yaml_file(config_path)
            
            if not config:
                self.logger.warning(f"Bot config file not found: {config_path}, using defaults")
                config = self._get_default_bot_config()
            
            # Apply environment variable overrides
            config = self._apply_env_overrides(config)
            
            # Cache configuration
            self._config_cache[config_path] = config
            
            self.logger.info(f"Bot configuration loaded: {config_path}")
            return config
            
        except Exception as e:
            self.logger.error(f"Failed to load bot config: {e}")
            return self._get_default_bot_config()

    def load_strategy_config(self, config_path: str = "config/strategies.yaml") -> Dict[str, Any]:
        """Load strategy-specific configuration"""
        if config_path in self._config_cache:
            return self._config_cache[config_path]
        
        try:
            config = self._load_yaml_file(config_path)
            
            if not config:
                self.logger.warning(f"Strategy config file not found: {config_path}, using defaults")
                config = self._get_default_strategy_config()
            
            # Cache configuration
            self._config_cache[config_path] = config
            
            self.logger.info(f"Strategy configuration loaded: {config_path}")
            return config
            
        except Exception as e:
            self.logger.error(f"Failed to load strategy config: {e}")
            return self._get_default_strategy_config()

    def load_phase_10_config(self, config_path: str = "config/phase_10.yaml") -> Dict[str, Any]:
        """Load Phase 10 specific configuration"""
        if config_path in self._config_cache:
            return self._config_cache[config_path]
        
        try:
            config = self._load_yaml_file(config_path)
            
            if not config:
                self.logger.warning(f"Phase 10 config file not found: {config_path}, using defaults")
                config = self._get_default_phase_10_config()
            
            # Apply environment variable overrides
            config = self._apply_env_overrides(config)
            
            # Merge with system config for safety settings
            system_config = self.load_system_config()
            
            # Ensure safety settings are respected
            config['safety'] = {
                **config.get('safety', {}),
                'demo_mode': system_config.get('trading_mode', {}).get('DEMO_MODE', True),
                'mainnet_demo': system_config.get('trading_mode', {}).get('mainnet_demo', False)
            }
            
            # Cache configuration
            self._config_cache[config_path] = config
            
            self.logger.info(f"Phase 10 configuration loaded: {config_path}")
            return config
            
        except Exception as e:
            self.logger.error(f"Failed to load Phase 10 config: {e}")
            return self._get_default_phase_10_config()
            
    def _load_yaml_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Load YAML configuration file"""
        path = Path(file_path)
        
        if not path.exists():
            return None
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except yaml.YAMLError as e:
            self.logger.error(f"YAML parsing error in {file_path}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error reading {file_path}: {e}")
            return None

    def _apply_env_overrides(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply environment variable overrides"""
        # API Keys
        if os.getenv('BYBIT_API_KEY'):
            config.setdefault('api', {})['api_key'] = os.getenv('BYBIT_API_KEY')
        
        if os.getenv('BYBIT_API_SECRET'):
            config.setdefault('api', {})['api_secret'] = os.getenv('BYBIT_API_SECRET')
        
        if os.getenv('BYBIT_TESTNET'):
            config.setdefault('api', {})['testnet'] = os.getenv('BYBIT_TESTNET').lower() == 'true'
        
        # Trading settings
        if os.getenv('POSITION_SIZE'):
            config.setdefault('trading', {})['position_size'] = float(os.getenv('POSITION_SIZE'))
        
        if os.getenv('CONFIDENCE_THRESHOLD'):
            config.setdefault('trading', {})['initial_confidence_threshold'] = float(os.getenv('CONFIDENCE_THRESHOLD'))
        
        # Session settings
        if os.getenv('SESSION_DURATION_HOURS'):
            config['session_duration_hours'] = int(os.getenv('SESSION_DURATION_HOURS'))
        
        return config

    def _validate_system_config(self, config: Dict[str, Any]):
        """Validate system configuration"""
        required_sections = ['intervals', 'paths', 'api', 'trading']
        
        for section in required_sections:
            if section not in config:
                raise ValueError(f"Missing required config section: {section}")
        
        # Validate intervals
        intervals = config['intervals']
        required_intervals = ['trade_seconds', 'analytics_minutes', 'monitoring_minutes']
        
        for interval in required_intervals:
            if interval not in intervals or intervals[interval] <= 0:
                raise ValueError(f"Invalid interval configuration: {interval}")
        
        # Validate API config
        api_config = config['api']
        if not api_config.get('api_key') or not api_config.get('api_secret'):
            self.logger.warning("API credentials not configured - testnet features may be limited")

    def _get_default_system_config(self) -> Dict[str, Any]:
        """Get default system configuration"""
        return {
            "session_duration_hours": 168,  # 7 days
            "intervals": {
                "trade_seconds": 30,
                "analytics_minutes": 5,
                "strategy_minutes": 60,
                "monitoring_minutes": 10,
                "reporting_hours": 24
            },
            "api": {
                "api_key": os.getenv('BYBIT_API_KEY', ''),
                "api_secret": os.getenv('BYBIT_API_SECRET', ''),
                "base_url": "https://api-testnet.bybit.com",
                "testnet": True
            },
            "trading": {
                "symbols": ["BTCUSDT", "ETHUSDT", "ADAUSDT"],
                "position_size": 0.01,
                "max_position_size": 0.05,
                "stop_loss_percentage": 0.02,
                "take_profit_percentage": 0.03,
                "initial_confidence_threshold": 0.75
            },
            "paths": {
                "data": "data",
                "models": "models",
                "reports": "reports",
                "logs": "logs"
            },
            "database": {
                "trades_db": "data/trades.db",
                "models_db": "data/models.db",
                "monitoring_db": "data/monitoring.db"
            },
            "scoring": {
                "weights": {
                    "win_rate": 25,
                    "sharpe_ratio": 20,
                    "prediction_accuracy": 20,
                    "drawdown_control": 15,
                    "api_reliability": 10,
                    "retraining_success": 10
                },
                "thresholds": {
                    "win_rate": 0.55,
                    "sharpe_ratio": 1.0,
                    "prediction_accuracy": 0.70,
                    "max_drawdown": 0.15,
                    "api_reliability": 0.95,
                    "retraining_success": 0.80,
                    "live_trading_score": 90.0
                }
            }
        }

    def _get_default_bot_config(self) -> Dict[str, Any]:
        """Get default bot configuration"""
        return {
            "global": {
                "log_level": "INFO",
                "max_retries": 3,
                "timeout_seconds": 30
            },
            "bots": {
                "market_analysis": {
                    "enabled": True,
                    "data_sources": ["bybit", "binance"],
                    "analysis_window_hours": 24,
                    "indicators": ["sma", "ema", "rsi", "macd", "bollinger"]
                },
                "sentiment": {
                    "enabled": True,
                    "sources": ["twitter", "reddit", "news"],
                    "update_interval_minutes": 15,
                    "sentiment_weight": 0.3
                },
                "strategy": {
                    "enabled": True,
                    "strategy_types": ["momentum", "mean_reversion", "breakout"],
                    "rebalance_interval_hours": 6,
                    "max_concurrent_positions": 3
                },
                "risk": {
                    "enabled": True,
                    "max_daily_loss": 0.05,
                    "position_limit": 0.1,
                    "correlation_threshold": 0.8,
                    "volatility_limit": 0.3
                },
                "memory": {
                    "enabled": True,
                    "retention_days": 30,
                    "cleanup_interval_hours": 24,
                    "max_memory_usage_gb": 2
                },
                "logger": {
                    "enabled": True,
                    "log_rotation_mb": 100,
                    "backup_count": 10,
                    "log_format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                }
            }
        }

    def _get_default_strategy_config(self) -> Dict[str, Any]:
        """Get default strategy configuration"""
        return {
            "strategies": {
                "momentum": {
                    "enabled": True,
                    "parameters": {
                        "lookback_periods": 14,
                        "momentum_threshold": 0.02,
                        "entry_confidence": 0.7,
                        "exit_confidence": 0.3
                    },
                    "weight": 0.4
                },
                "mean_reversion": {
                    "enabled": True,
                    "parameters": {
                        "zscore_threshold": 2.0,
                        "lookback_periods": 20,
                        "entry_confidence": 0.8,
                        "exit_confidence": 0.2
                    },
                    "weight": 0.3
                },
                "breakout": {
                    "enabled": True,
                    "parameters": {
                        "breakout_threshold": 0.015,
                        "volume_confirmation": True,
                        "entry_confidence": 0.75,
                        "exit_confidence": 0.25
                    },
                    "weight": 0.3
                }
            },
            "risk_management": {
                "position_sizing": {
                    "method": "kelly",
                    "max_position_size": 0.05,
                    "min_position_size": 0.001
                },
                "stop_loss": {
                    "method": "atr",
                    "multiplier": 2.0,
                    "max_loss": 0.02
                },
                "take_profit": {
                    "method": "risk_reward",
                    "ratio": 2.0,
                    "trailing": True
                }
            }
        }

    def _get_default_phase_10_config(self) -> Dict[str, Any]:
        """Get default Phase 10 configuration"""
        return {
            'learning': {
                'trade_frequency': 30,
                'retrain_interval': 43200,  # 12 hours
                'weekly_report': True,
                'top_bot_threshold': 0.7,
                'history_window': 168  # 7 days in hours
            },
            'safety': {
                'confidence_threshold': 0.80,
                'min_return_threshold': 0.15,
                'max_position_size': 1000,
                'demo_mode': True,
                'mainnet_demo': True
            },
            'reporting': {
                'formats': ['json', 'csv'],
                'include': {
                    'bot_performance': True,
                    'trade_details': True,
                    'market_conditions': True
                }
            }
        }

    def get_api_config(self) -> APIConfig:
        """Get structured API configuration"""
        config = self.load_system_config()
        api_config = config.get('api', {})
        
        return APIConfig(
            api_key=api_config.get('api_key', ''),
            api_secret=api_config.get('api_secret', ''),
            base_url=api_config.get('base_url', 'https://api-testnet.bybit.com'),
            testnet=api_config.get('testnet', True)
        )

    def get_trading_config(self) -> TradingConfig:
        """Get structured trading configuration"""
        config = self.load_system_config()
        trading_config = config.get('trading', {})
        
        return TradingConfig(
            symbols=trading_config.get('symbols', ['BTCUSDT']),
            position_size=trading_config.get('position_size', 0.01),
            max_position_size=trading_config.get('max_position_size', 0.05),
            stop_loss_percentage=trading_config.get('stop_loss_percentage', 0.02),
            take_profit_percentage=trading_config.get('take_profit_percentage', 0.03),
            initial_confidence_threshold=trading_config.get('initial_confidence_threshold', 0.75)
        )

    def get_paths_config(self) -> PathsConfig:
        """Get structured paths configuration"""
        config = self.load_system_config()
        paths_config = config.get('paths', {})
        
        return PathsConfig(
            data=paths_config.get('data', 'data'),
            models=paths_config.get('models', 'models'),
            reports=paths_config.get('reports', 'reports'),
            logs=paths_config.get('logs', 'logs')
        )

    def get_database_config(self) -> DatabaseConfig:
        """Get structured database configuration"""
        config = self.load_system_config()
        db_config = config.get('database', {})
        
        return DatabaseConfig(
            trades_db=db_config.get('trades_db', 'data/trades.db'),
            models_db=db_config.get('models_db', 'data/models.db'),
            monitoring_db=db_config.get('monitoring_db', 'data/monitoring.db')
        )

    def save_config(self, config: Dict[str, Any], file_path: str):
        """Save configuration to YAML file"""
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'w', encoding='utf-8') as f:            yaml.dump(config, f, default_flow_style=False, indent=2)
            
            # Clear cache for this file
            if file_path in self._config_cache:
                del self._config_cache[file_path]
                
            self.logger.info(f"Configuration saved: {file_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to save config to {file_path}: {e}")
            raise
            
    def reload_config(self, config_path: str) -> Dict[str, Any]:
        """Reload configuration from file"""
        # Clear cache
        if config_path in self._config_cache:
            del self._config_cache[config_path]
        
        # Reload based on config type
        if 'system' in config_path:
            return self.load_system_config(config_path)
        elif 'bot' in config_path:
            return self.load_bot_config(config_path)
        elif 'strateg' in config_path:
            return self.load_strategy_config(config_path)
        else:
            raise ValueError(f"Unknown config type: {config_path}")
            
    def load_yaml_config(self, file_path: str) -> Dict[str, Any]:
        """Load any YAML configuration file
        
        Args:
            file_path: Path to the YAML configuration file
            
        Returns:
            Dictionary containing configuration data
            
        Raises:
            FileNotFoundError: If the configuration file doesn't exist
            ValueError: If the configuration file is invalid
        """
        # Check cache first
        if file_path in self._config_cache:
            self.logger.debug(f"Using cached config for {file_path}")
            return self._config_cache[file_path]
            
        # Load the YAML file
        config = self._load_yaml_file(file_path)
        
        if config is None:
            raise FileNotFoundError(f"Configuration file not found or invalid: {file_path}")
            
        # Apply environment overrides
        config = self._apply_env_overrides(config)
        
        # Cache the config
        self._config_cache[file_path] = config
        
        self.logger.info(f"YAML configuration loaded: {file_path}")
        return config

    def clear_cache(self):
        """Clear configuration cache"""
        self._config_cache.clear()
        self.logger.info("Configuration cache cleared")

    def validate_config_file(self, file_path: str) -> Tuple[bool, List[str]]:
        """Validate configuration file"""
        errors = []
        
        try:
            config = self._load_yaml_file(file_path)
            
            if config is None:
                errors.append(f"Could not load file: {file_path}")
                return False, errors
            
            # Basic structure validation
            if 'system' in file_path:
                self._validate_system_config(config)
            
            return True, []
            
        except Exception as e:
            errors.append(str(e))
            return False, errors
