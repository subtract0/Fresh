# Fresh AI - Enhanced Agent System with Persistent Memory

🧠 **State-of-the-art autonomous AI agents** with persistent memory, continuous learning, and cross-session intelligence. Fresh AI enables agents to learn from experience, make better decisions based on historical context, and improve performance over time.

[![Tests](https://img.shields.io/badge/tests-32%2F32%20passing-brightgreen)](#testing)
[![Memory System](https://img.shields.io/badge/memory-intelligent%20%2B%20persistent-blue)](#memory-system)
[![Agents](https://img.shields.io/badge/agents-4%20enhanced-purple)](#enhanced-agents)
[![Documentation](https://img.shields.io/badge/docs-comprehensive-orange)](#documentation)

## 🎯 Mission ✅ ACCOMPLISHED

**IMPLEMENTED**: Persistent-memory and learning mother-agent system with specialized enhanced agents that learn from experience, maintain knowledge across sessions, and continuously improve through intelligent memory integration.

## 🚀 Quick Start

```bash
# 1. Install and setup
cd /path/to/Fresh
poetry install --no-root
export PYTHONPATH=$(pwd)

# 2. Test the memory system
PYTHONPATH=$(pwd) poetry run python scripts/demo-persistent-memory.py

# 3. Test enhanced agents
PYTHONPATH=$(pwd) poetry run python scripts/demo-agent-activity.py

# 4. Run the test suite
poetry run python -m pytest tests/test_intelligent_memory.py tests/test_firestore_memory.py
```

🎉 **Result**: Intelligent memory system with 4 enhanced agents ready for autonomous development!

## 📚 Documentation System

### 🎯 Core Guides
| Guide | Purpose | Audience |
|-------|---------|----------|
| **[Memory System](docs/MEMORY_SYSTEM.md)** | Complete memory architecture and usage | Developers, Agents |
| **[Enhanced Agents](docs/ENHANCED_AGENTS.md)** | Memory-driven agent capabilities | Agent Developers |
| **[API Reference](docs/API_REFERENCE.md)** | Comprehensive API documentation | Developers |
| **[Agent Development](docs/AGENT_DEVELOPMENT.md)** | Development best practices | AI Agents |
| **[Deployment Guide](docs/DEPLOYMENT.md)** | Operations and deployment | DevOps, SRE |

### 🏗️ Architecture
| Document | Focus | Cross-References |
|----------|-------|------------------|
| **[ADR-004: Persistent Memory](/.cursor/rules/ADR-004.md)** | Architecture decision (✅ IMPLEMENTED) | [Memory System](docs/MEMORY_SYSTEM.md), [Enhanced Agents](docs/ENHANCED_AGENTS.md) |
| **[Memory Store Implementations](docs/MEMORY_SYSTEM.md#memory-store-implementations)** | Storage layer architecture | [API Reference](docs/API_REFERENCE.md#memory-store-apis) |
| **[Agent Memory Integration](docs/ENHANCED_AGENTS.md#memory-integration)** | Agent-memory workflows | [Agent Development](docs/AGENT_DEVELOPMENT.md#memory-driven-development-practices) |

### 🛠️ Implementation
| Component | Documentation | Code |
|-----------|---------------|------|
| **Memory Stores** | [Memory System](docs/MEMORY_SYSTEM.md) | [`ai/memory/`](ai/memory/) |
| **Enhanced Agents** | [Enhanced Agents](docs/ENHANCED_AGENTS.md) | [`ai/agents/enhanced_agents.py`](ai/agents/enhanced_agents.py) |
| **Memory Tools** | [API Reference](docs/API_REFERENCE.md#memory-tool-apis) | [`ai/tools/`](ai/tools/) |
| **Testing** | [API Reference](docs/API_REFERENCE.md#usage-examples) | [`tests/`](tests/) |

## 🧠 Memory System

### Three-Tier Architecture

#### 1. **InMemoryMemoryStore** - Development
- Zero dependencies, fast access
- Perfect for testing and development
- Ephemeral storage (lost on restart)

#### 2. **IntelligentMemoryStore** - Enhanced Development
- Auto-classification of memory types
- Keyword extraction and importance scoring
- Semantic search and relationship detection
- Memory analytics and insights

#### 3. **FirestoreMemoryStore** - Production
- All intelligent features + persistent storage
- Cross-session memory with Firestore backend
- Local cache for performance
- Memory consolidation and cleanup
- Cross-session analytics

### Memory Classification

| Type | Examples | Auto-Detection |
|------|----------|----------------|
| **GOAL** | "Goal: Implement authentication" | ✅ Keywords: goal, objective, implement |
| **TASK** | "Task: Add unit tests" | ✅ Keywords: task, todo, add |
| **DECISION** | "Decision: Use JWT tokens" | ✅ Keywords: decision, choose, adr |
| **ERROR** | "Error: Database timeout" | ✅ Keywords: error, failed, bug |
| **KNOWLEDGE** | "Learned: Async improves performance" | ✅ Keywords: learned, discovered, insight |
| **PROGRESS** | "Progress: 80% complete" | ✅ Keywords: progress, complete, done |
| **CONTEXT** | "Using Python 3.12" | ✅ Environmental information |

**🔍 Details**: [Memory Classification](docs/MEMORY_SYSTEM.md#memory-classification)

---

## 🤖 Enhanced Agents

### Agent Capabilities

#### 🎯 EnhancedFather - Strategic Intelligence
- **Goal Evolution**: Tracks strategic objectives across sessions
- **Decision Learning**: Learns from past planning outcomes
- **Pattern Recognition**: Identifies successful strategic patterns
- **Context Continuity**: Maintains strategic context between sessions

#### 🏗️ EnhancedArchitect - Design Intelligence  
- **Design Patterns**: Builds repository of successful architectural decisions
- **ADR Outcomes**: Tracks long-term results of architectural choices
- **TDD Learning**: Remembers effective testing strategies
- **Complexity Analysis**: Learns from trade-offs and their impacts

#### 💻 EnhancedDeveloper - Implementation Learning
- **Solution Patterns**: Remembers successful implementation approaches
- **Bug Learning**: Learns from past bugs and their solutions
- **Refactoring Wisdom**: Tracks effective refactoring techniques
- **Code Quality**: Remembers what leads to maintainable code

#### 🔍 EnhancedQA - Quality Intelligence
- **Test Patterns**: Remembers effective testing strategies
- **Bug Pattern Recognition**: Learns common failure modes
- **Quality Metrics**: Tracks which quality measures work
- **Integration Wisdom**: Remembers failure-prone integration points

### Memory-Driven Development
```python
# Example: Enhanced agent workflow
from ai.agents.enhanced_agents import EnhancedDeveloper
from ai.tools.enhanced_memory_tools import PersistentMemorySearch, SmartWriteMemory

developer = EnhancedDeveloper()

# 1. Consult memory before starting
similar_work = PersistentMemorySearch(
    keywords=["jwt", "authentication", "implementation"]
).run()

# 2. Apply learned patterns
# ... implementation with memory insights ...

# 3. Store new learnings
SmartWriteMemory(
    content="Learned: JWT middleware pattern with refresh token rotation provides optimal security and maintainability",
    tags=["knowledge", "jwt", "security", "pattern"]
).run()
```

**📖 Deep Dive**: [Enhanced Agent Architecture](docs/ENHANCED_AGENTS.md)

---

## 🛠️ API Reference

### Memory Store APIs
```python
# Automatic store selection
from ai.memory.store import get_store
store = get_store()  # Firestore → Intelligent → InMemory

# Enhanced memory operations
from ai.memory.intelligent_store import IntelligentMemoryStore
store = IntelligentMemoryStore()
memory = store.write("Goal: Implement real-time communication")
# Returns: EnhancedMemoryItem with type=GOAL, importance=0.85, keywords=[...]
```

### Memory Tools
```python
# Smart memory storage with auto-classification
from ai.tools.enhanced_memory_tools import SmartWriteMemory
tool = SmartWriteMemory(content="Error: Database timeout", tags=["error"])
result = tool.run()  # Returns JSON with intelligence metadata

# Semantic keyword search
from ai.tools.enhanced_memory_tools import SemanticSearchMemory
search = SemanticSearchMemory(keywords=["database", "error"], limit=5)
results = search.run()  # Returns ranked, relevant memories
```

### Enhanced Agents
```python
# Create memory-driven agents
from ai.agents.enhanced_agents import create_enhanced_agents
agents = create_enhanced_agents()
# Returns: {'Father': EnhancedFather(), 'Architect': EnhancedArchitect(), ...}

# Gradual migration support
from ai.agents.enhanced_agents import get_agent
enhanced_father = get_agent('Father', enhanced=True)
standard_father = get_agent('Father', enhanced=False)
```

**📖 Deep Dive**: [API Reference Documentation](docs/API_REFERENCE.md)

---

## 🚀 Deployment

### Local Development
```bash
# Quick setup
export PYTHONPATH=$(pwd)
poetry install --no-root

# Test memory system
poetry run python scripts/demo-persistent-memory.py
```

### Production with Firestore
```bash
# Set up persistent memory
export FIREBASE_PROJECT_ID="your-project"
export FIREBASE_PRIVATE_KEY="your-key"
export FIREBASE_CLIENT_EMAIL="service@account.com"

# Deploy enhanced agents
PYTHONPATH=$(pwd) poetry run python -c "
from ai.agents.enhanced_agents import create_enhanced_agents
agents = create_enhanced_agents()
print(f'Deployed {len(agents)} enhanced agents')
"
```

**📖 Deep Dive**: [Deployment and Operations Guide](docs/DEPLOYMENT.md)

---

## 🧪 Testing

### Test Status
- ✅ **Intelligent Memory**: 16/16 tests passing
- ✅ **Firestore Memory**: 16/16 tests passing  
- ✅ **Full Test Suite**: 71 passed, 27 skipped
- ✅ **Demo Scripts**: Both persistent memory and agent activity demos working
- ✅ **Enhanced Agents**: All 4 agents tested and functional

### Running Tests
```bash
# Core memory tests
poetry run python -m pytest tests/test_intelligent_memory.py -v
poetry run python -m pytest tests/test_firestore_memory.py -v

# Full test suite
poetry run python -m pytest tests/ --tb=short

# Test enhanced agents
PYTHONPATH=$(pwd) poetry run python -c "
from ai.agents.enhanced_agents import create_enhanced_agents
agents = create_enhanced_agents()
print('✅ Enhanced agents working')
"
```

---

## 🧾 Documentation Alignment

Keep documentation continuously accurate and cross-referenced.

- Background service (full system): enabled by default via the system coordinator; runs periodic checks and stores failures/recoveries in memory
- Parallel agent (enhanced agency): DocumentationAgent runs in parallel from Father to perform on-demand checks and memory writes

Configuration
- DOCS_CHECK_ENABLED=true|false (default: true)
- DOCS_CHECK_INTERVAL_SEC=600 (default seconds)

Manual check
```bash
# Warp helper (after `source ./.warp`)
fresh::docs::check

# Or directly
python scripts/check_docs_alignment.py --strict
```

Status and metrics
```bash
python launch_agent_system.py --status
# Look for: docs_alignment_last_status, docs_alignment_last_run_age_sec, docs_alignment_interval_sec
```

---

## 📁 Project Structure
```
Fresh/
├── 📁 ai/
│   ├── 📁 memory/                    # Memory system implementation
│   │   ├── store.py                  # Base interfaces (includes InMemoryMemoryStore)
│   │   ├── intelligent_store.py      # Auto-classification and search
│   │   └── firestore_store.py        # Persistent Firestore storage
│   ├── 📁 agents/
│   │   ├── enhanced_agents.py        # 🆕 Enhanced agents with memory
│   │   ├── Father.py                 # Legacy strategic agent
│   │   ├── Architect.py              # Legacy design agent
│   │   ├── Developer.py              # Legacy implementation agent
│   │   └── QA.py                     # Legacy quality agent
│   └── 📁 tools/
│       ├── memory_tools.py           # Basic memory tools
│       ├── enhanced_memory_tools.py  # 🆕 Intelligent memory tools
│       └── persistent_memory_tools.py # 🆕 Cross-session memory tools
├── 📁 docs/                          # 🆕 Comprehensive documentation
│   ├── MEMORY_SYSTEM.md              # Memory architecture guide
│   ├── ENHANCED_AGENTS.md            # Enhanced agent capabilities
│   ├── API_REFERENCE.md              # Complete API documentation
│   ├── AGENT_DEVELOPMENT.md          # Development best practices
│   └── DEPLOYMENT.md                 # Operations and deployment
├── 📁 tests/
│   ├── test_intelligent_memory.py    # 🆕 Intelligent memory tests (16/16)
│   ├── test_firestore_memory.py      # 🆕 Firestore memory tests (16/16)
│   └── ...                           # Other test files
├── 📁 scripts/
│   ├── demo-persistent-memory.py     # 🆕 Memory system demonstration
│   └── demo-agent-activity.py        # 🆕 Agent activity simulation
└── 📁 .cursor/rules/
    └── ADR-004.md                    # 🆕 Persistent memory ADR (✅ IMPLEMENTED)
```
```

---

## 📊 Performance & Analytics

### System Metrics (Latest Demo)
- **Memory Operations**: 21 intelligent classifications completed
- **Search Performance**: Semantic search across multiple memory types
- **Learning Analytics**: Error-to-knowledge conversion ratio: 3:3 (100% learning rate)
- **Cross-Session Capability**: Ready for Firestore-backed persistence
- **Agent Performance**: All 4 enhanced agents operational with 8, 4, 6, and 6 memory tools respectively

### Memory Analytics Features
- **Cross-Session Insights**: Memory pattern analysis across deployments
- **Learning Velocity**: Track knowledge accumulation over time
- **Pattern Recognition**: Identify successful vs. failed approaches
- **Memory Consolidation**: Automatic cleanup with configurable rules
- **Agent Performance**: Track memory-driven decision quality

**🔍 Details**: [Memory Analytics](docs/API_REFERENCE.md#crosssessionanalytics)

---

## 🔧 Legacy Commands

### Development Commands
```bash
# Bootstrap development environment
bash scripts/bootstrap.sh

# Run comprehensive tests
bash scripts/run-tests.sh

# Create architecture decision records
poetry run python -c "from ai.tools.adr_logger import CreateADR; print(CreateADR(title='Decision title', status='Proposed').run())"

# Adaptive agent monitoring
PYTHONPATH=$(pwd) poetry run python scripts/watch-agents-adaptive.py

# TDD sandbox demo
poetry run python - <<'PY'
import tempfile, pathlib
from ai.loop.devcycle import run_devcycle_slugify_sandbox
base = pathlib.Path(tempfile.mkdtemp())
print(run_devcycle_slugify_sandbox(base))
PY
```

### Architecture Implementation
- **Agents**: [`ai/agents/`](ai/agents/) - Both enhanced and legacy implementations
- **Agency Swarm**: [`ai/agency.py`](ai/agency.py) - Agent orchestration and flows
- **TDD Cycle**: [`ai/loop/devcycle.py`](ai/loop/devcycle.py) - RED→GREEN→REFACTOR implementation
- **Quality Gates**: CI enforcement of TDD + ADR discipline

---

## 🆕 What's New

### ✅ Recently Implemented
- **Persistent Memory System**: Complete implementation with Firestore backend
- **Enhanced Agents**: 4 memory-driven agents with continuous learning
- **Intelligent Classification**: Automatic memory type detection and importance scoring
- **Cross-Session Analytics**: Memory pattern analysis and learning insights
- **Comprehensive Testing**: 32 tests covering all memory functionality
- **State-of-the-Art Documentation**: Interconnected, comprehensive guides

### 🔮 Coming Next
- **Advanced Learning Features**: Enhanced pattern recognition and knowledge synthesis
- **Agent Workflow Integration**: Production-ready agent orchestration
- **Memory Optimization**: Advanced consolidation and performance tuning
- **Multi-Agent Collaboration**: Enhanced cross-agent memory sharing

---

## 🏃‍♂️ Getting Started Paths

### 👩‍💻 For Developers
1. **[Quick Start](#quick-start)** - Get running in 5 minutes
2. **[API Reference](docs/API_REFERENCE.md)** - Integrate memory into your code
3. **[Agent Development Guide](docs/AGENT_DEVELOPMENT.md)** - Build memory-driven workflows

### 🤖 For AI Agents
1. **[Agent Development Guide](docs/AGENT_DEVELOPMENT.md)** - Learn the development patterns
2. **[Enhanced Agents Guide](docs/ENHANCED_AGENTS.md)** - Understand memory-driven capabilities
3. **[Memory System Guide](docs/MEMORY_SYSTEM.md)** - Master the memory architecture

### 🚀 For DevOps/SRE
1. **[Deployment Guide](docs/DEPLOYMENT.md)** - Production deployment patterns
2. **[API Reference](docs/API_REFERENCE.md#error-handling)** - Error handling and monitoring
3. **[Memory System Guide](docs/MEMORY_SYSTEM.md#memory-store-implementations)** - Storage configuration

### 🏗️ For Architects
1. **[ADR-004: Persistent Memory](/.cursor/rules/ADR-004.md)** - Architecture decisions
2. **[Memory System Architecture](docs/MEMORY_SYSTEM.md#architecture-overview)** - System design
3. **[Enhanced Agent Architecture](docs/ENHANCED_AGENTS.md#architecture-overview)** - Agent design patterns

---

## 📖 Complete Documentation Index

### 🎯 Core Documentation
- **[Memory System Architecture](docs/MEMORY_SYSTEM.md)** - Complete memory system overview and usage
- **[Enhanced Agent Architecture](docs/ENHANCED_AGENTS.md)** - Memory-driven agent capabilities
- **[API Reference](docs/API_REFERENCE.md)** - Comprehensive API documentation
- **[Agent Development Guide](docs/AGENT_DEVELOPMENT.md)** - Development best practices
- **[Deployment and Operations](docs/DEPLOYMENT.md)** - Production deployment guide

### 🏗️ Architecture Decisions
- **[ADR-004: Persistent Agent Memory](/.cursor/rules/ADR-004.md)** - ✅ IMPLEMENTED

### 🧪 Testing and Examples
- **[Intelligent Memory Tests](tests/test_intelligent_memory.py)** - 16 comprehensive tests
- **[Firestore Memory Tests](tests/test_firestore_memory.py)** - 16 persistent memory tests
- **[Persistent Memory Demo](scripts/demo-persistent-memory.py)** - Complete system demonstration
- **[Agent Activity Demo](scripts/demo-agent-activity.py)** - Enhanced agent simulation
- **Issue → PR (safe intake)**: Run the GitHub Action “Issue to PR (Autonomous Intake)” via workflow_dispatch or label an issue with “autonomous”. It creates a docs-only plan PR safely.

### 💾 Implementation Files
- **[Memory Store Factory](ai/memory/store.py)** - Store selection and interfaces
- **[Intelligent Memory Store](ai/memory/intelligent_store.py)** - Auto-classification and search
- **[Firestore Memory Store](ai/memory/firestore_store.py)** - Persistent storage implementation
- **[Enhanced Agents](ai/agents/enhanced_agents.py)** - Memory-driven agent implementations
- **[Enhanced Memory Tools](ai/tools/enhanced_memory_tools.py)** - Intelligent memory tools
- **[Persistent Memory Tools](ai/tools/persistent_memory_tools.py)** - Cross-session memory tools

---

*Fresh AI represents the future of autonomous agents: memory-driven, continuously learning, and intelligently adaptive. The comprehensive documentation system ensures that both humans and AI agents can understand, develop, and maintain this sophisticated system.*

**🚀 Ready to build the future of AI agents? Start with the [Agent Development Guide](docs/AGENT_DEVELOPMENT.md)!**

