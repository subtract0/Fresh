#!/usr/bin/env python3
"""
Comprehensive codebase bloat diagnostic scanner for Fresh AI.

This script analyzes the codebase to identify potential bloat including:
- Large files and directories
- Duplicate code patterns
- Unused/orphaned files
- Excessive dependencies
- Large binary files
- Dead code and imports

Usage:
    python scripts/diagnostic_scan.py [--output docs/_generated/diagnostic_report.md]
"""

import os
import sys
import hashlib
import ast
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any
from dataclasses import dataclass, field
from collections import defaultdict, Counter
import json
import argparse


@dataclass
class FileAnalysis:
    """Analysis of a single file."""
    path: str
    size_bytes: int
    line_count: int
    file_type: str
    issues: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DuplicateGroup:
    """Group of files with similar/duplicate content."""
    similarity: float
    files: List[str]
    content_hash: str
    line_count: int


class CodebaseDiagnostic:
    """Comprehensive codebase bloat analyzer."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.file_analyses: List[FileAnalysis] = []
        self.size_issues: List[Tuple[str, int, str]] = []
        self.duplicates: List[DuplicateGroup] = []
        self.unused_files: List[str] = []
        self.bloat_score = 0.0
        
        # Configuration
        self.large_file_threshold = 100 * 1024  # 100KB
        self.large_line_threshold = 1000  # 1000 lines
        self.binary_extensions = {'.pyc', '.pyo', '.so', '.dylib', '.dll', '.exe', '.bin', '.dat'}
        self.excluded_paths = {
            '__pycache__', '.git', '.pytest_cache', 'node_modules', 
            'venv', '.venv', 'env', 'autonomous_env', 'build', 'dist'
        }

    def run_diagnostic(self) -> Dict[str, Any]:
        """Run the complete diagnostic analysis."""
        print("🔍 Starting comprehensive codebase diagnostic scan...")
        
        # Phase 1: File analysis
        self.analyze_all_files()
        
        # Phase 2: Size analysis
        self.analyze_file_sizes()
        
        # Phase 3: Duplicate detection
        self.detect_duplicates()
        
        # Phase 4: Unused file detection
        self.detect_unused_files()
        
        # Phase 5: Dependency analysis
        dependency_analysis = self.analyze_dependencies()
        
        # Phase 6: Calculate bloat score
        self.calculate_bloat_score()
        
        # Generate report
        report = self.generate_report(dependency_analysis)
        
        print(f"✅ Diagnostic complete. Bloat score: {self.bloat_score:.1f}/10")
        
        return report

    def analyze_all_files(self):
        """Analyze all files in the repository."""
        print("📁 Analyzing all files...")
        
        total_files = 0
        for file_path in self.repo_root.rglob('*'):
            if file_path.is_file() and not self._is_excluded_path(file_path):
                analysis = self._analyze_single_file(file_path)
                if analysis:
                    self.file_analyses.append(analysis)
                total_files += 1
        
        print(f"   📄 Analyzed {len(self.file_analyses)} files")

    def _is_excluded_path(self, path: Path) -> bool:
        """Check if path should be excluded from analysis."""
        return any(excluded in str(path) for excluded in self.excluded_paths)

    def _analyze_single_file(self, file_path: Path) -> FileAnalysis:
        """Analyze a single file for potential issues."""
        try:
            rel_path = str(file_path.relative_to(self.repo_root))
            size_bytes = file_path.stat().st_size
            
            # Determine file type
            suffix = file_path.suffix.lower()
            if suffix == '.py':
                file_type = 'python'
            elif suffix in {'.md', '.txt', '.rst'}:
                file_type = 'documentation'
            elif suffix in {'.json', '.yaml', '.yml', '.toml', '.ini', '.cfg'}:
                file_type = 'config'
            elif suffix in self.binary_extensions:
                file_type = 'binary'
            else:
                file_type = 'other'
            
            # Count lines for text files
            line_count = 0
            issues = []
            metadata = {}
            
            if file_type != 'binary':
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        line_count = len(content.splitlines())
                        
                    # Analyze content for issues
                    if file_type == 'python':
                        py_issues, py_metadata = self._analyze_python_file(file_path, content)
                        issues.extend(py_issues)
                        metadata.update(py_metadata)
                    
                except UnicodeDecodeError:
                    issues.append("encoding_issue")
                    file_type = 'binary'
            
            # Check for size issues
            if size_bytes > self.large_file_threshold:
                issues.append("large_file")
            
            if line_count > self.large_line_threshold:
                issues.append("many_lines")
            
            return FileAnalysis(
                path=rel_path,
                size_bytes=size_bytes,
                line_count=line_count,
                file_type=file_type,
                issues=issues,
                metadata=metadata
            )
            
        except Exception as e:
            print(f"⚠️  Error analyzing {file_path}: {e}")
            return None

    def _analyze_python_file(self, file_path: Path, content: str) -> Tuple[List[str], Dict[str, Any]]:
        """Analyze Python file for specific issues."""
        issues = []
        metadata = {}
        
        try:
            tree = ast.parse(content)
            
            # Count different types of nodes
            imports = []
            functions = []
            classes = []
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        imports.extend([alias.name for alias in node.names])
                    else:
                        imports.append(node.module or 'relative_import')
                elif isinstance(node, ast.FunctionDef):
                    functions.append(node.name)
                elif isinstance(node, ast.ClassDef):
                    classes.append(node.name)
            
            metadata['imports'] = imports
            metadata['functions'] = functions
            metadata['classes'] = classes
            metadata['import_count'] = len(imports)
            metadata['function_count'] = len(functions)
            metadata['class_count'] = len(classes)
            
            # Check for potential issues
            if len(imports) > 20:
                issues.append("many_imports")
            
            if len(functions) > 50:
                issues.append("many_functions")
            
            # Check for long lines
            long_lines = [i for i, line in enumerate(content.splitlines(), 1) 
                         if len(line) > 120]
            if len(long_lines) > 10:
                issues.append("long_lines")
                metadata['long_lines_count'] = len(long_lines)
            
            # Check for potential dead code (functions starting with _test or _old)
            dead_code_patterns = [
                r'def _test_', r'def test_.*_old', r'def _old_', r'def deprecated_',
                r'class.*Test.*Old', r'class Old.*', r'# TODO.*remove'
            ]
            
            for pattern in dead_code_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    issues.append("potential_dead_code")
                    break
            
        except SyntaxError:
            issues.append("syntax_error")
        
        return issues, metadata

    def analyze_file_sizes(self):
        """Analyze file sizes to identify large files and directories."""
        print("📊 Analyzing file sizes...")
        
        # Sort files by size
        large_files = [
            (analysis.path, analysis.size_bytes, analysis.file_type)
            for analysis in self.file_analyses
            if analysis.size_bytes > self.large_file_threshold
        ]
        
        self.size_issues = sorted(large_files, key=lambda x: x[1], reverse=True)
        
        # Analyze directory sizes
        dir_sizes = defaultdict(int)
        for analysis in self.file_analyses:
            dir_path = str(Path(analysis.path).parent)
            dir_sizes[dir_path] += analysis.size_bytes
        
        large_dirs = [(path, size) for path, size in dir_sizes.items() 
                     if size > 1024 * 1024]  # > 1MB
        self.large_directories = sorted(large_dirs, key=lambda x: x[1], reverse=True)
        
        print(f"   📈 Found {len(self.size_issues)} large files")
        print(f"   📂 Found {len(self.large_directories)} large directories")

    def detect_duplicates(self):
        """Detect duplicate or very similar files."""
        print("🔍 Detecting duplicate content...")
        
        # Group files by content hash (for exact duplicates)
        content_hashes = defaultdict(list)
        
        # Group similar files by normalized content (for near-duplicates)
        normalized_hashes = defaultdict(list)
        
        for analysis in self.file_analyses:
            if analysis.file_type in ['python', 'documentation']:
                try:
                    file_path = self.repo_root / analysis.path
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Exact content hash
                    content_hash = hashlib.md5(content.encode()).hexdigest()
                    content_hashes[content_hash].append(analysis.path)
                    
                    # Normalized content (remove whitespace, comments for similarity)
                    normalized = self._normalize_content(content, analysis.file_type)
                    norm_hash = hashlib.md5(normalized.encode()).hexdigest()
                    normalized_hashes[norm_hash].append((analysis.path, len(content.splitlines())))
                    
                except Exception:
                    continue
        
        # Find exact duplicates
        for content_hash, files in content_hashes.items():
            if len(files) > 1:
                # Get line count from first file
                first_file_analysis = next(
                    a for a in self.file_analyses if a.path == files[0]
                )
                self.duplicates.append(DuplicateGroup(
                    similarity=1.0,
                    files=files,
                    content_hash=content_hash,
                    line_count=first_file_analysis.line_count
                ))
        
        # Find near-duplicates
        for norm_hash, file_data in normalized_hashes.items():
            if len(file_data) > 1:
                files = [fd[0] for fd in file_data]
                avg_lines = sum(fd[1] for fd in file_data) // len(file_data)
                
                # Only flag as near-duplicate if not already an exact duplicate
                if not any(set(files).issubset(set(dup.files)) for dup in self.duplicates):
                    self.duplicates.append(DuplicateGroup(
                        similarity=0.8,  # Estimated similarity
                        files=files,
                        content_hash=norm_hash,
                        line_count=avg_lines
                    ))
        
        print(f"   🔄 Found {len(self.duplicates)} duplicate/similar groups")

    def _normalize_content(self, content: str, file_type: str) -> str:
        """Normalize content for similarity comparison."""
        if file_type == 'python':
            # Remove comments and normalize whitespace
            lines = []
            for line in content.splitlines():
                # Remove comments
                if '#' in line and not line.strip().startswith('#'):
                    line = line.split('#')[0]
                # Normalize whitespace
                line = re.sub(r'\s+', ' ', line.strip())
                if line:
                    lines.append(line)
            return '\n'.join(lines)
        else:
            # For other files, just normalize whitespace
            return re.sub(r'\s+', ' ', content.strip())

    def detect_unused_files(self):
        """Detect potentially unused files."""
        print("🗑️  Detecting unused files...")
        
        # Simple heuristics for unused files
        python_files = [a for a in self.file_analyses if a.file_type == 'python']
        all_imports = set()
        
        # Collect all imports
        for analysis in python_files:
            imports = analysis.metadata.get('imports', [])
            all_imports.update(imports)
        
        # Check for Python files that are never imported
        for analysis in python_files:
            file_module = Path(analysis.path).stem
            
            # Skip certain files that are typically not imported
            if file_module in ['__init__', '__main__', 'main', 'app', 'cli']:
                continue
            
            # Skip test files
            if 'test' in analysis.path.lower():
                continue
                
            # Check if this module is imported anywhere
            is_imported = any(
                file_module in imp or analysis.path.replace('/', '.').replace('.py', '') in imp
                for imp in all_imports
            )
            
            if not is_imported:
                self.unused_files.append(analysis.path)
        
        print(f"   🗑️  Found {len(self.unused_files)} potentially unused files")

    def analyze_dependencies(self) -> Dict[str, Any]:
        """Analyze project dependencies for bloat."""
        print("📦 Analyzing dependencies...")
        
        dep_analysis = {
            'poetry_deps': [],
            'import_usage': Counter(),
            'unused_deps': [],
            'heavy_deps': []
        }
        
        # Read pyproject.toml for declared dependencies
        pyproject_path = self.repo_root / 'pyproject.toml'
        if pyproject_path.exists():
            try:
                import toml
                with open(pyproject_path, 'r') as f:
                    pyproject = toml.load(f)
                
                deps = pyproject.get('tool', {}).get('poetry', {}).get('dependencies', {})
                dep_analysis['poetry_deps'] = list(deps.keys())
                
                # Identify potentially heavy dependencies
                heavy_patterns = [
                    'tensorflow', 'torch', 'numpy', 'pandas', 'scipy', 
                    'matplotlib', 'jupyter', 'notebook', 'django', 'flask'
                ]
                
                for dep in deps.keys():
                    if any(pattern in dep.lower() for pattern in heavy_patterns):
                        dep_analysis['heavy_deps'].append(dep)
                        
            except Exception as e:
                print(f"⚠️  Could not parse pyproject.toml: {e}")
        
        # Count actual import usage
        for analysis in self.file_analyses:
            if analysis.file_type == 'python':
                imports = analysis.metadata.get('imports', [])
                for imp in imports:
                    # Extract root package name
                    root_pkg = imp.split('.')[0] if imp else ''
                    if root_pkg:
                        dep_analysis['import_usage'][root_pkg] += 1
        
        return dep_analysis

    def calculate_bloat_score(self):
        """Calculate overall bloat score (0-10, where 10 is very bloated)."""
        score = 0.0
        
        # File size bloat (0-3 points)
        total_size = sum(a.size_bytes for a in self.file_analyses)
        size_score = min(3.0, (total_size / (10 * 1024 * 1024)) * 3)  # 10MB = 3 points
        score += size_score
        
        # Large file count (0-2 points)
        large_file_ratio = len(self.size_issues) / max(len(self.file_analyses), 1)
        large_file_score = min(2.0, large_file_ratio * 10)
        score += large_file_score
        
        # Duplicate content (0-2 points)
        if self.duplicates:
            dup_files = sum(len(dup.files) for dup in self.duplicates)
            dup_ratio = dup_files / max(len(self.file_analyses), 1)
            dup_score = min(2.0, dup_ratio * 20)
            score += dup_score
        
        # Unused files (0-2 points)
        unused_ratio = len(self.unused_files) / max(len(self.file_analyses), 1)
        unused_score = min(2.0, unused_ratio * 20)
        score += unused_score
        
        # Complex files (0-1 point)
        complex_files = [a for a in self.file_analyses if 'many_functions' in a.issues or 'many_imports' in a.issues]
        complex_ratio = len(complex_files) / max(len(self.file_analyses), 1)
        complex_score = min(1.0, complex_ratio * 10)
        score += complex_score
        
        self.bloat_score = min(10.0, score)

    def generate_report(self, dependency_analysis: Dict[str, Any]) -> str:
        """Generate a comprehensive diagnostic report."""
        report = []
        
        # Header
        report.append("# 🔍 Codebase Bloat Diagnostic Report")
        report.append("")
        report.append(f"**Generated**: {self._get_timestamp()}")
        report.append(f"**Repository**: {self.repo_root.name}")
        report.append(f"**Bloat Score**: {self.bloat_score:.1f}/10.0")
        report.append("")
        
        # Health status
        if self.bloat_score < 3:
            report.append("## ✅ Overall Health: EXCELLENT")
            report.append("The codebase is lean and well-maintained with minimal bloat.")
        elif self.bloat_score < 6:
            report.append("## ⚠️ Overall Health: GOOD")
            report.append("Some areas for improvement identified, but overall manageable.")
        elif self.bloat_score < 8:
            report.append("## 🔶 Overall Health: NEEDS ATTENTION")
            report.append("Several bloat issues found that should be addressed.")
        else:
            report.append("## ❌ Overall Health: CRITICAL")
            report.append("Significant bloat issues requiring immediate attention.")
        
        report.append("")
        report.append("---")
        report.append("")
        
        # Summary statistics
        total_size = sum(a.size_bytes for a in self.file_analyses)
        total_lines = sum(a.line_count for a in self.file_analyses)
        
        report.append("## 📊 Summary Statistics")
        report.append("")
        report.append(f"- **Total Files**: {len(self.file_analyses)}")
        report.append(f"- **Total Size**: {self._format_bytes(total_size)}")
        report.append(f"- **Total Lines**: {total_lines:,}")
        report.append(f"- **Average File Size**: {self._format_bytes(total_size // max(len(self.file_analyses), 1))}")
        report.append("")
        
        # File type breakdown
        type_counts = Counter(a.file_type for a in self.file_analyses)
        type_sizes = defaultdict(int)
        for analysis in self.file_analyses:
            type_sizes[analysis.file_type] += analysis.size_bytes
        
        report.append("### File Type Breakdown")
        report.append("")
        for file_type, count in type_counts.most_common():
            size = self._format_bytes(type_sizes[file_type])
            report.append(f"- **{file_type.title()}**: {count} files, {size}")
        report.append("")
        
        # Large files section
        if self.size_issues:
            report.append("## 📈 Large Files")
            report.append("")
            report.append("Files larger than 100KB:")
            report.append("")
            
            for file_path, size_bytes, file_type in self.size_issues[:10]:
                size_str = self._format_bytes(size_bytes)
                report.append(f"### {file_path}")
                report.append(f"**Size**: {size_str} | **Type**: {file_type}")
                
                # Add specific recommendations
                if size_bytes > 1024 * 1024:  # > 1MB
                    report.append("**⚠️ CRITICAL**: Very large file - consider splitting or optimizing")
                elif size_bytes > 500 * 1024:  # > 500KB
                    report.append("**🔶 WARNING**: Large file - review for optimization opportunities")
                
                report.append("")
            
            if len(self.size_issues) > 10:
                report.append(f"*... and {len(self.size_issues) - 10} more large files*")
                report.append("")
        
        # Large directories
        if hasattr(self, 'large_directories') and self.large_directories:
            report.append("## 📂 Large Directories")
            report.append("")
            
            for dir_path, size_bytes in self.large_directories[:5]:
                size_str = self._format_bytes(size_bytes)
                report.append(f"- **{dir_path}**: {size_str}")
            report.append("")
        
        # Duplicates section
        if self.duplicates:
            report.append("## 🔄 Duplicate Content")
            report.append("")
            
            total_wasted_lines = 0
            for dup_group in self.duplicates:
                similarity_str = "Exact" if dup_group.similarity == 1.0 else f"{dup_group.similarity:.0%}"
                report.append(f"### {similarity_str} Match Group ({len(dup_group.files)} files)")
                report.append(f"**Lines per file**: ~{dup_group.line_count}")
                report.append(f"**Estimated wasted lines**: {dup_group.line_count * (len(dup_group.files) - 1)}")
                report.append("")
                report.append("**Files**:")
                for file_path in dup_group.files:
                    report.append(f"- `{file_path}`")
                report.append("")
                
                total_wasted_lines += dup_group.line_count * (len(dup_group.files) - 1)
            
            report.append(f"**Total Estimated Wasted Lines**: {total_wasted_lines:,}")
            report.append("")
        
        # Unused files section
        if self.unused_files:
            report.append("## 🗑️ Potentially Unused Files")
            report.append("")
            report.append("Files that appear to be unused (not imported by other modules):")
            report.append("")
            
            for file_path in self.unused_files[:20]:
                file_analysis = next(a for a in self.file_analyses if a.path == file_path)
                size_str = self._format_bytes(file_analysis.size_bytes)
                report.append(f"- `{file_path}` ({size_str})")
            
            if len(self.unused_files) > 20:
                report.append(f"- *... and {len(self.unused_files) - 20} more*")
            
            report.append("")
        
        # Code quality issues
        quality_issues = defaultdict(list)
        for analysis in self.file_analyses:
            for issue in analysis.issues:
                quality_issues[issue].append(analysis.path)
        
        if quality_issues:
            report.append("## ⚠️ Code Quality Issues")
            report.append("")
            
            issue_descriptions = {
                'many_imports': 'Files with excessive imports (>20)',
                'many_functions': 'Files with many functions (>50)',
                'long_lines': 'Files with many long lines (>120 chars)',
                'potential_dead_code': 'Files with potential dead code',
                'syntax_error': 'Files with syntax errors',
                'encoding_issue': 'Files with encoding problems'
            }
            
            for issue, files in quality_issues.items():
                if issue in issue_descriptions:
                    report.append(f"### {issue_descriptions[issue]}")
                    report.append(f"**Count**: {len(files)} files")
                    report.append("")
                    
                    for file_path in files[:5]:
                        report.append(f"- `{file_path}`")
                    
                    if len(files) > 5:
                        report.append(f"- *... and {len(files) - 5} more*")
                    
                    report.append("")
        
        # Dependencies analysis
        report.append("## 📦 Dependencies Analysis")
        report.append("")
        
        if dependency_analysis['poetry_deps']:
            report.append(f"**Total Dependencies**: {len(dependency_analysis['poetry_deps'])}")
            
            if dependency_analysis['heavy_deps']:
                report.append(f"**Heavy Dependencies**: {', '.join(dependency_analysis['heavy_deps'])}")
            
            # Most used imports
            if dependency_analysis['import_usage']:
                report.append("")
                report.append("**Most Used Imports**:")
                for pkg, count in dependency_analysis['import_usage'].most_common(10):
                    report.append(f"- `{pkg}`: {count} imports")
        
        report.append("")
        
        # Recommendations
        report.append("## 💡 Recommendations")
        report.append("")
        
        recommendations = []
        
        if len(self.size_issues) > 5:
            recommendations.append("**Large Files**: Review and split large files (>100KB) into smaller, focused modules")
        
        if self.duplicates:
            recommendations.append("**Duplicates**: Consolidate duplicate code into shared utilities or base classes")
        
        if len(self.unused_files) > 10:
            recommendations.append("**Unused Files**: Remove or archive files that are no longer needed")
        
        if any('many_imports' in a.issues for a in self.file_analyses):
            recommendations.append("**Import Cleanup**: Reduce excessive imports by splitting modules or using dependency injection")
        
        if any('long_lines' in a.issues for a in self.file_analyses):
            recommendations.append("**Code Formatting**: Set up automatic line length enforcement (Black, Ruff, etc.)")
        
        if dependency_analysis.get('heavy_deps'):
            recommendations.append("**Dependencies**: Review heavy dependencies - ensure they're all necessary")
        
        if not recommendations:
            recommendations.append("**Great Job!** The codebase appears to be well-maintained with minimal bloat.")
        
        for i, rec in enumerate(recommendations, 1):
            report.append(f"{i}. {rec}")
        
        report.append("")
        
        # Quick wins section
        quick_wins = []
        
        if len(self.unused_files) > 0:
            estimated_savings = sum(
                next(a.size_bytes for a in self.file_analyses if a.path == path)
                for path in self.unused_files[:10]
            )
            quick_wins.append(f"Remove {min(10, len(self.unused_files))} unused files → Save ~{self._format_bytes(estimated_savings)}")
        
        if self.duplicates:
            dup_savings = sum(dup.line_count * (len(dup.files) - 1) for dup in self.duplicates[:3])
            quick_wins.append(f"Consolidate top 3 duplicate groups → Save ~{dup_savings} lines")
        
        if quick_wins:
            report.append("## ⚡ Quick Wins")
            report.append("")
            for win in quick_wins:
                report.append(f"- {win}")
            report.append("")
        
        # Footer
        report.append("---")
        report.append("")
        report.append("*This report was generated automatically by the Fresh AI diagnostic scanner.*")
        
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
    parser = argparse.ArgumentParser(description='Run comprehensive codebase bloat diagnostic')
    parser.add_argument('--output', 
                       default='docs/_generated/diagnostic_report.md',
                       help='Output file for diagnostic report')
    parser.add_argument('--repo-root', default='.',
                       help='Repository root directory')
    
    args = parser.parse_args()
    
    repo_root = Path(args.repo_root).resolve()
    if not repo_root.exists():
        print(f"❌ Repository root does not exist: {repo_root}")
        sys.exit(1)
    
    # Run diagnostic
    diagnostic = CodebaseDiagnostic(repo_root)
    report_content = diagnostic.run_diagnostic()
    
    # Save report
    output_path = repo_root / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        f.write(report_content)
    
    print(f"📊 Diagnostic report saved to {output_path}")
    
    # Print summary to console
    print(f"\n📈 Summary:")
    print(f"   📄 Files analyzed: {len(diagnostic.file_analyses)}")
    print(f"   📈 Large files: {len(diagnostic.size_issues)}")
    print(f"   🔄 Duplicate groups: {len(diagnostic.duplicates)}")
    print(f"   🗑️  Unused files: {len(diagnostic.unused_files)}")
    print(f"   🏆 Bloat score: {diagnostic.bloat_score:.1f}/10")


if __name__ == '__main__':
    main()
