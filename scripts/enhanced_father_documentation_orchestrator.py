#!/usr/bin/env python3
"""
🧠 Enhanced Father Documentation Orchestrator
Strategic Planning Agent → Documentation Backlog → Autonomous Swarm Execution
"""
import asyncio
import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment
def load_env():
    """Load environment variables from .env file"""
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value.strip('"\'')

load_env()

def analyze_documentation_state():
    """Analyze current documentation state to inform strategic planning"""
    print("📊 Analyzing current documentation state...")
    
    doc_analysis = {
        "missing_readme_files": [],
        "outdated_docs": [],
        "missing_api_docs": [],
        "incomplete_user_guides": [],
        "missing_architecture_docs": []
    }
    
    # 1. Find directories missing README files
    try:
        result = subprocess.run([
            'find', '.', '-type', 'd', '-name', 'ai', '-o', '-name', 'scripts', 
            '-o', '-name', 'tests', '-not', '-path', './autonomous_env/*'
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)
        
        for dir_path in result.stdout.strip().split('\n'):
            if dir_path and not os.path.exists(os.path.join(dir_path, 'README.md')):
                doc_analysis["missing_readme_files"].append(dir_path.strip('./'))
    except Exception:
        pass
    
    # 2. Find Python files missing docstrings (API docs)
    try:
        result = subprocess.run([
            'find', '.', '-name', '*.py', '-path', '*/ai/*', 
            '-not', '-path', './autonomous_env/*'
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)
        
        py_files = [f.strip() for f in result.stdout.split('\n') if f.strip()][:15]
        
        for py_file in py_files:
            try:
                with open(py_file, 'r') as f:
                    content = f.read()
                    # Check if missing class or function docstrings
                    if ('class ' in content or 'def ' in content) and '"""' not in content:
                        doc_analysis["missing_api_docs"].append(py_file.lstrip('./'))
            except Exception:
                pass
    except Exception:
        pass
    
    # 3. Check for missing architecture documentation
    arch_docs = ['docs/ARCHITECTURE.md', 'docs/DESIGN.md', 'docs/SYSTEM_OVERVIEW.md']
    for doc in arch_docs:
        if not os.path.exists(doc):
            doc_analysis["missing_architecture_docs"].append(doc)
    
    # 4. Check existing docs for completeness
    docs_dir = Path("docs")
    if docs_dir.exists():
        for doc_file in docs_dir.glob("*.md"):
            try:
                with open(doc_file, 'r') as f:
                    content = f.read()
                    if len(content) < 500:  # Likely incomplete
                        doc_analysis["outdated_docs"].append(str(doc_file))
            except Exception:
                pass
    
    return doc_analysis

def create_enhanced_father_prompt(doc_analysis):
    """Create strategic planning prompt for Enhanced Father"""
    return f"""
# STRATEGIC DOCUMENTATION PLANNING SESSION

## Mission
You are the Enhanced Father - strategic planner for autonomous documentation improvement. 
Analyze the current documentation state and create a prioritized backlog of documentation tasks 
for our autonomous agent swarm.

## Current Documentation Analysis
{json.dumps(doc_analysis, indent=2)}

## Your Strategic Planning Role
1. **Analyze** the documentation gaps and prioritize by business impact
2. **Plan** 8-12 specific documentation tasks that autonomous agents can execute
3. **Structure** tasks for parallel execution by specialized documentation agents
4. **Focus** on high-impact improvements: user guides, API docs, architecture docs

## Required Output Format
Create a JSON response with this structure:
```json
{
  "strategic_assessment": "brief analysis of documentation priorities",
  "documentation_backlog": [
    {
      "type": "readme|api_docs|user_guide|architecture|tutorial",
      "priority": "high|medium|low", 
      "file_path": "path/to/create/or/update",
      "title": "Clear task title",
      "description": "Detailed task description for autonomous agents",
      "estimated_complexity": "simple|moderate|complex",
      "success_criteria": "How to measure completion"
    }
  ],
  "execution_strategy": "recommended parallel execution approach"
}
```

## Constraints for Autonomous Agents
- Tasks must be self-contained and executable by AI agents
- Focus on creating NEW documentation rather than major rewrites
- Prioritize user-facing and developer-facing documentation
- Each task should be completable in 3-5 minutes by an autonomous agent

Generate your strategic documentation plan now.
"""

async def consult_enhanced_father(doc_analysis):
    """Consult Enhanced Father for strategic documentation planning"""
    print("🧠 Consulting Enhanced Father for strategic planning...")
    
    # Setup OpenAI client for Enhanced Father consultation
    try:
        from openai import OpenAI
        
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")
        
        client = OpenAI(api_key=api_key)
        
        # Enhanced Father uses GPT-5 with high reasoning for strategic planning
        response = client.chat.completions.create(
            model="gpt-5",
            messages=[
                {
                    "role": "system", 
                    "content": "You are Enhanced Father - strategic planner for autonomous documentation swarms. You create prioritized backlogs for autonomous agents to execute."
                },
                {
                    "role": "user", 
                    "content": create_enhanced_father_prompt(doc_analysis)
                }
            ],
            reasoning_effort="high",  # High reasoning for strategic planning
            verbosity="low",
            max_completion_tokens=2000,
            temperature=0.2
        )
        
        father_response = response.choices[0].message.content
        
        # Extract JSON from response
        import re
        json_match = re.search(r'```json\n(.*?)\n```', father_response, re.DOTALL)
        if json_match:
            strategy_data = json.loads(json_match.group(1))
        else:
            # Fallback: try to parse the entire response as JSON
            strategy_data = json.loads(father_response)
        
        return strategy_data
        
    except Exception as e:
        print(f"⚠️ Enhanced Father consultation failed: {e}")
        # Fallback strategy
        return create_fallback_documentation_strategy(doc_analysis)

def create_fallback_documentation_strategy(doc_analysis):
    """Fallback documentation strategy if Enhanced Father is unavailable"""
    return {
        "strategic_assessment": "Fallback strategy focusing on high-impact documentation gaps",
        "documentation_backlog": [
            {
                "type": "readme",
                "priority": "high",
                "file_path": "ai/README.md",
                "title": "AI Module Overview Documentation",
                "description": "Create comprehensive README for the ai/ module explaining architecture, agents, and usage",
                "estimated_complexity": "moderate",
                "success_criteria": "Clear overview, usage examples, and module structure documented"
            },
            {
                "type": "user_guide",
                "priority": "high", 
                "file_path": "docs/USER_GUIDE.md",
                "title": "Complete User Guide for Fresh AI System",
                "description": "Create step-by-step user guide for setting up and using the Fresh AI Agent System",
                "estimated_complexity": "complex",
                "success_criteria": "End-to-end user journey documented with examples"
            },
            {
                "type": "api_docs",
                "priority": "medium",
                "file_path": "docs/API_REFERENCE.md",
                "title": "API Reference Documentation",
                "description": "Document all available CLI commands, their options, and usage examples",
                "estimated_complexity": "moderate",
                "success_criteria": "All commands documented with examples and parameters"
            },
            {
                "type": "architecture",
                "priority": "high",
                "file_path": "docs/SYSTEM_ARCHITECTURE.md", 
                "title": "System Architecture Documentation",
                "description": "Document the MotherAgent, parallel orchestration, and agent architecture",
                "estimated_complexity": "complex",
                "success_criteria": "Clear architectural diagrams and component relationships"
            },
            {
                "type": "tutorial",
                "priority": "medium",
                "file_path": "docs/QUICK_START.md",
                "title": "Quick Start Tutorial",
                "description": "Create 5-minute quick start guide for new users",
                "estimated_complexity": "simple",
                "success_criteria": "New user can be productive within 5 minutes"
            }
        ],
        "execution_strategy": "Execute high-priority tasks first with 3-5 parallel agents"
    }

async def main():
    """Main orchestration with Enhanced Father strategic planning"""
    print("🧠 Enhanced Father Documentation Orchestrator")
    print("📋 Strategic Planning → Documentation Backlog → Autonomous Execution")
    print("=" * 80)
    
    # 1. Analyze current documentation state
    doc_analysis = analyze_documentation_state()
    print(f"📊 Analysis complete: Found documentation gaps in {len(doc_analysis)} categories")
    
    # 2. Consult Enhanced Father for strategic planning
    strategy = await consult_enhanced_father(doc_analysis)
    
    print(f"\n🧠 ENHANCED FATHER STRATEGIC ASSESSMENT:")
    print(f"📋 {strategy['strategic_assessment']}")
    
    print(f"\n📝 DOCUMENTATION BACKLOG: {len(strategy['documentation_backlog'])} tasks")
    for i, task in enumerate(strategy['documentation_backlog'], 1):
        priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}
        print(f"{priority_icon.get(task['priority'], '⚪')} {i}. {task['title']} ({task['type']}) - {task['file_path']}")
    
    print(f"\n⚡ EXECUTION STRATEGY: {strategy['execution_strategy']}")
    
    # 3. Execute documentation tasks using parallel autonomous agents
    print(f"\n🚀 Launching autonomous documentation swarm...")
    
    # Import and run the parallel orchestrator for documentation tasks
    from scripts.parallel_autonomous_orchestrator import ParallelAutonomousOrchestrator
    
    # Convert strategic tasks to implementation format
    documentation_tasks = []
    for task in strategy['documentation_backlog']:
        documentation_tasks.append({
            "file_path": task["file_path"],
            "description": f"Create {task['type']} documentation: {task['description']} - Success criteria: {task['success_criteria']}"
        })
    
    # Configure for documentation creation (more workers, higher budget for quality)
    max_workers = 6  # More workers for parallel documentation
    budget_limit = len(documentation_tasks) * 0.08  # Higher budget for quality documentation
    
    print(f"\n🎯 LAUNCHING ENHANCED FATHER ORCHESTRATED DOCUMENTATION...")
    print(f"🧠 Strategic Planner: Enhanced Father")
    print(f"👥 Documentation Agents: {max_workers}")
    print(f"💰 Budget Limit: ${budget_limit:.2f}")
    print(f"📝 Documentation Tasks: {len(documentation_tasks)}")
    print("=" * 60)
    
    # Create and run orchestrator
    orchestrator = ParallelAutonomousOrchestrator(
        max_workers=max_workers, 
        budget_limit=budget_limit
    )
    
    # Execute Enhanced Father's strategic plan
    start_time = datetime.now()
    report = await orchestrator.run_parallel_batch(documentation_tasks)
    end_time = datetime.now()
    
    # Analyze results
    duration_minutes = (end_time - start_time).total_seconds() / 60
    success_rate = report["orchestration_summary"]["success_rate"]
    
    print(f"\n📚 ENHANCED FATHER ORCHESTRATED DOCUMENTATION COMPLETE!")
    print("=" * 70)
    print(f"✅ Documentation Created: {report['orchestration_summary']['successful']}/{len(documentation_tasks)}")
    print(f"💰 Total Cost: ${report['orchestration_summary']['total_cost']:.2f}")
    print(f"⏱️  Duration: {duration_minutes:.1f} minutes")
    print(f"🎯 Success Rate: {success_rate:.1%}")
    
    if success_rate >= 0.7:
        print(f"\n🏆 ENHANCED FATHER STRATEGY SUCCESSFUL!")
        print(f"🧠 Strategic planning + autonomous execution = excellent documentation")
        print(f"📚 Knowledge base significantly improved by Enhanced Father's guidance")
        
        # Auto-commit documentation improvements
        subprocess.run(['git', 'add', '-A'], cwd=Path(__file__).parent.parent)
        subprocess.run([
            'git', 'commit', '-m', 
            f"📚 Enhanced Father: {report['orchestration_summary']['successful']} documentation improvements\n\n"
            f"🧠 Enhanced Father strategic planning orchestrated documentation swarm\n"
            f"📋 Strategic assessment and backlog creation\n"
            f"🤖 {max_workers} autonomous documentation agents\n"
            f"💰 Cost: ${report['orchestration_summary']['total_cost']:.2f}\n"
            f"⚡ Duration: {duration_minutes:.1f} minutes\n"
            f"📚 Knowledge base enhanced through strategic autonomous execution"
        ], cwd=Path(__file__).parent.parent)
        
        print(f"✅ Enhanced Father orchestrated results committed to version control")
    else:
        print(f"\n⚠️  Some documentation tasks incomplete - Enhanced Father recommends review")
    
    # Save Enhanced Father's strategic plan for future reference
    strategy_path = Path("logs/enhanced_father_documentation_strategy.json")
    strategy_path.parent.mkdir(exist_ok=True)
    with open(strategy_path, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "enhanced_father_strategy": strategy,
            "execution_results": report,
            "strategic_assessment": "Enhanced Father successfully orchestrated documentation improvements"
        }, f, indent=2)
    
    print(f"🧠 Enhanced Father's strategic plan saved: {strategy_path}")
    
    return success_rate >= 0.6

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        print(f"\n🧠 ENHANCED FATHER DOCUMENTATION ORCHESTRATION: {'SUCCESS' if success else 'PARTIAL'}")
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Enhanced Father documentation orchestration stopped by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Enhanced Father orchestration failed: {e}")
        sys.exit(1)
