#!/usr/bin/env python3
"""
Test script for TradeMasterX Command Assistant
"""

import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(__file__))

from trademasterx.interface.assistant.command_assistant import CommandAssistant, NaturalLanguageParser
from rich.console import Console

console = Console()

def test_natural_language_parser():
    """Test the natural language parsing functionality"""
    console.print("\n[bold blue]Testing Natural Language Parser[/bold blue]")
    
    parser = NaturalLanguageParser()
    
    test_commands = [
        "pause the bot",
        "show me today's performance", 
        "what's the current risk level?",
        "run a system diagnostic",
        "retrain the models",
        "shutdown the system",
        "how is everything doing?",
        "stop trading immediately",
        "show me the logs"
    ]
    
    for test_cmd in test_commands:
        try:
            command, params = parser.parse_command(test_cmd)
            console.print(f"[cyan]'{test_cmd}'[/cyan] → [green]{command}[/green] {params}")
        except Exception as e:
            console.print(f"[red]Error parsing '{test_cmd}': {e}[/red]")

async def test_command_processing():
    """Test the command processing functionality"""
    console.print("\n[bold blue]Testing Command Processing[/bold blue]")
    
    try:
        assistant = CommandAssistant(personality='friendly')
        
        test_commands = [
            "help",
            "show status", 
            "what's the performance?",
            "run diagnostics"
        ]
        
        for cmd in test_commands:
            console.print(f"\n[yellow]Processing: '{cmd}'[/yellow]")
            try:
                await assistant.process_command(cmd)
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                
    except Exception as e:
        console.print(f"[red]Failed to create assistant: {e}[/red]")

def test_personality_system():
    """Test the personality system"""
    console.print("\n[bold blue]Testing Personality System[/bold blue]")
    
    personalities = ['professional', 'friendly', 'technical']
    
    for personality in personalities:
        try:
            assistant = CommandAssistant(personality=personality)
            console.print(f"\n[magenta]{personality.title()} Personality:[/magenta]")
            console.print(f"Greeting: {assistant.personality.config['greeting']}")
            
            sample_response = assistant.personality.format_response(
                "System is running normally", 'success'
            )
            console.print(f"Sample Response: {sample_response}")
            
        except Exception as e:
            console.print(f"[red]Error with {personality} personality: {e}[/red]")

def main():
    """Main test function"""
    console.print("[bold green]TradeMasterX Command Assistant - Test Suite[/bold green]")
    console.print("=" * 60)
    
    # Test 1: Natural Language Parser
    test_natural_language_parser()
    
    # Test 2: Personality System
    test_personality_system()
    
    # Test 3: Command Processing (async)
    console.print("\n" + "=" * 60)
    asyncio.run(test_command_processing())
    
    console.print("\n[bold green]✅ All tests completed![/bold green]")

if __name__ == "__main__":
    main()
