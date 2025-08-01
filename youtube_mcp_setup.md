# YouTube MCP Server Setup Instructions

## Local Build Status
The YouTube MCP server has been successfully built from source to resolve Node.js v23 compatibility issues:
- **Location**: `/Users/liammckendry/thunder_playbook/temp/youtube-mcp-server/dist/index.js`
- **API Key**: Configured in `~/.claude.json`
- **Status**: Ready for testing after Claude Code restart

## 1. Get YouTube API Key

### Steps to obtain API key:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the **YouTube Data API v3**:
   - Navigate to "APIs & Services" → "Library"
   - Search for "YouTube Data API v3"
   - Click on it and press "Enable"
4. Create API credentials:
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "API key"
   - Copy the API key
5. (Optional) Restrict the API key:
   - Click on the API key to edit
   - Under "API restrictions", select "Restrict key"
   - Choose "YouTube Data API v3"
   - Save changes

## 2. Configure YouTube MCP Server

### Add to `~/.claude.json`:

```json
{
  "mcpServers": {
    "youtube": {
      "command": "npx",
      "args": ["-y", "zubeid-youtube-mcp-server"],
      "env": {
        "YOUTUBE_API_KEY": "YOUR_API_KEY_HERE"
      }
    }
  }
}
```

### Alternative: Using environment variable (more secure):

1. Set environment variable in your shell profile (`~/.zshrc` or `~/.bash_profile`):
```bash
export YOUTUBE_API_KEY="your-actual-api-key-here"
```

2. Configure in `~/.claude.json`:
```json
{
  "mcpServers": {
    "youtube": {
      "command": "npx",
      "args": ["-y", "zubeid-youtube-mcp-server"],
      "env": {
        "YOUTUBE_API_KEY": "${YOUTUBE_API_KEY}"
      }
    }
  }
}
```

## 3. Restart Claude Code

After adding the configuration, restart Claude Code for the changes to take effect.

## 4. Verify Installation

In Claude Code, you should now have access to YouTube MCP tools. Test with:
- Ask Claude to search for hockey coaching videos
- The available tools will include YouTube search, transcript retrieval, etc.

## Available YouTube MCP Tools

Once configured, you'll have access to:
- **Video Search**: Search YouTube for videos by query
- **Get Video Details**: Retrieve video metadata, statistics
- **Get Transcripts**: Extract video transcripts with timestamps
- **Channel Operations**: Get channel info, list channel videos
- **Playlist Operations**: Get playlist details and items

## Troubleshooting

- **API Key Issues**: Ensure your API key has YouTube Data API v3 enabled
- **Connection Errors**: Check `claude mcp list` to verify server status
- **Tool Not Available**: Restart Claude Code after configuration changes