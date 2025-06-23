#!/usr/bin/env python3
"""
Phase 13 Chat Command Test
Simple test of the smart command assistant without complex dependencies
"""

import sys
import os
from pathlib import Path

# Add workspace to path
sys.path.insert(0, str(Path(__file__).parent))

def test_command_assistant_import():
    """Test importing the command assistant directly"""
    print("Testing Phase 13 Command Assistant import...")
    
    try:
        from trademasterx.interface.assistant.command_assistant import CommandAssistant
        print("✅ CommandAssistant import successful")
        return True
    except ImportError as e:
        print(f"❌ CommandAssistant import failed: {e}")
        return False

def test_api_integration_import():
    """Test importing the API integration"""
    print("Testing API integration import...")
    
    try:
        from trademasterx.interface.assistant.api_integration import APIIntegration
        print("✅ APIIntegration import successful")
        return True
    except ImportError as e:
        print(f"❌ APIIntegration import failed: {e}")
        return False

def test_conversation_engine_import():
    """Test importing the conversation engine"""
    print("Testing conversation engine import...")
    
    try:
        from trademasterx.interface.assistant.conversation_engine import ConversationEngine
        print("✅ ConversationEngine import successful")
        return True
    except ImportError as e:
        print(f"❌ ConversationEngine import failed: {e}")
        return False

def test_assistant_initialization():
    """Test creating a command assistant instance"""
    print("Testing CommandAssistant initialization...")
    
    try:
        from trademasterx.interface.assistant.command_assistant import CommandAssistant
        
        assistant = CommandAssistant(personality="professional")
        print("✅ CommandAssistant instance created successfully")
        print(f"   Personality: {assistant.personality}")
        print(f"   Commands available: {len(assistant.commands)}")
        return True
    except Exception as e:
        print(f"❌ CommandAssistant initialization failed: {e}")
        return False

def test_mock_commands():
    """Test basic command processing without external dependencies"""
    print("Testing mock command processing...")
    
    try:
        from trademasterx.interface.assistant.command_assistant import CommandAssistant
        
        assistant = CommandAssistant(personality="friendly")
        
        # Test help command
        response = assistant.process_command("help")
        print("✅ Help command processed successfully")
        
        # Test status command
        response = assistant.process_command("status")
        print("✅ Status command processed successfully")
        
        return True
    except Exception as e:
        print(f"❌ Mock command processing failed: {e}")
        return False

def test_api_integration():
    """Test API integration without actual API calls"""
    print("Testing API integration mock functionality...")
    
    try:
        from trademasterx.interface.assistant.api_integration import APIIntegration
        
        api = APIIntegration()
        
        # Test mock response
        response = api.generate_response("Hello, test message", use_mock=True)
        print("✅ Mock API response generated successfully")
        print(f"   Response: {response[:100]}...")
        
        return True
    except Exception as e:
        print(f"❌ API integration test failed: {e}")
        return False

def main():
    """Run all Phase 13 tests"""
    print(" Starting Phase 13 Smart Command Interface Tests")
    print("=" * 60)
    
    tests = [
        test_command_assistant_import,
        test_api_integration_import, 
        test_conversation_engine_import,
        test_assistant_initialization,
        test_mock_commands,
        test_api_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"❌ Test failed with exception: {e}\n")
    
    print("=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Phase 13 tests passed! Smart Command Interface is ready.")
        return True
    else:
        print(f"⚠️  {total - passed} tests failed. Phase 13 needs attention.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
