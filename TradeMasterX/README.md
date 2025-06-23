# TradeMasterX

A modular, extensible, and robust trading system for research, demo, and live trading. Inspired by the best open-source trading bots and designed for rapid experimentation and deployment.

## Features
- Modular analyzers (patterns, indicators, sentiment, news, copy trading)
- MasterBot for signal aggregation and decision-making
- Persistent memory and logging
- Configurable via YAML
- Extensible for new strategies and data sources
- Mini log for quick debugging and monitoring

## Project Structure
```
TradeMasterX/
  ├── trademasterx/
  │     ├── core/
  │     ├── utils/
  ├── tests/
  ├── config.yaml
  ├── memory.json
  ├── mini_log.txt
  ├── requirements.txt
  ├── README.md
  └── launch.py
```

## Setup
1. **Install Python 3.10** (recommended)
2. **Create and activate a virtual environment:**
   ```sh
   python3.10 -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```
3. **Install requirements:**
   ```sh
   pip install -r requirements.txt
   ```
4. **Run the demo:**
   ```sh
   python launch.py
   ```

## Running Tests
```sh
PYTHONPATH=TradeMasterX python -m unittest discover -s TradeMasterX/tests
```

## Architecture Overview
- **MasterBot:** Aggregates signals from all analyzers and makes decisions.
- **Analyzers:** Each module analyzes a different aspect (patterns, indicators, sentiment, news, copy trading).
- **Memory:** Stores signals and trades persistently.
- **Config:** Loads settings from YAML.
- **Mini Log:** Tracks all major events for quick debugging.

## Extending
- Add new analyzers in `trademasterx/core/analyzers/`.
- Update config as needed in `config.yaml`.
- Use the mini log for fast troubleshooting.

## License
MIT 