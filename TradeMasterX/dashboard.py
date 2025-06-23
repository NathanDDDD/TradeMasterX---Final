import streamlit as st
import pandas as pd
import json
import time
from datetime import datetime
import sys
import os

# Add the project root to Python path
sys.path.append('TradeMasterX')

from trademasterx.core.masterbot import MasterBot
from trademasterx.core.config import Config
from trademasterx.core.memory import Memory
from trademasterx.core.bybit_client import BybitClient
from trademasterx.utils.mini_log import get_last_events

# Page configuration
st.set_page_config(
    page_title="TradeMasterX Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
        color: #fafafa;
    }
    .stButton > button {
        background-color: #ff4b4b;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #ff3333;
    }
    .emergency-stop {
        background-color: #ff0000 !important;
        animation: blink 1s infinite;
    }
    @keyframes blink {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'bot' not in st.session_state:
    st.session_state.bot = MasterBot()
    st.session_state.config = Config('TradeMasterX/config.yaml')
    st.session_state.memory = Memory('TradeMasterX/memory.json')
    st.session_state.bybit = BybitClient()

# Header
st.title("🚀 TradeMasterX Dashboard")
st.markdown("---")

# Sidebar for controls
with st.sidebar:
    st.header("🎛️ Controls")
    
    # Emergency Controls
    st.subheader("🚨 Emergency Controls")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("EMERGENCY STOP", key="emergency_stop", help="Immediately halt all trading"):
            result = st.session_state.bot.emergency_stop()
            st.error("🚨 EMERGENCY STOP ACTIVATED!")
            st.json(result)
    
    with col2:
        if st.button("Reset Stop", key="reset_stop", help="Reset emergency stop"):
            result = st.session_state.bot.reset_emergency_stop()
            st.success("✅ Emergency stop reset!")
            st.json(result)
    
    # System Status
    st.subheader("📊 System Status")
    status = st.session_state.bot.get_system_status()
    st.json(status)
    
    # Bybit Status
    st.subheader("💱 Bybit Status")
    bybit_status = st.session_state.bybit.get_status()
    st.json(bybit_status)

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.header("📈 Market Analysis")
    
    # Sample data for demonstration
    sample_data = {
        'price': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113],
        'volume': [200, 210, 220, 230, 240, 250, 260, 270, 280, 290, 300, 310, 320, 330],
        'news': ['Market is bullish today', 'Record high reached'],
        'sentiment': ['positive', 'bullish rally'],
    }
    
    # Run analysis
    if st.button("🔄 Run Analysis", key="run_analysis"):
        with st.spinner("Running analysis..."):
            results = st.session_state.bot.aggregate_signals(sample_data)
            
            # Display results in a nice format
            for name, result in results.items():
                if result:
                    st.subheader(f"📊 {name}")
                    st.json(result)
                else:
                    st.subheader(f"📊 {name}")
                    st.info("No data available")
    
    # AI Assistant
    st.header("🤖 AI Assistant")
    ai_question = st.text_input("Ask AI for trading advice:", 
                               placeholder="What's the best strategy for BTC right now?")
    
    if st.button("💬 Ask AI", key="ask_ai"):
        if ai_question:
            with st.spinner("Getting AI advice..."):
                ai_advice = st.session_state.bot.get_ai_advice(sample_data, ai_question)
                st.subheader("🤖 AI Response")
                st.write(ai_advice)
        else:
            st.warning("Please enter a question for the AI.")

with col2:
    st.header("💰 Trading")
    
    # Bybit Balance
    if st.button("💳 Check Balance", key="check_balance"):
        balance = st.session_state.bybit.get_balance()
        st.subheader("💰 Account Balance")
        st.json(balance)
    
    # Market Data
    if st.button("📊 Get Market Data", key="get_market"):
        ticker = st.session_state.bybit.get_ticker()
        st.subheader("📊 Market Data")
        st.json(ticker)
    
    # Order Placement
    st.subheader("📝 Place Order")
    symbol = st.selectbox("Symbol", ["BTC/USDT", "ETH/USDT", "ADA/USDT"])
    side = st.selectbox("Side", ["buy", "sell"])
    amount = st.number_input("Amount", min_value=0.001, value=0.001, step=0.001)
    
    if st.button("📤 Place Order", key="place_order"):
        with st.spinner("Placing order..."):
            order = st.session_state.bybit.place_order(symbol, side, amount)
            st.subheader("📤 Order Result")
            st.json(order)

# Bottom section for logs
st.markdown("---")
st.header("📋 System Logs")

# Auto-refresh logs
if st.button("🔄 Refresh Logs", key="refresh_logs"):
    st.empty()

# Display recent logs
logs = get_last_events(20)
if logs:
    log_text = "".join(logs)
    st.text_area("Recent Events", log_text, height=200)
else:
    st.info("No logs available yet.")

# Footer
st.markdown("---")
st.markdown("**TradeMasterX Dashboard** - Professional Trading Platform")
st.markdown("*Real-time monitoring and control for your trading system*")

# Auto-refresh every 30 seconds
if st.button("⏰ Enable Auto-refresh", key="auto_refresh"):
    st.info("Auto-refresh enabled. Page will refresh every 30 seconds.")
    time.sleep(30)
    st.experimental_rerun() 