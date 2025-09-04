#!/bin/bash

# Real-Time Codebase Health Monitor
# Shows actual development activity and issues

while true; do
    clear
    echo "🏗️  REAL CODEBASE DEVELOPMENT MONITOR"
    echo "====================================="
    echo "📅 $(date)"
    echo ""
    
    # Check for running processes
    RUNNING_AGENTS=$(ps aux | grep -E "(fresh.*run|python.*ai)" | grep -v grep | wc -l | tr -d ' ')
    if [ "$RUNNING_AGENTS" -gt 0 ]; then
        echo "🟢 DEVELOPMENT ACTIVITY: $RUNNING_AGENTS processes active"
        ps aux | grep -E "(fresh.*run|python.*ai)" | grep -v grep | head -3 | while read line; do
            echo "   $(echo "$line" | awk '{print $11" "$12" "$13}')"
        done
    else
        echo "🔴 DEVELOPMENT ACTIVITY: No active processes"
    fi
    echo ""
    
    # Show recent agent activity
    echo "📋 RECENT DEVELOPMENT ATTEMPTS:"
    echo "--------------------------------"
    if [ -f simple_agent.log ]; then
        echo "Last simple agent run:"
        tail -5 simple_agent.log | sed 's/^/   /'
    fi
    echo ""
    
    # Check for actual broken windows (compile issues)
    echo "🚨 BROKEN WINDOWS CHECK:"
    echo "------------------------"
    
    # Try importing key modules
    echo "   Testing imports..."
    python3 -c "from ai.cli.fresh import main" 2>/dev/null && echo "   ✅ CLI module imports OK" || echo "   ❌ CLI module import failed"
    python3 -c "from ai.autonomous.loop import AutonomousLoop" 2>/dev/null && echo "   ✅ Autonomous loop imports OK" || echo "   ❌ Autonomous loop import failed"
    python3 -c "from ai.memory.intelligent_store import IntelligentMemoryStore" 2>/dev/null && echo "   ✅ Memory system imports OK" || echo "   ❌ Memory system import failed"
    
    # Check for syntax errors
    echo "   Checking for syntax errors..."
    SYNTAX_ERRORS=$(find ai/ -name "*.py" -exec python3 -m py_compile {} \; 2>&1 | grep -c "SyntaxError" || echo 0)
    if [ "$SYNTAX_ERRORS" -eq 0 ]; then
        echo "   ✅ No syntax errors found"
    else
        echo "   ❌ $SYNTAX_ERRORS syntax errors found"
    fi
    
    echo ""
    
    # Git status
    echo "📊 GIT STATUS:"
    echo "-------------"
    echo "   Current branch: $(git branch --show-current)"
    
    UNCOMMITTED=$(git status --porcelain | wc -l | tr -d ' ')
    if [ "$UNCOMMITTED" -eq 0 ]; then
        echo "   ✅ Working directory clean"
    else
        echo "   ⚠️  $UNCOMMITTED uncommitted changes"
        git status --porcelain | head -5 | sed 's/^/      /'
    fi
    
    # Recent commits
    echo "   Last 3 commits:"
    git log --oneline -3 | sed 's/^/      /'
    
    echo ""
    
    # Available working commands
    echo "🛠️  WORKING COMMANDS:"
    echo "-------------------"
    echo "   poetry run python -m ai.cli.fresh scan ."
    echo "   poetry run python -m ai.cli.fresh run --once"
    echo "   poetry run python -m ai.cli.fresh feature inventory"
    
    echo ""
    echo "🔄 Refreshing in 10 seconds... (Ctrl+C to exit)"
    sleep 10
done
