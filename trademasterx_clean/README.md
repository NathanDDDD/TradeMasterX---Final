# TradeMasterX 2.0 - Advanced AI Trading System

TradeMasterX 2.0 is a comprehensive, autonomous AI-powered trading system designed for cryptocurrency markets. It features advanced machine learning, real-time monitoring, and multi-phase development with safety controls.

## Features

- **Autonomous AI Trading**: Multi-agent system with reinforcement learning
- **Real-time Analytics**: Advanced market analysis and pattern recognition
- **Machine Learning**: Continuous model retraining and optimization
- **Safety Controls**: Comprehensive risk management and emergency stops
- **Web Dashboard**: Real-time monitoring and control interface
- **Desktop GUI**: Streamlit-based control center
- **CLI Interface**: Command-line control and automation
- **Multi-Strategy Support**: Dynamic strategy switching based on market conditions

## Project Structure

- `trademasterx/`: Main application source code
  - `ai/`: Core AI and machine learning components
  - `bots/`: Trading bot implementations
  - `core/`: Core system logic and controllers
  - `interface/`: Web, CLI, and GUI interfaces
  - `config/`: Configuration files
- `tests/`: Unit and integration tests
- `data/`: Trading data, logs, and models
- `scripts/`: Utility and maintenance scripts
- `main_app.py`: Main application entry point
- `setup.py`: Project installation script
- `requirements_new.txt`: Python dependencies

## Quick Start

### 1. Setup Environment

- **Prerequisites**:
  - Python 3.8+
  - `pip` and `venv`

- **Create virtual environment**:
  ```bash
  python -m venv .venv
  source .venv/bin/activate  # On Windows: .venv\Scripts\activate
  ```

### 2. Install Dependencies

Install the project in editable mode with all dependencies:
```bash
pip install -r requirements_new.txt
pip install -e .
```

### 3. Configure the System

- Copy `.env.example` to `.env`
- Add your API keys and other configurations to the `.env` file.

### 4. Run the Application

- **Main Application**:
  ```bash
  python main_app.py
  ```

- **Standalone Dashboard**:
  ```bash
  python start_dashboard.py
  ```

- **Run Tests**:
  ```bash
  python run_tests.py
  ```

## Usage

- **Web Dashboard**: Open `http://localhost:8080` to monitor the system in real-time.
- **Interactive CLI**: The main application runs in an interactive mode. Use commands like `status`, `help`, or `exit`.
- **Command Assistant**: Use natural language to control the bot (e.g., "pause the system", "show performance").

## Contributing

Contributions are welcome! Please create a pull request with a clear description of your changes.

---
Thank you for using TradeMasterX 2.0!
