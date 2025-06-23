#!/usr/bin/env python3
"""
TradeMasterX 2.0 - Production Launcher
=====================================

Quick launcher for TradeMasterX 2.0 production system.
This script provides easy access to all system features.

Usage:
    python launcher.py test           # Run system tests
    python launcher.py cli            # Launch CLI interface
    python launcher.py chat           # Start AI chat assistant
    python launcher.py web            # Launch web dashboard
    python launcher.py status         # Show system status
"""

import sys
import os
import subprocess
import importlib
from pathlib import Path

def print_banner():
    """Print the TradeMasterX banner"""
    print("="*60)
    print(" TradeMasterX 2.0 - Production System")
    print("="*60)
    print()

def run_tests():
    """Run comprehensive system tests"""
    print("🧪 Running comprehensive system tests...")
    try:
        result = subprocess.run([sys.executable, "phase_tester.py"], 
                              capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Failed to run tests: {e}")
        return False

def launch_cli():
    """Launch CLI interface"""
    print("🖥️ Launching CLI interface...")
    try:
        subprocess.run([sys.executable, "-m", "trademasterx.interface.cli.cli", "--help"])
    except Exception as e:
        print(f"❌ Failed to launch CLI: {e}")

def launch_chat():
    """Launch AI chat assistant"""
    print("💬 Starting AI chat assistant...")
    try:
        subprocess.run([sys.executable, "-m", "trademasterx.interface.cli.cli", "chat"])
    except Exception as e:
        print(f"❌ Failed to launch chat: {e}")

def launch_web():
    """Launch web dashboard"""
    print("🌐 Launching web dashboard...")
    try:
        subprocess.run([sys.executable, "-m", "trademasterx.interface.web.app"])
    except Exception as e:
        print(f"❌ Failed to launch web dashboard: {e}")

def show_status():
    """Show system status"""
    print("📊 Checking system status...")
    
    # Check if TradeMasterX is importable
    try:
        import trademasterx
        print("✅ TradeMasterX package: Available")
    except ImportError:
        print("❌ TradeMasterX package: Not available")
        return
    
    # Check key components
    components = [
        ("Kill Switch", "trademasterx.core.kill_switch"),
        ("Safety Dashboard", "trademasterx.core.safety_dashboard"),
        ("Risk Guard", "trademasterx.core.risk_guard"),
        ("Command Assistant", "trademasterx.interface.assistant.command_assistant"),
        ("CLI Interface", "trademasterx.interface.cli.cli"),
        ("Web Interface", "trademasterx.interface.web.app")
    ]
    
    for name, module_path in components:
        try:
            importlib.import_module(module_path)
            print(f"✅ {name}: Available")
        except ImportError as e:
            print(f"❌ {name}: Not available ({e})")
    
    # Check dependencies
    dependencies = ["rich", "anthropic", "openai", "flask", "click"]
    print("\n📦 Dependencies:")
    for dep in dependencies:
        try:
            importlib.import_module(dep)
            print(f"✅ {dep}: Installed")
        except ImportError:
            print(f"❌ {dep}: Missing")

def show_help():
    """Show help message"""
    print(__doc__)

def main():
    """Main launcher function"""
    print_banner()
    
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == "test":
        success = run_tests()
        if success:
            print("\n🎉 All tests completed successfully!")
        else:
            print("\n⚠️ Some tests failed. Check output above.")
    
    elif command == "cli":
        launch_cli()
    
    elif command == "chat":
        launch_chat()
    
    elif command == "web":
        launch_web()
    
    elif command == "status":
        show_status()
    
    elif command in ["help", "-h", "--help"]:
        show_help()
    
    else:
        print(f"❌ Unknown command: {command}")
        print("\nAvailable commands: test, cli, chat, web, status, help")

if __name__ == "__main__":
    main()
