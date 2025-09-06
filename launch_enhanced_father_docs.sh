#!/usr/bin/env bash
# 🧠 Enhanced Father Documentation Orchestrator v2.0
# MCP Reference: 688cf28d-e69c-4624-b7cb-0725f36f9518

# Strict error handling
set -euo pipefail

# Ensure we're in the project directory
cd "$(dirname "$0")"

# Ensure Poetry is available
if ! command -v poetry >/dev/null 2>&1; then
    echo "❌ Poetry not found. Please install Poetry first."
    exit 1
fi

# Title display
echo "🧠 ENHANCED FATHER - LEAN AUTONOMOUS SYSTEM OPTIMIZER"
echo "===================================================="
echo "💰 Budget: \$2.00"
echo "👥 Agents: 20 parallel autonomous optimization agents"
echo "🎯 Focus: SpaceX rocket approach - lean, efficient, autonomous agent optimized"
echo ""
echo "This will optimize the system for autonomous agents:"
echo "  • Hook up missing integrations that block agents"
echo "  • Eliminate technical debt that confuses agents" 
echo "  • Add memory/learning capabilities for agents"
echo "  • Create agent-optimized inline documentation"
echo "  • Streamline autonomous workflows"
echo "  • Build feedback loops for continuous learning"
echo ""

# Check dependencies
if ! poetry check >/dev/null 2>&1; then
    echo "❌ Poetry dependencies not installed. Running poetry install..."
    poetry install --no-root || exit 1
fi

# Set Python path
export PYTHONPATH="${PYTHONPATH:-$(pwd)}"

# Get approval
read -p "🚀 Launch Enhanced Father lean system optimization? (y/N): " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🧠 Launching Enhanced Father lean system optimization..."
    
    # Run with proper error handling and Poetry
    if ! poetry run python scripts/enhanced_father_documentation_orchestrator.py "$@"; then
        echo "❌ Enhanced Father optimization failed"
        exit 1
    fi
else
    echo "🛑 Enhanced Father optimization cancelled"
    exit 0
fi
