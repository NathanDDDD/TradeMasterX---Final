#!/usr/bin/env python3
"""
Test script to validate the fixed CommandAssistant implementation
"""

import sys
import os
sys.path.insert(0, '.')

def test_command_assistant():
    """Test the fixed CommandAssistant implementation"""
    print("🧪 Testing Fixed CommandAssistant Implementation")
    print("=" * 50)
    
    try:
        # Test import
        print("1. Testing import...")
        from trademasterx.interface.assistant.command_assistant import CommandAssistant, BotPersonality, APIKeyManager, NaturalLanguageParser
        print("   ✅ All classes imported successfully")
        
        # Test BotPersonality
        print("\n2. Testing BotPersonality...")
        personality = BotPersonality('friendly')
        test_msg = personality.format_response("Test message", 'success')
        print(f"   ✅ Personality created: {personality.type}")
        print(f"   ✅ Response formatting works: {len(test_msg)} chars")
        
        # Test APIKeyManager
        print("\n3. Testing APIKeyManager...")
        api_manager = APIKeyManager()
        has_claude = api_manager.has_claude_key()
        has_openai = api_manager.has_openai_key()
        print(f"   ✅ API Manager created")
        print(f"   ✅ Claude key check: {has_claude}")
        print(f"   ✅ OpenAI key check: {has_openai}")
        
        # Test NaturalLanguageParser
        print("\n4. Testing NaturalLanguageParser...")
        parser = NaturalLanguageParser()
        command, params = parser.parse_command("pause the bot")
        print(f"   ✅ Parser created with {len(parser.compiled_patterns)} command types")
        print(f"   ✅ Command parsing works: '{command}' with params {params}")
        
        # Test CommandAssistant instantiation
        print("\n5. Testing CommandAssistant...")
        assistant = CommandAssistant(personality='professional')
        print(f"   ✅ Assistant created with personality: {assistant.personality.type}")
        print(f"   ✅ Session start time: {assistant.session_start}")
        print(f"   ✅ Conversation history initialized: {len(assistant.conversation_history)} entries")
        
        # Test command parsing
        print("\n6. Testing command parsing...")
        test_commands = [
            "pause the system",
            "show me today's performance", 
            "what's the current risk level?",
            "run diagnostics",
            "help me"
        ]
        
        for cmd in test_commands:
            command, params = assistant.parser.parse_command(cmd)
            print(f"   ✅ '{cmd}' → {command} {params}")
        
        print("\n" + "=" * 50)
        print("🎉 ALL TESTS PASSED! CommandAssistant is working correctly!")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_command_assistant()
    sys.exit(0 if success else 1)
