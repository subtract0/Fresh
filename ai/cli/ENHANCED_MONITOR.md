# 🎮 Enhanced Interactive CLI Monitor

**Real-time agent monitoring and control dashboard with button-like controls**

## ✨ Features

- **🤖 Real-Time Agent Status**: Live status of all agent types (autonomous, scanner, product manager, documentation, custom)
- **🎮 Interactive Controls**: Keyboard shortcuts to start/stop different agent types
- **📊 Live Performance Metrics**: Cycle times, success rates, opportunities discovered
- **📝 Activity Feed**: Real-time log of agent actions and events
- **🚨 Safety Controls**: Emergency stop and safe operation monitoring
- **🎨 Professional UI**: Rich terminal interface with colors and panels

## 🚀 Quick Start

```bash
# Launch enhanced interactive monitor
poetry run python -m ai.cli.fresh monitor --enhanced

# Standard monitor (existing functionality)  
poetry run python -m ai.cli.fresh monitor
```

## 🎮 Controls

Once the enhanced monitor is running, use these keyboard shortcuts:

### Agent Controls
- **[1]** - Start **Autonomous Loop** (continuous improvement)
- **[2]** - Run **Single Scan** (repository analysis)
- **[3]** - Activate **Product Manager** (feature planning)
- **[4]** - Start **Documentation Agent** (doc generation)
- **[5]** - **Custom Spawn** (spawn agent for specific task)

### System Controls
- **[S]** - **Stop Current** operation
- **[E]** - **Emergency Stop** (stops everything immediately)
- **[R]** - **Refresh Status** 
- **[Q]** - **Quit** monitor

## 📊 Dashboard Layout

```
┌─────────────────────────────────────────────────────┐
│           🤖 Fresh Agent Control Dashboard          │
│                Live Monitor • 2025-01-05 02:22:43  │
└─────────────────────────────────────────────────────┘
┌─────────────── 🤖 Agent Status ────────────────────┐┌─────────── ⚡ Live Activity ───────────────┐
│ Agent Type     │ Status      │ Last Activity      ││ 📊 Metrics        │ 📝 Recent Activity   │
│ Autonomous     │ 🚀 running  │ 02:22:40          ││ Avg Cycle: 18.2s  │ [02:22:43] Started   │
│ Scanner        │ 😴 idle     │ Never             ││ Success: 95%      │ [02:22:40] Scan done │
│ Product Mgr    │ 😴 idle     │ Never             ││ Opportunities: 30K │ [02:22:35] Emergency │
│ Documentation  │ 😴 idle     │ Never             ││ Improvements: 5   │ [02:22:30] Cycle end │
│ Custom         │ 😴 idle     │ Never             │└─────────────────────────────────────────────┘
└─────────────────────────────────────────────────────┘
┌─────────────────── 🎛️ Controls ───────────────────┐
│ 🎮 Agent Controls                                   │
│                                                     │
│ [1] Autonomous Loop   [2] Single Scan   [3] PM     │
│ [4] Documentation     [5] Custom Spawn  [S] Stop   │
│ [E] Emergency Stop    [R] Refresh       [Q] Quit   │
│                                                     │
│ 🎯 Current: Autonomous Loop                        │
└─────────────────────────────────────────────────────┘
```

## 🎯 Agent Types

### 1. 🤖 Autonomous Loop
- **Purpose**: Continuous code improvement
- **Features**: Discovers opportunities, plans improvements, executes safely
- **Status**: Shows cycle count, last run time
- **Controls**: Start continuous loop, stop gracefully

### 2. 🔍 Scanner  
- **Purpose**: Repository analysis and issue detection
- **Features**: Finds TODOs, bugs, failing tests, security issues
- **Status**: Shows issues found, last scan time
- **Controls**: Run single scan

### 3. 📋 Product Manager
- **Purpose**: Feature planning and roadmap creation
- **Features**: Transforms ideas into actionable plans
- **Status**: Shows plans created, last activity
- **Controls**: Activate planning mode

### 4. 📚 Documentation Agent
- **Purpose**: Documentation generation and maintenance
- **Features**: Creates self-describing codebase documentation
- **Status**: Shows docs updated, last run
- **Controls**: Start documentation generation

### 5. 🛠️ Custom Agent
- **Purpose**: Ad-hoc task execution
- **Features**: Spawns agents for specific custom tasks
- **Status**: Shows tasks completed, last spawn
- **Controls**: Spawn agent with custom prompt

## 📊 Metrics Explained

- **Avg Cycle Time**: Average time for autonomous improvement cycles
- **Success Rate**: Percentage of successful improvements vs attempted
- **Opportunities**: Total improvement opportunities discovered
- **Total Improvements**: Count of successful improvements made

## 🚨 Safety Features

- **Emergency Stop**: Immediately halts all agent operations
- **Safe Operation**: Agents validate changes before execution
- **Status Monitoring**: Real-time visibility into all agent states
- **Graceful Shutdown**: Clean termination of operations

## 🔧 Technical Details

- **Framework**: Rich terminal UI library for professional display
- **Architecture**: Async/await for responsive real-time updates
- **Integration**: Uses existing CLI commands as backend
- **Performance**: 4 FPS update rate for smooth experience
- **Compatibility**: Works on macOS, Linux (terminal required)

## 🎨 Customization

The enhanced monitor uses the Rich library for professional terminal UI. You can customize:

- Colors and styling in the layout functions
- Update refresh rate (currently 4 FPS)
- Panel sizes and arrangement
- Keyboard shortcuts mapping

## 🐛 Troubleshooting

**Rich library not found?**
```bash
poetry install  # Should install Rich automatically
```

**Keyboard input not working?**
- Ensure terminal supports interactive input
- Try running in full terminal (not VS Code integrated terminal)

**Performance issues?**
- Reduce refresh rate in `run_monitor()` function
- Check system resources during agent operations

---

**Ready to control your agents with style!** 🚀✨
