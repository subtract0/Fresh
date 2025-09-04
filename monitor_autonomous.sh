#!/bin/bash

# Live Autonomous Development Monitor
# Shows real-time status of all running agents with cost tracking

while true; do
    clear
    echo "🤖 AUTONOMOUS DEVELOPMENT LIVE MONITOR"
    echo "======================================"
    echo "📅 $(date)"
    echo ""
    
    # Check if orchestration is running
    if ps aux | grep "auto start" | grep -v grep > /dev/null; then
        echo "🟢 ORCHESTRATION STATUS: ACTIVE"
        
        # Extract latest metrics from log
        echo ""
        echo "💰 COST TRACKING:"
        echo "----------------"
        
        # Get latest cost and runtime info
        LATEST_COST=$(tail -100 live_agent.log | grep "💰 Cost:" | tail -1 | sed 's/.*Cost: \$\([0-9.]*\).*/\1/')
        LATEST_BUDGET=$(tail -100 live_agent.log | grep "💰 Cost:" | tail -1 | sed 's/.*\$\([0-9.]*\)$/\1/')
        LATEST_RUNTIME=$(tail -100 live_agent.log | grep "⏱️ Runtime:" | tail -1 | sed 's/.*Runtime: \([0-9.]*\) minutes/\1/')
        
        if [ -n "$LATEST_COST" ] && [ -n "$LATEST_RUNTIME" ] && [ -n "$LATEST_BUDGET" ]; then
            COST_FLOAT=$(echo "$LATEST_COST" | bc -l 2>/dev/null || echo "$LATEST_COST")
            RUNTIME_FLOAT=$(echo "$LATEST_RUNTIME" | bc -l 2>/dev/null || echo "$LATEST_RUNTIME")
            BUDGET_FLOAT=$(echo "$LATEST_BUDGET" | bc -l 2>/dev/null || echo "$LATEST_BUDGET")
            
            # Calculate hourly rate (if runtime > 0)
            if [ $(echo "$RUNTIME_FLOAT > 0" | bc -l 2>/dev/null || echo "0") -eq 1 ]; then
                HOURLY_RATE=$(echo "scale=2; $COST_FLOAT * 60 / $RUNTIME_FLOAT" | bc -l 2>/dev/null || echo "0.00")
                ESTIMATED_24H=$(echo "scale=2; $HOURLY_RATE * 24" | bc -l 2>/dev/null || echo "0.00")
            else
                HOURLY_RATE="0.00"
                ESTIMATED_24H="0.00"
            fi
            
            PERCENTAGE=$(echo "scale=1; $COST_FLOAT * 100 / $BUDGET_FLOAT" | bc -l 2>/dev/null || echo "0.0")
            
            echo "   Current Total: \$$COST_FLOAT / \$$BUDGET_FLOAT ($PERCENTAGE%)"
            echo "   Hourly Rate: \$$HOURLY_RATE/hour"
            echo "   24h Estimate: \$$ESTIMATED_24H"
            echo "   Runtime: ${RUNTIME_FLOAT} minutes"
        else
            echo "   Status: Initializing cost tracking..."
        fi
        
        echo ""
        echo "🤖 AGENT ACTIVITY:"
        echo "-----------------"
        
        # Count active agents from latest status
        ACTIVE_AGENTS=$(tail -100 live_agent.log | grep "📊 Status:" | tail -1 | sed 's/.*Status: \([0-9]*\) active.*/\1/')
        COMPLETED_AGENTS=$(tail -100 live_agent.log | grep "📊 Status:" | tail -1 | sed 's/.*active, \([0-9]*\) completed.*/\1/')
        FAILED_AGENTS=$(tail -100 live_agent.log | grep "📊 Status:" | tail -1 | sed 's/.*completed, \([0-9]*\) failed/\1/')
        
        if [ -n "$ACTIVE_AGENTS" ]; then
            echo "   Active: $ACTIVE_AGENTS agents"
            echo "   Completed: $COMPLETED_AGENTS agents"  
            echo "   Failed: $FAILED_AGENTS agents"
        else
            echo "   Status: Reading agent metrics..."
        fi
        
        # Show recent agent activity
        echo ""
        echo "🚀 RECENT AGENT SPAWNS (Last 5):"
        echo "--------------------------------"
        tail -50 live_agent.log | grep "🚀.*starting work on" | tail -5 | while read line; do
            AGENT_ID=$(echo "$line" | sed 's/.*Agent \([a-f0-9]*\) starting.*/\1/')
            FEATURE=$(echo "$line" | sed 's/.*starting work on \(.*\)/\1/')
            echo "   Agent $AGENT_ID → $FEATURE"
        done
        
        # Show git branch count
        echo ""
        echo "🌿 GIT BRANCHES:"
        echo "---------------"
        BRANCH_COUNT=$(git branch 2>/dev/null | grep auto/ | wc -l | tr -d ' ')
        echo "   Autonomous branches: $BRANCH_COUNT"
        
        # Show latest 3 branches created
        echo "   Latest branches:"
        git branch 2>/dev/null | grep auto/ | tail -3 | sed 's/^/      /'
        
        # Show any recent errors
        echo ""
        echo "⚠️  RECENT ISSUES (Last 3):"
        echo "---------------------------"
        RECENT_ERRORS=$(tail -20 live_agent.log | grep "ERROR" | tail -3)
        if [ -n "$RECENT_ERRORS" ]; then
            echo "$RECENT_ERRORS" | sed 's/^/   /'
        else
            echo "   No recent errors"
        fi
        
    else
        echo "🔴 ORCHESTRATION STATUS: STOPPED"
        echo ""
        echo "Use: poetry run python -m ai.cli.fresh auto start --agents 20 --budget 50.0 --overnight --hours 24 --strategy highest_impact --no-approval"
    fi
    
    echo ""
    echo "🔄 Refreshing in 10 seconds... (Ctrl+C to exit)"
    sleep 10
done
