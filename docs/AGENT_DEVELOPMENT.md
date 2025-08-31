# 🤖 Agent Development Guide

> **For AI Agents**: This guide teaches you how to understand, develop, and maintain the Fresh agent ecosystem. Follow these standards to ensure consistency and quality.

**📚 Cross-References**: [Documentation Index](INDEX.md) | [Tool Reference](TOOLS.md) | [Agency Configuration](AGENCY_CONFIG.md) | [Memory System](../ai/memory/README.md)

---

## 🎯 Agent Development Overview

Fresh uses a **swarm-based architecture** where specialized agents collaborate through defined flows and shared memory. Each agent has:

- **Role**: Specialized function (planning, development, testing, etc.)
- **Tools**: Available capabilities (memory, MCP, ADR creation, etc.)
- **Instructions**: Behavior guidelines and responsibilities
- **Memory Context**: Shared persistent knowledge

### Agent Lifecycle
1. **Configuration** → [Deployment Guide](DEPLOYMENT.md#agent-configuration)
2. **Deployment** → [Interface Documentation](INTERFACES.md#deployment-interface)
3. **Execution** → [Memory System](../ai/memory/README.md#agent-memory-patterns)
4. **Monitoring** → [Monitoring Guide](MONITORING.md#agent-status)

---

## 🏗️ Agent Architecture

### Core Agents ([Agency Config](AGENCY_CONFIG.md))

| Agent | Role | Key Tools | Links |
|-------|------|-----------|--------|
| **Father** | Strategic Planning & Delegation | Memory, Planning, DoD | [Father.py](../ai/agents/Father.py) |
| **Architect** | TDD & ADR Enforcement | ADR Creation, Memory | [Architect.py](../ai/agents/Architect.py) |
| **Developer** | Implementation | MCP Client, Memory | [Developer.py](../ai/agents/Developer.py) |
| **QA** | Testing & Quality | MCP Client, Memory | [QA.py](../ai/agents/QA.py) |
| **Reviewer** | Code Review & Security | Memory, Context | [Reviewer.py](../ai/agents/Reviewer.py) |

### Agent Flow Patterns
```
Father (Strategic) 
  ↓
Architect (TDD Enforcement)
  ↓  
Developer (Implementation)
  ↓
QA (Testing & Validation)
  ↓
Reviewer (Security & Quality)
  ↓
[Back to Father for coordination]
```

**Implementation**: See [ai/agency.py](../ai/agency.py) for current wiring

---

## 🛠️ Available Tools

> **Complete Reference**: [Tool Documentation](TOOLS.md)

### Memory & Context
- **WriteMemory** / **ReadMemoryContext** - Persistent knowledge sharing
- **Memory Store Patterns** - [Memory System Guide](../ai/memory/README.md)

### Planning & Quality
- **GenerateNextSteps** - Heuristic planning based on context
- **GenerateReleaseNotes** - Auto-generate release documentation
- **DoDCheck** - Definition-of-Done validation with CI gates

### External Integration
- **DiscoverMCPServers** / **CallMCPTool** - [MCP Integration Guide](MCP.md)
- **CreateADR** - Architecture decision documentation

### Utility & Normalization
- **IntentNormalizer** - Tag standardization and deduplication
- **Test Runner Tools** - Pytest integration and validation

---

## 🎨 Creating New Agents

### 1. Agent Class Structure

```python path=null start=null
from agency_swarm import Agent
from ai.tools.memory_tools import WriteMemory, ReadMemoryContext

class YourAgent(Agent):
    def __init__(self):
        super().__init__(
            name="YourAgent",
            description="Brief role description",
            instructions="./path/to/instructions.md",  # or inline string
            tools=[WriteMemory, ReadMemoryContext, OtherTools],
            temperature=0.2,
        )
```

### 2. Instructions Template

Create detailed instructions in markdown:

```markdown path=null start=null
# YourAgent Instructions

## Role & Responsibilities
- Primary function and scope
- Key deliverables and outcomes

## Available Tools
- Tool descriptions and when to use them
- Cross-references to [Tool Documentation](TOOLS.md)

## Workflow Patterns
- How to interact with other agents
- Memory usage patterns from [Memory Guide](../ai/memory/README.md)

## Quality Standards
- Testing requirements
- ADR documentation needs per [ADR Guidelines](../.cursor/rules/ADR.md)
```

### 3. Update Agency Configuration

Add your agent to the swarm ([Agency Configuration](AGENCY_CONFIG.md)):

```python path=null start=null
# In ai/agency.py
agency_chart = [
    YourAgent,  # Add your agent
    [Father, YourAgent],  # Define flows
    [YourAgent, OtherAgent],
    # ... rest of flows
]
```

Or use the deployment interface ([Deployment Guide](DEPLOYMENT.md)):

```bash
./scripts/deploy.sh create your-swarm
./scripts/deploy.sh edit your-swarm  # Add your agent to YAML
```

---

## 📝 Documentation Standards

### Cross-Reference Requirements

**Every documentation file MUST:**

1. **Link to Documentation Index**: Include `[Documentation Index](INDEX.md)` in header
2. **Bidirectional Links**: Link to related docs AND be linked back from them
3. **Consistent Anchors**: Use `#kebab-case-headers` for navigation
4. **Update Cross-References**: When adding functionality, update all referencing docs

### Documentation File Template

```markdown path=null start=null
# 📄 Your Document Title

> **Brief Description**: One-line summary of document purpose

**📚 Cross-References**: [Documentation Index](INDEX.md) | [Related Doc 1](doc1.md) | [Related Doc 2](doc2.md)

---

## 🎯 Overview
[Content with cross-references to related docs]

## 🔗 Related Documentation
- [Specific Doc](path.md#specific-section) - Why this link is relevant
- [Implementation Guide](guide.md) - How this relates to implementation

---

> 💡 **Agent Tip**: [Specific guidance for agents using this documentation]
```

### Inline Code Documentation

**Python Docstring Standard**:

```python path=null start=null
def your_function(param: str) -> str:
    """Brief description of function purpose.
    
    Cross-references:
    - Related functionality: See tool_name in [Tool Reference](docs/TOOLS.md#tool-name)
    - Implementation pattern: [Development Patterns](docs/PATTERNS.md#pattern-name)
    
    Args:
        param: Description with type info
        
    Returns:
        Description of return value
        
    Related:
        - [Memory System](ai/memory/README.md) for persistence patterns
        - [Agent Architecture](docs/ARCHITECTURE.md) for context
    """
```

---

## 🔍 Reading Documentation as an Agent

### Navigation Strategy

1. **Start Here**: Always begin with [Documentation Index](INDEX.md)
2. **Follow Flows**: Use cross-references to understand relationships
3. **Check Implementation**: Link documentation to actual code files
4. **Validate Understanding**: Cross-check with [ADR decisions](docs/ADR_INDEX.md)

### Documentation Discovery Commands

```bash
# List all documentation
find docs/ -name "*.md" | sort

# Search for specific topics
grep -r "your topic" docs/ --include="*.md"

# Check cross-references to a specific doc
grep -r "filename.md" docs/ --include="*.md"
```

### Understanding Agent Context

**Before starting any task**:

1. Read [current agent configuration](DEPLOYMENT.md#current-deployment)
2. Check [memory context](../ai/memory/README.md#reading-context)
3. Review [available tools](TOOLS.md) for your role
4. Understand [quality requirements](QUALITY_GATES.md)

---

## 🎨 Maintaining Documentation Quality

### When Adding New Features

1. **Update Cross-References**: Add links to/from related docs
2. **Extend Tool Documentation**: Update [Tool Reference](TOOLS.md)
3. **Add Examples**: Include usage examples with cross-references
4. **Update Index**: Add to [Documentation Index](INDEX.md)

### When Modifying Existing Features

1. **Find All References**: Use `grep -r "feature_name" docs/`
2. **Update All Mentions**: Ensure consistency across all docs
3. **Validate Links**: Check that all cross-references remain valid
4. **Update Examples**: Refresh code examples and commands

### Documentation Validation Checklist

- [ ] All cross-references work (no broken links)
- [ ] Bidirectional linking maintained  
- [ ] Code examples tested and current
- [ ] Consistent formatting and style
- [ ] Added to [Documentation Index](INDEX.md)
- [ ] Related ADRs updated if architectural

---

## 🔗 Related Documentation

- **[Tool Reference](TOOLS.md)** - Complete catalog of available agent tools
- **[Agency Configuration](AGENCY_CONFIG.md)** - Swarm topology and flow management
- **[Deployment Guide](DEPLOYMENT.md)** - Agent deployment and configuration
- **[Memory System](../ai/memory/README.md)** - Persistent context and knowledge sharing
- **[Interface Documentation](INTERFACES.md)** - CLI and Python interfaces
- **[Quality Gates](QUALITY_GATES.md)** - DoD checks and validation requirements

---

> 💡 **Agent Tip**: Always start with the [Documentation Index](INDEX.md) when learning about Fresh. Follow cross-references to build comprehensive understanding before implementing changes. Maintain the documentation web when adding new functionality.
