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

# Spawn agent with Firebase persistent memory (WORKS) 🔥
poetry run python -m ai.cli.fresh --use-firestore spawn "your task" --output code

# Run autonomous development loop (WORKS)
poetry run python -m ai.cli.fresh run --once

# Orchestrate complex multi-agent research (WORKS)
poetry run python -m ai.cli.fresh orchestrate "analyze market trends for AI tools"

# Monitor agents with interactive dashboard (WORKS)
poetry run python -m ai.cli.fresh monitor --enhanced

# Launch web-based agent control dashboard (WORKS) 🆕
poetry run python -m ai.cli.fresh monitor --web
./launch_dashboard.sh  # Alternative launcher

# Autonomous loop control (WORKS)
poetry run python -m ai.cli.fresh autonomous-status
poetry run python -m ai.cli.fresh autonomous-cycle
poetry run python -m ai.cli.fresh autonomous-start
poetry run python -m ai.cli.fresh autonomous-stop
poetry run python -m ai.cli.fresh autonomous-emergency-stop
poetry run python -m ai.cli.fresh autonomous-clear-emergency

# Feature management and self-documenting loop (WORKS)
poetry run python -m ai.cli.fresh feature-inventory
poetry run python -m ai.cli.fresh feature-validate
poetry run python -m ai.cli.fresh feature-hook-missing
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

# FirestoreMemoryStore - WORKS (with credentials) 🔥
from ai.memory.firestore_store import FirestoreMemoryStore
store = FirestoreMemoryStore()  # Persistent cross-session memory
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

*No items currently in this section - see Firebase setup guide in docs/FIREBASE_INTEGRATION.md*

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
- **[Firebase Integration](docs/FIREBASE_INTEGRATION.md)** - Persistent memory setup guide 🔥
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

# Firebase (for persistent memory) - see docs/FIREBASE_INTEGRATION.md
export FIREBASE_PROJECT_ID=...         # Firebase project ID
export FIREBASE_CLIENT_EMAIL=...       # Service account email  
export FIREBASE_PRIVATE_KEY=...        # Service account private key
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

---

# 🤖 AI Agent Rules - The Agent's Bible

> **For All AI Agents Working on Fresh AI System**  
> **Precedence**: Rules listed in order of precedence (earlier = higher priority)  
> **Source**: Consolidated from 27 original rules, eliminating 18 duplicates  
> **Coverage**: All unique requirements preserved  
> **Status**: MANDATORY - These rules must guide all agent interactions

## 1. 📚 Project Documentation & Truth Source *(Highest Priority)*

**1.1** Use this `WARP.md` as the authoritative project guide for Fresh AI Agent System
- Reference: `/Users/am/Code/Fresh/WARP.md` (this file)
- Contains verified features, implementation status, and working examples
- See `docs/FEATURE_STATUS.md` for actual implementation truth matrix

**1.2** Before integration work, always check the most recent reference to ensure everything is state-of-the-art
- Must be documented as an architectural decision
- Include MCP reference: `688cf28d-e69c-4624-b7cb-0725f36f9518` when applicable
- *Original: aEaYmc0Wa0la6ORpSe0yD8, rDFn3SorYOYZDb77Bk0Nfv*

## 2. 🚧 Development Workflow & Quality Standards

**2.1** No Broken Windows Policy *(CRITICAL)*
- Always prioritize urgent/critical tasks first ("as long as this house is on fire, we won't go fishing")
- Fix issues before adding new features - never ship unfinished code
- Keep codebase clean, simple, tidy, well-tested, and well-documented
- *Original: 4XkBfuiZeaaxuUdUSIuI9C, B1GTGWAZ9NBjgwCHXyhb02*

**2.2** Git & Branch Management
- Always use a branch when building features
- Commit and push changes to GitHub safely following professional best practices
- *Original: GkRy7VAnM5HsW9C0JZdqPI (7 duplicates consolidated)*

**2.3** End-to-End Task Completion
- Take tasks end-to-end without interruption until all is done:
  - All broken windows fixed
  - All tests running
  - All changes committed and pushed to GitHub
- *Original: I5FebVXCYbUMudUOrGTgom*

**2.4** Test-First Development & Documentation
- AI agents should always start by creating tests before building features
- Document all key architectural decisions in `.cursor/rules/ADR.md`
- *Original: SLqHxGNVsR9lBWtddMuFVs*

**2.5** Test Requirements
- Tests must be necessary for the system to work
- Each test designed to always pass when condition is met, never pass when not met
- The condition tested must be necessary for program to function correctly
- *Original: D5IkgGIOXrnIx2btm2IoXQ (4 duplicates consolidated)*

## 3. 🛡️ Security & Safety Practices

**3.1** Environment & Secrets Management
- Keep .env files safe and local
- Never commit actual sensitive information to version control
- Follow best security practices for all integrations
- *Original: r7hQsRtnuHnuA6Nt5JWZAc*

**3.2** Database Safety
- Agents should never connect to production databases
- Must always use a staging environment during development
- Ensures safety and prevents unintended data changes
- *Original: vJvfCo2HFG5hIbFDbeiu8r*

## 4. 🎯 Mission & Architecture Guidance

**4.1** Core Mission
- Create a persistent-memory and learning mother-agent that spawns agents
- Expected agent arguments: name, instructions, model, output_type
- *Original: JXWXHObstS3LSFlAlppgCH (3 duplicates consolidated)*

**4.2** Self-Documenting System Loop
- Install self-documenting loop in core codebase ensuring:
  - Always implementing what is built
  - Maintaining feature documentation listing all features
  - Hooking up any features not yet integrated
  - Validating each feature meets necessity and uniqueness criteria
  - Ensuring all features are tested once and only once
- Avoids codebase bloat and redundant tests
- *Original: 810PrY6gGHKOCAY6TzRMcS (2 duplicates consolidated)*

## 5. 📢 Communication & Workflow Preferences

**5.1** Structured Global Workflow
- Follow summarize-plan-clarify-confirm workflow before code/destructive changes
- Search-first approach for debugging
- Concise English communication with copy-pastable deliverables
- Short, practical, bullet-pointed output with one sharp follow-up question only when essential
- *Original: uWO9aFcmI9KPxQDxFLau7S*

**5.2** Notification Management
- Reduce/solve excessive GitHub notification emails autonomously
- Contributes to 'broken windows' problem and must be addressed
- Solution should prevent notification overload
- *Original: s01GqEvqdOoCeZXzoX6UUH*

---

## 🎯 Agent Execution Protocol

### Before Every Task
1. **Read this WARP.md file** - Understand current project state
2. **Check `docs/FEATURE_STATUS.md`** - Verify what's actually implemented
3. **Review `.agent-instructions.md`** - Follow development protocols
4. **Apply No Broken Windows** - Fix urgent issues first

### During Task Execution
1. **Create tests first** - TDD approach required
2. **Use feature branches** - Professional Git workflow
3. **Document decisions** - Update ADRs as needed
4. **Follow summarize-plan-clarify-confirm** - Structured approach

### After Task Completion
1. **Verify all tests pass** - No broken windows
2. **Update documentation** - Keep docs aligned with code
3. **Commit and push professionally** - Complete the cycle
4. **Store insights in memory** - Learn for future tasks

---

## 📋 Rule Precedence & Auditability

**Duplicates Eliminated (18 rules)**:
- No Broken Windows: U2dqezKfogNUufjKalYp6k, ZAZm8fdJxYZMbM2BSLybb3, djEQZicOOMEVHBVCvotbGJ
- Git Practices: PEsDplSiDuXYpzEA6qAKjz, ka8M869ySub8uH7TLMWM6I, lwgkkCifMIebRQdGGUzJTb, o5fvdwyOC4sQR8VIwneHxm, sHKjqC5SZSw6NIHKTGTZBT, thmI1mt9PELi5OML1m6tvo
- Mission Statement: SJeJGdMF6y9AoCkGfCJMSs, iwcuudAXfhp2DleHlaHwP5
- Test Requirements: ZTGXECngBm5OQ9zqfYhk5z, juAS8J7azW6mlVoywakLrn, tsiNoKx78yv5Inxv2QL06p
- Self-Documenting: K76Q5BrxNsN6VtgFkM65to
- State-of-Art: rDFn3SorYOYZDb77Bk0Nfv

**Unique Rules Preserved (9 rules)**:
- All functional requirements maintained
- All unique constraints preserved
- Precedence order respected

---

*🤖 Agent Rules Generated: 2025-01-04 | Consolidation: 27 rules → 12 statements | Zero requirements lost*  
*These rules are MANDATORY for all AI agents working on the Fresh AI system*
