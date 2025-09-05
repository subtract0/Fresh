# Development Loop Components

This directory contains the core development cycle and workflow management components that implement continuous development loops and repository scanning.

## Components

### Development Cycle
- **`devcycle.py`** - Core RED→GREEN→REFACTOR development cycle implementation
- **`dev_loop.py`** - Development workflow orchestration and management

### Repository Analysis
- **`repo_scanner.py`** - Automated repository scanning and issue detection

## Features

### TDD Development Cycle
- RED: Test creation and failure identification
- GREEN: Minimal implementation to pass tests
- REFACTOR: Code improvement and optimization
- Memory integration for learning from past cycles

### Repository Scanning
- Code quality analysis
- Issue detection and prioritization
- Technical debt identification
- Automated improvement suggestions

## Usage

### Running a Development Cycle
```python
from ai.loop.devcycle import run_development_cycle

result = run_development_cycle(
    project_path="/path/to/project",
    target_feature="user_authentication",
    memory_enabled=True
)
```

### Repository Scanning
```python
from ai.loop.repo_scanner import scan_repository

scan_result = scan_repository(
    repo_path=".",
    output_format="json",
    include_suggestions=True
)
```

### Continuous Development Loop
```python
from ai.loop.dev_loop import continuous_development

# Start continuous development mode
continuous_development(
    watch_paths=["src/", "tests/"],
    auto_fix=False,  # Manual confirmation required
    memory_learning=True
)
```

## Configuration

Environment variables:
- `DEV_LOOP_AUTO_FIX` - Enable automatic fixing (default: false)
- `DEV_LOOP_WATCH_INTERVAL` - File watching interval in seconds
- `MEMORY_ENABLED` - Enable memory learning from development cycles

## Integration

### Memory System
The development loop integrates with the memory system to:
- Learn from successful and failed development patterns
- Remember effective refactoring techniques
- Store knowledge about code quality improvements

### Enhanced Agents
Works closely with enhanced agents:
- **EnhancedDeveloper** - Implementation and coding patterns
- **EnhancedArchitect** - Design and architectural decisions
- **EnhancedQA** - Testing strategies and quality metrics

## Related Documentation
- [TDD Guide](../../docs/TESTING_PRINCIPLES.md)
- [Development Workflow](../../docs/AGENT_DEVELOPMENT.md)
- [Memory Integration](../../docs/MEMORY_SYSTEM.md)
