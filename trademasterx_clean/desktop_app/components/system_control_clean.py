"""
System Control Panel Component - Clean Version
Handles starting/stopping TradeMasterX and dashboard
"""

import subprocess
import time
from pathlib import Path
from typing import Optional

class SystemControlPanel:
    """System control panel for TradeMasterX operations"""
    
    def __init__(self, parent_dir: Path):
        self.parent_dir = parent_dir
        self.trademasterx_process: Optional[subprocess.Popen] = None
        self.dashboard_process: Optional[subprocess.Popen] = None
    
    def start_trademasterx(self) -> bool:
        """Start the TradeMasterX system"""
        try:
            launch_script = self.parent_dir / "launch_production.py"
            
            if not launch_script.exists():
                print(f"Launch script not found: {launch_script}")
                return False
            
            # Start in background
            self.trademasterx_process = subprocess.Popen(
                ["python", str(launch_script)],
                cwd=str(self.parent_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Give it a moment to start
            time.sleep(2)
            
            # Check if process is still running
            return self.trademasterx_process.poll() is None
                
        except Exception as e:
            print(f"Error starting TradeMasterX: {e}")
            return False
    
    def stop_trademasterx(self) -> bool:
        """Stop the TradeMasterX system"""
        try:
            if self.trademasterx_process:
                self.trademasterx_process.terminate()
                self.trademasterx_process.wait(timeout=10)
                self.trademasterx_process = None
            return True
        except Exception as e:
            print(f"Error stopping TradeMasterX: {e}")
            return False
    
    def start_dashboard(self) -> bool:
        """Start the web dashboard"""
        try:
            dashboard_script = self.parent_dir / "simple_dashboard.py"
            
            if not dashboard_script.exists():
                print(f"Dashboard script not found: {dashboard_script}")
                return False
            
            # Start in background
            self.dashboard_process = subprocess.Popen(
                ["python", str(dashboard_script)],
                cwd=str(self.parent_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Give it a moment to start
            time.sleep(3)
            
            # Check if process is still running
            return self.dashboard_process.poll() is None
                
        except Exception as e:
            print(f"Error starting dashboard: {e}")
            return False
    
    def stop_dashboard(self) -> bool:
        """Stop the web dashboard"""
        try:
            if self.dashboard_process:
                self.dashboard_process.terminate()
                self.dashboard_process.wait(timeout=10)
                self.dashboard_process = None
            return True
        except Exception as e:
            print(f"Error stopping dashboard: {e}")
            return False
    
    def is_trademasterx_running(self) -> bool:
        """Check if TradeMasterX is running"""
        return self.trademasterx_process and self.trademasterx_process.poll() is None
    
    def is_dashboard_running(self) -> bool:
        """Check if dashboard is running"""
        return self.dashboard_process and self.dashboard_process.poll() is None
