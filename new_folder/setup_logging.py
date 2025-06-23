#!/usr/bin/env python3
"""
TradeMasterX 2.0 - Logging Setup Utility
Handles Unicode encoding issues on Windows systems
"""

import logging
import sys
import os
from pathlib import Path

def setup_logging(level=logging.INFO, log_file=None):
    """Setup logging with proper Unicode handling"""
    
    # Create logs directory if it doesn't exist
    if log_file:
        log_dir = Path(log_file).parent
        log_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure logging format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create handlers
    handlers = []
    
    # Console handler with Unicode support
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Handle Windows encoding issues
    if sys.platform == 'win32':
        # Use UTF-8 encoding for console output
        console_handler.setStream(sys.stdout)
        # Remove emojis from console output to avoid encoding issues
        class UnicodeFilter(logging.Filter):
            def filter(self, record):
                # Remove common emoji characters that cause issues
                if hasattr(record, 'msg') and isinstance(record.msg, str):
                    # Replace emojis with text equivalents
                    emoji_replacements = {
                        '🔍': '[CHECK]', '📁': '[DIR]', '✅': '[OK]', '❌': '[ERROR]',
                        '🔧': '[TOOL]', '🤖': '[AI]', '📊': '[DATA]', '📋': '[LIST]',
                        '🛑': '[STOP]', '🎛️': '[CONTROL]', '🌐': '[WEB]', '🎮': '[DEMO]',
                        '💰': '[MONEY]', '🚨': '[ALERT]', '🔄': '[SYNC]', '⏸️': '[PAUSE]',
                        '🛑': '[STOP]', '✅': '[OK]', '❓': '[QUESTION]', '💡': '[TIP]',
                        '⚠️': '[WARNING]', '🎉': '[SUCCESS]', '📈': '[CHART]', '🌍': '[GLOBAL]'
                    }
                    for emoji, replacement in emoji_replacements.items():
                        record.msg = record.msg.replace(emoji, replacement)
                return True
        
        console_handler.addFilter(UnicodeFilter())
    
    handlers.append(console_handler)
    
    # File handler if specified
    if log_file:
        try:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(formatter)
            handlers.append(file_handler)
        except Exception as e:
            print(f"Warning: Could not create log file {log_file}: {e}")
    
    # Configure root logger
    logging.basicConfig(
        level=level,
        handlers=handlers,
        force=True  # Override any existing configuration
    )
    
    return logging.getLogger()

def get_logger(name, level=logging.INFO):
    """Get a logger with proper Unicode handling"""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Ensure the logger has handlers
    if not logger.handlers:
        # Add a console handler if none exists
        console_handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger 