# ADR-003: Unified Enhanced Architecture Migration

**Status**: Accepted  
**Date**: 2025-01-06  
**Deciders**: Architecture Team  

## Context and Problem Statement

The Fresh AI Agent System currently operates with a dual architecture:
1. **Legacy agents**: `Father`, `Architect`, `Developer`, `QA` - basic functionality
2. **Enhanced agents**: `EnhancedFather`, `EnhancedArchitect`, etc. - with intelligent persistent memory

This creates technical debt, complexity, and maintenance overhead. Additionally:
- **State management fragility**: Operational state stored in JSON files (`.fresh/dev_loop_state.json`) creates concurrency issues
- **Configuration sprawl**: Settings scattered across env vars, YAML files, and code defaults  
- **Untestable emergent behavior**: No framework to validate learning and improvement over time

## Decision

We will migrate to a **Unified Enhanced Architecture** with the following changes:

### 1. Single Agent Architecture
- **Remove**: Legacy agent classes (`Father`, `Architect`, `Developer`)
- **Rename**: `EnhancedFather` → `Father`, `EnhancedArchitect` → `Architect`, etc.
- **Consolidate**: All agents use intelligent persistent memory by default
- **Simplify**: Remove `enhanced=True/False` parameters from APIs

### 2. Firestore-Backed State Management  
- **Migrate**: From JSON files to Firestore collections:
  ```
  - operational_state: Current loop state, active tasks
  - task_queue: Pending and completed tasks  
  - agent_status: Agent health, metrics, last activity
  - configuration: Runtime config overrides
  ```
- **Implement**: Distributed locking using Firestore transactions
- **Add**: Fallback to in-memory state when Firestore unavailable

### 3. Unified Configuration Management
- **Create**: `ai/config/settings.py` using Pydantic BaseSettings
- **Define**: Clear precedence: env vars > config file > code defaults
- **Consolidate**: All scattered configuration reads

### 4. Benchmark Harness for Learning Validation
- **Build**: `ai/benchmark/` framework to test emergent behavior
- **Implement**: Failure injection testing for ERROR → KNOWLEDGE learning
- **Add**: Decision tracing for dynamic dispatch transparency

## Rationale

### Benefits
1. **Reduced Complexity**: Single code path eliminates dual-system maintenance
2. **Improved Reliability**: Firestore state management eliminates JSON file race conditions
3. **Better Testability**: Benchmark harness validates learning and improvement over time
4. **Enhanced Transparency**: Decision logging makes agent choices traceable

### Risks Mitigated
- **Data Loss**: Migration scripts with validation ensure zero data loss
- **Concurrent Access**: Firestore transactions prevent state corruption
- **Configuration Confusion**: Unified settings eliminate configuration hunting

## Implementation Plan

### Phase 1: Agent Architecture Migration (Days 1-3)
1. Create new agent files with clean names
2. Update all references throughout codebase
3. Remove legacy implementations
4. Update tests and documentation

### Phase 2: State Management Migration (Days 4-6)
1. Design Firestore schema with atomic update patterns
2. Implement `FirestoreStateManager` with distributed locking
3. Migrate existing JSON state to Firestore
4. Update all state consumers

### Phase 3: Testing & Validation Framework (Days 7-9)  
1. Build benchmark harness architecture
2. Implement learning validation tests
3. Add dynamic dispatch tracing
4. Create failure injection framework

### Phase 4: Documentation & Deployment (Days 10-11)
1. Update all documentation to reflect new architecture
2. Comprehensive testing and validation
3. Deploy to feature branch with full test coverage

## Consequences

### Positive
- **Unified codebase**: Easier to maintain and extend
- **Robust state management**: No more race conditions or data corruption
- **Validated learning**: Confidence that the system actually improves over time
- **Clear configuration**: No more hunting for settings across files

### Negative
- **Migration effort**: Significant refactoring required
- **Temporary complexity**: During migration period, both systems may coexist
- **Firestore dependency**: Increased reliance on external service

### Neutral
- **API changes**: Some breaking changes to internal APIs (external APIs remain stable)
- **Test updates**: Many tests need updating but test coverage improves

## Validation

Success criteria:
- [ ] All tests passing with unified architecture
- [ ] Zero data loss during state migration  
- [ ] Benchmark harness demonstrates learning validation
- [ ] Multi-process scenarios work without state conflicts
- [ ] Configuration management eliminates scattered settings
- [ ] Documentation fully aligned with new architecture

## Related Decisions

This ADR supersedes:
- Dual agent architecture patterns
- JSON-based state management
- Scattered configuration approaches

This ADR enables:
- Future agent capability enhancements
- Advanced learning algorithms
- Production deployment scalability
