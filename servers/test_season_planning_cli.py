#!/usr/bin/env python3
"""
CLI Testing Script for Season Planning Agent

Tests iterative conversation flow with context persistence and tool usage.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add servers directory to path
sys.path.append(str(Path(__file__).resolve().parent))

from hockey_agents.season_planning_agent import create_season_planning_agent, run_season_planning_agent

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SeasonPlanningCLI:
    """CLI interface for testing the Season Planning Agent."""
    
    def __init__(self):
        self.agent = None
        self.session_id = None
    
    async def start_interactive_session(self):
        """Start an interactive CLI session with the Season Planning Agent."""
        print("🏒 Hockey Season Planning Agent - Interactive CLI")
        print("=" * 60)
        print("This tool helps you create comprehensive season plans through conversation.")
        print("Type 'help' for commands, 'quit' to exit.")
        print("=" * 60)
        
        try:
            # Create agent with persistent session
            print("\n🚀 Initializing Season Planning Agent...")
            self.agent = await create_season_planning_agent()
            self.session_id = self.agent.session.id
            print(f"✅ Session ID: {self.session_id}")
            print(f"📝 Session persistence: Enabled")
            print("-" * 60)
            
            # Start conversation loop
            await self._conversation_loop()
            
        except Exception as e:
            print(f"❌ Error initializing agent: {e}")
            return
        finally:
            if self.agent:
                await self.agent.cleanup()
                print("\n🧹 Session cleaned up. Thanks for using the Season Planning Agent!")
    
    async def _conversation_loop(self):
        """Main conversation loop."""
        print("\n💬 Ready to help you plan your season! What's your team like?")
        
        while True:
            try:
                # Get user input
                user_input = input("\nCoach: ").strip()
                
                # Handle special commands
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Good luck with your season! Great coaching!")
                    break
                elif user_input.lower() == 'help':
                    self._show_help()
                    continue
                elif user_input.lower() == 'session':
                    await self._show_session_info()
                    continue
                elif user_input.lower() == 'clear':
                    self._clear_screen()
                    continue
                elif not user_input:
                    continue
                
                # Process with agent
                print("\nAssistant: ", end="", flush=True)
                
                try:
                    response = await self.agent.run(user_input)
                    print(response)
                except Exception as e:
                    print(f"Sorry, I encountered an error: {e}")
                    logger.error(f"Error in agent.run: {e}")
                
                print("-" * 60)
                
            except KeyboardInterrupt:
                print("\n\n👋 Session interrupted. Thanks for planning with us!")
                break
            except Exception as e:
                print(f"\n❌ Unexpected error: {e}")
                logger.error(f"Conversation loop error: {e}")
    
    def _show_help(self):
        """Show help information."""
        print("\n📚 Season Planning Agent Commands:")
        print("  help      - Show this help message")
        print("  session   - Show session information")
        print("  clear     - Clear the screen")
        print("  quit/exit - End the session")
        print("\n💡 Tips:")
        print("  - Tell me about your team (age, level, experience)")
        print("  - Ask about season structure, practice planning, or development")
        print("  - The agent will guide you through creating a complete season plan")
        print("  - Your conversation is saved in this session")
    
    async def _show_session_info(self):
        """Show current session information."""
        print(f"\n📊 Session Information:")
        print(f"  Session ID: {self.session_id}")
        print(f"  Agent Type: Season Planning Specialist")
        print(f"  Tools Available: 6 MCP tools + Web Search")
        print(f"  Session Persistence: Enabled")
        
        # Try to get session history if available
        try:
            history = await self.agent.get_session_history()
            print(f"  Conversation Length: {len(history)} exchanges")
        except:
            print(f"  Conversation Length: Session active")
    
    def _clear_screen(self):
        """Clear the terminal screen."""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
        print("🏒 Hockey Season Planning Agent - Interactive CLI")
        print("=" * 60)


async def run_test_scenarios():
    """Run predefined test scenarios to validate agent functionality."""
    print("🧪 Running Season Planning Agent Test Scenarios")
    print("=" * 60)
    
    test_scenarios = [
        {
            "name": "New U10 House League Coach",
            "messages": [
                "Hi, I just volunteered to coach my daughter's U10 house league team. I've never coached before and don't know where to start with planning the season.",
                "We practice once a week and play games on weekends. The season runs from September to March.",
                "That sounds perfect! I want to keep it fun but also help them improve. What would a typical practice look like?"
            ]
        },
        {
            "name": "Experienced U14 Competitive Coach",
            "messages": [
                "I've been coaching U14 competitive for a few years but want to be more systematic with my season planning. We practice 3 times per week.",
                "Our main weaknesses last year were team play - especially breakouts and defensive zone coverage. How should I structure the season to address this?",
                "That makes sense. Can you create a season plan that focuses on building those systems?"
            ]
        },
        {
            "name": "Tool Usage Validation",
            "messages": [
                "What skills should U12 players be working on?",
                "What are the body checking rules for U14 competitive hockey?",
                "Can you create a practice plan for my U10 team focusing on skating and puck handling?"
            ]
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n🎯 Test Scenario {i}: {scenario['name']}")
        print("-" * 40)
        
        try:
            # Test with persistent session
            session_id = f"test_scenario_{i}"
            
            for j, message in enumerate(scenario['messages'], 1):
                print(f"\nMessage {j}: {message}")
                print("Response: ", end="", flush=True)
                
                response = await run_season_planning_agent(message, session_id)
                print(response[:200] + "..." if len(response) > 200 else response)
                
                # Short delay between messages
                await asyncio.sleep(1)
                
        except Exception as e:
            print(f"❌ Error in scenario {i}: {e}")
            logger.error(f"Test scenario {i} failed: {e}")
        
        print(f"\n✅ Scenario {i} complete")
        print("=" * 60)
    
    print("\n🎉 All test scenarios completed!")


async def main():
    """Main CLI entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Run test scenarios
        await run_test_scenarios()
    else:
        # Start interactive session
        cli = SeasonPlanningCLI()
        await cli.start_interactive_session()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)