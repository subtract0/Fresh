# System Services

This directory contains system-level services that provide ongoing functionality and maintenance for the Fresh AI system.

## Components

### Documentation Services
- **`self_documenting_loop.py`** - Automated documentation validation and synchronization service

## Features

### Self-Documenting Loop
The self-documenting loop service ensures that:
- Documentation stays synchronized with code changes
- Feature documentation is automatically updated
- Broken links and references are detected and reported
- Code examples in documentation remain functional

#### Key Capabilities
- Automatic feature inventory generation
- Documentation cross-reference validation
- Code example syntax checking
- Orphan file detection and cleanup
- Documentation freshness monitoring

## Usage

### Starting the Self-Documenting Service
```python
from ai.services.self_documenting_loop import SelfDocumentingLoop

service = SelfDocumentingLoop(
    check_interval=600,  # 10 minutes
    auto_fix_enabled=False,  # Manual review required
    memory_integration=True
)

# Start the service
service.start()
```

### Manual Documentation Check
```python
from ai.services.self_documenting_loop import validate_documentation

result = validate_documentation(
    project_root=".",
    output_format="json",
    strict_mode=True
)

print(f"Documentation score: {result.score}%")
```

## Configuration

Environment variables:
- `DOCS_CHECK_ENABLED` - Enable documentation checking service (default: true)
- `DOCS_CHECK_INTERVAL_SEC` - Check interval in seconds (default: 600)
- `DOCS_AUTO_FIX_ENABLED` - Enable automatic fixes (default: false)
- `DOCS_STRICT_MODE` - Enable strict validation mode (default: true)

## Service Integration

### Memory System
- Stores documentation improvement patterns
- Learns from successful documentation updates
- Remembers common documentation issues and solutions

### Enhanced Agents
- **DocumentationAgent** - Specialized agent for documentation tasks
- Coordinates with other agents for comprehensive documentation

### CI/CD Integration
- Can be integrated into CI/CD pipelines
- Provides automated documentation quality gates
- Generates documentation health reports

## Monitoring

The service provides metrics for:
- Documentation coverage percentage
- Broken link detection count
- Code example validation results
- Documentation freshness scores

## Related Documentation
- [Documentation Standards](../../docs/DOCS_STANDARDS.md)
- [Self-Documenting Loop Guide](../../docs/DOCS_STANDARDS.md#self-documenting-loop)
- [Quality Gates](../../docs/QUALITY_GATES.md)
