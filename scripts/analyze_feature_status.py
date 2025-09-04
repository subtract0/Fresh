#!/usr/bin/env python3
"""
Feature status analyzer - compares documentation claims with actual implementations.
Generates a truth matrix showing what's Implemented, Partial, or Missing.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple

# Feature mappings - what to look for to verify claims
FEATURE_CHECKS = {
    # Core CLI commands
    "fresh run": {
        "code_patterns": ["cmd_run", "run_development_cycle", "DevLoop"],
        "test_patterns": ["test_run", "test_dev.*cycle"],
        "status": None
    },
    "fresh spawn": {
        "code_patterns": ["cmd_spawn", "spawn_agent", "MotherAgent"],
        "test_patterns": ["test_spawn", "test_mother"],
        "status": None
    },
    "fresh scan": {
        "code_patterns": ["cmd_scan", "scan_repository"],
        "test_patterns": ["test_scan", "test_repo_scanner"],
        "status": None
    },
    
    # Memory System
    "InMemoryMemoryStore": {
        "code_patterns": ["class:InMemoryMemoryStore"],
        "test_patterns": ["test_inmemory_store", "test_memory_store"],
        "status": None
    },
    "IntelligentMemoryStore": {
        "code_patterns": ["class:IntelligentMemoryStore"],
        "test_patterns": ["test_intelligent_memory", "test_auto_classification"],
        "status": None
    },
    "FirestoreMemoryStore": {
        "code_patterns": ["class:FirestoreMemoryStore"],
        "test_patterns": ["test_firestore"],
        "env_required": ["FIREBASE_PROJECT_ID"],
        "status": None
    },
    
    # Enhanced Agents
    "EnhancedFather": {
        "code_patterns": ["class:EnhancedFather", "class:Father"],
        "test_patterns": ["test.*father", "test.*enhanced.*agent"],
        "status": None
    },
    "MotherAgent": {
        "code_patterns": ["class:MotherAgent", "spawn_agent"],
        "test_patterns": ["test_mother", "test_spawn"],
        "status": None
    },
    
    # Deployment scripts
    "./scripts/deploy.sh": {
        "file_exists": "scripts/deploy.sh",
        "executable": True,
        "status": None
    },
    "./scripts/ask.sh": {
        "file_exists": "scripts/ask.sh",
        "executable": True,
        "status": None
    },
    "./scripts/monitor.sh": {
        "file_exists": "scripts/monitor.sh",
        "status": None
    },
    
    # Telegram Bot
    "Telegram Integration": {
        "file_exists": "ai/interface/telegram_bot.py",
        "test_patterns": ["test_telegram"],
        "env_required": ["TELEGRAM_BOT_TOKEN"],
        "status": None
    },
    
    # MCP Integration
    "MCP Discovery": {
        "file_exists": "ai/integration/mcp_discovery.py",
        "test_patterns": ["test_mcp"],
        "status": None
    },
    
    # CI/CD Workflows
    "CI Tests": {
        "file_exists": ".github/workflows/ci.yml",
        "status": None
    },
    "ADR Check": {
        "file_exists": ".github/workflows/adr-check.yml",
        "status": None
    }
}

def load_inventory() -> Dict:
    """Load the generated inventory.json."""
    inventory_file = Path("docs/_generated/inventory.json")
    if not inventory_file.exists():
        raise FileNotFoundError("Run scripts/inventory_codebase.py first")
    with open(inventory_file, 'r') as f:
        return json.load(f)

def check_feature(feature_name: str, checks: Dict, inventory: Dict) -> str:
    """
    Check if a feature is Implemented, Partial, or Missing.
    Returns: 'Implemented', 'Partial', or 'Missing'
    """
    has_code = False
    has_tests = False
    file_exists = False
    is_executable = False
    
    # Check for file existence
    if "file_exists" in checks:
        file_path = Path(checks["file_exists"])
        file_exists = file_path.exists()
        if "executable" in checks and file_exists:
            is_executable = file_path.stat().st_mode & 0o111 != 0
            if checks.get("executable") and not is_executable:
                return "Partial"
        if not file_exists:
            return "Missing"
        has_code = True
    
    # Check code patterns
    if "code_patterns" in checks:
        for pattern in checks["code_patterns"]:
            # Check in agents
            for agent in inventory.get("agents", []):
                if pattern in agent["name"]:
                    has_code = True
                    break
            # Check in memory stores
            for store in inventory.get("memory_stores", []):
                if pattern in store["name"]:
                    has_code = True
                    break
            # Check in CLI commands
            for cmd in inventory.get("cli_commands", []):
                if pattern in cmd["function"]:
                    has_code = True
                    break
    
    # Check test patterns
    if "test_patterns" in checks:
        all_tests = []
        for test_file, test_funcs in inventory.get("tests", {}).items():
            all_tests.extend(test_funcs)
        
        for pattern in checks["test_patterns"]:
            pattern_re = re.compile(pattern)
            for test in all_tests:
                if pattern_re.search(test):
                    has_tests = True
                    break
    
    # Determine status
    if "file_exists" in checks:
        return "Implemented" if file_exists else "Missing"
    
    if has_code and has_tests:
        return "Implemented"
    elif has_code:
        return "Partial"  # Code exists but no tests
    else:
        return "Missing"

def generate_feature_matrix(inventory: Dict) -> List[Dict]:
    """Generate the feature status matrix."""
    results = []
    
    for feature_name, checks in FEATURE_CHECKS.items():
        status = check_feature(feature_name, checks, inventory)
        
        # Find evidence
        evidence = []
        if "file_exists" in checks and Path(checks["file_exists"]).exists():
            evidence.append(f"File: {checks['file_exists']}")
        
        if "code_patterns" in checks:
            for pattern in checks["code_patterns"]:
                for agent in inventory.get("agents", []):
                    if pattern in agent["name"]:
                        evidence.append(f"Agent: {agent['name']} in {agent['file']}")
                for store in inventory.get("memory_stores", []):
                    if pattern in store["name"]:
                        evidence.append(f"Memory: {store['name']} in {store['file']}")
                for cmd in inventory.get("cli_commands", []):
                    if pattern in cmd["function"]:
                        evidence.append(f"CLI: {cmd['command']} ({cmd['function']})")
        
        if "test_patterns" in checks:
            test_files = []
            for test_file, test_funcs in inventory.get("tests", {}).items():
                for pattern in checks["test_patterns"]:
                    pattern_re = re.compile(pattern)
                    matching_tests = [t for t in test_funcs if pattern_re.search(t)]
                    if matching_tests:
                        test_files.append(f"{test_file}: {len(matching_tests)} tests")
            if test_files:
                evidence.extend(test_files)
        
        results.append({
            "feature": feature_name,
            "status": status,
            "evidence": evidence[:3],  # Limit to 3 pieces of evidence
            "env_required": checks.get("env_required", [])
        })
    
    return results

def write_feature_status(matrix: List[Dict]):
    """Write the FEATURE_STATUS.md file."""
    output = """# Feature Status Matrix

Generated from automated codebase analysis. This is the source of truth for what's actually implemented.

Status Legend:
- ✅ **Implemented**: Code exists with tests
- ⚠️ **Partial**: Code exists but missing tests or incomplete
- ❌ **Missing**: Not implemented or not found

---

## Feature Implementation Status

| Feature | Status | Evidence | Requirements |
|---------|--------|----------|--------------|
"""
    
    # Group by status for better visibility
    implemented = [f for f in matrix if f["status"] == "Implemented"]
    partial = [f for f in matrix if f["status"] == "Partial"]
    missing = [f for f in matrix if f["status"] == "Missing"]
    
    for feature in implemented:
        evidence = "<br>".join(feature["evidence"][:2]) if feature["evidence"] else "Found"
        reqs = ", ".join(feature["env_required"]) if feature["env_required"] else "-"
        output += f"| {feature['feature']} | ✅ Implemented | {evidence} | {reqs} |\n"
    
    if partial:
        output += "| **--- Partial ---** | | | |\n"
        for feature in partial:
            evidence = "<br>".join(feature["evidence"][:2]) if feature["evidence"] else "Code only"
            reqs = ", ".join(feature["env_required"]) if feature["env_required"] else "-"
            output += f"| {feature['feature']} | ⚠️ Partial | {evidence} | {reqs} |\n"
    
    if missing:
        output += "| **--- Missing ---** | | | |\n"
        for feature in missing:
            evidence = "Not found"
            reqs = ", ".join(feature["env_required"]) if feature["env_required"] else "-"
            output += f"| {feature['feature']} | ❌ Missing | {evidence} | {reqs} |\n"
    
    output += f"""
---

## Summary

- ✅ **Implemented**: {len(implemented)} features
- ⚠️ **Partial**: {len(partial)} features  
- ❌ **Missing**: {len(missing)} features

Total: {len(matrix)} features analyzed

---

*Generated by scripts/analyze_feature_status.py*
*Last updated: {inventory['timestamp']}*
"""
    
    output_file = Path("docs/FEATURE_STATUS.md")
    output_file.parent.mkdir(exist_ok=True)
    with open(output_file, 'w') as f:
        f.write(output)
    
    print(f"✅ Feature status written to {output_file}")
    return implemented, partial, missing

def main():
    """Main analysis function."""
    print("Loading inventory...")
    inventory = load_inventory()
    
    print("Analyzing features...")
    matrix = generate_feature_matrix(inventory)
    
    print("Writing feature status...")
    implemented, partial, missing = write_feature_status(matrix)
    
    print(f"\n📊 Feature Analysis Complete:")
    print(f"  ✅ Implemented: {len(implemented)}")
    print(f"  ⚠️ Partial: {len(partial)}")
    print(f"  ❌ Missing: {len(missing)}")
    
    if missing:
        print(f"\n❌ Missing features that need attention:")
        for f in missing[:5]:
            print(f"  - {f['feature']}")

if __name__ == "__main__":
    inventory = load_inventory()
    main()
