@echo off
echo ====================================================
echo TradeMasterX 2.0 - Desktop GUI Launcher
echo ====================================================
echo.
echo Starting the desktop application...
echo.
echo The app will open in your browser at:
echo http://localhost:8501
echo.
echo Press Ctrl+C to stop the application
echo.

REM Navigate to the correct directory
cd /d "%~dp0"

REM Launch Streamlit app
python -m streamlit run desktop_app\app.py --server.headless true

pause
