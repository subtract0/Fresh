# 🚀 Fresh Autonomous Development System - Quick Start

## What is Fresh?

Fresh is an **autonomous development system** that continuously improves your codebase by:
- 🔍 **Scanning** for issues (TODOs, FIXMEs, failing tests)
- 🤖 **Dispatching** specialized AI agents to fix them
- 📊 **Monitoring** progress in real-time
- 🔄 **Learning** from each task through persistent memory

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/Fresh.git
cd Fresh

# Install dependencies
poetry install

# Make Fresh command executable
chmod +x fresh
```

## Quick Commands

### 1. Scan Your Repository
Find all issues in your codebase:
```bash
./fresh scan

# Output as JSON for scripting
./fresh scan --json

# Scan specific directory
./fresh scan /path/to/repo
```

### 2. Run Autonomous Development
Process issues automatically:
```bash
# Single cycle (process up to 5 tasks)
./fresh run

# Dry run (see what would be done)
./fresh run --dry-run

# Process more tasks
./fresh run --max-tasks 10
```

### 3. Continuous Monitoring
Keep Fresh running in the background:
```bash
# Simple continuous mode
./fresh run --watch

# With live dashboard (recommended)
./fresh monitor

# Custom interval (check every 10 minutes)
./fresh monitor --interval 600
```

### 4. Direct Agent Spawning
Spawn an agent for a specific task:
```bash
./fresh spawn "Implement user authentication"

# Specify output type
./fresh spawn "Write tests for payment module" --output tests

# Use different model
./fresh spawn "Optimize database queries" --model gpt-3.5-turbo
```

## 🎯 Try the Demo

See Fresh in action with our interactive demo:
```bash
python demo_autonomous.py
```

The demo will:
1. Create a temporary repository with sample issues
2. Scan for problems
3. Show agent dispatching
4. Display real-time progress (with dashboard option)

## System Architecture

```
Repository → Scanner → Mother Agent → Agent Swarm → Results
                           ↓
                    [Father, Architect, Developer, QA, Reviewer]
```

### Key Components

- **Mother Agent**: Spawns specialized agents based on task type
- **Repository Scanner**: Detects issues in your codebase
- **Development Loop**: Orchestrates the autonomous workflow
- **Console Dashboard**: Real-time monitoring interface
- **Memory System**: Persistent context across sessions

## Agent Specializations

| Agent | Specializes In | Triggered By |
|-------|---------------|--------------|
| **Father** | Strategic planning, coordination | General tasks, planning needs |
| **Architect** | System design, API structure | Design tasks, architecture issues |
| **Developer** | Code implementation, bug fixes | TODOs, FIXMEs, code tasks |
| **QA** | Test writing, quality assurance | Test-related tasks, failing tests |
| **Reviewer** | Code review, validation | Review requests, validation needs |

## Configuration

### State Persistence
Fresh maintains state between runs:
```bash
# State file location
.fresh/dev_loop_state.json

# Clear state to reprocess all tasks
rm .fresh/dev_loop_state.json
```

### Environment Variables
```bash
# Set OpenAI API key for agent execution
export OPENAI_API_KEY="your-key-here"

# Optional: GitHub integration
export GITHUB_TOKEN="your-github-token"
export GITHUB_REPO_OWNER="your-username"
export GITHUB_REPO_NAME="your-repo"
```

## Advanced Usage

### Filter Task Types
Process only specific types of issues:
```python
from ai.loop.dev_loop import DevLoop, TaskType

loop = DevLoop(
    task_types=[TaskType.FAILING_TEST, TaskType.FIXME],
    max_tasks=10
)
```

### Custom Agent Instructions
```python
from ai.agents.mother import MotherAgent

mother = MotherAgent()
result = mother.run(
    name="custom_task",
    instructions="Implement OAuth2 authentication with refresh tokens",
    model="gpt-4",
    output_type="code"
)
```

## Dashboard Features

When using `./fresh monitor` or `--dashboard`:

```
🤖 Fresh Autonomous Development Loop
┌─────────────────────────────────────────┐
│ 📊 Status         │ 📜 Recent Activity   │
├───────────────────┼──────────────────────┤
│ ⚡ Processing     │ 14:23:15 Developer   │
│ 📊 Found: 21      │   Fixed TODO in app  │
│ ✅ Processed: 5   │ 14:22:30 QA          │
│ ❌ Failed: 0      │   Added test cases   │
│ 📈 Success: 100%  │ 14:21:45 Father      │
│                   │   Created strategy   │
└───────────────────┴──────────────────────┘
```

## Troubleshooting

### Common Issues

1. **No tasks found**
   - Ensure you're in a git repository
   - Check that files aren't in ignored directories

2. **Agents not executing**
   - Verify OPENAI_API_KEY is set
   - Try with --dry-run first to test scanning

3. **Dashboard not showing**
   - Install Rich: `pip install rich`
   - Use terminal that supports ANSI colors

## Contributing

Fresh is designed to be extended. Key extension points:

1. **New Task Types**: Add to `TaskType` enum in `repo_scanner.py`
2. **Custom Agents**: Add to `ai/agents/` and wire into Mother Agent
3. **New Scanners**: Extend `RepoScanner` class
4. **Dashboard Widgets**: Modify `console_dashboard.py`

## License

MIT License - See LICENSE file for details

## Support

- 📖 Documentation: [docs/INDEX.md](docs/INDEX.md)
- 🐛 Issues: GitHub Issues
- 💬 Discussions: GitHub Discussions

---

**Ready to let Fresh improve your codebase autonomously?**

Start with: `./fresh scan` to see what Fresh can fix for you!
