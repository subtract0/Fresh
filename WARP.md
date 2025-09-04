# ⚡ WARP Terminal Guide

> **Fresh AI Agent System** - Baseline v0 for autonomous development with persistent memory
> 
> **Status**: See [Feature Status Matrix](docs/FEATURE_STATUS.md) for actual implementation status  
> **Requirements**: Python 3.12+, Poetry  
> **Documentation Accuracy**: Verified by automated analysis

---

## 🎯 Quick Reference

### ✅ What Works Now (Fully Implemented)

#### Core CLI Commands
```bash
# Scan repository for issues (WORKS)
poetry run python -m ai.cli.fresh scan . --json

# Spawn an agent for a specific task (WORKS) 
poetry run python -m ai.cli.fresh spawn "Fix the bug in auth module"

# Run autonomous development loop (WORKS)
poetry run python -m ai.cli.fresh run --once
```

#### Shell Scripts (Ready to Use)
```bash
# Bootstrap environment (WORKS)
./scripts/bootstrap.sh                   # Install deps, setup .env

# Deploy agent configurations (WORKS)
./scripts/deploy.sh create research-team # Create config
./scripts/deploy.sh list                 # List configs

# Request features - creates feature branch (WORKS)
./scripts/ask.sh "add OAuth support"     

# Run tests - matches CI (WORKS)
bash scripts/run-tests.sh               # All tests
poetry run pytest tests/test_name.py    # Single test

# Telegram bot interface (WORKS - needs token)
./scripts/telegram.sh                   # Launch bot (set TELEGRAM_BOT_TOKEN first)

# GitHub MCP server (WORKS - needs token)
./scripts/mcp-github.sh                 # Launch server (uses gh auth token)

# Monitor status (WORKS)
./scripts/monitor.sh                    # Check system status

# MVP planning (WORKS)
./scripts/mvp.sh                        # Generate MVP plan
```

#### Memory System (All Working)
```python
# InMemoryMemoryStore - WORKS
from ai.memory.store import InMemoryMemoryStore
store = InMemoryMemoryStore()

# IntelligentMemoryStore - WORKS  
from ai.memory.intelligent_store import IntelligentMemoryStore
store = IntelligentMemoryStore()  # Auto-classification, search, analytics
```

#### Enhanced Agents (Working)
- **MotherAgent**: Spawns and manages child agents
- **EnhancedFather**: Strategic planning with memory
- **DocumentationAgent**: Documentation alignment checks

#### Testing & CI (Active)
- **28 test files** with 200+ tests
- **CI Pipeline**: Tests run on every push/PR
- **ADR Check**: PRs must reference ADR-XXX

---

### ⚠️ Partial Implementation (Needs Setup)

#### FirestoreMemoryStore
```bash
# Code exists but requires environment setup:
export FIREBASE_PROJECT_ID=your-project
export FIREBASE_CLIENT_EMAIL=your-email  
export FIREBASE_PRIVATE_KEY=your-key

# Falls back to InMemoryStore if not configured
```

---

### 🚧 Not Yet Implemented (Documentation References Only)

These commands appear in docs but DON'T WORK yet:
- `fresh::docs::check` - Planned for doc validation
- `fresh::deploy::status` - Planned for deployment status  
- `fresh::monitor::live` - Planned for Rich UI monitoring
- `fresh run --watch` - Continuous mode not implemented
- Agency Swarm full orchestration - Requires additional setup

---

## 📚 Documentation & Truth

### Verify What's Real
```bash
# Regenerate feature inventory (source of truth)
poetry run python scripts/inventory_codebase.py
poetry run python scripts/analyze_feature_status.py

# View actual implementation status
cat docs/FEATURE_STATUS.md
```

### Key Documentation
- **[Feature Status Matrix](docs/FEATURE_STATUS.md)** - AUTO-GENERATED truth matrix
- **[Memory System](docs/MEMORY_SYSTEM.md)** - Memory architecture guide
- **[Enhanced Agents](docs/ENHANCED_AGENTS.md)** - Agent capabilities
- **[API Reference](docs/API_REFERENCE.md)** - API documentation

---

## 🔧 Common Tasks (Verified Working)

### Initial Setup
```bash
# Clone and setup
git clone https://github.com/yourusername/Fresh.git
cd Fresh
./scripts/bootstrap.sh

# Verify installation
poetry run python -m ai.cli.fresh scan . --json

# Run tests
poetry run pytest -q
```

### Working Examples
```bash
# Create an ADR (WORKS)
poetry run python -c "from ai.tools.adr_logger import CreateADR; \
  print(CreateADR(title='My Decision', status='Proposed').run())"

# Test memory system (WORKS)
poetry run python scripts/demo-persistent-memory.py

# Test agent activity (WORKS)
poetry run python scripts/demo-agent-activity.py

# Check for TODOs and issues (WORKS)
poetry run python -m ai.cli.fresh scan .
```

### Environment Variables
```bash
# Core (required for basic operation)
export PYTHONPATH=$(pwd)

# Optional (for advanced features)
export OPENAI_API_KEY=sk-...           # For LLM agents
export TELEGRAM_BOT_TOKEN=...          # For Telegram bot
export GITHUB_TOKEN=$(gh auth token)   # For GitHub operations
export FIREBASE_PROJECT_ID=...         # For persistent memory
```

---

## 🐛 Troubleshooting

### Feature Not Working?
1. Check `docs/FEATURE_STATUS.md` - is it actually implemented?
2. Check environment requirements in the Requirements column
3. Run specific tests: `poetry run pytest tests/test_<feature>.py -v`
4. Check inventory: `cat docs/_generated/inventory.json`

### Update Documentation to Match Reality
```bash
# Regenerate truth matrix
poetry run python scripts/inventory_codebase.py
poetry run python scripts/analyze_feature_status.py
```

---

## 📋 No Broken Windows Policy

This project follows strict quality rules:
1. **Fix issues before adding features**
2. **Keep tests passing** (CI enforces this)
3. **Keep documentation accurate** (use FEATURE_STATUS.md)
4. **Clean up before moving on**

---

## 🛑 Known Limitations

- **No linter config**: Ruff/Black/Mypy not configured yet
- **CI uses dummy keys**: OPENAI_API_KEY=dummy in CI (some tests skipped)
- **Firestore needs credentials**: Falls back to in-memory without Firebase setup
- **Some scripts not executable**: run with `bash script.sh` if needed

---

*Last verified: Generated from automated codebase analysis*  
*Truth source: [docs/FEATURE_STATUS.md](docs/FEATURE_STATUS.md)*
