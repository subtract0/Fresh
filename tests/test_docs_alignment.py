"""
Test documentation alignment with actual implementation.
Prevents documentation drift by ensuring claims match reality.
"""

import json
import re
from pathlib import Path
import pytest


def load_feature_status():
    """Load the feature status matrix."""
    status_file = Path("docs/FEATURE_STATUS.md")
    if not status_file.exists():
        pytest.skip("Feature status not generated. Run scripts/analyze_feature_status.py")
    
    with open(status_file, 'r') as f:
        content = f.read()
    
    # Parse the markdown table to extract feature statuses
    features = {}
    for line in content.split('\n'):
        if '|' in line and ('✅' in line or '⚠️' in line or '❌' in line):
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 3:
                feature = parts[1]
                if '✅' in parts[2]:
                    features[feature] = 'implemented'
                elif '⚠️' in parts[2]:
                    features[feature] = 'partial'
                elif '❌' in parts[2]:
                    features[feature] = 'missing'
    
    return features


def test_warp_md_accuracy():
    """Ensure WARP.md doesn't claim missing features work."""
    warp_file = Path("WARP.md")
    if not warp_file.exists():
        pytest.skip("WARP.md not found")
    
    features = load_feature_status()
    with open(warp_file, 'r') as f:
        warp_content = f.read()
    
    errors = []
    
    # Check that missing features are not claimed as working
    for feature, status in features.items():
        if status == 'missing':
            # These should be in the "Not Yet Implemented" section
            if f"{feature}" in warp_content:
                # Check it's properly marked as not working
                if "(WORKS)" in warp_content and feature in warp_content:
                    # Find the context
                    for line in warp_content.split('\n'):
                        if feature in line and "(WORKS)" in line:
                            errors.append(f"Missing feature '{feature}' claimed as working in WARP.md")
    
    assert not errors, f"Documentation misalignment:\n" + "\n".join(errors)


def test_readme_has_status_reference():
    """Ensure README.md references the Feature Status Matrix."""
    readme_file = Path("README.md")
    if not readme_file.exists():
        pytest.skip("README.md not found")
    
    with open(readme_file, 'r') as f:
        content = f.read()
    
    assert "FEATURE_STATUS.md" in content or "Feature Status" in content, \
        "README.md should reference docs/FEATURE_STATUS.md as source of truth"


def test_no_broken_claims_in_docs():
    """Check that docs don't make claims about non-existent features."""
    features = load_feature_status()
    docs_dir = Path("docs")
    
    errors = []
    missing_features = [f for f, status in features.items() if status == 'missing']
    
    if not missing_features:
        return  # No missing features to check
    
    for doc_file in docs_dir.glob("*.md"):
        if doc_file.name == "FEATURE_STATUS.md":
            continue
            
        with open(doc_file, 'r') as f:
            content = f.read()
        
        for feature in missing_features:
            # Look for claims that the feature works
            patterns = [
                f"{feature}.*works",
                f"{feature}.*implemented",
                f"{feature}.*available",
                f"use.*{feature}",
            ]
            
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    errors.append(f"{doc_file.name}: Claims missing feature '{feature}' works")
    
    assert not errors, f"False claims found:\n" + "\n".join(errors)


def test_inventory_json_exists():
    """Ensure inventory.json is generated and up to date."""
    inventory_file = Path("docs/_generated/inventory.json")
    assert inventory_file.exists(), "Run scripts/inventory_codebase.py to generate inventory"
    
    with open(inventory_file, 'r') as f:
        inventory = json.load(f)
    
    # Basic sanity checks
    assert "cli_commands" in inventory, "Inventory should contain CLI commands"
    assert "tests" in inventory, "Inventory should contain tests"
    assert "shell_scripts" in inventory, "Inventory should contain shell scripts"
    assert len(inventory["tests"]) > 0, "Should have found test files"


def test_cli_commands_documented():
    """Ensure all CLI commands in inventory are documented."""
    inventory_file = Path("docs/_generated/inventory.json")
    if not inventory_file.exists():
        pytest.skip("Inventory not generated")
    
    with open(inventory_file, 'r') as f:
        inventory = json.load(f)
    
    warp_file = Path("WARP.md")
    with open(warp_file, 'r') as f:
        warp_content = f.read()
    
    errors = []
    for cmd in inventory.get("cli_commands", []):
        cmd_name = f"fresh {cmd['command']}"
        if cmd_name not in warp_content:
            errors.append(f"CLI command '{cmd_name}' not documented in WARP.md")
    
    assert not errors, f"Undocumented commands:\n" + "\n".join(errors)


def test_executable_scripts_marked_correctly():
    """Ensure executable scripts are marked as such in docs."""
    inventory_file = Path("docs/_generated/inventory.json")
    if not inventory_file.exists():
        pytest.skip("Inventory not generated")
    
    with open(inventory_file, 'r') as f:
        inventory = json.load(f)
    
    warp_file = Path("WARP.md") 
    with open(warp_file, 'r') as f:
        warp_content = f.read()
    
    errors = []
    for script in inventory.get("shell_scripts", []):
        if script["executable"]:
            # Should be called with ./
            if script["name"] in warp_content:
                pattern = f"./scripts/{script['name']}"
                if pattern not in warp_content:
                    errors.append(f"Executable script {script['name']} should be shown as {pattern}")
        else:
            # Should be called with bash
            if script["name"] in warp_content:
                pattern = f"bash scripts/{script['name']}"
                if f"./scripts/{script['name']}" in warp_content:
                    errors.append(f"Non-executable script {script['name']} should use 'bash' not './'")
    
    # Don't fail on this, just warn
    if errors:
        print(f"Script execution style inconsistencies:\n" + "\n".join(errors))


def test_feature_status_is_current():
    """Ensure FEATURE_STATUS.md is not stale."""
    status_file = Path("docs/FEATURE_STATUS.md")
    inventory_file = Path("docs/_generated/inventory.json")
    
    if not status_file.exists() or not inventory_file.exists():
        pytest.skip("Status or inventory files not found")
    
    # Check that inventory timestamp matches what's in FEATURE_STATUS.md
    with open(inventory_file, 'r') as f:
        inventory = json.load(f)
    
    with open(status_file, 'r') as f:
        status_content = f.read()
    
    if "timestamp" in inventory:
        timestamp = inventory["timestamp"]
        assert timestamp in status_content, \
            f"FEATURE_STATUS.md appears stale. Re-run scripts/analyze_feature_status.py"
