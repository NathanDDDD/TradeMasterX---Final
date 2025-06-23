"""
Enhanced AI Chat Component for TradeMasterX Desktop GUI
Provides chat interface with CommandAssistant integration
Supports both OpenAI and Claude APIs
"""

import streamlit as st
import sys
import os
from pathlib import Path
import asyncio
import traceback
from datetime import datetime

# Add parent directory to path for imports
current_dir = Path(__file__).parent.parent.parent
sys.path.append(str(current_dir))

def render_ai_chat():
    """Render the AI Command Chat interface"""
    st.header("🤖 AI Command Chat")
    st.markdown("---")
    
    # Initialize session state
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'ai_provider' not in st.session_state:
        st.session_state.ai_provider = "openai"
    
    # AI Provider Selection
    col1, col2 = st.columns([1, 3])
    with col1:
        ai_provider = st.selectbox(
            "AI Provider:",
            ["openai", "claude"],
            index=0 if st.session_state.ai_provider == "openai" else 1,
            key="ai_provider_select"
        )
        st.session_state.ai_provider = ai_provider
    
    with col2:
        provider_name = "OpenAI GPT-3.5" if ai_provider == "openai" else "Claude-3 Haiku"
        st.info(f"Using {provider_name} for AI assistance")
    
    # Chat interface
    chat_container = st.container()
    
    # Display chat history
    with chat_container:
        for i, message in enumerate(st.session_state.chat_history):
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
                    response = get_ai_response(user_input, ai_provider)
                    st.write(response)
                    # Add AI response to history
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                except Exception as e:
                    error_msg = f"Error getting AI response: {str(e)}"
                    st.error(error_msg)
                    st.session_state.chat_history.append({"role": "assistant", "content": error_msg})
    
    # Chat controls
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🗑️ Clear Chat", key="clear_chat"):
            st.session_state.chat_history = []
            st.rerun()
    
    with col2:
        if st.button("💾 Export Chat", key="export_chat"):
            export_chat_history()
    
    with col3:
        if st.button("🔧 Test Connection", key="test_connection"):
            test_ai_connection(ai_provider)
    
    with col4:
        if st.button("📋 Show Commands", key="show_commands"):
            show_available_commands()

def get_ai_response(user_input: str, provider: str) -> str:
    """Get AI response from selected provider"""
    try:
        if provider == "openai":
            return get_openai_response(user_input)
        elif provider == "claude":
            response = get_claude_response(user_input)
            # If Claude fails due to credit issues, fall back to OpenAI
            if "credit balance is too low" in response:
                st.warning("⚠️ Claude API has insufficient credits, falling back to OpenAI...")
                return get_openai_response(user_input)
            return response
        else:
            return "Unsupported AI provider selected."
    except Exception as e:
        # Fallback to CommandAssistant if AI APIs fail
        fallback_response = get_command_assistant_response(user_input)
        return f"🔄 API Error, using system fallback: {fallback_response}"

def get_openai_response(user_input: str) -> str:
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

def get_claude_response(user_input: str) -> str:
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

def test_ai_connection(provider: str):
    """Test AI API connection"""
    with st.spinner(f"Testing {provider.title()} connection..."):
        try:
            if provider == "openai":
                response = get_openai_response("Hello, can you confirm the connection is working?")
            else:
                response = get_claude_response("Hello, can you confirm the connection is working?")
            
            if "❌" not in response:
                st.success(f"✅ {provider.title()} connection successful!")
                st.info(f"Response: {response[:100]}...")
            else:
                st.error(f"❌ {provider.title()} connection failed: {response}")
        except Exception as e:
            st.error(f"❌ Connection test failed: {str(e)}")

def export_chat_history():
    """Export chat history to downloadable file"""
    if not st.session_state.chat_history:
        st.warning("No chat history to export")
        return
    
    # Format chat history
    export_text = f"TradeMasterX AI Chat Export\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    for message in st.session_state.chat_history:
        role = "User" if message["role"] == "user" else "AI Assistant"
        export_text += f"{role}: {message['content']}\n\n"
    
    # Create download button
    st.download_button(
        label="📄 Download Chat History",
        data=export_text,
        file_name=f"trademasterx_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
        mime="text/plain"
    )

def show_available_commands():
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

def get_command_assistant_response(user_input: str) -> str:
    """Get response from integrated CommandAssistant (fallback method)"""
    try:
        # Try to import and use CommandAssistant
        from trademasterx.interface.assistant.command_assistant import CommandAssistant
        
        assistant = CommandAssistant()
        response = assistant.process_command(user_input)
        
        if isinstance(response, dict):
            if response.get('success'):
                return f"✅ {response.get('message', 'Command executed successfully')}"
            else:
                return f"❌ {response.get('message', 'Command failed')}"
        else:
            return str(response)
            
    except ImportError:
        return "❌ CommandAssistant not available - using AI fallback only"
    except Exception as e:
        return f"❌ CommandAssistant error: {str(e)}"

# Legacy class for backward compatibility
class AIChatInterface:
    """Legacy AI chat interface for backward compatibility"""
    
    def __init__(self):
        self.command_assistant = None
        self.initialize_assistant()
    
    def initialize_assistant(self):
        """Initialize the CommandAssistant"""
        try:
            from trademasterx.interface.assistant import CommandAssistant
            self.command_assistant = CommandAssistant(personality='friendly')
        except ImportError:
            try:
                from core_clean.interface.assistant import CommandAssistant
                self.command_assistant = CommandAssistant(personality='friendly')
            except ImportError:
                st.error("CommandAssistant not available. Please check installation.")
                self.command_assistant = None
    
    def process_command(self, user_input: str) -> str:
        """Process a user command and return AI response"""
        return get_command_assistant_response(user_input)
