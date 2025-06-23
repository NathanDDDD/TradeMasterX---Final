#!/usr/bin/env python3
"""
TradeMasterX 2.0 Setup Script
Production-grade Python package setup with comprehensive dependencies and entry points
"""

from setuptools import setup, find_packages
import os
import sys
from pathlib import Path

# Read version from __init__.py
def get_version():
    init_file = Path(__file__).parent / "trademasterx" / "__init__.py"
    if init_file.exists():
        with open(init_file, "r") as f:
            for line in f:
                if line.startswith("__version__"):
                    return line.split("=")[1].strip().strip('"').strip("'")
    return "2.0.0"

# Read the contents of your README file
def get_long_description():
    this_directory = Path(__file__).parent
    return (this_directory / "README.md").read_text(encoding='utf-8')

# Read requirements
def get_requirements():
    req_file = Path(__file__).parent / "requirements.txt"
    if req_file.exists():
        with open(req_file, "r") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return [
        # Core dependencies
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "scipy>=1.7.0",
        "scikit-learn>=1.0.0",
        
        # Web interface
        "flask>=2.0.0",
        "flask-socketio>=5.0.0",
        "werkzeug>=2.0.0",
        
        # Configuration and data
        "pyyaml>=6.0",
        "python-dotenv>=0.19.0",
        "click>=8.0.0",
        
        # Database and caching
        "sqlalchemy>=1.4.0",
        "redis>=4.0.0",
        "sqlite3",  # Usually included with Python
        
        # Async and concurrency
        "asyncio",
        "threading",
        "multiprocessing",
        
        # Monitoring and logging
        "psutil>=5.8.0",
        "structlog>=21.0.0",
        
        # Data analysis and visualization
        "matplotlib>=3.4.0",
        "seaborn>=0.11.0",
        "plotly>=5.0.0",
        
        # Time series and financial
        "pandas-ta>=0.3.0",
        "yfinance>=0.1.70",
        
        # Testing and development
        "pytest>=6.0.0",
        "pytest-asyncio>=0.18.0",
        "black>=21.0.0",
        "flake8>=4.0.0",
        "mypy>=0.910",
    ]

# Development requirements
def get_dev_requirements():
    return [
        "pytest>=6.0.0",
        "pytest-cov>=2.12.0",
        "pytest-asyncio>=0.18.0",
        "black>=21.0.0",
        "flake8>=4.0.0",
        "mypy>=0.910",
        "pre-commit>=2.15.0",
        "sphinx>=4.0.0",
        "sphinx-rtd-theme>=1.0.0",
        "tox>=3.24.0",
    ]

# Optional dependencies for different features
extras_require = {
    "web": [
        "flask>=2.0.0",
        "flask-socketio>=5.0.0",
        "gunicorn>=20.1.0",
    ],
    "redis": [
        "redis>=4.0.0",
        "hiredis>=2.0.0",
    ],
    "postgresql": [
        "psycopg2-binary>=2.9.0",
    ],
    "monitoring": [
        "prometheus-client>=0.11.0",
        "grafana-api>=1.0.0",
    ],
    "ml": [
        "tensorflow>=2.7.0",
        "torch>=1.10.0",
        "xgboost>=1.5.0",
        "lightgbm>=3.3.0",
    ],
    "dev": get_dev_requirements(),
}

# All optional dependencies
extras_require["all"] = list(set(sum(extras_require.values(), [])))

setup(
    # Basic package information
    name="trademasterx",
    version=get_version(),
    description="Advanced AI-Powered Trading System with Intelligent Bot Management",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    
    # Author and contact information
    author="TradeMasterX Development Team",
    author_email="dev@trademasterx.com",
    maintainer="TradeMasterX Team",
    maintainer_email="support@trademasterx.com",
    
    # URLs and links
    url="https://github.com/trademasterx/trademasterx",
    project_urls={
        "Documentation": "https://docs.trademasterx.com",
        "Source": "https://github.com/trademasterx/trademasterx",
        "Tracker": "https://github.com/trademasterx/trademasterx/issues",
        "Funding": "https://github.com/sponsors/trademasterx",
    },
    
    # Package configuration
    packages=find_packages(exclude=["tests*", "docs*", "examples*"]),
    include_package_data=True,
    package_data={
        "trademasterx": [
            "config/*.yaml",
            "config/*.json",
            "interface/web/templates/*.html",
            "interface/web/static/css/*.css",
            "interface/web/static/js/*.js",
            "data/*.sql",
            "schemas/*.json",
        ],
    },
    
    # Dependencies
    python_requires=">=3.8",
    install_requires=get_requirements(),
    extras_require=extras_require,
    
    # Entry points for command-line scripts
    entry_points={
        "console_scripts": [
            # Main launchers
            "trademasterx=trademasterx.cli:main",
            "tmx=trademasterx.cli:main",
            
            # Specific components
            "tmx-web=trademasterx.interface.web.app:main",
            "tmx-master=trademasterx.core.master_bot:main",
            "tmx-validate=trademasterx.core.validation:main",
            
            # Bot management
            "tmx-bot=trademasterx.cli.bot_cli:main",
            "tmx-analytics=trademasterx.bots.analytics.analytics_bot:main",
            "tmx-strategy=trademasterx.bots.strategy.strategy:main",
            "tmx-risk=trademasterx.bots.system.risk_bot:main",
            
            # Utilities
            "tmx-config=trademasterx.config.config_loader:main",
            "tmx-logs=trademasterx.bots.system.logger_bot:main",
            "tmx-backup=trademasterx.utils.backup:main",
        ],
        
        # Plugin system for custom bots
        "trademasterx.bots": [
            "analytics=trademasterx.bots.analytics.analytics_bot:AnalyticsBot",
            "strategy=trademasterx.bots.strategy.strategy:StrategyBot",
            "risk=trademasterx.bots.system.risk_bot:RiskBot",
            "memory=trademasterx.bots.system.memory_bot:MemoryBot",
            "logger=trademasterx.bots.system.logger_bot:LoggerBot",
        ],
        
        # Configuration presets
        "trademasterx.presets": [
            "conservative=trademasterx.config.presets:conservative_config",
            "aggressive=trademasterx.config.presets:aggressive_config",
            "balanced=trademasterx.config.presets:balanced_config",
        ],
    },
    
    # Classification
    classifiers=[
        # Development Status
        "Development Status :: 4 - Beta",
        
        # Intended Audience
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        
        # Topic
        "Topic :: Office/Business :: Financial",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        
        # License
        "License :: OSI Approved :: MIT License",
        
        # Programming Language
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        
        # Operating System
        "Operating System :: OS Independent",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",
        
        # Environment
        "Environment :: Console",
        "Environment :: Web Environment",
        
        # Natural Language
        "Natural Language :: English",
    ],
    
    # Keywords for PyPI search
    keywords=[
        "trading", "algorithmic-trading", "quantitative-finance",
        "ai", "machine-learning", "bot", "automation",
        "financial-analysis", "risk-management", "portfolio",
        "backtesting", "strategy", "signals", "analytics",
        "flask", "web-interface", "real-time", "monitoring"
    ],
    
    # Minimum Python version and platform requirements
    platforms=["any"],
    
    # Zip safety
    zip_safe=False,
      # Testing
    
    # Command-line options for setup.py
    options={
        "build_scripts": {
            "executable": sys.executable,
        },
        "egg_info": {
            "tag_build": "",
            "tag_date": False,
        },
    },
      # Additional metadata for packaging
    license="MIT",
    
    # Data files outside of package
    data_files=[
        ("config", [
            "trademasterx/config/system.yaml",
            "trademasterx/config/bots.yaml", 
            "trademasterx/config/strategies.yaml"
        ]),
        ("docs", ["README.md", "CHANGELOG.md"]),
    ],
)

# Post-install message
if __name__ == "__main__":
    print("\n" + "="*60)
    print(" TradeMasterX 2.0 Installation Complete!")
    print("="*60)
    print("\nQuick Start:")
    print("  1. Initialize configuration: tmx config init")
    print("  2. Start web interface:     tmx web --port 5000")
    print("  3. Launch master bot:       tmx master start")
    print("  4. View help:               tmx --help")
    print("\nDocumentation: https://docs.trademasterx.com")
    print("Support: https://github.com/trademasterx/trademasterx/issues")
    print("="*60 + "\n")
