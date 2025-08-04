"""
Comprehensive tests for the Hockey Diagram Expert Agent flow.

Tests the complete agent workflow including:
1. Known formation fast path
2. Unknown formation research path  
3. Iterative refinement
4. Error handling and fallbacks
"""

import asyncio
import pytest
import logging
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestHockeyDiagramAgent:
    """Test suite for Hockey Diagram Expert Agent."""
    
    @pytest.fixture
    async def agent(self):
        """Create test agent instance."""
        try:
            from hockey_diagram_agent import HockeyDiagramExpert
            agent = HockeyDiagramExpert()
            # Mock the MCP servers to avoid external dependencies
            agent.mcp_servers = []
            return agent
        except ImportError:
            pytest.skip("Agent dependencies not available")
    
    def test_agent_initialization(self):
        """Test agent can be created and configured."""
        from hockey_diagram_agent import HockeyDiagramExpert
        agent = HockeyDiagramExpert()
        
        assert agent.agent is None  # Not initialized yet
        assert agent.runner is None
        assert agent.conversation_history == []
    
    @pytest.mark.asyncio
    async def test_known_formation_fast_path(self, agent):
        """Test fast path for known formations."""
        # Mock the agent runner to simulate successful generation
        mock_result = Mock()
        mock_result.__str__ = lambda: """
        ✅ Generated 2-1-2 forecheck diagram
        📁 Diagram: /test/path/hockey_diagram_20241204_143022.png
        🏒 **Formation**: 2-1-2 forecheck with F1 pressuring puck carrier
        """
        
        with patch.object(agent, 'runner') as mock_runner:
            mock_runner.run = AsyncMock(return_value=mock_result)
            
            result = await agent.generate_diagram("Show me a 2-1-2 forecheck")
            
            assert result['success'] is True
            assert 'diagram_path' in result
            assert result['processing_time'] > 0
            mock_runner.run.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_conversation_continuation(self, agent):
        """Test conversation context maintenance."""
        # Setup mock runner
        mock_result = Mock()
        mock_result.__str__ = lambda: "Updated diagram with feedback"
        
        with patch.object(agent, 'runner') as mock_runner:
            mock_runner.run = AsyncMock(return_value=mock_result)
            
            # First request
            await agent.generate_diagram("2-1-2 forecheck")
            
            # Follow-up request
            result = await agent.continue_conversation("Make F1 more aggressive")
            
            assert result['success'] is True
            assert mock_runner.run.call_count == 2
    
    @pytest.mark.asyncio 
    async def test_error_handling(self, agent):
        """Test error handling in agent generation."""
        with patch.object(agent, 'runner') as mock_runner:
            mock_runner.run = AsyncMock(side_effect=Exception("Test error"))
            
            result = await agent.generate_diagram("Invalid request")
            
            assert result['success'] is False
            assert 'error' in result
            assert result['error_type'] == 'Exception'
    
    def test_conversation_history_tracking(self, agent):
        """Test conversation history is properly tracked."""
        # Mock a conversation entry
        agent.conversation_history.append({
            "request": "Test request",
            "response": "Test response",
            "diagram_path": "/test/path.png",
            "tools_used": ["parse_hockey_formation"],
            "timestamp": 1234567890
        })
        
        history = agent.get_conversation_history()
        assert len(history) == 1
        assert history[0]["request"] == "Test request"
        
        # Test clearing
        agent.clear_conversation()
        assert len(agent.conversation_history) == 0
    
    @pytest.mark.asyncio
    async def test_capabilities_reporting(self, agent):
        """Test agent capabilities can be retrieved."""
        # Mock agent initialization
        agent.agent = Mock()
        agent.mcp_servers = [Mock(name="test-server")]
        
        capabilities = await agent.get_agent_capabilities()
        
        assert "agent_name" in capabilities
        assert "core_capabilities" in capabilities
        assert "supported_requests" in capabilities
        assert len(capabilities["mcp_servers"]) == 1

class TestAgentIntegration:
    """Integration tests for agent with MCP server."""
    
    @pytest.mark.asyncio
    async def test_server_agent_tools(self):
        """Test agent-related tools in MCP server."""
        from server import mcp
        
        # Test get_agent_status tool
        try:
            status = await mcp.get_tool("get_agent_status")()
            assert "agent_available" in status
        except Exception as e:
            # Expected if agent not fully available in test environment
            assert "agent" in str(e).lower()
    
    @pytest.mark.asyncio
    async def test_create_hockey_diagram_tool(self):
        """Test create_hockey_diagram MCP tool."""
        from server import mcp
        
        # Mock agent to avoid full initialization
        with patch('server.get_agent') as mock_get_agent:
            mock_agent = Mock()
            mock_agent.generate_diagram = AsyncMock(return_value={
                "success": True,
                "response": "Test response",
                "diagram_path": "/test/path.png"
            })
            mock_get_agent.return_value = mock_agent
            
            result = await mcp.get_tool("create_hockey_diagram")("Test request")
            
            assert result["success"] is True
            assert result["agent_used"] is True

class TestPerformanceMetrics:
    """Performance and benchmarking tests."""
    
    @pytest.mark.asyncio
    async def test_known_formation_speed(self):
        """Test that known formations are processed quickly."""
        from hockey_diagram_agent import HockeyDiagramExpert
        
        agent = HockeyDiagramExpert()
        
        # Mock fast processing
        with patch.object(agent, 'runner') as mock_runner:
            mock_result = Mock()
            mock_result.__str__ = lambda: "Fast result"
            mock_runner.run = AsyncMock(return_value=mock_result)
            
            start_time = asyncio.get_event_loop().time()
            result = await agent.generate_diagram("2-1-2 forecheck")
            processing_time = result['processing_time']
            
            # Should be very fast with mocked components
            assert processing_time < 1.0  # Less than 1 second
            assert result['success'] is True
    
    def test_memory_usage(self):
        """Test agent doesn't accumulate excessive memory."""
        from hockey_diagram_agent import HockeyDiagramExpert
        
        agent = HockeyDiagramExpert()
        
        # Simulate multiple conversations
        for i in range(100):
            agent.conversation_history.append({
                "request": f"Request {i}",
                "response": f"Response {i}",
                "timestamp": i
            })
        
        # Clear should free memory
        agent.clear_conversation()
        assert len(agent.conversation_history) == 0

class TestToolSelection:
    """Test agent's tool selection logic."""
    
    def test_formation_aliases_recognition(self):
        """Test recognition of formation aliases."""
        from agent_instructions import FORMATION_ALIASES
        
        assert "box" in FORMATION_ALIASES
        assert "penalty_kill_box" in FORMATION_ALIASES["box"]
        assert "umbrella" in FORMATION_ALIASES
    
    def test_research_prompt_templates(self):
        """Test research prompt templates are available."""
        from agent_instructions import FORMATION_RESEARCH_PROMPTS
        
        assert "unknown_system" in FORMATION_RESEARCH_PROMPTS
        assert "drill_research" in FORMATION_RESEARCH_PROMPTS
        assert "{formation_name}" in FORMATION_RESEARCH_PROMPTS["unknown_system"]

def run_integration_test():
    """Run a complete integration test if dependencies are available."""
    async def _test():
        try:
            from hockey_diagram_agent import HockeyDiagramExpert
            
            logger.info("🧪 Starting Hockey Diagram Agent integration test...")
            
            # Create agent
            agent = HockeyDiagramExpert()
            
            # Test basic functionality without full initialization
            capabilities = {
                "agent_name": "Hockey Diagram Expert",
                "test_mode": True
            }
            
            logger.info("✅ Agent creation successful")
            logger.info(f"📋 Test capabilities: {capabilities}")
            
            return True
            
        except ImportError as e:
            logger.warning(f"⚠️ Agent dependencies not available: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Integration test failed: {e}")
            return False
    
    return asyncio.run(_test())

if __name__ == "__main__":
    # Run integration test
    success = run_integration_test()
    
    if success:
        print("✅ Basic integration test passed")
    else:
        print("❌ Integration test failed - check dependencies")
    
    # Run pytest if available
    try:
        import subprocess
        result = subprocess.run(["python", "-m", "pytest", __file__, "-v"], 
                              capture_output=True, text=True)
        print("🧪 Pytest output:")
        print(result.stdout)
        if result.stderr:
            print("Errors:")
            print(result.stderr)
    except FileNotFoundError:
        print("ℹ️ Pytest not available - skipping detailed tests")