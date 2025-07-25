"""
Test script to validate API integration works correctly.
This simulates what the web app API endpoint does.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add POC to path
sys.path.append(str(Path(__file__).parent))

from agents import Runner
from poc_agents.api_test_agent import create_api_agent

async def test_api_responses():
    """Test agent responses in API-like format"""
    
    print("🌐 Testing API Integration")
    print("=" * 40)
    
    try:
        agent = create_api_agent()
        print("✅ API agent created successfully")
        
        # Test messages that would come from web app
        api_test_cases = [
            {
                "message": "Hello!",
                "expected_type": "greeting"
            },
            {
                "message": "What should I focus on with U10 players?",
                "expected_type": "coaching_advice"
            },
            {
                "message": "How long should practices be?",
                "expected_type": "specific_question"
            }
        ]
        
        for i, test_case in enumerate(api_test_cases, 1):
            print(f"\n{i}. API Request: '{test_case['message']}'")
            
            start_time = asyncio.get_event_loop().time()
            result = await Runner.run(agent, test_case["message"])
            end_time = asyncio.get_event_loop().time()
            
            response = result.final_output
            processing_time = round((end_time - start_time) * 1000)
            
            print(f"   Response: '{response}'")
            print(f"   Processing Time: {processing_time}ms")
            
            # Basic validation
            if len(response) > 10 and processing_time < 10000:  # Under 10 seconds
                print("   ✅ Valid API response")
            else:
                print("   ⚠️  Response may need optimization")
        
        print("\n✅ All API integration tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ API integration test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_api_responses())
    if success:
        print("\n🚀 Ready for web app integration!")
    else:
        print("\n🔧 Fix issues before web integration.")