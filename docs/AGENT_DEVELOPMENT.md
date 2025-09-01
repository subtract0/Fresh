# 🤖 Agent Development Guide

> **For AI Agents**: This guide teaches you how to understand, develop, and maintain the Fresh agent ecosystem. Follow these standards to ensure consistency and quality.

**📚 Cross-References**: [Documentation Index](INDEX.md) | [API Reference](API_REFERENCE.md) | [Enhanced Agents](ENHANCED_AGENTS.md) | [Memory System](MEMORY_SYSTEM.md) | [Deployment Guide](DEPLOYMENT.md)

---

## 🎯 Agent Development Overview

Fresh uses a **memory-driven agent architecture** where enhanced agents learn from experience and collaborate through persistent memory. The system now offers two agent types:

### Standard Agents (Legacy)
- **Role**: Specialized function without persistent memory
- **Tools**: Basic capabilities (memory, MCP, ADR creation, etc.)
- **Instructions**: Static behavior guidelines
- **Memory Context**: Session-only memory

### Enhanced Agents (Recommended) 
- **Role**: Memory-driven specialization with continuous learning
- **Tools**: Enhanced memory capabilities + standard tools
- **Intelligence**: Auto-classification, pattern recognition, cross-session learning
- **Memory Context**: Persistent knowledge with Firestore backend

### Agent Lifecycle
1. **Configuration** → [Enhanced Agents Guide](ENHANCED_AGENTS.md#agent-specifications)
2. **Memory Setup** → [Memory System Setup](MEMORY_SYSTEM.md#memory-store-implementations)
3. **Deployment** → [Deployment Guide](DEPLOYMENT.md#enhanced-agent-deployment)
4. **Learning** → [Enhanced Agent Workflows](ENHANCED_AGENTS.md#learning-workflows)
5. **Monitoring** → [Memory Analytics](API_REFERENCE.md#crosssessionanalytics)

---

## 🏗️ Agent Architecture

### Enhanced Agents (Recommended)

| Agent | Role | Memory Strategy | Key Tools | Links |
|-------|------|----------------|-----------|--------|
| **EnhancedFather** | Strategic Planning with Cross-Session Goals | Goal evolution, decision learning, pattern recognition | SmartWriteMemory, PersistentMemorySearch, CrossSessionAnalytics | [Enhanced Agents](ENHANCED_AGENTS.md#enhancedfather---strategic-planner) |
| **EnhancedArchitect** | Design Intelligence with ADR Outcomes | Design patterns, ADR tracking, TDD learning | SmartWriteMemory, GetMemoryByType, PersistentMemorySearch | [Enhanced Agents](ENHANCED_AGENTS.md#enhancedarchitect---design-intelligence) |
| **EnhancedDeveloper** | Implementation Learning with Bug Prevention | Solution patterns, bug learning, refactoring wisdom | SmartWriteMemory, SemanticSearchMemory, GetRelatedMemories | [Enhanced Agents](ENHANCED_AGENTS.md#enhanceddeveloper---implementation-learning) |
| **EnhancedQA** | Quality Intelligence with Failure Pattern Recognition | Test patterns, bug patterns, quality metrics | SmartWriteMemory, SemanticSearchMemory, GetMemoryByType | [Enhanced Agents](ENHANCED_AGENTS.md#enhancedqa---quality-intelligence) |

### Legacy Agents (Standard)

| Agent | Role | Key Tools | Links |
|-------|------|-----------|--------|
| **Father** | Strategic Planning | Memory, Planning, DoD | [Father.py](../ai/agents/Father.py) |
| **Architect** | TDD & ADR Enforcement | ADR Creation, Memory | [Architect.py](../ai/agents/Architect.py) |
| **Developer** | Implementation | MCP Client, Memory | [Developer.py](../ai/agents/Developer.py) |
| **QA** | Testing & Quality | MCP Client, Memory | [QA.py](../ai/agents/QA.py) |

### Enhanced Agent Flow Patterns
```
EnhancedFather (Strategic + Memory) 
  ↓ (with memory context sharing)
EnhancedArchitect (TDD + Design Patterns)
  ↓ (with implementation pattern sharing)
EnhancedDeveloper (Implementation + Bug Learning)
  ↓ (with test pattern sharing)
EnhancedQA (Testing + Failure Patterns)
  ↓
[Back to EnhancedFather with consolidated learnings]
```

**Memory-Driven Flow**: Each handoff includes relevant memory context from past similar work
**Implementation**: See [enhanced_agents.py](../ai/agents/enhanced_agents.py) and [Memory Integration](ENHANCED_AGENTS.md#memory-integration)

---

## 🛠️ Available Tools

> **Complete Reference**: [API Reference](API_REFERENCE.md)

### Enhanced Memory Tools
- **SmartWriteMemory** - Auto-classifying memory storage with intelligence metadata
- **SemanticSearchMemory** - Keyword-based intelligent search with relevance ranking
- **GetMemoryByType** - Type-filtered memory retrieval (goals, tasks, errors, etc.)
- **GetRelatedMemories** - Relationship-based memory exploration
- **PersistentMemorySearch** - Cross-session memory search with advanced filtering
- **CrossSessionAnalytics** - Memory pattern analysis across sessions
- **MemoryLearningPatterns** - Learning evolution and pattern analysis
- **MemoryConsolidation** - Memory cleanup and optimization

### Basic Memory Tools (Legacy)
- **WriteMemory** / **ReadMemoryContext** - Basic persistent knowledge sharing
- **Memory Store Patterns** - [Memory System Guide](MEMORY_SYSTEM.md)

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

## 🎨 Creating Enhanced Agents

### 1. Enhanced Agent Class Structure

```python path=null start=null
from ai.agents.enhanced_agents import Agent  # Enhanced base with fallback
from ai.tools.enhanced_memory_tools import SmartWriteMemory, SemanticSearchMemory
from ai.tools.persistent_memory_tools import PersistentMemorySearch, CrossSessionAnalytics

class YourEnhancedAgent(Agent):
    def __init__(self):
        super().__init__(
            name="YourAgent",
            description="Your agent with persistent memory and learning capabilities",
            instructions=(
                "You are YourAgent with enhanced memory capabilities:\n"
                "\n"
                "MEMORY STRATEGY:\n"
                "- Use SmartWriteMemory for insights, decisions, and learnings\n"
                "- Use PersistentMemorySearch to learn from past experiences\n"
                "- Use CrossSessionAnalytics to understand patterns\n"
                "\n"
                "LEARNING APPROACH:\n"
                "- Always check past similar work before starting\n"
                "- Apply learned patterns and avoid known issues\n"
                "- Store insights and learnings for future reference\n"
            ),
            tools=[
                SmartWriteMemory,
                PersistentMemorySearch,
                SemanticSearchMemory,
                CrossSessionAnalytics,
                # ... other tools
            ],
            temperature=0.2,
        )
```

### 2. Legacy Agent Class Structure (Standard)

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
