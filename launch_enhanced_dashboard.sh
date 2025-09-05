#!/bin/bash

# 🚀 Enhanced Fresh AI Dashboard Launcher
# 
# Comprehensive browser-based interface with:
# - Real-time Mother Agent conversation
# - Preset orchestration templates
# - Live multi-agent task monitoring
# - Complete system control
#
# Usage: ./launch_enhanced_dashboard.sh [--port 8080] [--no-browser]

set -e

# Default values
PORT=8080
OPEN_BROWSER=true

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --port)
      PORT="$2"
      shift 2
      ;;
    --no-browser)
      OPEN_BROWSER=false
      shift
      ;;
    -h|--help)
      echo "🚀 Enhanced Fresh AI Dashboard Launcher"
      echo ""
      echo "Options:"
      echo "  --port PORT      Set dashboard port (default: 8080)"
      echo "  --no-browser     Don't open browser automatically"
      echo "  -h, --help       Show this help message"
      echo ""
      echo "Features:"
      echo "  🤖 Conversational Mother Agent interface"
      echo "  📋 Preset orchestration templates"
      echo "  ⚡ Live multi-agent task monitoring"
      echo "  📊 Real-time progress visualization"
      echo "  🔧 Complete CLI integration"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      echo "Use --help for usage information"
      exit 1
      ;;
  esac
done

echo "🚀 Starting Enhanced Fresh AI Dashboard..."
echo ""
echo "📊 Dashboard URL: http://localhost:$PORT"
echo "🤖 Mother Agent: Real-time conversation interface"
echo "📋 Templates: Pre-configured orchestration tasks"
echo "⚡ Live Tasks: Multi-agent progress monitoring"
echo ""

# Check if in Fresh directory
if [[ ! -f "pyproject.toml" ]] || [[ ! -d "ai" ]]; then
    echo "❌ Error: Must run from Fresh project root directory"
    echo "Current directory: $(pwd)"
    echo "Expected: /Users/am/Code/Fresh"
    exit 1
fi

# Check Poetry installation
if ! command -v poetry &> /dev/null; then
    echo "❌ Error: Poetry not installed"
    echo "Install with: curl -sSL https://install.python-poetry.org | python3 -"
    exit 1
fi

# Install dependencies if needed
if [[ ! -d ".venv" ]]; then
    echo "📦 Installing dependencies..."
    poetry install
fi

# Set browser flag
BROWSER_FLAG=""
if [[ "$OPEN_BROWSER" == "false" ]]; then
    BROWSER_FLAG="--no-browser"
fi

# Launch enhanced dashboard
echo "🚀 Launching Enhanced Dashboard..."
echo "Press Ctrl+C to stop"
echo ""

# Set PYTHONPATH and launch
export PYTHONPATH="$(pwd)"
poetry run python ai/interface/enhanced_dashboard.py --port "$PORT" $BROWSER_FLAG
