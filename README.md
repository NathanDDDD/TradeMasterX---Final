# TradeMasterX — Telegram Signals Channel

A Python bot that scans crypto markets and posts trading signals to a Telegram channel. Signals only — no trading execution, no portfolio management, no user interaction.

## What It Does

- Scans configurable trading pairs on a schedule (default: every 5 minutes)
- Runs 4 technical analysis strategies: RSI Reversal, MACD Cross, EMA Cross, Bollinger Bounce
- Only emits a signal when 2+ strategies agree (confluence filter)
- Posts clean, formatted signals to a Telegram channel with entry, SL, and 3 TP levels
- Sends a daily recap at end of day

## Signal Format

```
🔔 SIGNAL — LONG 🟢

Pair:      BTC/USDT
Entry:     68,200.00 — 68,500.00
Stop Loss: 66,800.00 ❌

🎯 TP1: 69,500.00 (50%)
🎯 TP2: 71,000.00 (30%)
🎯 TP3: 73,200.00 (20%)

Timeframe: 4h
Risk:      2%
R:R:       2.85
Strategy:  RSI Reversal + MACD Cross

— TradeMasterX
```

## Setup

### 1. Create Telegram Bot & Channel

1. Message [@BotFather](https://t.me/BotFather) → `/newbot` → copy the bot token
2. Create a Telegram Channel (e.g. `@TradeMasterXSignals`)
3. Add your bot as a channel **admin** with "Post Messages" permission

### 2. Configure

```bash
cp .env.example .env
```

Edit `.env` with your bot token and channel ID.

### 3. Install & Run

```bash
pip install -r requirements.txt
python main.py
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `TELEGRAM_BOT_TOKEN` | — | Bot token from @BotFather |
| `TELEGRAM_CHANNEL_ID` | — | Channel ID or @username |
| `EXCHANGE` | `binance` | Any CCXT-supported exchange |
| `TRADING_PAIRS` | `BTC/USDT,ETH/USDT,...` | Comma-separated pairs |
| `TIMEFRAMES` | `1h,4h` | Comma-separated timeframes |
| `SCAN_INTERVAL_MINUTES` | `5` | Minutes between scans |
| `MIN_CONFLUENCE` | `2` | Min indicators that must agree |

## Project Structure

```
├── config/settings.py          # Pydantic settings from .env
├── signals/
│   ├── data_fetcher.py         # CCXT OHLCV data
│   ├── indicators.py           # RSI, MACD, EMA, Bollinger
│   ├── strategies.py           # Signal logic + confluence
│   └── models.py               # Signal dataclass
├── telegram_bot/
│   ├── formatter.py            # Signal → Telegram message
│   └── publisher.py            # Send to channel
├── main.py                     # Entry point + scheduler loop
├── requirements.txt
└── .env.example
```
