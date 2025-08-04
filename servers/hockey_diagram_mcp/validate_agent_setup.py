"""
Validation script for Hockey Diagram Agent setup.
Checks dependencies, imports, and basic functionality.
"""

import sys
import asyncio
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class AgentValidator:
    """Validates the Hockey Diagram Agent setup."""
    
    def __init__(self):
        self.checks_passed = 0
        self.checks_total = 0
        self.errors = []
    
    def check(self, description: str, condition: bool, error_msg: str = None):
        """Run a validation check."""
        self.checks_total += 1
        
        if condition:
            self.checks_passed += 1
            logger.info(f"✅ {description}")
        else:
            error = error_msg or f"Failed: {description}"
            self.errors.append(error)
            logger.error(f"❌ {error}")
    
    def validate_dependencies(self):
        """Check required dependencies are installed."""
        logger.info("🔍 Checking dependencies...")
        
        # Check OpenAI Agents SDK
        try:
            from agents import Agent, Runner
            self.check("OpenAI Agents SDK imported", True)
        except ImportError as e:
            self.check("OpenAI Agents SDK imported", False, f"Missing agents package: {e}")
        
        # Check MCP support
        try:
            from agents.mcp import MCPServerStdio
            self.check("MCP server support available", True)
        except ImportError as e:
            self.check("MCP server support available", False, f"Missing MCP support: {e}")
        
        # Check OpenAI SDK
        try:
            import openai
            self.check("OpenAI SDK available", True)
        except ImportError:
            self.check("OpenAI SDK available", False, "Missing openai package")
        
        # Check environment variables
        import os
        api_key = os.getenv("OPENAI_API_KEY")
        self.check("OPENAI_API_KEY set", bool(api_key), "OPENAI_API_KEY not found in environment")
    
    def validate_file_structure(self):
        """Check required files exist."""
        logger.info("📁 Checking file structure...")
        
        current_dir = Path(__file__).parent
        
        required_files = [
            "hockey_diagram_agent.py",
            "agent_instructions.py", 
            "server.py",
            "two_stage_parser.py",
            "generator.py",
            "zone_grid.py"
        ]
        
        for file in required_files:
            file_path = current_dir / file
            self.check(f"{file} exists", file_path.exists(), f"Missing file: {file}")
    
    def validate_imports(self):
        """Check agent files can be imported."""
        logger.info("📦 Checking imports...")
        
        try:
            from agent_instructions import EXPERT_INSTRUCTIONS
            self.check("Agent instructions import", True)
        except ImportError as e:
            self.check("Agent instructions import", False, str(e))
        
        try:
            from hockey_diagram_agent import HockeyDiagramExpert
            self.check("Hockey diagram agent import", True)
        except ImportError as e:
            self.check("Hockey diagram agent import", False, str(e))
        
        try:
            import server
            self.check("MCP server import", True)
        except ImportError as e:
            self.check("MCP server import", False, str(e))
    
    async def validate_agent_creation(self):
        """Test agent can be created."""
        logger.info("🤖 Testing agent creation...")
        
        try:
            from hockey_diagram_agent import HockeyDiagramExpert
            agent = HockeyDiagramExpert()
            self.check("Agent instance created", True)
            
            # Test capabilities method
            if hasattr(agent, 'get_agent_capabilities'):
                try:
                    # Mock the agent to avoid full initialization
                    agent.agent = type('MockAgent', (), {})()
                    agent.mcp_servers = []
                    capabilities = await agent.get_agent_capabilities()
                    self.check("Agent capabilities retrieved", isinstance(capabilities, dict))
                except Exception as e:
                    self.check("Agent capabilities retrieved", False, str(e))
            else:
                self.check("Agent has capabilities method", False)
                
        except Exception as e:
            self.check("Agent instance created", False, str(e))
    
    def validate_mcp_tools(self):
        """Check MCP tools are properly defined."""
        logger.info("🛠️ Checking MCP tools...")
        
        try:
            import server
            
            # Check if FastMCP instance exists
            if hasattr(server, 'mcp'):
                self.check("MCP server instance exists", True)
                
                # Check for agent-specific tools
                tool_names = ['create_hockey_diagram', 'get_agent_status', 'clear_agent_conversation']
                
                for tool_name in tool_names:
                    # This is a simplified check - in practice, tools are registered differently
                    self.check(f"Tool {tool_name} defined", hasattr(server, tool_name) or tool_name in str(server))
            else:
                self.check("MCP server instance exists", False)
                
        except Exception as e:
            self.check("MCP tools validation", False, str(e))
    
    def print_summary(self):
        """Print validation summary."""
        logger.info("\n" + "="*50)
        logger.info("VALIDATION SUMMARY")
        logger.info("="*50)
        
        success_rate = (self.checks_passed / self.checks_total * 100) if self.checks_total > 0 else 0
        
        if self.checks_passed == self.checks_total:
            logger.info(f"🎉 ALL CHECKS PASSED ({self.checks_passed}/{self.checks_total})")
        else:
            logger.info(f"📊 {self.checks_passed}/{self.checks_total} checks passed ({success_rate:.1f}%)")
        
        if self.errors:
            logger.info("\n❌ ISSUES FOUND:")
            for i, error in enumerate(self.errors, 1):
                logger.info(f"{i}. {error}")
            
            logger.info("\n🔧 RECOMMENDED ACTIONS:")
            if any("agents package" in error for error in self.errors):
                logger.info("- Install OpenAI Agents SDK: pip install openai-agents")
            if any("OPENAI_API_KEY" in error for error in self.errors):
                logger.info("- Set OPENAI_API_KEY environment variable")
            if any("Missing file" in error for error in self.errors):
                logger.info("- Ensure all required files are in the correct location")
        else:
            logger.info("\n✅ Setup appears to be complete!")
        
        return self.checks_passed == self.checks_total

async def main():
    """Run full validation."""
    print("🔍 Hockey Diagram Agent Setup Validation")
    print("="*50)
    
    validator = AgentValidator()
    
    # Run all validations
    validator.validate_dependencies()
    validator.validate_file_structure()
    validator.validate_imports()
    await validator.validate_agent_creation()
    validator.validate_mcp_tools()
    
    # Print summary
    success = validator.print_summary()
    
    return success

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️ Validation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Validation failed with error: {e}")
        sys.exit(1)