"""
AI Chat Interface Component
Handles natural language commands using CommandAssistant
"""

import streamlit as st
import asyncio
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent.parent.absolute()
sys.path.append(str(parent_dir))

class AIChatInterface:
    """AI chat interface for natural language commands"""
    
    def __init__(self):
        self.command_assistant = None
        self.initialize_assistant()
    
    def initialize_assistant(self):
        """Initialize the CommandAssistant"""
        try:
            # Import CommandAssistant
            from trademasterx.interface.assistant import CommandAssistant
            self.command_assistant = CommandAssistant(personality='friendly')
        except ImportError:
            try:
                # Fallback to core_clean version
                from core_clean.interface.assistant import CommandAssistant
                self.command_assistant = CommandAssistant(personality='friendly')
            except ImportError:
                st.error("CommandAssistant not available. Please check installation.")
                self.command_assistant = None
    
    def process_command(self, user_input: str) -> str:
        """Process a user command and return AI response"""
        if not self.command_assistant:
            return "❌ AI Assistant not available. Please check configuration."
        
        try:
            # Process the command asynchronously
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            response = loop.run_until_complete(
                self.command_assistant.process_command(user_input)
            )
            loop.close()
            
            return response.get('message', 'Command processed successfully.')
            
        except Exception as e:
            return f"❌ Error processing command: {str(e)}"
    
    def get_available_commands(self) -> List[str]:
        """Get list of available commands"""
        return [
            "status", "health", "performance", "anomalies",
            "retrain", "start", "stop", "pause", "resume",
            "help", "quit"
        ]
    
    def get_command_suggestions(self, partial_input: str) -> List[str]:
        """Get command suggestions based on partial input"""
        commands = self.get_available_commands()
        suggestions = []
        
        # Simple matching
        for cmd in commands:
            if cmd.startswith(partial_input.lower()):
                suggestions.append(cmd)
        
        # Add some natural language suggestions
        if "status" in partial_input.lower():
            suggestions.extend(["Show me system status", "How is everything?"])
        elif "start" in partial_input.lower():
            suggestions.extend(["Start trading", "Begin operations"])
        elif "stop" in partial_input.lower():
            suggestions.extend(["Stop trading", "Halt operations"])
        
        return suggestions[:5]  # Limit to 5 suggestions
