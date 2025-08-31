# 🤖 Telegram Bot Interface

> **Foolproof User Interface**: Submit development requests through Telegram and let the Father agent intelligently deploy specialized agent teams.

**📚 Cross-References**: [Documentation Index](INDEX.md) | [Interface Documentation](INTERFACES.md) | [Agent Development Guide](AGENT_DEVELOPMENT.md) | [Father Agent](../ai/agents/Father.py)

---

## 🎯 Overview

The Fresh Telegram Bot provides a **foolproof interface** for users to interact with the agent system. Users can submit development requests in natural language, and the Father agent will:

1. **Analyze the request** using context from memory, ADRs, and documentation
2. **Determine optimal agent configuration** - what kind, how many, with what instructions
3. **Spawn specialized agents** dynamically configured for the task
4. **Coordinate execution** through the persistent memory system

### Key Features

- **Natural Language Interface**: Describe what you want in plain English
- **Intelligent Analysis**: Father agent considers context, documentation, and ADRs
- **Dynamic Agent Spawning**: Creates custom agent teams for each task
- **Persistent Memory**: Conversations and context persist across sessions
- **Real-time Updates**: Get progress updates as agents work
- **Security**: Optional user authorization and input validation

---

## 🚀 Quick Start

### 1. Set Up Telegram Bot

1. **Create Bot with @BotFather**:
   - Message @BotFather on Telegram
   - Use `/newbot` command
   - Follow prompts to create your bot
   - Save the bot token

2. **Configure Environment**:
   ```bash
   # Add to .env file
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   
   # Optional: Restrict to specific users
   TELEGRAM_AUTHORIZED_USERS=123456789,987654321
   ```

### 2. Install Dependencies

```bash
# Install Telegram dependencies
poetry add python-telegram-bot

# Or let the script install them automatically
./scripts/telegram.sh
```

### 3. Run the Bot

```bash
./scripts/telegram.sh
```

The bot will start and display connection information.

---

## 💬 User Commands

### Core Commands

| Command | Purpose | Example |
|---------|---------|---------|
| `/start` | Welcome and introduction | `/start` |
| `/request` | Submit development request | `/request` |
| `/status` | Check system status | `/status` |
| `/help` | Show detailed help | `/help` |

### Request Flow

1. **Initiate**: User types `/request`
2. **Choose Type**: Select from predefined categories or describe freely
3. **Describe**: Provide detailed description of what you want
4. **Review**: Father agent analyzes and proposes agent team
5. **Approve**: User reviews and approves deployment
6. **Monitor**: Get updates as agents work

---

## 🧠 Father Agent Decision Making

The Father agent uses sophisticated analysis to determine the optimal agent configuration:

### Analysis Inputs

- **User Request**: Natural language description
- **Memory Context**: Previous conversations and decisions
- **Documentation**: README, ADRs, agent guides
- **System State**: Current capabilities and available tools

### Decision Factors

- **Task Type**: Development, documentation, bug fix, deployment
- **Complexity**: Simple tasks vs. complex multi-step projects
- **Required Skills**: Technical domains and specializations needed
- **Resource Availability**: Available tools and agent types
- **Historical Context**: Similar requests and their outcomes

### Example Decision Process

**User Request**: *"Add a web scraper tool for documentation"*

**Father Analysis**:
```
Task Type: Development
Complexity: Medium
Required Skills: Web scraping, tool integration, documentation
Optimal Team: Architect + Developer + QA + Documenter
Estimated Time: 45-60 minutes
```

**Proposed Agents**:
- **Architect** (1): Design tool architecture and integration points
- **Developer** (1): Implement web scraper with MCP integration  
- **QA** (1): Test functionality and edge cases
- **Documenter** (1): Create usage documentation and examples

---

## 🛠️ Technical Architecture

### Components

- **[Telegram Bot](../ai/interface/telegram_bot.py)**: Main interface handling user interactions
- **[Father Decision Maker](../ai/interface/telegram_bot.py#L44)**: Request analysis and agent selection
- **[Agent Spawner](../ai/interface/agent_spawner.py)**: Dynamic agent creation and deployment
- **[Memory Integration](../ai/memory/README.md)**: Persistent context and coordination

### Request Processing Flow

```
User Request
    ↓
Telegram Bot (input validation, session management)
    ↓  
Father Decision Maker (analyze context, determine agents)
    ↓
Agent Spawner (create configurations, deploy agents)
    ↓
Memory System (store context, coordinate execution)
    ↓
Response to User (confirmation, progress updates)
```

### Security Features

- **User Authorization**: Optional whitelist of authorized users
- **Input Validation**: Sanitize and validate all user inputs
- **Rate Limiting**: Prevent abuse and excessive requests
- **Safe Execution**: All agent operations run in controlled environment
- **Audit Trail**: All interactions logged in memory system

---

## 🎨 Request Types & Examples

### Development Requests

**Example**: *"Build a REST API endpoint for user authentication"*

**Agent Team**:
- Architect: Design API structure and authentication flow
- Developer: Implement endpoint with proper validation
- QA: Test security and functionality
- Documenter: Create API documentation

### Documentation Requests

**Example**: *"Create a troubleshooting guide for common setup issues"*

**Agent Team**:
- Researcher: Analyze common issues from support tickets and documentation
- Documenter: Create structured troubleshooting guide with solutions

### Bug Fix Requests

**Example**: *"Fix the memory leak in the agent spawning process"*

**Agent Team**:
- Debugger: Analyze memory usage patterns and identify leak source
- Developer: Implement targeted fix with monitoring
- QA: Validate fix and add regression tests

### Deployment Requests

**Example**: *"Set up automated deployment pipeline for the bot"*

**Agent Team**:
- DevOps: Design pipeline architecture and security considerations
- Developer: Implement CI/CD configuration and scripts
- QA: Test deployment process and rollback procedures

---

## 🔧 Configuration Options

### Environment Variables

```bash
# Required
TELEGRAM_BOT_TOKEN=your_bot_token

# Optional Security
TELEGRAM_AUTHORIZED_USERS=user_id_1,user_id_2
TELEGRAM_RATE_LIMIT=10  # requests per minute
TELEGRAM_MAX_REQUEST_LENGTH=1000  # characters

# Optional Features
TELEGRAM_ENABLE_LOGGING=true
TELEGRAM_LOG_LEVEL=INFO
```

### Bot Behavior

```python
# In telegram_bot.py - customize these settings
PROCESSING_TIMEOUT = 300  # seconds
MAX_AGENTS_PER_REQUEST = 5
SUPPORTED_TASK_TYPES = ["development", "documentation", "bugfix", "deployment", "analysis"]
```

---

## 📊 Monitoring & Debugging

### Bot Status

```bash
# Check bot status
./scripts/telegram.sh status

# View recent activity
./scripts/monitor.sh
```

### Memory Inspection

The bot stores all interactions in the persistent memory system:

```python
from ai.tools.memory_tools import ReadMemoryContext

# Get recent Telegram activity
context = ReadMemoryContext(limit=20, tags=["telegram"]).run()
print(context)
```

### Spawn History

```python
from ai.interface.agent_spawner import get_agent_spawner

spawner = get_agent_spawner()
history = spawner.get_spawn_history(limit=10)
active_agents = spawner.list_active_agents()
```

---

## 🔍 Troubleshooting

### Common Issues

**Bot not responding**:
- Check `TELEGRAM_BOT_TOKEN` is correct
- Verify bot is running with `./scripts/telegram.sh`
- Check network connectivity

**"Access denied" errors**:
- Verify user ID is in `TELEGRAM_AUTHORIZED_USERS`
- Check user permissions with @BotFather

**Agent spawning fails**:
- Check memory system is operational
- Verify all required dependencies are installed
- Review spawn logs in memory system

**Memory system errors**:
- Ensure Firestore is properly configured
- Check Firebase credentials and permissions
- Verify database exists and is accessible

### Debug Mode

```bash
# Run with debug logging
TELEGRAM_LOG_LEVEL=DEBUG ./scripts/telegram.sh
```

---

## 🎯 Best Practices

### For Users

- **Be Specific**: Include context about what you want to achieve
- **Mention Constraints**: Any technical requirements or limitations  
- **Reference Existing Work**: Mention related features or documentation
- **Iterate**: Start with simple requests and build complexity

### For Administrators

- **Monitor Usage**: Regular checks of spawn history and resource usage
- **Update Documentation**: Keep bot help text and guides current
- **Security Reviews**: Regular audits of authorized users and permissions
- **Backup Strategy**: Ensure memory system has proper backup and recovery

---

## 🔗 Related Documentation

- **[Interface Documentation](INTERFACES.md)** - All available interfaces including CLI
- **[Agent Development Guide](AGENT_DEVELOPMENT.md)** - Creating and configuring agents
- **[Memory System Guide](../ai/memory/README.md)** - Understanding context persistence
- **[Tool Reference](TOOLS.md)** - Available tools for agent configuration
- **[Deployment Guide](DEPLOYMENT.md)** - System deployment and management

---

## 🚀 Advanced Usage

### Custom Agent Templates

Create custom agent templates for recurring task types:

```python
# In telegram_bot.py - add custom patterns
custom_patterns = {
    "api_development": {
        "agents": [
            {"type": "APIArchitect", "role": "API Design", ...},
            {"type": "BackendDeveloper", "role": "Implementation", ...},
            {"type": "APITester", "role": "Testing & Validation", ...}
        ]
    }
}
```

### Integration with External Tools

The bot can be extended to integrate with external tools and services:

- **GitHub Integration**: Automatically create issues and PRs
- **Slack Notifications**: Send updates to team channels
- **Monitoring Systems**: Alert on agent failures or completions
- **CI/CD Pipelines**: Trigger builds and deployments

### Webhook Mode

For production deployments, consider webhook mode instead of polling:

```python
# Webhook configuration in telegram_bot.py
application.run_webhook(
    listen="0.0.0.0",
    port=PORT,
    url_path=TOKEN,
    webhook_url=f"https://yourdomain.com/{TOKEN}"
)
```

---

> 💡 **Agent Tip**: The Telegram bot is designed to be the primary user interface for the Fresh agent system. It abstracts away the complexity of agent management while providing intelligent task delegation through the Father agent's decision-making capabilities.

The bot serves as a **force multiplier** - turning simple user requests into sophisticated multi-agent workflows that leverage the full power of the Fresh ecosystem! 🤖✨
