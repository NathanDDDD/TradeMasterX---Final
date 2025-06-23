#!/usr/bin/env python3
"""
TradeMasterX 2.0 - Phase 10 Full Operations
Runs both the learning loop and the analyzer for continuous model improvement
"""

import asyncio
import sys
import os
from pathlib import Path
import logging
import argparse
import signal
import subprocess
from datetime import datetime
import threading
import time

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/phase_10_ops.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("Phase10Operations")

# Track child processes for cleanup
child_processes = []
shutdown_event = threading.Event()

def signal_handler(sig, frame):
    """Handle interruption signals and cleanup"""
    logger.info("🛑 Shutdown signal received - stopping all processes")
    shutdown_event.set()
    
    for process in child_processes:
        if process.poll() is None:  # If process is still running
            logger.info(f"Terminating process PID: {process.pid}")
            try:
                process.terminate()
                process.wait(timeout=5)  # Wait up to 5 seconds
            except subprocess.TimeoutExpired:
                logger.warning(f"Force killing process PID: {process.pid}")
                process.kill()
    
    logger.info("✅ All processes terminated")
    sys.exit(0)

def start_phase_10_learning():
    """Start the Phase 10 learning loop in a separate process"""
    logger.info(" Starting Phase 10 learning loop...")
    
    try:
        learning_process = subprocess.Popen(
            ["python", "run_phase_10_direct.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        child_processes.append(learning_process)
        logger.info(f"✅ Learning loop started with PID: {learning_process.pid}")
        
        return learning_process
    except Exception as e:
        logger.error(f"❌ Failed to start learning loop: {e}")
        return None

def start_analyzer(interval_minutes=10):
    """Start the analyzer in continuous monitoring mode"""
    logger.info(f"📊 Starting analyzer with {interval_minutes} minute interval...")
    
    try:
        analyzer_process = subprocess.Popen(
            ["python", "phase_10_analyzer.py", "--monitor"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        child_processes.append(analyzer_process)
        logger.info(f"✅ Analyzer started with PID: {analyzer_process.pid}")
        
        return analyzer_process
    except Exception as e:
        logger.error(f"❌ Failed to start analyzer: {e}")
        return None

def monitor_processes(processes):
    """Monitor child processes and restart if they fail"""
    while True:
        for i, process in enumerate(processes):
            if process.poll() is not None:  # Process has exited
                exit_code = process.poll()
                stdout, stderr = process.communicate()
                
                logger.warning(f"⚠️ Process {process.pid} exited with code {exit_code}")
                
                if exit_code != 0:
                    logger.error(f"Process stderr: {stderr}")
                    
                    # Restart the process
                    if i == 0:  # Learning loop
                        logger.info("🔄 Restarting learning loop...")
                        processes[i] = start_phase_10_learning()
                    elif i == 1:  # Analyzer
                        logger.info("🔄 Restarting analyzer...")
                        processes[i] = start_analyzer()
                        
        # Check every 5 seconds
        time.sleep(5)

if __name__ == "__main__":
    # Setup argument parser
    parser = argparse.ArgumentParser(description='TradeMasterX 2.0 Phase 10 Operations')
    parser.add_argument('--learning-only', action='store_true', 
                        help='Start only the learning loop without analytics')
    parser.add_argument('--analytics-only', action='store_true',
                        help='Start only the analytics without the learning loop')
    parser.add_argument('--analyzer-interval', type=int, default=10,
                        help='Interval in minutes between analyzer runs (default: 10)')
    
    args = parser.parse_args()
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Print welcome banner
    print("\n" + "=" * 80)
    print(f" TRADEMASTERX 2.0 - PHASE 10 OPERATIONS")
    print(f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Start requested processes
    active_processes = []
    
    if args.analytics_only:
        analyzer = start_analyzer(args.analyzer_interval)
        if analyzer:
            active_processes.append(analyzer)
    elif args.learning_only:
        learning = start_phase_10_learning()
        if learning:
            active_processes.append(learning)
    else:
        # Start both by default
        learning = start_phase_10_learning()
        if learning:
            active_processes.append(learning)
            
        # Wait a bit for the learning loop to produce initial data
        import time
        time.sleep(20)
        
        analyzer = start_analyzer(args.analyzer_interval)
        if analyzer:
            active_processes.append(analyzer)
    
    if not active_processes:
        logger.error("❌ No processes started successfully - exiting")
        sys.exit(1)
        
    try:
        # Monitor and restart processes as needed
        monitor_processes(active_processes)
    except KeyboardInterrupt:
        logger.info("👋 Shutting down on user request")
        signal_handler(None, None)  # Use our cleanup handler
