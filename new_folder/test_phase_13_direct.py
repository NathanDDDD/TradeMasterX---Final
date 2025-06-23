#!/usr/bin/env python3
"""
Phase 13 Direct Test - Test command assistant functionality directly
"""

import sys
import os
import logging
from pathlib import Path

# Setup path for imports
sys.path.insert(0, os.path.abspath('.'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('Phase13DirectTest')

def test_command_assistant():
    """Test the command assistant directly"""
    logger.info("Testing Phase 13 Command Assistant...")
    
    try:
        # Import the command assistant
        from trademasterx.interface.assistant.command_assistant import CommandAssistant
        from trademasterx.interface.assistant.api_integration import APIIntegration
        from trademasterx.interface.assistant.conversation_engine import ConversationEngine
        
        logger.info("✓ Successfully imported Phase 13 components")
        
        # Test 1: Initialize Command Assistant
        try:
            assistant = CommandAssistant(personality="professional", setup_keys=False)
            logger.info("✓ CommandAssistant initialized successfully")
        except Exception as e:
            logger.error(f"❌ CommandAssistant initialization failed: {e}")
            return False
        
        # Test 2: Test command parsing
        try:
            test_commands = [
                "status",
                "pause bot",
                "show performance",
                "help",
                "what is the system status?"
            ]
            
            for cmd in test_commands:
                result = assistant.parse_command(cmd)
                if result:
                    logger.info(f"✓ Parsed command '{cmd}' -> {result['command']}")
                else:
                    logger.warning(f"⚠ Could not parse command: {cmd}")
            
            logger.info("✓ Command parsing tests completed")
        except Exception as e:
            logger.error(f"❌ Command parsing failed: {e}")
            return False
        
        # Test 3: Test API Integration (without keys)
        try:
            api_integration = APIIntegration()
            
            # Test mock mode
            mock_response = api_integration.process_command_with_ai(
                "What is the system status?", 
                {"system": "test"}, 
                use_mock=True
            )
            
            if mock_response and "response" in mock_response:
                logger.info("✓ API Integration mock mode working")
            else:
                logger.warning("⚠ API Integration mock mode returned unexpected result")
            
        except Exception as e:
            logger.error(f"❌ API Integration test failed: {e}")
            return False
        
        # Test 4: Test Conversation Engine
        try:
            conv_engine = ConversationEngine()
            
            # Test conversation processing
            response = conv_engine.process_conversation(
                message="Test message",
                context={"test": True},
                session_id="test_session"
            )
            
            if response:
                logger.info("✓ Conversation Engine working")
            else:
                logger.warning("⚠ Conversation Engine returned no response")
            
        except Exception as e:
            logger.error(f"❌ Conversation Engine test failed: {e}")
            return False
        
        # Test 5: Test personality system
        try:
            personalities = ["professional", "friendly", "technical"]
            for personality in personalities:
                assistant_test = CommandAssistant(personality=personality, setup_keys=False)
                logger.info(f"✓ {personality.capitalize()} personality initialized")
                
        except Exception as e:
            logger.error(f"❌ Personality system test failed: {e}")
            return False
        
        logger.info("✓ All Phase 13 component tests passed!")
        return True
        
    except ImportError as e:
        logger.error(f"❌ Failed to import Phase 13 components: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error during Phase 13 testing: {e}")
        return False

def test_cli_integration():
    """Test CLI integration"""
    logger.info("Testing CLI integration...")
    
    try:
        # Test if the CLI module can be imported
        from trademasterx.interface.cli.cli import cli
        logger.info("✓ CLI module imported successfully")
        
        # Check if chat command is registered
        commands = [cmd.name for cmd in cli.commands.values()]
        if 'chat' in commands:
            logger.info("✓ Chat command is registered in CLI")
            return True
        else:
            logger.warning("⚠ Chat command not found in CLI")
            return False
            
    except Exception as e:
        logger.error(f"❌ CLI integration test failed: {e}")
        return False

def test_dependencies():
    """Test required dependencies"""
    logger.info("Testing Phase 13 dependencies...")
    
    required_packages = [
        'rich',
        'anthropic', 
        'openai',
        'sqlite3',
        'click'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'sqlite3':
                import sqlite3
            elif package == 'rich':
                import rich
            elif package == 'anthropic':
                import anthropic
            elif package == 'openai':
                import openai
            elif package == 'click':
                import click
            
            logger.info(f"✓ {package} is available")
        except ImportError:
            logger.error(f"❌ {package} is missing")
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"Missing packages: {', '.join(missing_packages)}")
        return False
    else:
        logger.info("✓ All required dependencies are available")
        return True

def main():
    """Run all Phase 13 tests"""
    logger.info("=" * 60)
    logger.info("PHASE 13 DIRECT TESTING")
    logger.info("=" * 60)
    
    tests = [
        ("Dependencies", test_dependencies),
        ("Command Assistant", test_command_assistant),
        ("CLI Integration", test_cli_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\nRunning {test_name} test...")
        try:
            result = test_func()
            results.append((test_name, result))
            logger.info(f"{test_name} test: {'✓ PASSED' if result else '❌ FAILED'}")
        except Exception as e:
            logger.error(f"{test_name} test: ❌ ERROR - {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("PHASE 13 TEST SUMMARY")
    logger.info("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASSED" if result else "❌ FAILED"
        logger.info(f"{test_name:20} {status}")
    
    success_rate = (passed / total) * 100 if total > 0 else 0
    logger.info(f"\nSuccess Rate: {success_rate:.1f}% ({passed}/{total})")
    
    if success_rate >= 80:
        logger.info("🎉 PHASE 13 CORE FUNCTIONALITY: SUCCESS")
        return True
    else:
        logger.info("❌ PHASE 13 CORE FUNCTIONALITY: NEEDS ATTENTION")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
