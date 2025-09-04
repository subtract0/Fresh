# 🤖 Autonomous Development Orchestration Guide

This guide shows you how to run **multiple autonomous development agents** that work in the background to continuously improve your codebase.

## 🚀 Quick Start

### 1. Run 10 Agents Overnight (10 EUR Budget)

```bash
# Start autonomous orchestration with overnight mode
fresh auto start --agents 10 --budget 10.0 --overnight --hours 8

# Monitor progress (in another terminal)
fresh auto status

# Stop gracefully
fresh auto stop
```

### 2. Interactive Development (User Approval)

```bash  
# Start with user approval checkpoints
fresh auto start --agents 5 --budget 5.0 --hours 4

# Approve agents when they ask
fresh auto status  # See which agents need approval
fresh auto approve abc12345  # Approve specific agent
```

### 3. Monitor with Dashboard

```bash
# Start orchestration in background
fresh auto start --agents 10 --overnight &

# Launch monitoring dashboard
python ai/orchestration/monitoring_dashboard.py
```

## 📋 Command Reference

### Start Orchestration

```bash
fresh auto start [OPTIONS]

OPTIONS:
  --agents N        Maximum number of agents (default: 10)
  --budget AMOUNT   Budget in USD (default: 10.0)  
  --overnight       Enable 24/7 operation mode
  --hours N         Maximum runtime hours (default: 8)
  --no-approval     Skip user approval checkpoints
  --strategy TYPE   Feature selection (highest_impact|safest|random)
```

### Monitor Status

```bash
fresh auto status [OPTIONS]

OPTIONS:
  --format FORMAT   Output format (summary|detailed|json)
```

Example output:
```
🤖 AUTONOMOUS ORCHESTRATION STATUS
==================================================
Running: Yes
Cost: $3.25 / $10.00
Agents: 7

🤖 AGENTS:
  🛠️ abc12345 | implementing | build_enhanced_agency
     Runtime: 15.5min | Cost: $0.75
     
  👤 def67890 | awaiting_user | demo_enhanced_agency  
     Runtime: 8.2min | Cost: $0.25
     ❓ Question: Agent completed work, please test branch...

⚠️  1 agents awaiting your approval:
   Use: fresh auto approve def67890
```

### Approve Agents

```bash
fresh auto approve AGENT_ID

# Examples:
fresh auto approve abc12345     # Full or partial ID
fresh auto approve abc          # Prefix matching
```

### Stop Orchestration  

```bash
fresh auto stop [OPTIONS]

OPTIONS:
  --force          Force immediate stop (may interrupt agents)
```

## 🏗️ How It Works

### Agent Lifecycle

Each autonomous agent follows this workflow:

1. **🔍 Analysis**: Analyze target feature and create branch
2. **🛠️ Implementation**: Implement improvements/fixes 
3. **🧪 Testing**: Run tests and verify functionality
4. **👤 User Approval**: Wait for your testing/approval (optional)
5. **📋 Commit & PR**: Create commit and GitHub pull request
6. **✅ Complete**: Agent finishes and reports results

### Feature Selection

Agents automatically select features to improve based on:

- **Necessity**: Feature marked as needed in inventory
- **Unhooked**: Feature not accessible via CLI/API
- **Quality Score**: Features with improvement potential  
- **Safety**: Non-destructive operations preferred

### Cost Management

- **Budget Limits**: Hard stop when budget reached
- **Per-Agent Limits**: Each agent has cost cap (~$1.00 USD)
- **Real-time Tracking**: Monitor costs in real-time
- **Graceful Degradation**: Fewer agents as budget consumed

## 🛡️ Safety Features

### Built-in Safety Controls

- ✅ **Feature Branch Creation**: Each agent works on isolated branch
- ✅ **Test Verification**: All changes tested before commit
- ✅ **User Approval**: Optional checkpoints for your review
- ✅ **Budget Limits**: Hard financial caps
- ✅ **Time Limits**: Maximum runtime protection
- ✅ **Graceful Shutdown**: Ctrl+C stops safely
- ✅ **Error Recovery**: Failed agents don't affect others
- ✅ **Progress Logging**: Full audit trail of all actions

### User Interaction Points

Agents will pause and ask for your approval when:
- Implementation is complete and ready for testing
- Tests are failing and need human intervention  
- Complex changes require architectural decisions
- User timeout exceeded (continues automatically)

## 🌙 Overnight Operation

### Setup for Overnight Running

```bash
# Start overnight mode (8 hour limit)
fresh auto start --agents 10 --budget 10.0 --overnight --hours 8 --no-approval

# Or with tmux/screen for persistence
tmux new-session -d -s autonomous 'fresh auto start --overnight --agents 10'
```

### Morning Review

```bash
# Check what happened overnight
fresh auto status --format detailed

# Review generated PRs
gh pr list --label "autonomous"

# Check logs
ls .fresh/logs/orchestrator_*.log
```

### Expected Overnight Results

With 10 EUR budget overnight:
- **5-15 agents** typically spawned
- **2-8 successful PRs** created
- **Multiple features** hooked up to CLI
- **Test coverage** improvements
- **Documentation** updates
- **Code quality** improvements

## 📊 Monitoring & Observability

### Real-time Monitoring

```bash
# Terminal dashboard
python ai/orchestration/monitoring_dashboard.py

# Status checks
fresh auto status
fresh auto status --format json | jq '.agents | length'
```

### Log Analysis

```bash
# View orchestrator logs
tail -f .fresh/logs/orchestrator_$(date +%Y%m%d)*.log

# View agent progress
grep "Agent.*completed" .fresh/logs/orchestrator*.log

# Cost tracking
grep "Cost:" .fresh/logs/orchestrator*.log
```

### Reports

Final orchestration reports saved to:
```
.fresh/orchestration_report_YYYYMMDD_HHMMSS.json
```

Contains:
- Total runtime and cost
- Agent success/failure rates
- Generated PR links
- Performance metrics

## 💡 Best Practices

### For Overnight Running

1. **Set Conservative Budget**: Start with $5-10 USD
2. **Use Safe Strategy**: `--strategy safest` for first runs
3. **Enable Logging**: Check logs in morning
4. **Test Branch Protection**: Ensure main branch protected
5. **Review PRs**: Review all autonomous PRs before merging

### For Interactive Development

1. **Start Small**: Use 2-3 agents initially
2. **Monitor Actively**: Check status every 30 minutes
3. **Approve Quickly**: Don't leave agents waiting long
4. **Test Branches**: Actually test the changes agents make
5. **Provide Feedback**: Use GitHub PR reviews for learning

### For Production Use

1. **Separate Repository**: Use development/testing repo first
2. **Branch Protection**: Require PR reviews before merge
3. **Cost Alerts**: Monitor OpenAI API usage
4. **Regular Monitoring**: Check agent progress
5. **Backup Strategy**: Ensure Git history preserved

## 🐛 Troubleshooting

### Common Issues

**Orchestration won't start:**
```bash
# Check dependencies
poetry run python -c "from ai.orchestration.autonomous_orchestrator import AutonomousOrchestrator"

# Check permissions
git config user.name
git config user.email
gh auth status
```

**Agents failing:**
```bash
# Check agent logs
fresh auto status --format detailed

# View specific agent errors
grep "failed" .fresh/logs/orchestrator*.log
```

**High costs:**
```bash
# Monitor cost in real-time
fresh auto status | grep Cost

# Stop if needed
fresh auto stop
```

### Emergency Procedures

**Emergency Stop:**
```bash
fresh auto stop --force
```

**Check for runaway costs:**
```bash
# Monitor OpenAI API usage
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
  https://api.openai.com/v1/usage

# View usage dashboard
open https://platform.openai.com/usage
```

## 🎯 Example Scenarios

### Scenario 1: Weekend Code Cleanup

```bash
# Friday evening - start overnight cleanup
fresh auto start --agents 8 --budget 8.0 --overnight --strategy safest

# Monday morning - review results
fresh auto status
gh pr list --state open --label autonomous
```

### Scenario 2: Feature Hookup Sprint

```bash  
# Interactive session hooking up features
fresh auto start --agents 3 --budget 3.0 --hours 2

# Approve agents as they complete work
watch "fresh auto status"
```

### Scenario 3: Test Coverage Improvement

```bash
# Focus on testing improvements
fresh auto start --agents 5 --budget 5.0 --strategy highest_impact

# Monitor for test-related improvements
fresh auto status --format detailed | grep -i test
```

## 📈 Success Metrics

Track the autonomous development impact:

- **Features Hooked Up**: Previously inaccessible features now available via CLI
- **Test Coverage**: New tests added for uncovered code
- **Quality Score**: Average feature quality improvement
- **PR Success Rate**: Percentage of autonomous PRs that are merged
- **Cost Efficiency**: Improvement value per dollar spent
- **Time Savings**: Manual work automated

## 🤝 Human-AI Collaboration

The system is designed for **human-AI collaboration**:

- **Agents do the tedious work**: Feature hookups, basic tests, documentation
- **You do the creative work**: Architecture decisions, complex logic, code review
- **Agents learn from feedback**: PR reviews help improve future work
- **You maintain control**: Approval checkpoints and override capabilities

This creates a **force multiplier** for your development productivity while maintaining code quality and project control.

---

🎉 **Congratulations!** You now have autonomous agents working on your codebase 24/7, continuously improving and maintaining your software while you focus on the high-value creative work.
