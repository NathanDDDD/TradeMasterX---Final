"""
Status Dashboard Component
Displays real-time system status and metrics
"""

import streamlit as st
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

class StatusDashboard:
    """Real-time system status dashboard"""
    
    def __init__(self, parent_dir: Path):
        self.parent_dir = parent_dir
        self.status_file = parent_dir / "reports" / "ai_status.json"
        self.reports_dir = parent_dir / "reports"
    
    def load_system_status(self) -> Optional[Dict[str, Any]]:
        """Load system status from JSON file"""
        try:
            if self.status_file.exists():
                with open(self.status_file, 'r') as f:
                    return json.load(f)
            else:
                # Return mock data if file doesn't exist
                return self.get_mock_status()
        except Exception as e:
            st.warning(f"Could not load status file: {e}")
            return self.get_mock_status()
    
    def get_mock_status(self) -> Dict[str, Any]:
        """Generate mock status data for demonstration"""
        return {
            "timestamp": datetime.now().isoformat(),
            "system_health": {
                "status": "HEALTHY",
                "uptime": "2h 34m",
                "memory_usage": "45%",
                "cpu_usage": "23%"
            },
            "ai_status": {
                "confidence": 0.87,
                "active": True,
                "last_decision": "2 minutes ago"
            },
            "anomalies": {
                "count": 0,
                "last_detected": "None",
                "severity": "Low"
            },
            "strategies": {
                "momentum_strategy": {
                    "weight": 1.2,
                    "active": True,
                    "performance": 0.15
                },
                "mean_reversion": {
                    "weight": 0.8,
                    "active": True,
                    "performance": 0.08
                },
                "breakout_strategy": {
                    "weight": 1.1,
                    "active": False,
                    "performance": 0.12
                }
            },
            "components": {
                "observer_agent": "ACTIVE",
                "ai_orchestrator": "ACTIVE",
                "reinforcement_engine": "ACTIVE",
                "anomaly_auditor": "ACTIVE",
                "dashboard": "ACTIVE"
            },
            "performance": {
                "total_trades": 247,
                "win_rate": 0.73,
                "avg_return": 0.089,
                "sharpe_ratio": 1.42
            }
        }
    
    def get_recent_alerts(self) -> pd.DataFrame:
        """Get recent system alerts"""
        try:
            # Look for alert files in reports directory
            alert_files = list(self.reports_dir.glob("*alert*.json"))
            alerts = []
            
            for file in alert_files[-10:]:  # Last 10 alerts
                try:
                    with open(file, 'r') as f:
                        alert_data = json.load(f)
                        alerts.append({
                            "timestamp": alert_data.get("timestamp", "Unknown"),
                            "type": alert_data.get("type", "Unknown"),
                            "message": alert_data.get("message", "No message"),
                            "severity": alert_data.get("severity", "Info")
                        })
                except:
                    continue
            
            if alerts:
                return pd.DataFrame(alerts)
            else:
                # Return sample alerts
                return pd.DataFrame([
                    {
                        "timestamp": "2025-06-13T21:30:00",
                        "type": "Performance",
                        "message": "Strategy momentum_strategy showing strong performance",
                        "severity": "Info"
                    },
                    {
                        "timestamp": "2025-06-13T21:15:00",
                        "type": "System",
                        "message": "AI model confidence above 85%",
                        "severity": "Info"
                    }
                ])
                
        except Exception as e:
            st.warning(f"Could not load alerts: {e}")
            return pd.DataFrame()
    
    def get_performance_metrics(self) -> Dict[str, float]:
        """Get performance metrics"""
        status = self.load_system_status()
        if status and "performance" in status:
            return status["performance"]
        
        # Mock performance data
        return {
            "total_trades": 247,
            "win_rate": 0.73,
            "avg_return": 0.089,
            "sharpe_ratio": 1.42,
            "max_drawdown": -0.045,
            "profit_factor": 2.1
        }
    
    def format_uptime(self, uptime_str: str) -> str:
        """Format uptime string for display"""
        try:
            # Parse uptime and format nicely
            return uptime_str
        except:
            return "Unknown"
    
    def get_health_color(self, status: str) -> str:
        """Get color for health status"""
        status_colors = {
            "HEALTHY": "green",
            "ACTIVE": "green",
            "WARNING": "orange",
            "ERROR": "red",
            "INACTIVE": "gray"
        }
        return status_colors.get(status.upper(), "gray")
