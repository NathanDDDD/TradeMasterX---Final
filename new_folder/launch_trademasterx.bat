@echo off
REM TradeMasterX 2.0 - Production Launch Script for Windows
REM Phase 15 Complete - Launch Ready System

echo ===============================================================================
echo TRADEMASTERX 2.0 - PRODUCTION LAUNCH
echo Phase 15 Complete - AI Trading System Ready
echo ===============================================================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo Python installation: OK

REM Check if required files exist
if not exist "phase_14_complete_autonomous_ai.py" (
    echo ERROR: Core AI system file missing
    echo Please ensure all TradeMasterX files are present
    pause
    exit /b 1
)

if not exist "main_app.py" (
    echo ERROR: Main application file missing
    echo Please ensure all TradeMasterX files are present
    pause
    exit /b 1
)

echo Core files: OK

REM Create required directories
if not exist "logs" mkdir logs
if not exist "reports" mkdir reports
if not exist "data" mkdir data

echo Directories: OK

echo.
echo ===============================================================================
echo LAUNCHING TRADEMASTERX 2.0...
echo ===============================================================================
echo.
echo Choose launch mode:
echo 1. Quick Validation Test (Recommended first run)
echo 2. Production Launch (Full system)
echo 3. Development Mode (Main app only)
echo.
set /p choice="Enter your choice (1-3): "

if "%choice%"=="1" (
    echo.
    echo Running validation test...
    python quick_phase_15_validation.py
    echo.
    echo Validation complete. Check results above.
    pause
) else if "%choice%"=="2" (
    echo.
    echo Starting production system...
    echo Dashboard will open at: http://localhost:8080
    echo Press Ctrl+C to shutdown gracefully
    echo.
    python launch_production.py
) else if "%choice%"=="3" (
    echo.
    echo Starting development mode...
    python main_app.py
) else (
    echo Invalid choice. Please run the script again.
    pause
    exit /b 1
)

echo.
echo ===============================================================================
echo TradeMasterX 2.0 session ended
echo ===============================================================================
pause
