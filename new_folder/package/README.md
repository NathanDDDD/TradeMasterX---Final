# TradeMasterX 2.0 - Production-Grade Trading System

## 🎯 Advanced AI-Powered Cryptocurrency Trading Platform

A complete, production-ready automated cryptocurrency trading system with advanced analytics, risk management, and real-time monitoring capabilities. Built with modern Python architecture and containerized deployment.

## ⭐ Key Features

### 🤖 Advanced Bot System
- **AnalyticsBot** - Pattern analysis, performance tracking, prediction accuracy
- **StrategyBot** - Multi-strategy signal generation with risk management
- **RiskBot** - Portfolio risk monitoring with emergency management
- **MemoryBot** - Intelligent caching and data management
- **LoggerBot** - Comprehensive logging with audit trails

### 🎛️ Interfaces
- **Web Interface** - Modern Flask dashboard with real-time updates
- **CLI Interface** - Command-line tools for automation and scripting
- **REST API** - Full API for integration and monitoring

### 🔧 Core Features
- **MasterBot Orchestration** - Centralized bot lifecycle management
- **Dynamic Configuration** - YAML/JSON configuration with hot-reload
- **Performance Scoring** - Real-time assessment and optimization
- **Multi-layer Storage** - Redis, SQLite, and memory caching
- **Docker Deployment** - Production-ready containerization

##  Quick Start

### Prerequisites
- Python 3.8+
- Docker (optional)
- Redis (optional, for enhanced caching)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd trademasterx

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .

# Copy environment configuration
cp .env.example .env
# Edit .env with your API keys and settings
```

### Quick Launch

```bash
# Start web interface
trademasterx-web --host 0.0.0.0 --port 5000

# Or use CLI
trademasterx-cli start --config config/system.yaml

# Or run with Docker
docker-compose up -d
```

## 📁 Project Structure

```
trademasterx/
├── setup.py                           # Package setup and entry points
├── requirements.txt                   # Production dependencies
├── docker-compose.yml                 # Docker orchestration
├── Dockerfile                         # Container configuration
├── .env.example                       # Environment variables template
├── config/
│   ├── system.yaml                    # System configuration
│   ├── bots.yaml                      # Bot configurations
│   └── strategies.yaml                # Trading strategies
├── trademasterx/                      # Main package
│   ├── __init__.py                    # Package initialization
│   ├── core/                          # Core functionality
│   │   ├── master_bot.py              # Master orchestration
│   │   ├── bot_registry.py            # Bot factory and lifecycle
│   │   └── scoring.py                 # Performance assessment
│   ├── bots/                          # Bot implementations
│   │   ├── analytics/                 # Analytics bots
│   │   ├── strategy/                  # Strategy bots
│   │   └── system/                    # System management bots
│   ├── config/                        # Configuration management
│   │   └── config_loader.py           # YAML/JSON configuration
│   └── interface/                     # User interfaces
│       ├── web/                       # Flask web interface
│       └── cli/                       # Command-line interface
└── docs/                              # Documentation
    ├── PROJECT_STRUCTURE.md           # Detailed architecture
    ├── BOT_REFERENCE.md               # Bot development guide
    └── API_REFERENCE.md               # API documentation
```

## 🔧 Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Bybit Testnet API
Edit `config/master_config.json`:
```json
{
  "bybit_testnet": {
    "api_key": "your_testnet_api_key_here",
    "api_secret": "your_testnet_api_secret_here",
    "base_url": "https://api-testnet.bybit.com"
  }
}
```

### 3. Launch 7-Day Training Session
```bash
cd launch
python testnet_controller.py
```

## 📊 System Features

### Trade Execution
- **30-second intervals** - ~20,160 trades over 7 days
- **Multi-symbol support** - BTCUSDT, ETHUSDT, ADAUSDT
- **Adaptive confidence thresholds** - Dynamic adjustment based on performance
- **Risk management** - Stop-loss and take-profit automation

### Model Retraining
- **12-hour cycles** - 14 retraining sessions over 7 days
- **Performance validation** - Automatic rollback on >5% accuracy drop
- **Version management** - Model versioning and improvement tracking
- **Stalled training handling** - Automatic detection and recovery

### Real-Time Monitoring
- **Performance tracking** - Win rate, Sharpe ratio, drawdown monitoring
- **Error spike detection** - 15-minute pause on API issues
- **Confidence adjustment** - ±2% threshold changes based on accuracy
- **System health monitoring** - API reliability and retraining success tracking

### Daily Reporting
- **Midnight generation** - Automated daily performance summaries
- **Strategy analysis** - Individual strategy contribution tracking
- **Trend identification** - Performance pattern recognition
- **Comprehensive metrics** - Trade counts, PnL, accuracy statistics

### Final Assessment
- **Live readiness score** - 0-100 scale with weighted components
- **Approval thresholds** - Score ≥90 for live trading approval
- **Component analysis** - Win rate, Sharpe ratio, prediction accuracy
- **Recommendations** - Specific improvement suggestions

## 🎛️ Monitoring & Control

### Real-Time Metrics
- **Trade Performance**: Win rate, profit/loss ratio, Sharpe ratio
- **Prediction Accuracy**: Model confidence and correctness tracking  
- **System Health**: API reliability, retraining success rate
- **Risk Management**: Maximum drawdown monitoring

### Adaptive Adjustments
- **Confidence Thresholds**: Automatic adjustment based on accuracy
  - Accuracy ≥80% → Increase threshold by 2%
  - Accuracy ≤65% → Reduce threshold by 2%
- **Error Handling**: 15-minute trading pause on API error spikes
- **Model Management**: Automatic rollback on performance degradation

### Session Progress
- **7-Day Tracking**: Automatic completion after 168 hours
- **Milestone Checkpoints**: Daily progress reporting
- **Emergency Stop**: Manual intervention capability
- **Graceful Shutdown**: Clean session termination

## 📈 Performance Targets

### Minimum Thresholds for Live Trading Approval
- **Win Rate**: ≥55%
- **Sharpe Ratio**: ≥1.0
- **Prediction Accuracy**: ≥70%
- **Maximum Drawdown**: ≤15%
- **API Reliability**: ≥95%
- **Retraining Success**: ≥80%

### Scoring Weights
- **Win Rate**: 25%
- **Sharpe Ratio**: 20%
- **Prediction Accuracy**: 20%
- **Drawdown Control**: 15%
- **API Reliability**: 10%
- **Retraining Success**: 10%

## 🚨 Safety Features

### Risk Management
- **Position sizing limits** - Maximum 5% per trade
- **Stop-loss protection** - 2% maximum loss per trade
- **Drawdown monitoring** - Automatic pause on excessive losses
- **Emergency stop** - Manual intervention capability

### Error Handling
- **API error recovery** - Automatic retry with exponential backoff
- **Model validation** - Performance verification before deployment
- **Graceful degradation** - Continue operation with reduced functionality
- **Comprehensive logging** - Detailed error tracking and analysis

### Data Integrity
- **Database backups** - Automatic data preservation
- **Model versioning** - Complete training history tracking
- **Report generation** - Comprehensive session documentation
- **Audit trails** - Complete decision and action logging

## 📋 Usage Examples

### Start Complete 7-Day Session
```bash
python launch/testnet_controller.py
```

### Manual Final Assessment
```bash
python core/assessment/readiness_estimator.py
```

### Emergency Stop
```bash
# Ctrl+C in running session or
# Send SIGTERM signal to process
```

## 📊 Expected Outputs

### Daily Reports
- **Location**: `reports/daily/daily_report_YYYYMMDD.json`
- **Content**: Trade statistics, performance metrics, strategy analysis
- **Schedule**: Generated at midnight daily

### Final Assessment
- **Location**: `reports/final/final_testnet_evaluation.json`
- **Content**: Complete 7-day analysis with live trading readiness score
- **Trigger**: Automatic after 168-hour session completion

### System Logs
- **Location**: `logs/master_controller_YYYYMMDD_HHMMSS.log`
- **Content**: Detailed system operation logs with timestamps
- **Level**: INFO, WARNING, ERROR with component identification

## 🔄 Continuous Operation

The system operates continuously for 7 days with:
- **30-second trade cycles** - Continuous market engagement
- **12-hour retraining** - Model improvement and adaptation
- **10-minute monitoring** - Real-time performance tracking
- **Daily reporting** - Progress documentation
- **Final assessment** - Live trading readiness evaluation

## ⚡ Quick Start

1. **Setup**: Configure API credentials in `config/master_config.json`
2. **Launch**: Run `python launch/testnet_controller.py`
3. **Monitor**: Check logs and reports for real-time status
4. **Complete**: Review final assessment after 7 days
5. **Deploy**: If score ≥90, system approved for live trading

## 🏆 Success Criteria

**APPROVED FOR LIVE TRADING** when:
- Final readiness score ≥90/100
- All critical thresholds met
- Comprehensive validation passed
- 7-day session completed successfully

---

**TradeMasterX 2.0 Phase 9A & 9B Complete**  
*Ready for 7-day Bybit Testnet Training with Live Trading Readiness Assessment*

## 🔧 Configuration

### System Configuration (config/system.yaml)
```yaml
system:
  name: "TradeMasterX"
  version: "2.0"
  debug: false
  
master_bot:
  monitoring_interval: 5
  max_concurrent_bots: 10
  
api:
  rate_limit: 100
  timeout: 30
```

### Bot Configuration (config/bots.yaml)
Configure individual bot settings, API keys, and operational parameters.

### Strategy Configuration (config/strategies.yaml)
Define trading strategies, risk parameters, and signal generation rules.

## 🤖 Bot System

### Core Bots
- **AnalyticsBot** - Market analysis, pattern detection, performance tracking
- **StrategyBot** - Signal generation, position sizing, multi-strategy coordination
- **RiskBot** - Portfolio risk assessment, emergency management, drawdown control

### System Bots
- **MemoryBot** - Multi-layer caching, data persistence, cleanup automation
- **LoggerBot** - Structured logging, audit trails, alert management

## 🌐 Web Interface

Access the web dashboard at `http://localhost:5000`

### Features
- **Real-time Dashboard** - Live system status and performance metrics
- **Bot Management** - Create, configure, start/stop bots
- **Analytics Dashboard** - Market analysis and pattern visualization
- **Risk Monitoring** - Portfolio risk assessment and alerts
- **Configuration Manager** - Live configuration updates
- **Log Viewer** - Comprehensive log analysis

## 💻 CLI Interface

```bash
# Start the system
trademasterx-cli start

# Create a new bot
trademasterx-cli bot create analytics --config analytics_config.yaml

# View system status
trademasterx-cli status

# Stop all bots
trademasterx-cli stop
```

## 🐳 Docker Deployment

### Quick Start
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production Deployment
```bash
# Build production image
docker build -t trademasterx:latest .

# Run with custom configuration
docker run -d \
  --name trademasterx \
  -p 5000:5000 \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/data:/app/data \
  trademasterx:latest
```

## 📊 Performance Monitoring

### Metrics Tracked
- **Trading Performance** - Win rate, profit/loss, Sharpe ratio
- **System Performance** - CPU usage, memory consumption, API latency
- **Bot Performance** - Individual bot efficiency and accuracy
- **Risk Metrics** - VaR, drawdown, position sizes

### Alerts
- Real-time performance alerts
- Risk threshold notifications
- System health monitoring
- API error tracking

## 🔒 Security Features

- **API Key Management** - Secure credential storage
- **Rate Limiting** - API call throttling
- **Access Control** - Role-based permissions
- **Audit Logging** - Complete activity tracking
- **Encryption** - Data encryption at rest and in transit

## 🧪 Testing

```bash
# Run unit tests
python -m pytest tests/

# Run integration tests
python -m pytest tests/integration/

# Run system validation
python validate_system.py
```

## 📈 Performance Optimization

### Memory Management
- Intelligent caching with TTL
- Automatic cleanup of stale data
- Memory usage monitoring

### Database Optimization
- Connection pooling
- Query optimization
- Index management

### API Optimization
- Request batching
- Intelligent retry logic
- Rate limit compliance

## 🛠️ Development

### Adding New Bots
1. Create bot class inheriting from base bot
2. Implement required methods
3. Register in bot registry
4. Add configuration schema

### Extending Strategies
1. Implement strategy in StrategyBot
2. Add configuration parameters
3. Update signal generation logic
4. Test with backtesting framework

## 📝 Logging

### Log Levels
- **ERROR** - System errors and exceptions
- **WARN** - Performance warnings and alerts
- **INFO** - General system information
- **DEBUG** - Detailed debugging information

### Log Storage
- SQLite database for structured logs
- File-based logging for development
- Real-time log streaming to web interface

## 🔧 Troubleshooting

### Common Issues
1. **Bot Not Starting** - Check configuration and API keys
2. **Memory Issues** - Adjust cache settings and cleanup intervals
3. **API Errors** - Verify rate limits and connection settings
4. **Performance Issues** - Review monitoring metrics and optimize

### Debug Mode
```bash
# Enable debug mode
export DEBUG=true
trademasterx-cli start --debug
```

## 📚 Documentation

- [Project Structure](docs/PROJECT_STRUCTURE.md) - Detailed architecture overview
- [Bot Reference](docs/BOT_REFERENCE.md) - Bot development and configuration
- [API Reference](docs/API_REFERENCE.md) - REST API documentation
- [Configuration Guide](docs/CONFIGURATION.md) - Complete configuration reference

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation** - Check the docs/ directory
- **Issues** - Submit GitHub issues for bugs
- **Discussions** - Use GitHub discussions for questions

## 🎯 Roadmap

### Phase 3.0 (Future)
- [ ] Machine Learning Pipeline Integration
- [ ] Advanced Risk Management Models
- [ ] Multi-Exchange Support
- [ ] Mobile Application
- [ ] Cloud Deployment Templates

---

**TradeMasterX 2.0** - Professional-grade automated trading system built for reliability, scalability, and performance.
