# API Reference

*Auto-generated on 2025-09-05T15:44:00.116118*

## Overview

The Fresh AI Agent System provides both REST API endpoints and CLI commands for all features.

## REST API Endpoints

### Base URL
```
http://localhost:8000
```

### Authentication
Most endpoints require authentication. Include your API key in the Authorization header:
```
Authorization: Bearer your-api-key
```

## Available Endpoints

### Main_Router API

# CLI Commands

The system provides comprehensive CLI commands through Poetry:

### Core Commands
```bash
# Scan repository for issues
poetry run python -m ai.cli.fresh scan . --json

# Spawn an agent for a specific task
poetry run python -m ai.cli.fresh spawn "Fix the bug in auth module"

# Run autonomous development loop
poetry run python -m ai.cli.fresh run --once

# Monitor agents
poetry run python -m ai.cli.fresh monitor --enhanced

# Feature management
poetry run python -m ai.cli.fresh feature-inventory
poetry run python -m ai.cli.fresh feature-validate
```

### Batch Operations
```bash
# Run full-scale implementation
python scripts/run_fullscale_implementation.py --budget 50 --agents 3

# Monitor with dashboard
python ai/dashboard/enhanced_dashboard.py

# CI/CD operations  
python scripts/automated_cicd_pipeline.py --batch-id 1
```

---

*This documentation is automatically maintained by the Fresh AI Agent System.*