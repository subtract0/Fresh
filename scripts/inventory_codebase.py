#!/usr/bin/env python3
"""
Automated codebase inventory generator.
Scans for actual implementations and generates a JSON inventory of what exists.
"""

import json
import os
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Any

def get_python_functions(file_path: Path) -> List[Dict[str, str]]:
    """Extract function definitions from a Python file."""
    functions = []
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            # Find all function definitions
            func_pattern = r'def\s+(\w+)\s*\([^)]*\):\s*(?:"""([^"]*?)""")?'
            matches = re.findall(func_pattern, content, re.MULTILINE | re.DOTALL)
            for name, docstring in matches:
                # Handle relative path properly
                rel_path = str(file_path)
                if file_path.is_absolute():
                    try:
                        rel_path = str(file_path.relative_to(Path.cwd()))
                    except ValueError:
                        rel_path = str(file_path)
                functions.append({
                    'name': name,
                    'docstring': docstring.strip() if docstring else '',
                    'file': rel_path
                })
            
            # Find class definitions
            class_pattern = r'class\s+(\w+)[^:]*:\s*(?:"""([^"]*?)""")?'
            class_matches = re.findall(class_pattern, content, re.MULTILINE | re.DOTALL)
            for name, docstring in class_matches:
                # Handle relative path properly
                rel_path = str(file_path)
                if file_path.is_absolute():
                    try:
                        rel_path = str(file_path.relative_to(Path.cwd()))
                    except ValueError:
                        rel_path = str(file_path)
                functions.append({
                    'name': f'class:{name}',
                    'docstring': docstring.strip() if docstring else '',
                    'file': rel_path
                })
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return functions

def get_shell_scripts() -> List[Dict[str, Any]]:
    """Scan scripts directory for shell scripts."""
    scripts = []
    scripts_dir = Path('scripts')
    if scripts_dir.exists():
        for script in scripts_dir.glob('*.sh'):
            info = {'name': script.name, 'path': str(script), 'executable': os.access(script, os.X_OK)}
            # Try to extract description from first comment
            try:
                with open(script, 'r') as f:
                    lines = f.readlines()[:10]
                    for line in lines:
                        if line.startswith('#') and not line.startswith('#!'):
                            info['description'] = line[1:].strip()
                            break
            except:
                pass
            scripts.append(info)
    return scripts

def get_cli_commands() -> List[Dict[str, str]]:
    """Extract CLI commands from ai/cli/fresh.py."""
    commands = []
    cli_file = Path('ai/cli/fresh.py')
    if cli_file.exists():
        try:
            with open(cli_file, 'r') as f:
                content = f.read()
                # Find all cmd_ functions
                cmd_pattern = r'def\s+(cmd_\w+)\s*\([^)]*\):\s*(?:"""([^"]*?)""")?'
                matches = re.findall(cmd_pattern, content, re.MULTILINE | re.DOTALL)
                for name, docstring in matches:
                    cmd_name = name.replace('cmd_', '').replace('_', '-')
                    commands.append({
                        'command': cmd_name,
                        'function': name,
                        'docstring': docstring.strip() if docstring else ''
                    })
        except Exception as e:
            print(f"Error parsing CLI: {e}")
    return commands

def get_tests() -> Dict[str, List[str]]:
    """Scan for test files and extract test functions."""
    tests = {}
    test_dir = Path('tests')
    if test_dir.exists():
        for test_file in test_dir.glob('test_*.py'):
            test_functions = []
            try:
                with open(test_file, 'r') as f:
                    content = f.read()
                    # Find test functions
                    test_pattern = r'def\s+(test_\w+)\s*\('
                    matches = re.findall(test_pattern, content)
                    test_functions = matches
            except:
                pass
            if test_functions:
                # Use relative path from cwd
                rel_path = str(test_file)
                if test_file.is_absolute():
                    try:
                        rel_path = str(test_file.relative_to(Path.cwd()))
                    except ValueError:
                        rel_path = str(test_file)
                tests[rel_path] = test_functions
    return tests

def get_github_workflows() -> List[Dict[str, Any]]:
    """Scan GitHub workflows."""
    workflows = []
    workflow_dir = Path('.github/workflows')
    if workflow_dir.exists():
        for workflow in workflow_dir.glob('*.yml'):
            info = {'name': workflow.name, 'path': str(workflow)}
            try:
                with open(workflow, 'r') as f:
                    content = f.read()
                    # Extract workflow name
                    name_match = re.search(r'name:\s*(.+)', content)
                    if name_match:
                        info['workflow_name'] = name_match.group(1).strip()
                    # Check if it runs tests
                    info['runs_tests'] = 'pytest' in content or 'run-tests' in content
            except:
                pass
            workflows.append(info)
    return workflows

def get_agent_classes() -> List[Dict[str, str]]:
    """Find all agent class definitions."""
    agents = []
    # Scan ai/agents directory
    agents_dir = Path('ai/agents')
    if agents_dir.exists():
        for py_file in agents_dir.glob('*.py'):
            agents.extend([a for a in get_python_functions(py_file) if a['name'].startswith('class:')])
    return agents

def get_memory_implementations() -> List[Dict[str, str]]:
    """Find memory store implementations."""
    stores = []
    memory_dir = Path('ai/memory')
    if memory_dir.exists():
        for py_file in memory_dir.glob('*.py'):
            funcs = get_python_functions(py_file)
            stores.extend([f for f in funcs if 'Store' in f['name']])
    return stores

def check_dependencies() -> Dict[str, bool]:
    """Check which optional dependencies are available."""
    deps = {}
    try:
        import agency_swarm
        deps['agency_swarm'] = True
    except ImportError:
        deps['agency_swarm'] = False
    
    try:
        import google.cloud.firestore
        deps['google_cloud_firestore'] = True
    except ImportError:
        deps['google_cloud_firestore'] = False
    
    try:
        import openai
        deps['openai'] = True
    except ImportError:
        deps['openai'] = False
    
    return deps

def main():
    """Generate comprehensive codebase inventory."""
    inventory = {
        'timestamp': subprocess.check_output(['date', '-u', '+%Y-%m-%d %H:%M:%S UTC']).decode().strip(),
        'python_version': subprocess.check_output(['python', '--version']).decode().strip(),
        'cwd': str(Path.cwd()),
        'shell_scripts': get_shell_scripts(),
        'cli_commands': get_cli_commands(),
        'tests': get_tests(),
        'workflows': get_github_workflows(),
        'agents': get_agent_classes(),
        'memory_stores': get_memory_implementations(),
        'dependencies': check_dependencies(),
        'stats': {
            'total_python_files': len(list(Path('.').glob('**/*.py'))),
            'total_test_files': len(list(Path('tests').glob('test_*.py'))) if Path('tests').exists() else 0,
            'total_docs': len(list(Path('.').glob('**/*.md'))),
        }
    }
    
    # Write inventory
    output_file = Path('docs/_generated/inventory.json')
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(inventory, f, indent=2)
    
    print(f"✅ Inventory written to {output_file}")
    print(f"\nSummary:")
    print(f"  - Shell scripts: {len(inventory['shell_scripts'])}")
    print(f"  - CLI commands: {len(inventory['cli_commands'])}")
    print(f"  - Test files: {len(inventory['tests'])}")
    print(f"  - Workflows: {len(inventory['workflows'])}")
    print(f"  - Agent classes: {len(inventory['agents'])}")
    print(f"  - Memory stores: {len(inventory['memory_stores'])}")
    
    return inventory

if __name__ == '__main__':
    main()
