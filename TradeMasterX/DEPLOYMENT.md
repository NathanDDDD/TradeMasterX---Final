# TradeMasterX Deployment Guide

This guide covers deploying TradeMasterX in various production environments.

## 🚀 Quick Start

### Local Development
```bash
# Clone the repository
git clone https://github.com/NathanDDDD/TradeMasterX---Final.git
cd TradeMasterX---Final

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the dashboard
streamlit run dashboard.py

# Or run CLI mode
python launch.py
```

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)
```bash
# Copy environment variables
cp env.example .env
# Edit .env with your API keys

# Build and run
docker-compose up -d

# Access dashboard at http://localhost:8501
```

### Using Docker directly
```bash
# Build the image
docker build -t trademasterx .

# Run with environment variables
docker run -d \
  -p 8501:8501 \
  -e ANTHROPIC_API_KEY=your_key \
  -e BYBIT_API_KEY=your_key \
  -v $(pwd)/data:/app/data \
  trademasterx
```

## ☁️ Cloud Deployment

### AWS EC2
```bash
# Launch Ubuntu instance
# Install Docker
sudo apt update
sudo apt install docker.io docker-compose

# Clone repository
git clone https://github.com/NathanDDDD/TradeMasterX---Final.git
cd TradeMasterX---Final

# Configure environment
cp env.example .env
# Edit .env with your API keys

# Deploy
sudo docker-compose up -d

# Configure security group to allow port 8501
```

### Google Cloud Platform
```bash
# Create Compute Engine instance
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Deploy using same steps as AWS
```

### DigitalOcean Droplet
```bash
# Create Ubuntu droplet
# Install Docker
sudo apt update && sudo apt install docker.io docker-compose

# Deploy using same steps as AWS
```

## 🔧 Environment Configuration

### Required Environment Variables
```bash
# AI Services (Optional)
ANTHROPIC_API_KEY=your_claude_api_key
OPENAI_API_KEY=your_openai_api_key

# Trading (Optional)
BYBIT_API_KEY=your_bybit_api_key
BYBIT_API_SECRET=your_bybit_secret

# Alerts (Optional)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# System
LOG_LEVEL=INFO
TRADING_MODE=demo  # or live
```

### Configuration File
Edit `config.yaml` for trading parameters:
```yaml
trading:
  risk: 0.01
  symbols: ['BTCUSDT', 'ETHUSDT']
  timeframe: '1h'
logging:
  level: INFO
```

## 📊 Monitoring & Health Checks

### Health Check Endpoint
The dashboard includes a health check at:
```
http://your-server:8501/_stcore/health
```

### Log Monitoring
```bash
# View logs
docker-compose logs -f trademasterx

# Or view log files directly
tail -f mini_log.txt
tail -f memory.json
```

### Alert Configuration
1. **Telegram Bot Setup**:
   - Create bot via @BotFather
   - Get bot token and chat ID
   - Add to environment variables

2. **Test Alerts**:
   ```python
   from trademasterx.utils.alerts import AlertSystem
   alerts = AlertSystem()
   alerts.test_alert()
   ```

## 🔒 Security Considerations

### API Key Security
- Never commit API keys to version control
- Use environment variables or secure key management
- Rotate keys regularly
- Use testnet/sandbox environments for development

### Network Security
- Use HTTPS in production
- Configure firewall rules
- Limit access to necessary ports only
- Use VPN for remote access

### Data Protection
- Encrypt sensitive data at rest
- Use secure connections for API calls
- Implement proper backup strategies
- Monitor for unauthorized access

## 📈 Production Checklist

- [ ] Environment variables configured
- [ ] API keys secured and tested
- [ ] Database/volume mounts configured
- [ ] Monitoring and alerts set up
- [ ] Backup strategy implemented
- [ ] Security measures in place
- [ ] Performance testing completed
- [ ] Documentation updated

## 🛠️ Troubleshooting

### Common Issues

**Dashboard not accessible**:
- Check if port 8501 is open
- Verify Docker container is running
- Check logs for errors

**API connection issues**:
- Verify API keys are correct
- Check network connectivity
- Ensure API rate limits not exceeded

**Memory/disk space**:
- Monitor log file sizes
- Implement log rotation
- Clean up old data periodically

### Getting Help
- Check the logs in `mini_log.txt`
- Review system status in dashboard
- Open an issue on GitHub
- Check the troubleshooting section in README

## 🔄 Updates & Maintenance

### Updating TradeMasterX
```bash
# Pull latest changes
git pull origin main

# Rebuild Docker image
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Backup Strategy
```bash
# Backup configuration and data
tar -czf trademasterx-backup-$(date +%Y%m%d).tar.gz \
  config.yaml memory.json mini_log.txt data/
```

### Monitoring Scripts
Create cron jobs for regular monitoring:
```bash
# Check system health every 5 minutes
*/5 * * * * curl -f http://localhost:8501/_stcore/health || echo "Dashboard down"
```

## 📞 Support

For deployment issues:
1. Check this guide first
2. Review the logs
3. Open an issue on GitHub
4. Include environment details and error messages 