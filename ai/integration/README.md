# Integration Components

This directory contains integration modules for connecting the Fresh AI system with external services and platforms.

## Components

### GitHub Integration
- **`github.py`** - Core GitHub API integration and utilities
- **`github_pr.py`** - Pull request automation and management

### Service Discovery
- **`mcp_discovery.py`** - Model Context Protocol (MCP) service discovery and management

## Features

### GitHub Integration
- Repository analysis and scanning
- Pull request creation and management
- Issue tracking and automation
- Code review assistance

### MCP Discovery
- Automatic discovery of MCP servers
- Service health monitoring
- Connection management and routing

## Usage

### GitHub Integration
```python
from ai.integration.github import GitHubIntegration

gh = GitHubIntegration()
pr = gh.create_pull_request(
    repo="owner/repository",
    title="Automated improvement",
    body="Description of changes",
    head="feature-branch",
    base="main"
)
```

### MCP Discovery
```python
from ai.integration.mcp_discovery import discover_mcp_servers

servers = discover_mcp_servers()
for server in servers:
    print(f"Found MCP server: {server.name} at {server.url}")
```

## Configuration

Set the following environment variables:
- `GITHUB_TOKEN` - GitHub personal access token for API access
- `MCP_SERVER_URLS` - Comma-separated list of MCP server URLs to discover

## Dependencies
- `github` - Python GitHub API client
- `requests` - HTTP client for MCP communication

## Related Documentation
- [GitHub Integration Guide](../../docs/GITHUB_INTEGRATION.md)
- [MCP Documentation](../../docs/MCP.md)
