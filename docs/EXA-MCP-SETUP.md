# EXA-MCP Integration Setup Guide

This guide explains how to enable real web research capabilities in the Fresh Agent Orchestration System using EXA API through MCP (Model Context Protocol).

## Overview

The Fresh orchestration system includes sophisticated research agents that can perform real web searches, company analysis, and market research using EXA AI's search capabilities. By default, the system runs in simulation mode, but you can enable real research with proper configuration.

## Prerequisites

1. **EXA API Access**: Sign up at [exa.ai](https://exa.ai) to get API credentials
2. **MCP Server**: Configure Model Context Protocol server for EXA integration
3. **Fresh System**: Have the Enhanced Agent Orchestration System installed

## Setup Steps

### 1. Get EXA API Credentials

1. Visit [exa.ai](https://exa.ai) and create an account
2. Navigate to your API settings/dashboard
3. Generate an API key
4. Note your API key (keep it secure!)

### 2. Configure MCP Server

The Fresh system includes MCP integration that can connect to EXA services. You need to configure the MCP server:

#### Option A: Local MCP Configuration

Create or update your MCP configuration file:

```json
{
  "mcpServers": {
    "research": {
      "command": "exa-mcp-server",
      "args": ["--api-key", "${EXA_API_KEY}"],
      "env": {
        "EXA_API_KEY": "your-exa-api-key-here"
      }
    }
  }
}
```

#### Option B: Environment Variables

Set the EXA API key in your environment:

```bash
# Add to your ~/.zshrc, ~/.bashrc, or .env file
export EXA_API_KEY="your-exa-api-key-here"

# For the current session
export EXA_API_KEY="your-exa-api-key-here"
```

### 3. Install EXA MCP Server

If you're using a standard EXA MCP server implementation:

```bash
# Option 1: Install via npm (if available)
npm install -g @exa-ai/mcp-server

# Option 2: Install via pip (if available)
pip install exa-mcp-server

# Option 3: Clone and setup manually
git clone https://github.com/exa-ai/mcp-server
cd mcp-server
npm install
npm run build
```

### 4. Verify Configuration

Test your EXA integration:

```bash
# Run the orchestration test to check MCP connectivity
poetry run python test_orchestration.py

# Look for these messages:
# ✅ Real EXA search completed via MCP
# ✅ Real company research completed for [company]
```

If you see "⚠️ MCP not configured, using simulation" messages, the integration needs setup.

### 5. Test Real Research

Try the orchestration with a simple command:

```bash
# Basic test
poetry run fresh orchestrate "Research the current state of AI agent platforms"

# With constraints
poetry run fresh orchestrate "Find competitors in autonomous software deployment" \
  --budget under_$500 \
  --timeline same_day \
  --skip-clarifications
```

## Available Research Capabilities

Once EXA-MCP is configured, your orchestration system can perform:

### Web Search (`web_search_exa`)
- Real-time web searches with customizable results count
- Market trend analysis
- Technology research
- Industry insights

```bash
fresh orchestrate "Research current trends in AI automation tools"
```

### Company Research (`company_research_exa`)
- Company profile analysis
- Funding information
- Competitor identification
- Industry positioning

```bash
fresh orchestrate "Analyze competitors in the SaaS automation space"
```

### LinkedIn Search (`linkedin_search_exa`)
- Professional network research
- Company employee insights
- Industry professional analysis

### Content Crawling (`crawling_exa`)
- Deep content extraction from specific URLs
- Detailed article analysis
- Research report generation

## Simulation vs Real Mode

### Simulation Mode (Default)
- **When**: No EXA API key configured or MCP server unavailable
- **Behavior**: Returns structured mock data for testing and development
- **Indicators**: Messages show "using simulation" or "MCP not configured"
- **Benefits**: Works offline, no API costs, consistent testing

### Real Mode (EXA Enabled)
- **When**: EXA API properly configured via MCP
- **Behavior**: Makes actual web searches and company research calls
- **Indicators**: Messages show "Real EXA search completed" or "via MCP"
- **Benefits**: Actual data, current information, comprehensive research

## Configuration Verification

### Check MCP Status
```bash
# Check available MCP servers
poetry run fresh mcp status

# Refresh MCP discovery
poetry run fresh mcp refresh
```

### Test Individual Components
```python
# Test the MCP integration directly
from ai.tools.mcp_client import CallMCPTool

# Test web search
search_tool = CallMCPTool(
    server="research",
    tool="web_search_exa", 
    args={"query": "AI agent platforms", "numResults": 5}
)

result = search_tool.run()
print(f"Result: {result}")

# Look for real data vs mock response
```

## Troubleshooting

### Common Issues

#### 1. "MCP not configured" Messages
- **Cause**: EXA API key not set or MCP server not running
- **Solution**: Verify API key environment variable and MCP server status

#### 2. "Mock result" Responses
- **Cause**: MCP server returning placeholder data instead of real EXA results
- **Solution**: Check MCP server logs, verify EXA API key validity

#### 3. Import Errors
- **Cause**: Missing MCP client dependencies
- **Solution**: Run `poetry install` to ensure all dependencies are present

#### 4. API Rate Limits
- **Cause**: Hitting EXA API rate limits during heavy orchestration
- **Solution**: Add delays between requests or implement request batching

### Debug Mode

Enable verbose logging to debug MCP integration:

```bash
# Set debug environment variable
export FRESH_DEBUG=1

# Run orchestration with debug output
poetry run fresh orchestrate "test command" --skip-clarifications
```

### Check Logs

Review orchestration logs for detailed information:

```bash
# Check recent orchestration results
ls -la .fresh/orchestration-*.log

# View specific orchestration log
tail -f .fresh/orchestration-latest.log
```

## Performance Considerations

### API Usage Optimization

- **Batch Requests**: Group similar research queries when possible
- **Cache Results**: Store research results to avoid duplicate API calls
- **Rate Limiting**: Respect EXA API rate limits to avoid throttling

### Cost Management

- **Result Limits**: Use appropriate `numResults` parameters (default: 5-10)
- **Query Optimization**: Make specific queries to reduce unnecessary API calls
- **Simulation Mode**: Use simulation for development/testing to avoid API costs

## Advanced Configuration

### Custom MCP Integration

If you need custom EXA integration:

1. **Extend MCP Tools**: Add custom tools to `ai/tools/mcp_client.py`
2. **Custom Server Config**: Create specialized MCP server configurations
3. **Result Processing**: Add custom result processing for specific use cases

### Orchestration Tuning

Configure orchestration for optimal EXA usage:

```python
# In your orchestration setup
enhanced_mother = EnhancedMotherAgent()

# Configure research parameters
constraints = {
    "research_depth": "comprehensive",  # vs "quick"
    "max_results_per_query": 10,
    "enable_company_research": True,
    "enable_linkedin_search": False  # if not needed
}

result = await enhanced_mother.orchestrate_complex_task(
    command="Your research command",
    constraints=constraints
)
```

## Security Best Practices

1. **API Key Protection**: Never commit EXA API keys to version control
2. **Environment Variables**: Use secure environment variable management
3. **Access Control**: Limit EXA API access to authorized users only
4. **Monitoring**: Monitor API usage for unusual patterns

## Support and Resources

### Documentation
- [EXA AI Documentation](https://docs.exa.ai)
- [Model Context Protocol Spec](https://modelcontextprotocol.io)
- [Fresh Agent System ADR-012](./ADR-012-enhanced-agent-orchestration.md)

### Getting Help
- Check the troubleshooting section above
- Review orchestration logs for error details
- Test in simulation mode first to isolate MCP issues
- Verify API credentials and server configuration

### Example Working Configuration

Here's a complete working example:

```bash
# 1. Set environment variable
export EXA_API_KEY="exa_xxxxxxxxxxxxxxxxxxxx"

# 2. Test MCP status
poetry run fresh mcp status

# 3. Run a test orchestration
poetry run fresh orchestrate "Research AI agent market trends" \
  --skip-clarifications \
  --output-format json > research_results.json

# 4. Check for real data indicators
grep -i "real.*search.*completed" logs/orchestration.log
```

If everything is configured correctly, you should see real research data with current, accurate information from EXA's web search capabilities integrated into your autonomous agent orchestration system.
