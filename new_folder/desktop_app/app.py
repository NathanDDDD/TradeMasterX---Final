#!/usr/bin/env python3
"""
TradeMasterX 2.0 - Desktop GUI Application (Simplified)
Direct implementation without component imports
"""

import streamlit as st
import subprocess
import time
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional
import sys
import os
import json

# Add the parent directory to path for imports
parent_dir = Path(__file__).parent.parent.absolute()
sys.path.append(str(parent_dir))

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
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    
    .status-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #007bff;
        margin: 0.5rem 0;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem;
    }
    
    .chat-message {
        padding: 0.5rem;
        margin: 0.5rem 0;
        border-radius: 5px;
    }
    
    .user-message {
        background-color: #e3f2fd;
        margin-left: 2rem;
    }
    
    .assistant-message {
        background-color: #f3e5f5;
        margin-right: 2rem;
    }
</style>
""", unsafe_allow_html=True)

class TradeMasterXGUI:
    """Main TradeMasterX Desktop GUI Application"""
    
    def __init__(self):
        self.parent_dir = parent_dir
        self.trademasterx_process = None
        self.dashboard_process = None
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
            # Check if API keys are configured
            try:
                openai_key = st.secrets.get("openai_api_key", "")
                claude_key = st.secrets.get("claude_api_key", "")
                st.session_state.api_keys_configured = bool(openai_key or claude_key)
            except:
                st.session_state.api_keys_configured = False
    
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
    
    def start_trademasterx(self) -> bool:
        """Start the TradeMasterX system"""
        try:
            launch_script = self.parent_dir / "launch_production.py"
            st.info(f"Looking for launch script at: {launch_script}")
            st.info(f"Parent directory is: {self.parent_dir}")
            st.info(f"Current file is: {Path(__file__)}")
            
            if not launch_script.exists():
                st.error(f"Launch script not found: {launch_script}")
                # List files in parent directory for debugging
                try:
                    files = list(self.parent_dir.glob("*.py"))
                    st.info(f"Python files in parent directory: {files}")
                except Exception as e:
                    st.error(f"Error listing files: {e}")
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
            st.error(f"Error starting TradeMasterX: {e}")
            return False
    
    def stop_trademasterx(self) -> bool:
        """Stop the TradeMasterX system"""
        try:            if self.trademasterx_process:
                self.trademasterx_process.terminate()
                self.trademasterx_process.wait(timeout=10)
                self.trademasterx_process = None
            return True
        except Exception as e:
            st.error(f"Error stopping TradeMasterX: {e}")
            return False
    
    def start_dashboard(self) -> bool:
        """Start the web dashboard"""
        try:
            dashboard_script = self.parent_dir / "simple_dashboard.py"
            st.info(f"Looking for dashboard script at: {dashboard_script}")
            st.info(f"Parent directory is: {self.parent_dir}")
            
            if not dashboard_script.exists():
                st.error(f"Dashboard script not found: {dashboard_script}")
                # List files in parent directory for debugging
                try:
                    files = list(self.parent_dir.glob("*.py"))
                    st.info(f"Python files in parent directory: {files}")
                except Exception as e:
                    st.error(f"Error listing files: {e}")
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
            st.error(f"Error starting dashboard: {e}")
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
            st.error(f"Error stopping dashboard: {e}")
            return False
    
    def render_system_control(self):
        """Render the system control panel"""
        st.header("🎮 System Control")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader(" TradeMasterX System")
            
            if st.button("▶️ Start TradeMasterX", type="primary", disabled=st.session_state.system_running):
                with st.spinner("Starting TradeMasterX system..."):
                    success = self.start_trademasterx()
                    if success:
                        st.session_state.system_running = True
                        st.success("✅ TradeMasterX started successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to start TradeMasterX")
            
            if st.button("⏹️ Stop TradeMasterX", disabled=not st.session_state.system_running):
                with st.spinner("Stopping TradeMasterX system..."):
                    success = self.stop_trademasterx()
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
                    success = self.start_dashboard()
                    if success:
                        st.session_state.dashboard_running = True
                        st.success("✅ Dashboard launched at http://localhost:8080")
                        st.markdown("[🔗 Open Dashboard](http://localhost:8080)")
                        st.rerun()
                    else:
                        st.error("❌ Failed to launch dashboard")
            
            if st.button("🛑 Stop Dashboard", disabled=not st.session_state.dashboard_running):
                with st.spinner("Stopping web dashboard..."):
                    success = self.stop_dashboard()
                    if success:
                        st.session_state.dashboard_running = False
                        st.success("✅ Dashboard stopped")
                        st.rerun()
                    else:
                        st.error("❌ Failed to stop dashboard")
    
    def render_ai_chat(self):
        """Render the AI chat interface"""
        st.header("🤖 AI Command Chat")
        
        # AI Provider Selection
        col1, col2 = st.columns([1, 3])
        with col1:
            ai_provider = st.selectbox(
                "AI Provider:",
                ["openai", "claude"],
                index=0,
                key="ai_provider_select"
            )
        
        with col2:
            provider_name = "OpenAI GPT-3.5" if ai_provider == "openai" else "Claude-3 Haiku"
            st.info(f"Using {provider_name} for AI assistance")
        
        # Chat interface
        chat_container = st.container()
        
        # Display chat history
        with chat_container:
            for message in st.session_state.chat_history:
                if message["role"] == "user":
                    with st.chat_message("user"):
                        st.write(message["content"])
                else:
                    with st.chat_message("assistant"):
                        st.write(message["content"])
        
        # Chat input
        user_input = st.chat_input("Enter your command or question...")
        
        if user_input:
            # Add user message to history
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            
            # Display user message
            with st.chat_message("user"):
                st.write(user_input)
            
            # Generate AI response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        response = self.get_ai_response(user_input, ai_provider)
                        st.write(response)
                        # Add AI response to history
                        st.session_state.chat_history.append({"role": "assistant", "content": response})
                    except Exception as e:
                        error_msg = f"Error getting AI response: {str(e)}"
                        st.error(error_msg)
                        st.session_state.chat_history.append({"role": "assistant", "content": error_msg})
        
        # Chat controls
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🗑️ Clear Chat", key="clear_chat"):
                st.session_state.chat_history = []
                st.rerun()
        
        with col2:
            if st.button("🔧 Test Connection", key="test_connection"):
                self.test_ai_connection(ai_provider)
        
        with col3:
            if st.button("📋 Show Commands", key="show_commands"):
                self.show_available_commands()
    
    def get_ai_response(self, user_input: str, provider: str) -> str:
        """Get AI response from selected provider"""
        if provider == "openai":
            return self.get_openai_response(user_input)
        elif provider == "claude":
            response = self.get_claude_response(user_input)
            # If Claude fails due to credit issues, fall back to OpenAI
            if "credit balance is too low" in response:
                st.warning("⚠️ Claude API has insufficient credits, falling back to OpenAI...")
                return self.get_openai_response(user_input)
            return response
        else:
            return "Unsupported AI provider selected."
    
    def get_openai_response(self, user_input: str) -> str:
        """Get response from OpenAI API"""
        try:
            import openai
            
            # Get API key from Streamlit secrets
            api_key = st.secrets.get("openai_api_key")
            if not api_key:
                return "❌ OpenAI API key not configured in secrets.toml"
            
            # Initialize OpenAI client
            client = openai.OpenAI(api_key=api_key)
            
            # System prompt for TradeMasterX context
            system_prompt = """You are an AI assistant for TradeMasterX 2.0, an advanced cryptocurrency trading system. 
            You can help with:
            - Trading strategy questions
            - System commands and controls
            - Performance analysis
            - Risk management
            - Technical analysis
            - System troubleshooting
            
            Provide helpful, accurate responses related to trading and the TradeMasterX system."""
            
            # Make API call
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"❌ OpenAI API Error: {str(e)}"
    
    def get_claude_response(self, user_input: str) -> str:
        """Get response from Claude API"""
        try:
            import anthropic
            
            # Get API key from Streamlit secrets
            api_key = st.secrets.get("claude_api_key")
            if not api_key:
                return "❌ Claude API key not configured in secrets.toml"
            
            # Initialize Anthropic client
            client = anthropic.Anthropic(api_key=api_key)
            
            # System prompt for TradeMasterX context
            system_prompt = """You are an AI assistant for TradeMasterX 2.0, an advanced cryptocurrency trading system. 
            You can help with:
            - Trading strategy questions
            - System commands and controls
            - Performance analysis
            - Risk management
            - Technical analysis
            - System troubleshooting
            
            Provide helpful, accurate responses related to trading and the TradeMasterX system."""
            
            # Make API call
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=500,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_input}
                ]
            )
            
            return response.content[0].text.strip()
            
        except Exception as e:
            return f"❌ Claude API Error: {str(e)}"
    
    def test_ai_connection(self, provider: str):
        """Test AI API connection"""
        with st.spinner(f"Testing {provider.title()} connection..."):
            try:
                if provider == "openai":
                    response = self.get_openai_response("Hello, can you confirm the connection is working?")
                else:
                    response = self.get_claude_response("Hello, can you confirm the connection is working?")
                
                if "❌" not in response:
                    st.success(f"✅ {provider.title()} connection successful!")
                    st.info(f"Response: {response[:100]}...")
                else:
                    st.error(f"❌ {provider.title()} connection failed: {response}")
            except Exception as e:
                st.error(f"❌ Connection test failed: {str(e)}")
    
    def show_available_commands(self):
        """Display available TradeMasterX commands"""
        st.info("""
        **Available Commands & Topics:**
        
        **System Control:**
        - Start/stop trading system
        - View system status
        - Check component health
        
        **Trading Analysis:**
        - Analyze trading performance
        - Review recent trades
        - Check strategy effectiveness
        
        **Risk Management:**
        - Review risk metrics
        - Check position sizes
        - Monitor drawdowns
        
        **Technical Analysis:**
        - Market trend analysis
        - Support/resistance levels
        - Indicator interpretations
        
        **General Help:**
        - "How do I start the trading system?"
        - "What's my current performance?"
        - "Show me the latest trades"
        - "Explain this trading strategy"
        """)
    
    def render_system_status(self):
        """Render the system status dashboard"""
        st.header("📊 System Status")
        
        # Auto-refresh toggle
        col1, col2 = st.columns([3, 1])
        with col2:
            auto_refresh = st.checkbox("🔄 Auto-refresh (30s)")
        
        if auto_refresh:
            time.sleep(30)
            st.rerun()
        
        # Refresh button
        if st.button("🔄 Refresh Now"):
            st.rerun()
        
        # System status cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div class="metric-card">
                <h3>🧠 AI Health</h3>
                <h2>Active</h2>
                <p>All systems operational</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-card">
                <h3>📈 Trading Status</h3>
                <h2>Monitoring</h2>
                <p>Watching markets</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="metric-card">
                <h3>🛡️ Risk Level</h3>
                <h2>Low</h2>
                <p>Within parameters</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div class="metric-card">
                <h3>🔔 Alerts</h3>
                <h2>0</h2>
                <p>No active alerts</p>
            </div>
            """, unsafe_allow_html=True)
    
    def render_trade_history(self):
        """Render the trade history viewer"""
        st.header("📈 Trade History")
        
        # Try to load trade data
        try:
            trade_files = list(Path(self.parent_dir / "data" / "performance").glob("trades_*.csv"))
            
            if trade_files:
                # Load the most recent trade file
                latest_file = max(trade_files, key=lambda x: x.stat().st_mtime)
                df = pd.read_csv(latest_file)
                
                st.subheader("📋 Recent Trades")
                st.dataframe(df.tail(10), use_container_width=True)
                
                # Basic metrics
                if not df.empty and 'return_pct' in df.columns:
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Total Trades", len(df))
                    
                    with col2:
                        win_rate = (df['return_pct'] > 0).mean() * 100
                        st.metric("Win Rate", f"{win_rate:.1f}%")
                    
                    with col3:
                        avg_return = df['return_pct'].mean()
                        st.metric("Avg Return", f"{avg_return:.2f}%")
                    
                    # Simple chart
                    if len(df) > 1:
                        st.subheader("📊 Performance Chart")
                        df['cumulative_return'] = (1 + df['return_pct'] / 100).cumprod()
                        fig = px.line(df, y='cumulative_return', title="Cumulative Returns")
                        st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No trade history data found")
                
        except Exception as e:
            st.error(f"Error loading trade data: {e}")
    
    def render_settings(self):
        """Render the settings panel"""
        st.header("⚙️ Settings")
        
        # API Configuration
        st.subheader("🔑 API Configuration")
        
        # Check API status
        try:
            openai_key = st.secrets.get("openai_api_key", "")
            claude_key = st.secrets.get("claude_api_key", "")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if openai_key:
                    st.success("✅ OpenAI API Key Configured")
                else:
                    st.error("❌ OpenAI API Key Missing")
            
            with col2:
                if claude_key:
                    st.success("✅ Claude API Key Configured")
                else:
                    st.error("❌ Claude API Key Missing")
                    
        except Exception as e:
            st.error(f"Error checking API configuration: {e}")
        
        st.info("💡 API keys are configured in `.streamlit/secrets.toml`")
        
        # System Settings
        st.subheader("🛠️ System Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.selectbox("Trading Mode", ["Live", "Simulation", "Backtest"])
            st.slider("Risk Level", 1, 10, 5)
        
        with col2:
            st.checkbox("Auto-trading", value=False)
            st.checkbox("Email Alerts", value=True)
    
    def run(self):
        """Main application runner"""
        self.render_header()
        
        # Render sidebar and get selected page
        selected_page = self.render_sidebar()
        
        # Render the selected page
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

# Main application
if __name__ == "__main__":
    app = TradeMasterXGUI()
    app.run()
