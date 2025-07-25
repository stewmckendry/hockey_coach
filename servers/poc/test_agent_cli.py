"""
CLI test script for basic agent functionality.

This script allows testing the agent through command line interface:
- Validates OpenAI Agents SDK installation
- Tests basic agent responses
- Provides interactive testing environment
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the POC directory to Python path
sys.path.append(str(Path(__file__).parent))

# Import from the correct agents module (not local agents)
import agents
from poc_agents.basic_test_agent import create_test_agent

async def test_basic_agent():
    """Test basic agent functionality with predefined inputs"""
    
    print("🏒 Hockey Coach AI - Agent Test Suite")
    print("=" * 50)
    
    try:
        # Create agent
        print("📝 Creating test agent...")
        agent = create_test_agent()
        print("✅ Agent created successfully")
        
        # Test cases
        test_inputs = [
            "Hello",
            "What should I focus on with U10 players?",
            "How are you doing today?",
            "Tell me about hockey coaching"
        ]
        
        print("\n🧪 Running test scenarios...")
        print("-" * 30)
        
        for i, test_input in enumerate(test_inputs, 1):
            print(f"\n{i}. Testing input: '{test_input}'")
            print("   Response: ", end="")
            
            try:
                # Run agent with test input
                result = await agents.Runner.run(agent, test_input)
                response = result.final_output
                print(f"'{response}'")
                
                # Basic validation
                if len(response) > 10:  # Response should be substantial
                    print("   ✅ Response received and valid")
                else:
                    print("   ⚠️  Response too short, may indicate issue")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
                return False
        
        print(f"\n✅ All test scenarios completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create agent: {e}")
        return False

async def interactive_test():
    """Interactive testing mode"""
    
    print("\n🎮 Interactive Mode")
    print("=" * 30)
    print("Type messages to test the agent. Type 'quit' to exit.")
    
    try:
        agent = create_test_agent()
        print("✅ Agent ready for interactive testing")
        
        while True:
            user_input = input("\n💬 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
                
            if not user_input:
                continue
                
            try:
                print("🤖 Agent: ", end="")
                result = await agents.Runner.run(agent, user_input)
                response = result.final_output
                print(response)
                
            except Exception as e:
                print(f"❌ Error: {e}")
                
    except Exception as e:
        print(f"❌ Failed to start interactive mode: {e}")

async def main():
    """Main test function"""
    
    print("🚀 Starting OpenAI Agents SDK Test")
    print("=" * 50)
    
    # Check environment
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found in environment")
        print("   Please set your OpenAI API key in .env file")
        return
    
    print("✅ Environment check passed")
    
    # Run automated tests
    test_success = await test_basic_agent()
    
    if test_success:
        # Offer interactive testing
        response = input("\n🎮 Run interactive test? (y/n): ").lower()
        if response == 'y':
            await interactive_test()
    else:
        print("\n❌ Automated tests failed. Fix issues before interactive testing.")

if __name__ == "__main__":
    # Run the test
    asyncio.run(main())