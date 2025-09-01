#!/usr/bin/env python3
"""
Automated codebase cleanup and optimization script for Fresh AI.

This script addresses the bloat issues identified by the diagnostic scan:
- Removes unused files (after confirmation)
- Cleans up duplicate content
- Fixes common quality issues
- Optimizes large files
- Removes temporary/system files

Usage:
    python scripts/automated_cleanup.py [--dry-run] [--auto-confirm]
"""

import os
import sys
import shutil
import json
import ast
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any
from dataclasses import dataclass
from collections import defaultdict
import argparse
import hashlib
import re


@dataclass
class CleanupAction:
    """Represents a cleanup action to be performed."""
    action_type: str
    target: str
    reason: str
    size_savings: int = 0
    risk_level: str = "LOW"  # LOW, MEDIUM, HIGH
    auto_safe: bool = True


class CodebaseCleanup:
    """Automated codebase cleanup and optimization."""

    def __init__(self, repo_root: Path, dry_run: bool = False, auto_confirm: bool = False):
        self.repo_root = repo_root
        self.dry_run = dry_run
        self.auto_confirm = auto_confirm
        self.cleanup_actions: List[CleanupAction] = []
        self.total_savings = 0
        
        # Load diagnostic report if available
        self.diagnostic_data = self._load_diagnostic_report()
        
        # Common patterns for cleanup
        self.temp_patterns = {
            '*.pyc', '*.pyo', '__pycache__', '.pytest_cache',
            '.DS_Store', 'Thumbs.db', '*.tmp', '*.temp',
            '.coverage', 'htmlcov', '.mypy_cache', '.ruff_cache'
        }
        
        self.unused_file_patterns = {
            '*_old.py', '*_backup.py', '*_temp.py', '*_test_old.py',
            'temp_*.py', 'backup_*.py', 'old_*.py'
        }

    def run_cleanup(self) -> Dict[str, Any]:
        """Run the complete cleanup process."""
        print("🧹 Starting automated codebase cleanup...")
        
        if self.dry_run:
            print("   🔍 DRY RUN MODE: No changes will be made")
        
        # Phase 1: Identify cleanup actions
        self._identify_temp_files()
        self._identify_unused_files()
        self._identify_duplicates()
        self._identify_large_files()
        self._identify_quality_issues()
        
        # Phase 2: Present cleanup plan
        self._present_cleanup_plan()
        
        # Phase 3: Execute cleanup (if confirmed)
        if self._confirm_cleanup():
            executed_actions = self._execute_cleanup()
        else:
            executed_actions = []
        
        # Phase 4: Generate report
        report = self._generate_cleanup_report(executed_actions)
        
        return report

    def _load_diagnostic_report(self) -> Dict[str, Any]:
        """Load the diagnostic report if available."""
        report_path = self.repo_root / 'docs/_generated/diagnostic_report.md'
        if not report_path.exists():
            return {}
        
        # For now, we'll re-run a light diagnostic
        # In the future, we could parse the markdown report
        return {}

    def _identify_temp_files(self):
        """Identify temporary and system files for removal."""
        print("🗑️  Identifying temporary files...")
        
        temp_files = []
        for pattern in self.temp_patterns:
            temp_files.extend(self.repo_root.rglob(pattern))
        
        for temp_file in temp_files:
            if temp_file.is_file() and not self._is_excluded_path(temp_file):
                size = temp_file.stat().st_size
                self.cleanup_actions.append(CleanupAction(
                    action_type="remove_temp_file",
                    target=str(temp_file.relative_to(self.repo_root)),
                    reason="Temporary/system file",
                    size_savings=size,
                    risk_level="LOW",
                    auto_safe=True
                ))
                self.total_savings += size
        
        print(f"   📁 Found {len([a for a in self.cleanup_actions if a.action_type == 'remove_temp_file'])} temporary files")

    def _identify_unused_files(self):
        """Identify potentially unused files."""
        print("🔍 Identifying unused files...")
        
        # Get all Python files
        python_files = [f for f in self.repo_root.rglob('*.py') if not self._is_excluded_path(f)]
        all_imports = set()
        
        # Extract all imports
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, (ast.Import, ast.ImportFrom)):
                        if isinstance(node, ast.Import):
                            all_imports.update([alias.name for alias in node.names])
                        elif node.module:
                            all_imports.add(node.module)
            except:
                continue
        
        # Check for unused Python files
        for py_file in python_files:
            rel_path = py_file.relative_to(self.repo_root)
            module_name = str(rel_path).replace('/', '.').replace('.py', '')
            file_stem = py_file.stem
            
            # Skip certain files
            if file_stem in ['__init__', '__main__', 'main', 'app', 'cli', 'setup']:
                continue
            
            if 'test' in str(rel_path).lower():
                continue
            
            # Skip files that match patterns indicating they're entry points
            entry_point_patterns = [
                r'^(start_|launch_|run_|demo_|autonomous_)',
                r'(launcher|starter|main)\.py$',
                r'^scripts/',
            ]
            
            is_entry_point = any(re.search(pattern, str(rel_path)) for pattern in entry_point_patterns)
            
            # Check if imported
            is_imported = any(
                file_stem in imp or module_name in imp or str(rel_path) in imp
                for imp in all_imports
            )
            
            # Check for unused file patterns
            matches_unused_pattern = any(
                py_file.match(pattern) for pattern in self.unused_file_patterns
            )
            
            if not is_imported and (matches_unused_pattern or is_entry_point):
                size = py_file.stat().st_size
                risk = "MEDIUM" if is_entry_point else "LOW"
                
                self.cleanup_actions.append(CleanupAction(
                    action_type="remove_unused_file",
                    target=str(rel_path),
                    reason="Appears to be unused (not imported)",
                    size_savings=size,
                    risk_level=risk,
                    auto_safe=not is_entry_point
                ))
                self.total_savings += size
        
        unused_count = len([a for a in self.cleanup_actions if a.action_type == 'remove_unused_file'])
        print(f"   🗑️  Found {unused_count} potentially unused files")

    def _identify_duplicates(self):
        """Identify duplicate files for consolidation."""
        print("🔄 Identifying duplicate files...")
        
        content_hashes = defaultdict(list)
        
        # Hash content of text files
        for file_path in self.repo_root.rglob('*.py'):
            if file_path.is_file() and not self._is_excluded_path(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    content_hash = hashlib.md5(content.encode()).hexdigest()
                    content_hashes[content_hash].append(file_path)
                except:
                    continue
        
        # Find exact duplicates
        for content_hash, files in content_hashes.items():
            if len(files) > 1:
                # Keep the first file, mark others for removal
                keep_file = min(files, key=lambda f: len(str(f)))  # Keep shortest path
                
                for duplicate_file in files[1:]:
                    size = duplicate_file.stat().st_size
                    rel_path = duplicate_file.relative_to(self.repo_root)
                    
                    self.cleanup_actions.append(CleanupAction(
                        action_type="remove_duplicate",
                        target=str(rel_path),
                        reason=f"Exact duplicate of {keep_file.relative_to(self.repo_root)}",
                        size_savings=size,
                        risk_level="MEDIUM",
                        auto_safe=False
                    ))
                    self.total_savings += size
        
        dup_count = len([a for a in self.cleanup_actions if a.action_type == 'remove_duplicate'])
        print(f"   🔄 Found {dup_count} duplicate files")

    def _identify_large_files(self):
        """Identify large files that could be optimized."""
        print("📊 Identifying large files...")
        
        large_threshold = 100 * 1024  # 100KB
        
        for file_path in self.repo_root.rglob('*'):
            if file_path.is_file() and not self._is_excluded_path(file_path):
                size = file_path.stat().st_size
                
                if size > large_threshold:
                    rel_path = file_path.relative_to(self.repo_root)
                    
                    # Special handling for specific large files
                    if file_path.name == 'inventory.json':
                        # This is a generated file - we can optimize it
                        self.cleanup_actions.append(CleanupAction(
                            action_type="optimize_json",
                            target=str(rel_path),
                            reason=f"Large JSON file ({self._format_bytes(size)}) - can be minified",
                            size_savings=size // 4,  # Estimate 25% savings
                            risk_level="LOW",
                            auto_safe=True
                        ))
                    elif file_path.suffix == '.lock':
                        # Lock files are managed by package managers
                        pass
                    else:
                        # Just note the large file
                        self.cleanup_actions.append(CleanupAction(
                            action_type="note_large_file",
                            target=str(rel_path),
                            reason=f"Large file ({self._format_bytes(size)}) - manual review recommended",
                            size_savings=0,
                            risk_level="LOW",
                            auto_safe=True
                        ))
        
        large_count = len([a for a in self.cleanup_actions if 'large_file' in a.action_type])
        print(f"   📈 Found {large_count} large files")

    def _identify_quality_issues(self):
        """Identify code quality issues that can be auto-fixed."""
        print("⚠️ Identifying quality issues...")
        
        quality_fixes = 0
        
        # Check for files with syntax errors
        for py_file in self.repo_root.rglob('*.py'):
            if self._is_excluded_path(py_file):
                continue
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Try to parse
                ast.parse(content)
                
                # Check for common issues
                if len(content.splitlines()) > 1000:
                    self.cleanup_actions.append(CleanupAction(
                        action_type="note_large_module",
                        target=str(py_file.relative_to(self.repo_root)),
                        reason="Large module (>1000 lines) - consider splitting",
                        size_savings=0,
                        risk_level="LOW",
                        auto_safe=True
                    ))
                    quality_fixes += 1
                
            except SyntaxError:
                self.cleanup_actions.append(CleanupAction(
                    action_type="note_syntax_error",
                    target=str(py_file.relative_to(self.repo_root)),
                    reason="Syntax error - manual fix required",
                    size_savings=0,
                    risk_level="HIGH",
                    auto_safe=False
                ))
                quality_fixes += 1
            except:
                continue
        
        print(f"   ⚠️  Found {quality_fixes} quality issues")

    def _is_excluded_path(self, path: Path) -> bool:
        """Check if path should be excluded from analysis."""
        excluded = {
            '.git', '__pycache__', '.pytest_cache', 'node_modules', 
            'venv', '.venv', 'env', 'autonomous_env', 'build', 'dist',
            '.mypy_cache', '.ruff_cache', 'htmlcov'
        }
        return any(excluded_part in str(path) for excluded_part in excluded)

    def _present_cleanup_plan(self):
        """Present the cleanup plan to the user."""
        print("\n📋 Cleanup Plan")
        print("=" * 50)
        
        if not self.cleanup_actions:
            print("✨ No cleanup actions needed - codebase is already clean!")
            return
        
        # Group actions by type
        action_groups = defaultdict(list)
        for action in self.cleanup_actions:
            action_groups[action.action_type].append(action)
        
        total_files = len([a for a in self.cleanup_actions if a.action_type.startswith('remove')])
        print(f"📊 Total actions: {len(self.cleanup_actions)}")
        print(f"📁 Files to be processed: {total_files}")
        print(f"💾 Estimated space savings: {self._format_bytes(self.total_savings)}")
        print()
        
        # Show actions by category
        for action_type, actions in action_groups.items():
            action_name = self._get_action_name(action_type)
            print(f"### {action_name} ({len(actions)} items)")
            
            # Show a few examples
            for action in actions[:5]:
                risk_icon = "🔴" if action.risk_level == "HIGH" else "🟡" if action.risk_level == "MEDIUM" else "🟢"
                size_str = f" ({self._format_bytes(action.size_savings)})" if action.size_savings > 0 else ""
                print(f"   {risk_icon} {action.target}{size_str}")
                print(f"      → {action.reason}")
            
            if len(actions) > 5:
                print(f"   ... and {len(actions) - 5} more")
            print()

    def _get_action_name(self, action_type: str) -> str:
        """Get human-readable action name."""
        names = {
            'remove_temp_file': '🗑️ Remove Temporary Files',
            'remove_unused_file': '🗑️ Remove Unused Files',
            'remove_duplicate': '🔄 Remove Duplicates',
            'optimize_json': '📊 Optimize JSON Files',
            'note_large_file': '📈 Large Files (Review)',
            'note_large_module': '📄 Large Modules (Review)',
            'note_syntax_error': '❌ Syntax Errors (Manual Fix)'
        }
        return names.get(action_type, action_type)

    def _confirm_cleanup(self) -> bool:
        """Get user confirmation for cleanup actions."""
        if self.dry_run:
            return False
        
        if not self.cleanup_actions:
            return False
        
        if self.auto_confirm:
            # Only auto-confirm safe actions
            safe_actions = [a for a in self.cleanup_actions if a.auto_safe]
            self.cleanup_actions = safe_actions
            return True
        
        print(f"🤔 Proceed with cleanup? (y/N): ", end='')
        response = input().strip().lower()
        return response in ['y', 'yes']

    def _execute_cleanup(self) -> List[CleanupAction]:
        """Execute the cleanup actions."""
        print("\n🚀 Executing cleanup...")
        
        executed_actions = []
        
        for action in self.cleanup_actions:
            try:
                success = self._execute_single_action(action)
                if success:
                    executed_actions.append(action)
                    print(f"   ✅ {action.action_type}: {action.target}")
                else:
                    print(f"   ❌ Failed: {action.target}")
            except Exception as e:
                print(f"   ❌ Error executing {action.target}: {e}")
        
        print(f"\n✅ Cleanup complete! {len(executed_actions)} actions executed.")
        
        return executed_actions

    def _execute_single_action(self, action: CleanupAction) -> bool:
        """Execute a single cleanup action."""
        target_path = self.repo_root / action.target
        
        if action.action_type == 'remove_temp_file':
            if target_path.is_file():
                target_path.unlink()
                return True
            elif target_path.is_dir():
                shutil.rmtree(target_path)
                return True
        
        elif action.action_type == 'remove_unused_file':
            if target_path.is_file():
                target_path.unlink()
                return True
        
        elif action.action_type == 'remove_duplicate':
            if target_path.is_file():
                target_path.unlink()
                return True
        
        elif action.action_type == 'optimize_json':
            if target_path.is_file() and target_path.suffix == '.json':
                # Minify JSON
                with open(target_path, 'r') as f:
                    data = json.load(f)
                
                with open(target_path, 'w') as f:
                    json.dump(data, f, separators=(',', ':'), ensure_ascii=False)
                
                return True
        
        # Note actions don't actually do anything
        elif action.action_type.startswith('note_'):
            return True
        
        return False

    def _generate_cleanup_report(self, executed_actions: List[CleanupAction]) -> str:
        """Generate a cleanup report."""
        report = []
        
        # Header
        report.append("# 🧹 Codebase Cleanup Report")
        report.append("")
        report.append(f"**Generated**: {self._get_timestamp()}")
        report.append(f"**Repository**: {self.repo_root.name}")
        report.append(f"**Mode**: {'DRY RUN' if self.dry_run else 'EXECUTION'}")
        report.append("")
        
        if not executed_actions:
            report.append("## ✨ No Actions Performed")
            report.append("")
            if self.dry_run:
                report.append("This was a dry run - no changes were made.")
            else:
                report.append("No cleanup actions were needed or confirmed.")
            report.append("")
        else:
            # Summary
            total_savings = sum(a.size_savings for a in executed_actions)
            files_removed = len([a for a in executed_actions if a.action_type.startswith('remove')])
            
            report.append("## 📊 Summary")
            report.append("")
            report.append(f"- **Actions Executed**: {len(executed_actions)}")
            report.append(f"- **Files Removed**: {files_removed}")
            report.append(f"- **Space Saved**: {self._format_bytes(total_savings)}")
            report.append("")
            
            # Actions by category
            action_groups = defaultdict(list)
            for action in executed_actions:
                action_groups[action.action_type].append(action)
            
            report.append("## 🗂️ Actions Performed")
            report.append("")
            
            for action_type, actions in action_groups.items():
                action_name = self._get_action_name(action_type)
                total_size = sum(a.size_savings for a in actions)
                
                report.append(f"### {action_name}")
                report.append(f"**Count**: {len(actions)} items")
                if total_size > 0:
                    report.append(f"**Size Saved**: {self._format_bytes(total_size)}")
                report.append("")
                
                for action in actions[:10]:  # Show first 10
                    size_str = f" ({self._format_bytes(action.size_savings)})" if action.size_savings > 0 else ""
                    report.append(f"- `{action.target}`{size_str}")
                
                if len(actions) > 10:
                    report.append(f"- *... and {len(actions) - 10} more*")
                
                report.append("")
        
        # Recommendations
        if executed_actions:
            report.append("## 💡 Next Steps")
            report.append("")
            report.append("1. **Test the application** to ensure nothing was broken")
            report.append("2. **Review large files** noted in the report for manual optimization")
            report.append("3. **Fix syntax errors** identified during the scan")
            report.append("4. **Run tests** to verify system integrity")
            report.append("5. **Commit changes** if everything looks good")
            report.append("")
        
        # Footer
        report.append("---")
        report.append("")
        report.append("*This report was generated by the Fresh AI automated cleanup system.*")
        
        return "\n".join(report)

    def _format_bytes(self, bytes_count: int) -> str:
        """Format bytes into human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_count < 1024.0:
                return f"{bytes_count:.1f} {unit}"
            bytes_count /= 1024.0
        return f"{bytes_count:.1f} TB"

    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()


def main():
    parser = argparse.ArgumentParser(description='Automated codebase cleanup')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be done without making changes')
    parser.add_argument('--auto-confirm', action='store_true',
                       help='Automatically confirm safe operations')
    parser.add_argument('--output', 
                       default='docs/_generated/cleanup_report.md',
                       help='Output file for cleanup report')
    parser.add_argument('--repo-root', default='.',
                       help='Repository root directory')
    
    args = parser.parse_args()
    
    repo_root = Path(args.repo_root).resolve()
    if not repo_root.exists():
        print(f"❌ Repository root does not exist: {repo_root}")
        sys.exit(1)
    
    # Run cleanup
    cleanup = CodebaseCleanup(repo_root, args.dry_run, args.auto_confirm)
    report_content = cleanup.run_cleanup()
    
    # Save report
    output_path = repo_root / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        f.write(report_content)
    
    print(f"📊 Cleanup report saved to {output_path}")


if __name__ == '__main__':
    main()
