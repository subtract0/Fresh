# Interface Components

This directory contains user interface and external integration components for the Fresh AI system.

## Components

### Agent Spawning Interface
- **`agent_spawner.py`** - Agent creation and management interface
- **`deploy_agents.py`** - Agent deployment utilities

### User Interfaces
- **`console_dashboard.py`** - Command-line dashboard for system monitoring
- **`telegram_bot.py`** - Telegram bot interface for remote agent interaction

### Task Management
- **`ask_implement.py`** - Task specification and implementation request interface

## Usage

### Telegram Bot
```python
from ai.interface.telegram_bot import start_bot
start_bot()  # Requires TELEGRAM_BOT_TOKEN environment variable
```

### Console Dashboard
```python
from ai.interface.console_dashboard import display_dashboard
display_dashboard()  # Shows system status and metrics
```

### Agent Spawning
```python
from ai.interface.agent_spawner import spawn_agent
agent = spawn_agent("Developer", "Implement user authentication")
```

## Configuration

Set the following environment variables:
- `TELEGRAM_BOT_TOKEN` - For Telegram bot functionality

## Related Documentation
- [Telegram Bot Guide](../../docs/TELEGRAM_BOT.md)
- [Agent Development Guide](../../docs/AGENT_DEVELOPMENT.md)
