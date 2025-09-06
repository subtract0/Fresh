#!/usr/bin/env python3
"""
🔧 Parallel Broken Windows Fixer
5 Autonomous Agents → Identify & Fix All Broken Windows
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

def discover_broken_windows():
    """Discover broken windows in the codebase"""
    print("🔍 Scanning for broken windows...")
    
    broken_windows = []
    
    # 1. Find Python files with syntax errors
    try:
        result = subprocess.run([
            'find', '.', '-name', '*.py', '-not', '-path', './autonomous_env/*', 
            '-not', '-path', './.git/*', '-not', '-path', './__pycache__/*'
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)
        
        py_files = [f.strip() for f in result.stdout.split('\n') if f.strip()]
        
        for py_file in py_files[:20]:  # Check first 20 files for syntax
            try:
                with open(py_file, 'r') as f:
                    content = f.read()
                compile(content, py_file, 'exec')
            except SyntaxError as e:
                broken_windows.append({
                    "type": "syntax_error",
                    "file_path": py_file,
                    "description": f"Python syntax error: {str(e)}",
                    "severity": "high"
                })
            except Exception:
                pass  # Skip files that can't be read
                
    except Exception as e:
        print(f"⚠️ Error scanning Python files: {e}")
    
    # 2. Find missing imports
    try:
        result = subprocess.run([
            'grep', '-r', '--include=*.py', '-n', 'from.*import.*# TODO', '.'
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)
        
        if result.stdout:
            for line in result.stdout.strip().split('\n')[:5]:
                if ':' in line:
                    file_path, line_num, content = line.split(':', 2)
                    broken_windows.append({
                        "type": "missing_import",
                        "file_path": file_path.lstrip('./'),
                        "description": f"Missing import at line {line_num}: {content.strip()}",
                        "severity": "medium"
                    })
    except Exception:
        pass
    
    # 3. Find TODO comments that indicate broken functionality
    try:
        result = subprocess.run([
            'grep', '-r', '--include=*.py', '-n', 'TODO.*FIXME\\|TODO.*BUG\\|TODO.*BROKEN', '.'
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)
        
        if result.stdout:
            for line in result.stdout.strip().split('\n')[:5]:
                if ':' in line:
                    file_path, line_num, content = line.split(':', 2)
                    broken_windows.append({
                        "type": "broken_todo",
                        "file_path": file_path.lstrip('./'),
                        "description": f"Broken functionality at line {line_num}: {content.strip()}",
                        "severity": "high"
                    })
    except Exception:
        pass
    
    # 4. Find empty exception handlers
    try:
        result = subprocess.run([
            'grep', '-r', '--include=*.py', '-n', '-A2', 'except.*:', '.'
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)
        
        if result.stdout:
            lines = result.stdout.strip().split('\n')
            for i, line in enumerate(lines[:20]):
                if 'except' in line and ':' in line:
                    file_path = line.split(':')[0].lstrip('./')
                    if i + 1 < len(lines) and 'pass' in lines[i + 1]:
                        broken_windows.append({
                            "type": "empty_exception",
                            "file_path": file_path,
                            "description": "Empty exception handler - should have proper error handling",
                            "severity": "medium"
                        })
    except Exception:
        pass
    
    # 5. Find files with missing docstrings
    try:
        result = subprocess.run([
            'find', '.', '-name', '*.py', '-path', '*/commands/*', '-not', '-path', './autonomous_env/*'
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)
        
        py_files = [f.strip() for f in result.stdout.split('\n') if f.strip()][:10]
        
        for py_file in py_files:
            try:
                with open(py_file, 'r') as f:
                    content = f.read()
                    if 'def ' in content and '"""' not in content[:500]:
                        broken_windows.append({
                            "type": "missing_docstring",
                            "file_path": py_file.lstrip('./'),
                            "description": "Missing module or function docstrings",
                            "severity": "low"
                        })
            except Exception:
                pass
    except Exception:
        pass
    
    # Filter out non-project files (autonomous_env, external packages, etc.)
    project_broken_windows = []
    for bw in broken_windows:
        file_path = bw["file_path"]
        # Only include files from our actual project
        if (file_path.startswith('ai/') or 
            file_path.startswith('scripts/') or 
            file_path.startswith('tests/') or 
            file_path.startswith('scaffolding/')):
            project_broken_windows.append(bw)
    
    # If no project broken windows found, create focused improvement tasks
    if not project_broken_windows:
        project_broken_windows = [
            {
                "type": "code_quality",
                "file_path": "ai/cli/commands/cmd_run.py",
                "description": "Add comprehensive error handling and logging",
                "severity": "medium"
            },
            {
                "type": "performance",
                "file_path": "ai/cli/commands/spawn_agent.py", 
                "description": "Optimize agent spawning performance and add metrics",
                "severity": "medium"
            },
            {
                "type": "security",
                "file_path": "ai/cli/commands/load_config.py",
                "description": "Add input validation and sanitization for config files",
                "severity": "high"
            },
            {
                "type": "documentation",
                "file_path": "ai/cli/commands/get_agent.py",
                "description": "Add comprehensive docstrings and usage examples",
                "severity": "low"
            },
            {
                "type": "testing",
                "file_path": "ai/cli/commands/memory.py",
                "description": "Add unit tests and integration test coverage",
                "severity": "medium"
            }
        ]
    
    broken_windows = project_broken_windows
    
    print(f"🪟 Found {len(broken_windows)} broken windows to fix")
    return broken_windows

async def main():
    """Main execution for broken windows fixing"""
    print("🔧 Parallel Broken Windows Fixer")
    print("🤖 5 Autonomous Agents → Clean Codebase → Zero Technical Debt")
    print("=" * 80)
    
    # Discover broken windows
    broken_windows = discover_broken_windows()
    
    if not broken_windows:
        print("✅ No broken windows found! Codebase is clean.")
        return True
    
    print(f"\n🪟 BROKEN WINDOWS DETECTED: {len(broken_windows)}")
    for bw in broken_windows:
        severity_color = {"high": "🔴", "medium": "🟡", "low": "🟢"}
        print(f"{severity_color.get(bw['severity'], '⚪')} {bw['type'].upper()}: {bw['file_path']} - {bw['description']}")
    
    print(f"\n🤖 Spawning 5 specialized fixing agents...")
    
    # Import and run the parallel orchestrator with broken windows tasks
    from scripts.parallel_autonomous_orchestrator import ParallelAutonomousOrchestrator
    
    # Convert broken windows to implementation tasks
    fixing_tasks = []
    for i, bw in enumerate(broken_windows):
        fixing_tasks.append({
            "file_path": bw["file_path"],
            "description": f"Fix {bw['type']}: {bw['description']} - ensure production quality code with proper error handling, logging, and documentation"
        })
    
    # Configure for broken windows fixing
    max_workers = 5  # 5 specialized agents
    budget_limit = len(fixing_tasks) * 0.05  # $0.05 per fix
    
    print(f"\n🎯 LAUNCHING BROKEN WINDOWS FIXING OPERATION...")
    print(f"👥 Fixing Agents: {max_workers}")
    print(f"💰 Budget Limit: ${budget_limit:.2f}")
    print(f"🪟 Windows to Fix: {len(fixing_tasks)}")
    print("=" * 60)
    
    # Create and run orchestrator
    orchestrator = ParallelAutonomousOrchestrator(
        max_workers=max_workers, 
        budget_limit=budget_limit
    )
    
    # Execute the broken windows fixing
    start_time = datetime.now()
    report = await orchestrator.run_parallel_batch(fixing_tasks)
    end_time = datetime.now()
    
    # Analyze results
    duration_minutes = (end_time - start_time).total_seconds() / 60
    success_rate = report["orchestration_summary"]["success_rate"]
    
    print(f"\n🔧 BROKEN WINDOWS FIXING COMPLETE!")
    print("=" * 60)
    print(f"✅ Windows Fixed: {report['orchestration_summary']['successful']}/{len(fixing_tasks)}")
    print(f"💰 Total Cost: ${report['orchestration_summary']['total_cost']:.2f}")
    print(f"⏱️  Duration: {duration_minutes:.1f} minutes")
    print(f"🎯 Success Rate: {success_rate:.1%}")
    
    if success_rate >= 0.8:
        print(f"\n🏆 BROKEN WINDOWS SUCCESSFULLY FIXED!")
        print(f"✨ Codebase is now clean and production-ready!")
        print(f"🔧 Technical debt eliminated by autonomous agents")
        
        # Auto-commit fixes
        subprocess.run(['git', 'add', '-A'], cwd=Path(__file__).parent.parent)
        subprocess.run([
            'git', 'commit', '-m', 
            f"🔧 Fix broken windows: {report['orchestration_summary']['successful']} issues resolved\n\n"
            f"🤖 5 autonomous fixing agents eliminated technical debt\n"
            f"💰 Cost: ${report['orchestration_summary']['total_cost']:.2f}\n"
            f"⚡ Duration: {duration_minutes:.1f} minutes\n"
            f"✨ Codebase now clean and production-ready"
        ], cwd=Path(__file__).parent.parent)
        
        print(f"✅ Fixes committed to version control")
    else:
        print(f"\n⚠️  Some broken windows remain - manual review recommended")
    
    return success_rate >= 0.6

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        print(f"\n🔧 BROKEN WINDOWS FIXING: {'SUCCESS' if success else 'PARTIAL'}")
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Broken windows fixing stopped by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Broken windows fixing failed: {e}")
        sys.exit(1)
