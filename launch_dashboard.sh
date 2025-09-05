#!/bin/bash

# 🚀 Fresh AI Agent Dashboard Launcher
# 
# Quick launcher for the web-based agent control dashboard
# 
# Usage:
#   ./launch_dashboard.sh           # Start dashboard on port 8080
#   ./launch_dashboard.sh 9000     # Start dashboard on port 9000
#   ./launch_dashboard.sh --help   # Show help

set -e

PORT=${1:-8080}

if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    echo "🚀 Fresh AI Agent Dashboard Launcher"
    echo ""
    echo "Usage:"
    echo "  ./launch_dashboard.sh           # Start on port 8080 (default)"
    echo "  ./launch_dashboard.sh 9000     # Start on port 9000"
    echo "  ./launch_dashboard.sh --help   # Show this help"
    echo ""
    echo "Features:"
    echo "  🎛️  Agent Controls - Start/stop all agent types"
    echo "  📊 Live Monitoring - Real-time status and activity"
    echo "  🛑 Emergency Stop - Safety controls"
    echo "  📈 Performance Metrics - Track agent productivity"
    echo ""
    exit 0
fi

echo "🚀 Starting Fresh AI Agent Dashboard..."
echo "📊 Dashboard will be available at: http://localhost:$PORT"
echo "🛑 Press Ctrl+C to stop"
echo ""

# Check if poetry is available
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry not found. Please install Poetry first:"
    echo "   curl -sSL https://install.python-poetry.org | python3 -"
    exit 1
fi

# Check if we're in the right directory
if [[ ! -f "pyproject.toml" ]]; then
    echo "❌ Please run this script from the Fresh project root directory"
    exit 1
fi

# Install dependencies if needed
if [[ ! -d ".venv" ]] || [[ ! -f "poetry.lock" ]]; then
    echo "📦 Installing dependencies..."
    poetry install --no-dev
fi

# Launch the dashboard with correct Python path
PYTHONPATH="$(pwd)" poetry run python ai/interface/web_dashboard.py --port "$PORT"
