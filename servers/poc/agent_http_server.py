#!/usr/bin/env python3
"""
Simple HTTP server for the MCP agent to avoid subprocess issues.
"""

import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import sys
import os
from pathlib import Path
from urllib.parse import parse_qs
import logging

# Add POC to path
sys.path.append(str(Path(__file__).parent))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Read the request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            # Parse JSON
            data = json.loads(post_data.decode('utf-8'))
            message = data.get('message', '')
            
            logger.info(f"Received message: {message}")
            
            # Import and run agent
            from poc_agents.web_native_mcp_agent import run_web_mcp_agent_with_logging
            
            # Run the agent
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                response = loop.run_until_complete(run_web_mcp_agent_with_logging(message))
                
                # Send response
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response_data = {
                    'response': response,
                    'timestamp': '2025-07-25T14:22:00.000Z',
                    'processingTime': 1000
                }
                
                self.wfile.write(json.dumps(response_data).encode('utf-8'))
                
            finally:
                loop.close()
                
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            error_data = {
                'error': str(e),
                'timestamp': '2025-07-25T14:22:00.000Z',
                'processingTime': 0
            }
            self.wfile.write(json.dumps(error_data).encode('utf-8'))
    
    def do_OPTIONS(self):
        # Handle CORS preflight
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        # Suppress default HTTP logging
        pass

def main():
    port = 8002  # Use different port to avoid conflicts
    server = HTTPServer(('localhost', port), AgentHandler)
    print(f"🚀 Agent HTTP server running on http://localhost:{port}")
    print("Ready to receive agent requests...")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        server.shutdown()

if __name__ == "__main__":
    main()