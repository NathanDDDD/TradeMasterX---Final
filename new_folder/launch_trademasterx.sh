#!/bin/bash
# TradeMasterX 2.0 - Production Launch Script for Linux/Mac
# Phase 15 Complete - Launch Ready System

echo "==============================================================================="
echo "TRADEMASTERX 2.0 - PRODUCTION LAUNCH"
echo "Phase 15 Complete - AI Trading System Ready"
echo "==============================================================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8+ and try again"
    exit 1
fi

echo "Python installation: OK"

# Check if required files exist
if [ ! -f "phase_14_complete_autonomous_ai.py" ]; then
    echo "ERROR: Core AI system file missing"
    echo "Please ensure all TradeMasterX files are present"
    exit 1
fi

if [ ! -f "main_app.py" ]; then
    echo "ERROR: Main application file missing"
    echo "Please ensure all TradeMasterX files are present"
    exit 1
fi

echo "Core files: OK"

# Create required directories
mkdir -p logs reports data

echo "Directories: OK"

echo ""
echo "==============================================================================="
echo "LAUNCHING TRADEMASTERX 2.0..."
echo "==============================================================================="
echo ""
echo "Choose launch mode:"
echo "1. Quick Validation Test (Recommended first run)"
echo "2. Production Launch (Full system)"
echo "3. Development Mode (Main app only)"
echo ""
read -p "Enter your choice (1-3): " choice

case $choice in
    1)
        echo ""
        echo "Running validation test..."
        python3 quick_phase_15_validation.py
        echo ""
        echo "Validation complete. Check results above."
        read -p "Press Enter to continue..."
        ;;
    2)
        echo ""
        echo "Starting production system..."
        echo "Dashboard will open at: http://localhost:8080"
        echo "Press Ctrl+C to shutdown gracefully"
        echo ""
        python3 launch_production.py
        ;;
    3)
        echo ""
        echo "Starting development mode..."
        python3 main_app.py
        ;;
    *)
        echo "Invalid choice. Please run the script again."
        exit 1
        ;;
esac

echo ""
echo "==============================================================================="
echo "TradeMasterX 2.0 session ended"
echo "==============================================================================="
