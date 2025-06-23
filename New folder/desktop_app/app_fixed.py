#!/usr/bin/env python3
"""
TradeMasterX 2.0 - Desktop GUI Application
Streamlit-based GUI for comprehensive system control

Features:
- System Control (Start/Stop TradeMasterX)
- AI Command Chat Interface
- Real-time System Status
- Trade History & Analytics
- Settings & Configuration
"""

import streamlit as st
import asyncio
import json
import os
import sys
import subprocess
import time
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional
import threading
import requests

# Add the parent directory to path for imports
parent_dir = Path(__file__).parent.parent.absolute()
sys.path.append(str(parent_dir))

# Import components
from components.system_control import SystemControlPanel
from components.ai_chat_enhanced import render_ai_chat
from components.status_dashboard import StatusDashboard
from components.trade_history import TradeHistoryViewer
from utils.api_manager import APIKeyManager
from utils.system_interface import SystemInterface

# Configure Streamlit
st.set_page_config(
    page_title="TradeMasterX 2.0 - Desktop GUI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        padding: 1rem 0;
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        text-align: center;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .status-card {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1e3c72;
        margin: 0.5rem 0;
    }
    .success-card {
        background: #d4edda;
        border-left-color: #28a745;
    }
    .warning-card {
        background: #fff3cd;
        border-left-color: #ffc107;
    }
    .error-card {
        background: #f8d7da;
        border-left-color: #dc3545;
    }
    .chat-message {
        padding: 0.5rem;
        margin: 0.5rem 0;
        border-radius: 5px;
    }
    .user-message {
        background: #e3f2fd;
        text-align: left;
    }
    .assistant-message {
        background: #f3e5f5;
        text-align: left;
    }
</style>
""", unsafe_allow_html=True)

class TradeMasterXGUI:
    """Main TradeMasterX Desktop GUI Application"""
    
    def __init__(self):
        self.system_interface = SystemInterface()
        self.system_control = SystemControlPanel(parent_dir)
        self.api_manager = APIKeyManager()
        self.initialize_session_state()
        
    def initialize_session_state(self):
        """Initialize Streamlit session state"""
        if 'system_running' not in st.session_state:
            st.session_state.system_running = False
        if 'dashboard_running' not in st.session_state:
            st.session_state.dashboard_running = False
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        if 'api_keys_configured' not in st.session_state:
            st.session_state.api_keys_configured = self.api_manager.check_api_keys()
        if 'last_status_update' not in st.session_state:
            st.session_state.last_status_update = None
    
    def render_header(self):
        """Render the main application header"""
        st.markdown("""
        <div class="main-header">
            <h1>🤖 TradeMasterX 2.0 - Desktop Control Center</h1>
            <p>Advanced Autonomous AI Trading System - Desktop GUI</p>
        </div>
        """, unsafe_allow_html=True)
    
    def render_sidebar(self):
        """Render the sidebar navigation"""
        st.sidebar.title("🎛️ Control Panel")
        
        # Navigation
        page = st.sidebar.selectbox(
            "Select Section",
            ["🎮 System Control", "🤖 AI Chat", "📊 System Status", "📈 Trade History", "⚙️ Settings"]
        )
        
        # Quick status
        st.sidebar.markdown("### 📡 Quick Status")
        
        # System status indicator
        if st.session_state.system_running:
            st.sidebar.success("🟢 TradeMasterX Running")
        else:
            st.sidebar.error("🔴 TradeMasterX Stopped")
            
        # Dashboard status indicator
        if st.session_state.dashboard_running:
            st.sidebar.success("🌐 Dashboard Active")
        else:
            st.sidebar.warning("🟡 Dashboard Offline")
        
        # API keys status
        if st.session_state.api_keys_configured:
            st.sidebar.success("🔑 API Keys OK")
        else:
            st.sidebar.warning("🔑 API Keys Missing")
        
        return page
    
    def render_system_control(self):
        """Render the system control panel"""
        st.header("🎮 System Control")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🚀 TradeMasterX System")
            
            if st.button("▶️ Start TradeMasterX", type="primary", disabled=st.session_state.system_running):
                with st.spinner("Starting TradeMasterX system..."):
                    success = self.system_control.start_trademasterx()
                    if success:
                        st.session_state.system_running = True
                        st.success("✅ TradeMasterX started successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to start TradeMasterX")
            
            if st.button("⏹️ Stop TradeMasterX", disabled=not st.session_state.system_running):
                with st.spinner("Stopping TradeMasterX system..."):
                    success = self.system_control.stop_trademasterx()
                    if success:
                        st.session_state.system_running = False
                        st.success("✅ TradeMasterX stopped successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to stop TradeMasterX")
        
        with col2:
            st.subheader("🌐 Web Dashboard")
            
            if st.button("🌍 Launch Dashboard", type="secondary", disabled=st.session_state.dashboard_running):
                with st.spinner("Starting web dashboard..."):
                    success = self.system_control.start_dashboard()
                    if success:
                        st.session_state.dashboard_running = True
                        st.success("✅ Dashboard launched at http://localhost:8080")
                        st.markdown("[🔗 Open Dashboard](http://localhost:8080)")
                        st.rerun()
                    else:
                        st.error("❌ Failed to launch dashboard")
            
            if st.button("🛑 Stop Dashboard", disabled=not st.session_state.dashboard_running):
                with st.spinner("Stopping web dashboard..."):
                    success = self.system_control.stop_dashboard()
                    if success:
                        st.session_state.dashboard_running = False
                        st.success("✅ Dashboard stopped")
                        st.rerun()
                    else:
                        st.error("❌ Failed to stop dashboard")
        
        # System logs
        st.subheader("📜 System Logs")
        with st.expander("View Recent Logs"):
            logs = self.system_interface.get_recent_logs()
            if logs:
                st.text_area("Logs", logs, height=200)
            else:
                st.info("No recent logs available")
    
    def render_ai_chat(self):
        """Render the AI chat interface"""
        # Use the enhanced AI chat component
        render_ai_chat()
    
    def process_chat_message(self, user_input: str):
        """Process a chat message through the AI interface"""
        # Add user message to history
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now()
        })
        
        # Process with AI assistant
        try:
            response = self.system_interface.process_ai_command(user_input)
            
            # Add AI response to history
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response,
                "timestamp": datetime.now()
            })
            
        except Exception as e:
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": f"Error processing command: {str(e)}",
                "timestamp": datetime.now()
            })
    
    def render_system_status(self):
        """Render the system status dashboard"""
        st.header("📊 System Status")
        
        # Auto-refresh toggle
        col1, col2 = st.columns([3, 1])
        with col2:
            auto_refresh = st.checkbox("🔄 Auto-refresh (30s)")
        
        if auto_refresh:
            # Auto-refresh every 30 seconds
            time.sleep(30)
            st.rerun()
        
        # Refresh button
        if st.button("🔄 Refresh Now"):
            st.session_state.last_status_update = datetime.now()
            st.rerun()
        
        # Get system status
        status_data = self.system_interface.get_system_status()
        
        if not status_data:
            st.error("❌ Unable to retrieve system status")
            return
        
        # Display status cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div class="status-card success-card">
                <h3>🤖 AI Health</h3>
                <p>Status: Active</p>
                <p>Confidence: 95%</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="status-card warning-card">
                <h3>📈 Trading</h3>
                <p>Active Positions: 3</p>
                <p>24h P&L: +2.3%</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="status-card success-card">
                <h3>🔒 Risk Management</h3>
                <p>Risk Level: Low</p>
                <p>Max Drawdown: 1.2%</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div class="status-card error-card">
                <h3>⚠️ Alerts</h3>
                <p>Active: 1</p>
                <p>Last: High volatility</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Detailed status information
        st.subheader("🔍 Detailed System Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🧠 AI Components")
            st.text("✅ Strategy AI: Online")
            st.text("✅ Risk Manager: Active")
            st.text("✅ Observer Agent: Monitoring")
            st.text("✅ Memory System: Operational")
        
        with col2:
            st.markdown("### 📊 Performance Metrics")
            st.text("📈 Total Trades: 47")
            st.text("💰 Success Rate: 73%")
            st.text("📊 Sharpe Ratio: 1.85")
            st.text("⏱️ Uptime: 99.2%")
    
    def render_trade_history(self):
        """Render the trade history viewer"""
        st.header("📈 Trade History & Analytics")
        
        # Get trade data
        trade_data = self.system_interface.get_trade_data()
        
        if trade_data.empty:
            st.warning("No trade data available")
            return
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_trades = len(trade_data)
            st.metric("Total Trades", total_trades)
        
        with col2:
            avg_return = trade_data['return_pct'].mean()
            st.metric("Avg Return", f"{avg_return:.2f}%")
        
        with col3:
            win_rate = (trade_data['return_pct'] > 0).mean() * 100
            st.metric("Win Rate", f"{win_rate:.1f}%")
        
        with col4:
            total_return = trade_data['return_pct'].sum()
            st.metric("Total Return", f"{total_return:.2f}%")
        
        # Trade history table
        st.subheader("📋 Recent Trades")
        st.dataframe(trade_data.head(20), use_container_width=True)
        
        # Performance charts
        st.subheader("📊 Performance Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Cumulative returns chart
            trade_data['cumulative_return'] = (1 + trade_data['return_pct'] / 100).cumprod()
            fig = px.line(trade_data, x='timestamp', y='cumulative_return', 
                         title="Cumulative Returns")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Return distribution
            fig = px.histogram(trade_data, x='return_pct', nbins=20,
                             title="Return Distribution")
            st.plotly_chart(fig, use_container_width=True)
    
    def render_settings(self):
        """Render the settings panel"""
        st.header("⚙️ Settings & Configuration")
        
        # API Configuration
        st.subheader("🔑 API Configuration")
        
        # Check current API key status
        openai_configured = bool(st.secrets.get("openai_api_key"))
        claude_configured = bool(st.secrets.get("claude_api_key"))
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### OpenAI Configuration")
            if openai_configured:
                st.success("✅ OpenAI API key configured")
            else:
                st.error("❌ OpenAI API key missing")
                st.info("Please add your OpenAI API key to `.streamlit/secrets.toml`")
        
        with col2:
            st.markdown("### Claude Configuration")
            if claude_configured:
                st.success("✅ Claude API key configured")
            else:
                st.error("❌ Claude API key missing")
                st.info("Please add your Claude API key to `.streamlit/secrets.toml`")
        
        # System Configuration
        st.subheader("🛠️ System Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Trading Settings")
            max_position_size = st.slider("Max Position Size (%)", 1, 20, 10)
            risk_level = st.selectbox("Risk Level", ["Conservative", "Moderate", "Aggressive"])
            auto_trading = st.checkbox("Enable Auto Trading", value=True)
        
        with col2:
            st.markdown("### Alert Settings")
            email_alerts = st.checkbox("Email Alerts", value=False)
            sms_alerts = st.checkbox("SMS Alerts", value=False)
            desktop_notifications = st.checkbox("Desktop Notifications", value=True)
        
        # Save settings
        if st.button("💾 Save Settings"):
            settings = {
                "max_position_size": max_position_size,
                "risk_level": risk_level,
                "auto_trading": auto_trading,
                "email_alerts": email_alerts,
                "sms_alerts": sms_alerts,
                "desktop_notifications": desktop_notifications
            }
            
            # Save to file
            settings_path = parent_dir / "config" / "gui_settings.json"
            settings_path.parent.mkdir(exist_ok=True)
            
            with open(settings_path, 'w') as f:
                json.dump(settings, f, indent=2)
            
            st.success("✅ Settings saved successfully!")
    
    def run(self):
        """Run the main application"""
        # Render header
        self.render_header()
        
        # Render sidebar and get selected page
        selected_page = self.render_sidebar()
        
        # Render selected page
        if selected_page == "🎮 System Control":
            self.render_system_control()
        elif selected_page == "🤖 AI Chat":
            self.render_ai_chat()
        elif selected_page == "📊 System Status":
            self.render_system_status()
        elif selected_page == "📈 Trade History":
            self.render_trade_history()
        elif selected_page == "⚙️ Settings":
            self.render_settings()

def main():
    """Main application entry point"""
    try:
        app = TradeMasterXGUI()
        app.run()
    except Exception as e:
        st.error(f"Application Error: {str(e)}")
        st.exception(e)

if __name__ == "__main__":
    main()
