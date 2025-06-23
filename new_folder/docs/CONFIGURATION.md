# Configuration Guide

## Overview

TradeMasterX 2.0 uses a hierarchical configuration system that supports multiple formats and sources. The system prioritizes configurations in the following order:

1. Environment variables
2. Command-line arguments
3. YAML configuration files
4. JSON configuration files
5. Default values

## Configuration Files

### System Configuration (config/system.yaml)

```yaml
# System-wide configuration
system:
  name: "TradeMasterX"
  version: "2.0"
  debug: false
  log_level: "INFO"
  
  # Working directories
  data_dir: "data"
  logs_dir: "logs"
  reports_dir: "reports"
  
  # Performance settings
  max_workers: 4
  memory_limit_mb: 1024
  cpu_limit_percent: 50

# Master bot configuration
master_bot:
  monitoring_interval: 5              # seconds
  max_concurrent_bots: 10
  auto_restart_failed_bots: true
  health_check_interval: 30           # seconds
  
  # Resource limits
  resource_limits:
    memory_mb: 512
    cpu_percent: 25
    max_file_handles: 1000

# API configuration
api:
  rate_limit: 100                     # requests per minute
  timeout: 30                         # seconds
  max_payload_size: "10MB"
  cors_enabled: true
  cors_origins: ["*"]

# Database configuration
database:
  type: "sqlite"                      # sqlite, postgresql, mysql
  path: "data/trademasterx.db"        # for SQLite
  # For PostgreSQL/MySQL:
  # host: "localhost"
  # port: 5432
  # username: "trademasterx"
  # password: "password"
  # database: "trademasterx"
  
  # Connection pool settings
  pool_size: 10
  max_overflow: 20
  pool_timeout: 30

# Cache configuration
cache:
  type: "memory"                      # memory, redis
  # For Redis:
  # redis_url: "redis://localhost:6379/0"
  # redis_password: "password"
  
  # Cache settings
  default_ttl: 3600                   # seconds
  max_size_mb: 256
  cleanup_interval: 300               # seconds

# Logging configuration
logging:
  level: "INFO"                       # DEBUG, INFO, WARN, ERROR
  format: "structured"                # simple, structured, json
  
  # Output configuration
  console_enabled: true
  file_enabled: true
  database_enabled: true
  
  # File logging
  file_path: "logs/trademasterx.log"
  max_file_size_mb: 100
  backup_count: 5
  
  # Log retention
  retention_days: 30
  compression_enabled: true

# Security configuration
security:
  secret_key: "${SECRET_KEY}"         # Environment variable
  jwt_secret: "${JWT_SECRET}"
  session_timeout: 3600               # seconds
  
  # API security
  api_key_required: true
  rate_limiting_enabled: true
  
  # Encryption
  encryption_enabled: true
  encryption_algorithm: "AES-256-GCM"

# Monitoring configuration
monitoring:
  enabled: true
  interval: 10                        # seconds
  metrics_retention_days: 7
  
  # System metrics
  system_metrics_enabled: true
  performance_metrics_enabled: true
  business_metrics_enabled: true
  
  # Alerting
  alerting_enabled: true
  alert_channels: ["email", "webhook"]
  
# Notification configuration
notifications:
  email:
    enabled: false
    smtp_host: "smtp.gmail.com"
    smtp_port: 587
    username: "${EMAIL_USERNAME}"
    password: "${EMAIL_PASSWORD}"
    from_address: "noreply@trademasterx.com"
    
  webhook:
    enabled: false
    url: "${WEBHOOK_URL}"
    timeout: 10
    retry_count: 3

# Development settings
development:
  auto_reload: true
  debug_toolbar: false
  profiling_enabled: false
  test_mode: false
```

### Bot Configuration (config/bots.yaml)

```yaml
# Analytics bot configuration
analytics:
  enabled: true
  auto_start: true
  instances: 1
  
  config:
    # Pattern analysis settings
    pattern_analysis:
      window_size: 100
      confidence_threshold: 0.7
      min_occurrences: 5
      patterns_to_track:
        - "head_and_shoulders"
        - "support_resistance"
        - "trend_lines"
        - "triangles"
      
    # Signal analysis settings
    signal_analysis:
      tracking_period: 24             # hours
      accuracy_threshold: 0.6
      min_confidence: 0.5
      signal_types:
        - "buy"
        - "sell"
        - "hold"
      
    # Performance tracking
    performance:
      comparison_window: 168          # hours (1 week)
      metrics_retention: 720          # hours (30 days)
      benchmark_bot_id: null
      
    # Data sources
    data_sources:
      - type: "market_data"
        symbols: ["BTCUSDT", "ETHUSDT", "ADAUSDT"]
        timeframes: ["1m", "5m", "15m", "1h", "4h", "1d"]
      - type: "social_sentiment"
        sources: ["twitter", "reddit"]
        
    # Storage settings
    storage:
      cache_patterns: true
      cache_ttl: 1800                 # seconds
      persist_results: true

# Strategy bot configuration
strategy:
  enabled: true
  auto_start: false
  instances: 1
  
  config:
    # Strategy settings
    strategies:
      momentum:
        enabled: true
        weight: 0.4
        parameters:
          lookback_period: 20
          threshold: 0.02
          confirmation_period: 3
          
      mean_reversion:
        enabled: true
        weight: 0.3
        parameters:
          lookback_period: 50
          std_threshold: 2.0
          reversion_confidence: 0.7
          
      breakout:
        enabled: true
        weight: 0.3
        parameters:
          lookback_period: 30
          volume_threshold: 1.5
          confirmation_candles: 2
    
    # Risk management
    risk_management:
      max_position_size: 0.1          # 10% of portfolio
      stop_loss: 0.02                 # 2%
      take_profit: 0.06               # 6%
      max_daily_loss: 0.05            # 5%
      position_sizing_method: "kelly" # fixed, percent, kelly
      
    # Signal generation
    signal_generation:
      min_confidence: 0.6
      consensus_threshold: 0.7        # Require 70% strategy agreement
      signal_timeout: 300             # seconds
      
    # Execution settings
    execution:
      order_type: "market"            # market, limit
      slippage_tolerance: 0.001       # 0.1%
      retry_attempts: 3
      timeout: 30                     # seconds

# System bots configuration
system:
  # Risk management bot
  risk_bot:
    enabled: true
    auto_start: true
    
    config:
      # Monitoring settings
      monitoring_interval: 30         # seconds
      portfolio_check_interval: 60   # seconds
      
      # Risk calculation
      risk_calculation:
        var_confidence: 0.95          # 95% VaR
        lookback_period: 252          # trading days
        correlation_threshold: 0.8
        
      # Alert thresholds
      alert_thresholds:
        var_95: 0.05                  # 5% daily VaR
        max_drawdown: 0.15            # 15% max drawdown
        correlation_limit: 0.8        # 80% max correlation
        concentration_limit: 0.3      # 30% max single position
        
      # Emergency actions
      emergency_actions:
        enabled: true
        auto_close_positions: true    # Auto-close on extreme risk
        risk_threshold: 0.9           # 90% risk score trigger
        cooldown_period: 3600         # seconds
        
  # Memory management bot
  memory_bot:
    enabled: true
    auto_start: true
    
    config:
      # Cache configuration
      cache:
        memory_limit_mb: 256
        lru_enabled: true
        ttl_default: 3600             # seconds
        ttl_cleanup_interval: 300     # seconds
        
      # Redis configuration (if enabled)
      redis:
        enabled: false
        host: "localhost"
        port: 6379
        db: 0
        password: null
        connection_pool_size: 10
        
      # Storage configuration
      storage:
        sqlite_path: "data/memory.db"
        batch_size: 1000
        compression_enabled: true
        
      # Cleanup settings
      cleanup:
        auto_cleanup: true
        cleanup_interval: 3600        # seconds
        retention_days: 30
        compress_old_data: true
        
  # Logging bot
  logger_bot:
    enabled: true
    auto_start: true
    
    config:
      # Log processing
      processing:
        batch_size: 100
        flush_interval: 10            # seconds
        async_processing: true
        
      # Storage configuration
      storage:
        sqlite_path: "data/logs.db"
        table_name: "application_logs"
        index_fields: ["timestamp", "level", "bot_id"]
        
      # Alert configuration
      alerts:
        enabled: true
        rules:
          - level: "ERROR"
            threshold: 5              # errors per minute
            action: "email"
          - level: "WARN"
            threshold: 20             # warnings per minute
            action: "webhook"
            
      # Log retention
      retention:
        default_days: 30
        error_logs_days: 90
        audit_logs_days: 365
        compression_after_days: 7
        
      # Performance tracking
      performance:
        track_metrics: true
        metrics_interval: 60          # seconds
        slow_query_threshold: 1000    # milliseconds

# Bot dependencies
dependencies:
  analytics:
    requires: []
    optional: ["memory_bot"]
    
  strategy:
    requires: ["analytics"]
    optional: ["risk_bot", "memory_bot"]
    
  risk_bot:
    requires: []
    optional: ["logger_bot"]
    
  memory_bot:
    requires: []
    optional: []
    
  logger_bot:
    requires: []
    optional: []

# Resource allocation
resources:
  analytics:
    memory_mb: 256
    cpu_percent: 20
    
  strategy:
    memory_mb: 128
    cpu_percent: 15
    
  risk_bot:
    memory_mb: 64
    cpu_percent: 10
    
  memory_bot:
    memory_mb: 128
    cpu_percent: 5
    
  logger_bot:
    memory_mb: 64
    cpu_percent: 5
```

### Strategy Configuration (config/strategies.yaml)

```yaml
# Default strategy configuration
default_strategy: "multi_signal"

# Strategy definitions
strategies:
  # Momentum strategy
  momentum:
    name: "Momentum Strategy"
    description: "Trend-following momentum strategy"
    enabled: true
    
    parameters:
      # Lookback periods
      short_period: 10
      long_period: 30
      confirmation_period: 3
      
      # Thresholds
      momentum_threshold: 0.02        # 2% momentum required
      volume_threshold: 1.2           # 20% above average volume
      confidence_threshold: 0.6
      
      # Risk parameters
      max_position_size: 0.08         # 8% of portfolio
      stop_loss_percent: 0.015        # 1.5%
      take_profit_percent: 0.045      # 4.5%
      
    # Technical indicators
    indicators:
      - name: "sma"
        periods: [10, 20, 50]
      - name: "ema"
        periods: [12, 26]
      - name: "rsi"
        period: 14
      - name: "macd"
        fast: 12
        slow: 26
        signal: 9
      - name: "volume_sma"
        period: 20
        
  # Mean reversion strategy
  mean_reversion:
    name: "Mean Reversion Strategy"
    description: "Statistical mean reversion strategy"
    enabled: true
    
    parameters:
      # Statistical parameters
      lookback_period: 50
      std_multiplier: 2.0
      reversion_threshold: 0.7
      
      # Entry/exit conditions
      oversold_threshold: 30          # RSI level
      overbought_threshold: 70        # RSI level
      confidence_threshold: 0.65
      
      # Risk parameters
      max_position_size: 0.06         # 6% of portfolio
      stop_loss_percent: 0.02         # 2%
      take_profit_percent: 0.04       # 4%
      
    indicators:
      - name: "bollinger_bands"
        period: 20
        std: 2
      - name: "rsi"
        period: 14
      - name: "stochastic"
        k_period: 14
        d_period: 3
      - name: "williams_r"
        period: 14
        
  # Breakout strategy
  breakout:
    name: "Breakout Strategy"
    description: "Price breakout momentum strategy"
    enabled: true
    
    parameters:
      # Breakout detection
      lookback_period: 30
      breakout_threshold: 0.005       # 0.5% price breakout
      volume_confirmation: true
      volume_multiplier: 1.5
      
      # Confirmation
      confirmation_candles: 2
      false_breakout_filter: true
      consolidation_period: 10
      
      # Risk parameters
      max_position_size: 0.1          # 10% of portfolio
      stop_loss_percent: 0.01         # 1%
      take_profit_percent: 0.05       # 5%
      
    indicators:
      - name: "donchian_channel"
        period: 20
      - name: "atr"
        period: 14
      - name: "volume_profile"
        period: 50
      - name: "support_resistance"
        lookback: 100

# Multi-strategy configuration
multi_signal:
  name: "Multi-Signal Strategy"
  description: "Consensus-based multi-strategy approach"
  enabled: true
  
  # Strategy weights
  strategy_weights:
    momentum: 0.4
    mean_reversion: 0.3
    breakout: 0.3
    
  # Consensus requirements
  consensus:
    minimum_agreement: 0.6            # 60% strategy agreement required
    weight_threshold: 0.7             # Combined weight threshold
    confidence_boost: 0.1             # Confidence boost for consensus
    
  # Signal filtering
  signal_filters:
    min_confidence: 0.5
    max_conflicting_signals: 1        # Max opposing signals allowed
    correlation_check: true
    market_condition_filter: true
    
  # Risk management
  risk_management:
    max_total_exposure: 0.8           # 80% of portfolio
    correlation_limit: 0.6            # Max 60% correlation between positions
    sector_concentration_limit: 0.4   # 40% max in any sector
    
# Market condition detection
market_conditions:
  trending:
    indicators:
      - name: "adx"
        threshold: 25
      - name: "trend_strength"
        threshold: 0.6
    strategy_preferences:
      momentum: 1.2                   # Boost momentum in trending markets
      mean_reversion: 0.8             # Reduce mean reversion
      
  ranging:
    indicators:
      - name: "adx"
        threshold: 20
        operator: "less_than"
      - name: "volatility"
        threshold: 0.02
        operator: "less_than"
    strategy_preferences:
      momentum: 0.7                   # Reduce momentum in ranging markets
      mean_reversion: 1.3             # Boost mean reversion
      
  volatile:
    indicators:
      - name: "volatility"
        threshold: 0.05
      - name: "atr_ratio"
        threshold: 1.5
    strategy_preferences:
      breakout: 1.2                   # Boost breakout in volatile markets
      mean_reversion: 0.6             # Reduce mean reversion

# Risk management rules
risk_rules:
  position_sizing:
    method: "kelly"                   # fixed, percent, volatility, kelly
    base_size: 0.02                   # 2% base position size
    max_size: 0.1                     # 10% maximum position size
    volatility_adjustment: true
    
  stop_loss:
    method: "atr"                     # fixed, percent, atr, trailing
    atr_multiplier: 2.0
    min_stop_loss: 0.005              # 0.5% minimum
    max_stop_loss: 0.03               # 3% maximum
    trailing_enabled: true
    
  take_profit:
    method: "risk_reward"             # fixed, percent, risk_reward
    risk_reward_ratio: 2.5            # 2.5:1 reward to risk
    partial_profit_levels: [0.5, 0.75] # Take partial profits at 50% and 75%
    
  portfolio_limits:
    max_positions: 10
    max_daily_trades: 20
    max_weekly_loss: 0.1              # 10% weekly loss limit
    max_drawdown: 0.15                # 15% maximum drawdown

# Backtesting configuration
backtesting:
  enabled: true
  
  # Data configuration
  data:
    start_date: "2023-01-01"
    end_date: "2023-12-31"
    symbols: ["BTCUSDT", "ETHUSDT", "ADAUSDT", "BNBUSDT"]
    timeframes: ["1h", "4h", "1d"]
    
  # Execution simulation
  execution:
    slippage: 0.001                   # 0.1% slippage
    commission: 0.001                 # 0.1% commission
    latency_ms: 100                   # 100ms execution latency
    
  # Performance metrics
  metrics:
    - "total_return"
    - "sharpe_ratio"
    - "max_drawdown"
    - "win_rate"
    - "profit_factor"
    - "calmar_ratio"
    
  # Optimization
  optimization:
    enabled: false
    method: "grid_search"             # grid_search, random_search, genetic
    parameters:
      momentum_threshold: [0.01, 0.02, 0.03]
      std_multiplier: [1.5, 2.0, 2.5]
    objective: "sharpe_ratio"

# Paper trading configuration
paper_trading:
  enabled: true
  initial_balance: 10000              # USD
  
  # Simulation settings
  execution_delay: 0.1                # seconds
  slippage_model: "linear"            # linear, sqrt, fixed
  commission_rate: 0.001              # 0.1%
  
  # Risk management
  max_leverage: 1.0                   # No leverage in paper trading
  margin_requirement: 1.0             # 100% margin
  
  # Reporting
  daily_reports: true
  performance_tracking: true
  trade_logging: true

# Live trading configuration (disabled by default)
live_trading:
  enabled: false
  
  # Exchange configuration
  exchange:
    name: "binance"                   # binance, bybit, ftx
    api_key: "${EXCHANGE_API_KEY}"
    api_secret: "${EXCHANGE_API_SECRET}"
    testnet: true                     # Use testnet for safety
    
  # Order execution
  order_execution:
    default_order_type: "limit"       # market, limit, stop_limit
    price_offset: 0.0005              # 0.05% price offset for limit orders
    timeout: 30                       # seconds
    retry_attempts: 3
    
  # Safety features
  safety:
    max_order_size: 100               # USD
    daily_loss_limit: 50              # USD
    position_limit: 5                 # Max 5 positions
    emergency_stop: true              # Enable emergency stop
    
  # Monitoring
  monitoring:
    order_status_check_interval: 5    # seconds
    position_sync_interval: 30        # seconds
    balance_check_interval: 60        # seconds
```

## Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# System configuration
TRADEMASTERX_DEBUG=false
TRADEMASTERX_LOG_LEVEL=INFO
TRADEMASTERX_SECRET_KEY=your-secret-key-here
TRADEMASTERX_JWT_SECRET=your-jwt-secret-here

# Database configuration
DATABASE_URL=sqlite:///data/trademasterx.db
# For PostgreSQL: postgresql://username:password@localhost:5432/trademasterx

# Cache configuration
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=

# API Keys (for live trading - keep secure!)
EXCHANGE_API_KEY=
EXCHANGE_API_SECRET=
EXCHANGE_PASSPHRASE=

# Notification settings
EMAIL_USERNAME=
EMAIL_PASSWORD=
WEBHOOK_URL=

# External services
TWITTER_API_KEY=
TWITTER_API_SECRET=
COINMARKETCAP_API_KEY=

# Development settings
FLASK_ENV=production
FLASK_DEBUG=false
```

## Configuration Validation

The system validates all configuration files on startup. Common validation rules include:

- **Type checking**: Ensures values match expected types
- **Range validation**: Numeric values within acceptable ranges
- **Dependency checking**: Required services are available
- **Security validation**: API keys and secrets are properly formatted

## Configuration Hot-Reloading

The system supports hot-reloading of configuration without restart for most settings:

```python
# Update configuration via API
POST /api/config
{
  "bots": {
    "analytics": {
      "pattern_analysis": {
        "confidence_threshold": 0.8
      }
    }
  }
}
```

## Best Practices

1. **Security**: Never commit API keys or secrets to version control
2. **Environment-specific**: Use different configurations for development, staging, and production
3. **Documentation**: Document all custom configuration parameters
4. **Validation**: Test configuration changes in development environment first
5. **Backup**: Keep backups of working configurations

This configuration system provides flexibility while maintaining security and reliability across different deployment environments.
