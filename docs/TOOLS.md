# 🛠️ Tool Reference

> **Complete Tool Catalog**: All available tools for agents with usage examples and cross-references.

**📚 Cross-References**: [Documentation Index](INDEX.md) | [Agent Development Guide](AGENT_DEVELOPMENT.md) | [MCP Integration](MCP.md) | [Interface Documentation](INTERFACES.md)

---

## 🎯 Tool Categories

### Memory & Context Management
- **[WriteMemory](#writememory)** - Store knowledge and context
- **[ReadMemoryContext](#readmemorycontext)** - Retrieve relevant context

### Planning & Quality Assurance  
- **[GenerateNextSteps](#generatenextsteps)** - Heuristic planning from context
- **[GenerateReleaseNotes](#generatereleasenotes)** - Auto-generate release documentation
- **[DoDCheck](#dodcheck)** - Definition-of-Done validation

### External Integration
- **[DiscoverMCPServers](#discovermcpservers)** - Find available MCP servers
- **[CallMCPTool](#callmcptool)** - Execute MCP server tools safely

### Architecture & Documentation
- **[CreateADR](#createadr)** - Generate architectural decision records
- **[IntentNormalizer](#intentnormalizer)** - Standardize intent tags

---

## 📝 Memory & Context Tools

### WriteMemory

**Purpose**: Store knowledge, context, and state for cross-agent sharing  
**Location**: [ai/tools/memory_tools.py](../ai/tools/memory_tools.py)  
**Related**: [Memory System Guide](../ai/memory/README.md)

```python path=null start=null
WriteMemory(
    content="Goal: Implement MCP browser integration",
    tags=["feature", "mcp", "browser"]
).run()
```

**Parameters**:
- `content` (str): Information to store
- `tags` (List[str]): Categorization tags for retrieval

**Usage Patterns**:
- **Goal Setting**: Store high-level objectives
- **Context Sharing**: Share state between agent handoffs  
- **Progress Tracking**: Record completed tasks and decisions

### ReadMemoryContext

**Purpose**: Retrieve relevant stored context for current task  
**Location**: [ai/tools/memory_tools.py](../ai/tools/memory_tools.py)  
**Related**: [Memory System Guide](../ai/memory/README.md)

```python path=null start=null
context = ReadMemoryContext(
    tags=["feature", "mcp"], 
    limit=10
).run()
```

**Parameters**:
- `tags` (List[str], optional): Filter by specific tags
- `limit` (int): Maximum number of entries to retrieve

**Usage Patterns**:
- **Task Context**: Understand current project state
- **Agent Handoffs**: Get context from previous agents
- **Decision History**: Review past architectural choices

---

## 📋 Planning & Quality Tools

### GenerateNextSteps

**Purpose**: Generate actionable next steps based on memory context  
**Location**: [ai/tools/next_steps.py](../ai/tools/next_steps.py)  
**Related**: [Agent Development Guide](AGENT_DEVELOPMENT.md#planning-quality)

```python path=null start=null
steps = GenerateNextSteps(
    limit=5,
    tags=["feature", "implementation"]
).run()
```

**Parameters**:
- `limit` (int): Maximum number of steps to generate
- `tags` (List[str], optional): Focus on specific tagged context

**Usage Patterns**:
- **Sprint Planning**: Break down large goals into tasks
- **Agent Coordination**: Plan handoffs between agents
- **Progress Tracking**: Generate next actions from current state

### GenerateReleaseNotes

**Purpose**: Auto-generate release notes from memory context  
**Location**: [ai/tools/release_notes.py](../ai/tools/release_notes.py)  
**Related**: [Quality Gates](QUALITY_GATES.md)

```python path=null start=null
notes = GenerateReleaseNotes(
    limit=20,
    tags=None  # All tags
).run()
```

**Parameters**:
- `limit` (int): Maximum context entries to consider
- `tags` (List[str], optional): Filter context by tags

**Output**: Markdown-formatted release notes with features, fixes, and improvements

### DoDCheck

**Purpose**: Run Definition-of-Done checks (tests, ADRs, quality gates)  
**Location**: [ai/tools/dod_checker.py](../ai/tools/dod_checker.py)  
**Related**: [Quality Gates](QUALITY_GATES.md), [Testing Guide](TESTING.md)

```python path=null start=null
report = DoDCheck(
    lookback_commits=10
).run()
```

**Parameters**:
- `lookback_commits` (int): Number of recent commits to analyze

**Checks Performed**:
- Tests changed when source changed
- Pytest execution status  
- ADR references in recent commits
- Code quality indicators

**Output**: Markdown report with pass/fail status and recommendations

---

## 🔌 External Integration Tools

### DiscoverMCPServers

**Purpose**: Find available Model Context Protocol servers  
**Location**: [ai/tools/mcp_client.py](../ai/tools/mcp_client.py)  
**Related**: [MCP Integration Guide](MCP.md)

```python path=null start=null
servers = DiscoverMCPServers().run()
# Returns list of server configurations with available tools
```

**Returns**: List of MCP server configurations including:
- Server names and descriptions
- Available tools and their schemas
- Connection status

**Common Servers**:
- **browser** - Web browsing and scraping
- **puppeteer** - Advanced browser automation  
- **research** - Information gathering tools
- **documentation** - Documentation generation
- **shell** - System command execution

### CallMCPTool

**Purpose**: Execute tools on MCP servers with mock/safe responses  
**Location**: [ai/tools/mcp_client.py](../ai/tools/mcp_client.py)  
**Related**: [MCP Integration Guide](MCP.md), [Security Guidelines](SECURITY.md)

```python path=null start=null
result = CallMCPTool(
    server_name="browser",
    tool_name="navigate",
    arguments={"url": "https://example.com"}
).run()
```

**Parameters**:
- `server_name` (str): Target MCP server
- `tool_name` (str): Tool to execute
- `arguments` (dict): Tool-specific parameters

**Safety Features**:
- Returns mock responses for development
- Validates tool availability before execution
- Logs all tool calls for debugging

---

## 📐 Architecture & Documentation Tools

### CreateADR

**Purpose**: Generate numbered Architectural Decision Records  
**Location**: [ai/tools/adr_logger.py](../ai/tools/adr_logger.py)  
**Related**: [ADR Guidelines](../.cursor/rules/ADR.md), [ADR Index](ADR_INDEX.md)

```python path=null start=null
adr_path = CreateADR(
    title="Adopt MCP for External Tool Integration",
    status="Proposed"
).run()
```

**Parameters**:
- `title` (str): Decision title
- `status` (str): Proposed | Accepted | Deprecated | Superseded

**Output**: Creates numbered ADR file (ADR-XXX.md) in `.cursor/rules/`

**Environment Variables**:
- `ADR_DIR` - Override default output directory

### IntentNormalizer

**Purpose**: Standardize and deduplicate intent tags  
**Location**: [ai/tools/intent.py](../ai/tools/intent.py)  
**Related**: [Agent Development Guide](AGENT_DEVELOPMENT.md#utility-normalization)

```python path=null start=null
normalized = IntentNormalizer(
    tags=["feat", "feature", "bug-fix", "documentation"]
).run()
# Returns: ["feature", "bug", "docs"]
```

**Normalization Rules**:
- `feat`/`feature` → `feature`
- `bug-fix`/`bugfix` → `bug` 
- `documentation`/`doc` → `docs`
- `refactor`/`refactoring` → `refactor`
- `adr`/`decision` → `adr`

**Features**:
- Deduplication of duplicate tags
- Consistent ordering (feature, bug, docs, refactor, adr)
- Preserves unknown tags as-is

---

## 🖥️ Interface Tools

### CLI Scripts

**Location**: [scripts/](../scripts/)  
**Related**: [Interface Documentation](INTERFACES.md), [WARP Guide](../WARP.md)

| Script | Purpose | Usage |
|--------|---------|--------|
| **deploy.sh** | Agent deployment management | `./scripts/deploy.sh create team-name` |
| **ask.sh** | Feature request interface | `./scripts/ask.sh "add web scraper"` |
| **monitor.sh** | Agent status monitoring | `./scripts/monitor.sh` |
| **mvp.sh** | MVP planning execution | `./scripts/mvp.sh` |
| **bootstrap.sh** | Environment setup | `bash scripts/bootstrap.sh` |

### Python Interfaces

**Agent Deployment**: [ai/interface/deploy_agents.py](../ai/interface/deploy_agents.py)
```bash
python -m ai.interface.deploy_agents create research-team
python -m ai.interface.deploy_agents deploy research-team "focus on docs"
```

**Feature Requests**: [ai/interface/ask_implement.py](../ai/interface/ask_implement.py)  
```bash
python -m ai.interface.ask_implement "implement MCP browser integration"
```

---

## 🔧 Tool Implementation Patterns

### Error Handling

All tools should implement consistent error handling:

```python path=null start=null
def run(self) -> str:
    """Execute tool with error handling."""
    try:
        # Tool implementation
        result = self._execute()
        return result
    except Exception as e:
        return f"Error in {self.__class__.__name__}: {str(e)}"
```

### Memory Integration  

Tools working with memory should follow these patterns:

```python path=null start=null
from ai.memory.store import get_memory_store

def run(self) -> str:
    store = get_memory_store()
    # Use store.write() or store.read() as needed
```

### Cross-References in Tool Output

Tool outputs should include relevant cross-references:

```python path=null start=null
def generate_output(self) -> str:
    return f"""
## Results
{self.results}

## Related Documentation
- [Tool Reference](docs/TOOLS.md#{self.tool_name.lower()})
- [Usage Guide](docs/GUIDE.md)
"""
```

---

## 🔗 Related Documentation

- **[Agent Development Guide](AGENT_DEVELOPMENT.md)** - Using tools in agent development
- **[MCP Integration Guide](MCP.md)** - External tool integration patterns  
- **[Memory System Guide](../ai/memory/README.md)** - Memory and context management
- **[Interface Documentation](INTERFACES.md)** - CLI and Python interfaces
- **[Quality Gates](QUALITY_GATES.md)** - DoD checks and validation requirements
- **[Security Guidelines](SECURITY.md)** - Safe tool usage and mock patterns

---

> 💡 **Agent Tip**: Always check tool availability with `DiscoverMCPServers()` before using external tools. Use memory tools for cross-agent coordination and context sharing. Reference this documentation when implementing new tools to maintain consistency.
