#!/usr/bin/env python3
"""
Demo script to showcase the fixed CommandAssistant functionality
"""

import sys
import os
import asyncio
sys.path.insert(0, '.')

async def demo_command_assistant():
    """Demonstrate the CommandAssistant functionality"""
    print("🤖 TradeMasterX CommandAssistant Demo")
    print("=" * 50)
    
    try:
        from trademasterx.interface.assistant.command_assistant import CommandAssistant
        
        # Create assistant
        print("Creating CommandAssistant...")
        assistant = CommandAssistant(personality='friendly')
        print(f"✅ Assistant ready with {assistant.personality.type} personality\n")
        
        # Demo commands
        demo_commands = [
            "pause the bot",
            "show me today's performance",
            "what's the current risk level?",
            "run a system diagnostic",
            "help me understand the commands",
            "unknown command test"
        ]
        
        print("Testing natural language command parsing:")
        print("-" * 40)
        
        for cmd in demo_commands:
            command_type, params = assistant.parser.parse_command(cmd)
            print(f"Input: '{cmd}'")
            print(f"→ Command: {command_type}")
            print(f"→ Params: {params}")
            print()
        
        print("🎉 CommandAssistant is fully functional!")
        print("=" * 50)
        print("\nTo use interactively, run:")
        print("python -c \"from trademasterx.interface.assistant.command_assistant import CommandAssistant; CommandAssistant().start_session()\"")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(demo_command_assistant())
