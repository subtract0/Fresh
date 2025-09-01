# Agency Configuration

This guide explains how the enhanced agency is constructed and configured.

Key entry points:
- ai/enhanced_agency.py — build_enhanced_agency(), initialize_intelligent_memory()
- ai/agency.py — legacy/basic agency wiring (if present)

Examples:
- Lightweight: Father → Architect → Developer (build_lightweight_enhanced_agency)
- Full: Father → Architect → Developer → QA → Reviewer → Father (build_enhanced_agency)

Memory initialization priority:
1) Enhanced Firestore (if FIREBASE_* env present)
2) IntelligentMemoryStore
3) Basic Firestore (fallback)
4) InMemory (final fallback)

Cross-references:
- Enhanced Agents: ./ENHANCED_AGENTS.md
- Memory System: ./MEMORY_SYSTEM.md

