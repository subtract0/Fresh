# Agency Configuration

This guide explains how the enhanced agency is constructed and configured.

Key entry points:
- ai/enhanced_agency.py — build_enhanced_agency(), initialize_intelligent_memory()
- ai/agency.py — legacy/basic agency wiring (if present)

Examples:
- Lightweight: Father → Architect → Developer (build_lightweight_enhanced_agency)
- Full: Father → Architect → Developer → QA → Reviewer → Father (build_enhanced_agency)
- Parallel Docs: Father → DocumentationAgent (runs in parallel for docs alignment)

Memory initialization priority:
1) Enhanced Firestore (if FIREBASE_* env present)
2) IntelligentMemoryStore
3) Basic Firestore (fallback)
4) InMemory (final fallback)

Documentation Management:
- DocumentationAgent is included by default in the enhanced agency as a parallel branch
- Background alignment loop can be enabled via environment variables (in launcher):
  - DOCS_CHECK_ENABLED=true|false (default: true)
  - DOCS_CHECK_INTERVAL_SEC=600 (default seconds)

Cross-references:
- Enhanced Agents: ./ENHANCED_AGENTS.md
- Memory System: ./MEMORY_SYSTEM.md

