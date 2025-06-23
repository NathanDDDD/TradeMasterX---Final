# API Reference

## Overview

TradeMasterX 2.0 provides a comprehensive RESTful API for system control, monitoring, and bot management. The API supports both synchronous HTTP requests and real-time WebSocket connections for live updates.

## Base URL

```
Development: http://localhost:5000/api
Production: https://your-domain.com/api
```

## Authentication

### API Key Authentication
```http
Authorization: Bearer YOUR_API_KEY
```

### Session Authentication
For web interface, session-based authentication is used with CSRF protection.

## Common Response Format

### Success Response
```json
{
  "success": true,
  "data": {},
  "timestamp": "2023-01-01T12:00:00Z",
  "message": "Operation completed successfully"
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Detailed error message",
    "details": {}
  },
  "timestamp": "2023-01-01T12:00:00Z"
}
```

## System Endpoints

### Get System Status
Get overall system health and statistics.

```http
GET /api/status
```

**Response:**
```json
{
  "success": true,
  "data": {
    "timestamp": "2023-01-01T12:00:00Z",
    "master_bot_active": true,
    "active_bots": 5,
    "total_bots": 8,
    "system_health": "healthy",
    "active_connections": 3,
    "bots": {
      "analytics_001": {
        "active": true,
        "type": "AnalyticsBot",
        "last_update": "2023-01-01T11:59:00Z"
      }
    }
  }
}
```

### System Health Check
Quick health check endpoint for monitoring.

```http
GET /api/health
```

**Response:**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "uptime": 3600,
    "memory_usage": {
      "rss": 134217728,
      "vms": 268435456,
      "percent": 12.5
    }
  }
}
```

## Bot Management Endpoints

### List All Bots
Get information about all registered and active bots.

```http
GET /api/bots
```

**Response:**
```json
{
  "success": true,
  "data": {
    "registered": ["analytics", "strategy", "risk", "memory", "logger"],
    "active": {
      "analytics_001": {
        "type": "AnalyticsBot",
        "status": "active",
        "created": "2023-01-01T10:00:00Z",
        "config": {
          "window_size": 100,
          "confidence_threshold": 0.7
        }
      }
    },
    "available_types": ["analytics", "strategy", "risk", "memory", "logger"]
  }
}
```

### Create New Bot
Create a new bot instance of the specified type.

```http
POST /api/bots/{bot_type}
Content-Type: application/json

{
  "config": {
    "window_size": 100,
    "confidence_threshold": 0.7,
    "auto_start": true
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "bot_id": "analytics_002",
    "message": "Bot analytics_002 created successfully"
  }
}
```

### Get Bot Details
Get detailed information about a specific bot.

```http
GET /api/bots/{bot_id}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "bot_id": "analytics_001",
    "type": "AnalyticsBot",
    "status": "active",
    "created": "2023-01-01T10:00:00Z",
    "last_update": "2023-01-01T11:59:00Z",
    "config": {
      "window_size": 100,
      "confidence_threshold": 0.7
    },
    "metrics": {
      "patterns_detected": 15,
      "signals_active": 3,
      "accuracy": 0.85
    }
  }
}
```

### Update Bot Configuration
Update configuration for an existing bot.

```http
PUT /api/bots/{bot_id}/config
Content-Type: application/json

{
  "config": {
    "window_size": 150,
    "confidence_threshold": 0.8
  }
}
```

### Start Bot
Start a bot instance.

```http
POST /api/bots/{bot_id}/start
```

**Response:**
```json
{
  "success": true,
  "data": {
    "message": "Bot analytics_001 started successfully"
  }
}
```

### Stop Bot
Stop a bot instance.

```http
POST /api/bots/{bot_id}/stop
```

### Delete Bot
Delete a bot instance.

```http
DELETE /api/bots/{bot_id}
```

## Analytics Endpoints

### Get Analytics Summary
Get comprehensive analytics summary.

```http
GET /api/analytics/summary
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total_patterns": 45,
    "active_signals": 8,
    "bot_performance": {
      "average_accuracy": 0.82,
      "total_trades": 156,
      "successful_trades": 128
    },
    "market_analysis": {
      "trend": "bullish",
      "volatility": "medium",
      "strength": 0.75
    },
    "last_update": "2023-01-01T11:59:00Z"
  }
}
```

### Get Pattern Analysis
Get detailed pattern analysis results.

```http
GET /api/analytics/patterns
```

**Query Parameters:**
- `limit` (optional): Number of patterns to return (default: 50)
- `confidence_min` (optional): Minimum confidence threshold (default: 0.5)
- `time_range` (optional): Time range in hours (default: 24)

**Response:**
```json
{
  "success": true,
  "data": {
    "patterns": [
      {
        "id": "pattern_001",
        "type": "head_and_shoulders",
        "confidence": 0.85,
        "detected_at": "2023-01-01T11:30:00Z",
        "timeframe": "1h",
        "symbol": "BTCUSDT",
        "parameters": {
          "left_shoulder": 45000,
          "head": 47000,
          "right_shoulder": 45500
        }
      }
    ],
    "total_count": 45,
    "summary": {
      "most_common_type": "support_resistance",
      "average_confidence": 0.72
    }
  }
}
```

### Get Signal Analysis
Get trading signal analysis and performance.

```http
GET /api/analytics/signals
```

**Response:**
```json
{
  "success": true,
  "data": {
    "active_signals": [
      {
        "id": "signal_001",
        "type": "buy",
        "strategy": "momentum",
        "confidence": 0.78,
        "generated_at": "2023-01-01T11:45:00Z",
        "symbol": "BTCUSDT",
        "price": 45000,
        "target": 46500,
        "stop_loss": 44000
      }
    ],
    "signal_performance": {
      "total_signals": 234,
      "successful_signals": 189,
      "accuracy": 0.81,
      "average_return": 0.025
    }
  }
}
```

## Strategy Endpoints

### Get Strategy Status
Get current strategy status and performance.

```http
GET /api/strategies/status
```

**Response:**
```json
{
  "success": true,
  "data": {
    "active_strategies": [
      {
        "name": "momentum",
        "weight": 0.4,
        "status": "active",
        "performance": {
          "accuracy": 0.83,
          "total_signals": 45,
          "successful_signals": 37
        }
      }
    ],
    "portfolio_status": {
      "total_value": 10000,
      "available_balance": 7500,
      "open_positions": 3,
      "unrealized_pnl": 125.50
    }
  }
}
```

### Execute Strategy Command
Execute a strategy-specific command.

```http
POST /api/strategies/{strategy_name}/execute
Content-Type: application/json

{
  "command": "generate_signal",
  "parameters": {
    "symbol": "BTCUSDT",
    "timeframe": "1h"
  }
}
```

## Risk Management Endpoints

### Get Risk Assessment
Get current portfolio risk assessment.

```http
GET /api/risk/assessment
```

**Response:**
```json
{
  "success": true,
  "data": {
    "overall_risk_score": 0.65,
    "risk_level": "medium",
    "portfolio_metrics": {
      "value_at_risk_95": 0.03,
      "maximum_drawdown": 0.08,
      "sharpe_ratio": 1.25,
      "volatility": 0.15
    },
    "position_analysis": [
      {
        "symbol": "BTCUSDT",
        "position_size": 0.1,
        "risk_contribution": 0.4,
        "unrealized_pnl": 45.50
      }
    ],
    "alerts": [
      {
        "level": "warning",
        "message": "Portfolio correlation increased",
        "timestamp": "2023-01-01T11:30:00Z"
      }
    ]
  }
}
```

### Set Risk Limits
Update risk management parameters.

```http
POST /api/risk/limits
Content-Type: application/json

{
  "max_position_size": 0.15,
  "stop_loss_threshold": 0.02,
  "daily_loss_limit": 0.05,
  "var_limit": 0.04
}
```

## Configuration Endpoints

### Get Configuration
Get current system configuration.

```http
GET /api/config
```

**Response:**
```json
{
  "success": true,
  "data": {
    "system": {
      "name": "TradeMasterX",
      "version": "2.0",
      "debug": false
    },
    "bots": {
      "analytics": {
        "enabled": true,
        "auto_start": true
      }
    },
    "strategies": {
      "default_strategy": "multi_signal",
      "risk_management": {
        "max_position_size": 0.1
      }
    }
  }
}
```

### Update Configuration
Update system configuration.

```http
POST /api/config
Content-Type: application/json

{
  "system": {
    "debug": true
  },
  "bots": {
    "analytics": {
      "window_size": 200
    }
  }
}
```

## Logging Endpoints

### Get Logs
Retrieve system logs with filtering options.

```http
GET /api/logs
```

**Query Parameters:**
- `level` (optional): Log level filter (DEBUG, INFO, WARN, ERROR)
- `limit` (optional): Number of logs to return (default: 100)
- `start_time` (optional): Start time filter (ISO format)
- `end_time` (optional): End time filter (ISO format)
- `bot_id` (optional): Filter by specific bot

**Response:**
```json
{
  "success": true,
  "data": {
    "logs": [
      {
        "id": "log_001",
        "timestamp": "2023-01-01T11:59:00Z",
        "level": "INFO",
        "message": "Bot analytics_001 started successfully",
        "bot_id": "analytics_001",
        "metadata": {
          "module": "bot_registry",
          "function": "start_bot"
        }
      }
    ],
    "total_count": 1500,
    "filtered_count": 100
  }
}
```

### Get Audit Trail
Get audit trail for specific operations.

```http
GET /api/logs/audit
```

**Response:**
```json
{
  "success": true,
  "data": {
    "audit_entries": [
      {
        "id": "audit_001",
        "timestamp": "2023-01-01T11:59:00Z",
        "user": "system",
        "action": "bot_created",
        "resource": "analytics_001",
        "details": {
          "bot_type": "analytics",
          "config": {
            "window_size": 100
          }
        }
      }
    ]
  }
}
```

## WebSocket API

### Connection
Connect to WebSocket for real-time updates.

```javascript
const socket = io('ws://localhost:5000');

// Join monitoring room for real-time updates
socket.emit('join_room', { room: 'monitoring' });

// Listen for status updates
socket.on('status_update', (data) => {
  console.log('System status update:', data);
});
```

### Events

#### status_update
Real-time system status updates.

```json
{
  "timestamp": "2023-01-01T12:00:00Z",
  "system": {
    "active": true,
    "uptime": "2 hours",
    "memory_usage": {
      "percent": 12.5
    }
  },
  "bots": {
    "analytics_001": {
      "active": true,
      "metrics": {
        "patterns_detected": 15
      }
    }
  }
}
```

#### bot_command_result
Result of bot command execution.

```json
{
  "success": true,
  "message": "Bot analytics_001 started",
  "bot_id": "analytics_001",
  "command": "start"
}
```

#### alert
System alerts and notifications.

```json
{
  "level": "warning",
  "message": "High memory usage detected",
  "timestamp": "2023-01-01T12:00:00Z",
  "source": "system_monitor"
}
```

## Error Codes

### System Errors
- `SYS_001`: System initialization failed
- `SYS_002`: Configuration error
- `SYS_003`: Resource unavailable

### Bot Errors
- `BOT_001`: Bot not found
- `BOT_002`: Bot creation failed
- `BOT_003`: Invalid bot configuration
- `BOT_004`: Bot operation timeout

### API Errors
- `API_001`: Invalid request format
- `API_002`: Missing required parameters
- `API_003`: Authentication failed
- `API_004`: Rate limit exceeded

## Rate Limiting

API endpoints are rate limited to prevent abuse:
- **Standard endpoints**: 100 requests per minute
- **Bot management**: 50 requests per minute
- **Configuration updates**: 10 requests per minute

Rate limit headers are included in responses:
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## SDK Examples

### Python SDK
```python
import requests
from typing import Dict, Any

class TradeMasterXClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    def get_status(self) -> Dict[str, Any]:
        response = requests.get(
            f'{self.base_url}/status',
            headers=self.headers
        )
        return response.json()
    
    def create_bot(self, bot_type: str, config: Dict[str, Any]) -> str:
        response = requests.post(
            f'{self.base_url}/bots/{bot_type}',
            json={'config': config},
            headers=self.headers
        )
        result = response.json()
        return result['data']['bot_id']

# Usage
client = TradeMasterXClient('http://localhost:5000/api', 'your-api-key')
status = client.get_status()
bot_id = client.create_bot('analytics', {'window_size': 100})
```

### JavaScript SDK
```javascript
class TradeMasterXClient {
  constructor(baseUrl, apiKey) {
    this.baseUrl = baseUrl;
    this.headers = {
      'Authorization': `Bearer ${apiKey}`,
      'Content-Type': 'application/json'
    };
  }
  
  async getStatus() {
    const response = await fetch(`${this.baseUrl}/status`, {
      headers: this.headers
    });
    return response.json();
  }
  
  async createBot(botType, config) {
    const response = await fetch(`${this.baseUrl}/bots/${botType}`, {
      method: 'POST',
      headers: this.headers,
      body: JSON.stringify({ config })
    });
    const result = await response.json();
    return result.data.bot_id;
  }
}

// Usage
const client = new TradeMasterXClient('http://localhost:5000/api', 'your-api-key');
const status = await client.getStatus();
const botId = await client.createBot('analytics', { windowSize: 100 });
```

This API reference provides comprehensive documentation for integrating with and controlling the TradeMasterX 2.0 system programmatically.
