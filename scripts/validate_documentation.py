#!/usr/bin/env python3
"""
Documentation Validation Script
Validates documentation completeness, accuracy, and agent-readiness.
Designed to be run as quality gate in CI/CD pipeline.
"""

import os
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Set
from datetime import datetime
import ast
import re

class DocumentationValidator:
    def __init__(self, root_path: str = "/Users/am/Code/Fresh"):
        self.root = Path(root_path)
        self.validation_results = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'unknown',
            'score': 0.0,
            'checks': {},
            'errors': [],
            'warnings': [],
            'improvements': []
        }
        
    def validate_all(self, strict: bool = False) -> Dict:
        """Run all validation checks."""
        print("🔍 Starting comprehensive documentation validation...")
        
        checks = [
            ('manifest_exists', self._check_manifest_exists),
            ('manifest_valid', self._check_manifest_valid),
            ('agent_instructions_exist', self._check_agent_instructions_exist),
            ('readme_coverage', self._check_readme_coverage),
            ('file_headers', self._check_file_headers),
            ('link_validation', self._check_link_validation),
            ('feature_documentation', self._check_feature_documentation),
            ('api_documentation', self._check_api_documentation),
            ('examples_runnable', self._check_examples_runnable),
            ('orphan_files', self._check_orphan_files),
            ('documentation_freshness', self._check_documentation_freshness)
        ]
        
        total_score = 0
        max_score = len(checks) * 10  # Each check worth up to 10 points
        
        for check_name, check_func in checks:
            try:
                score, issues = check_func()
                self.validation_results['checks'][check_name] = {
                    'score': score,
                    'max_score': 10,
                    'status': 'pass' if score >= 7 else 'warn' if score >= 4 else 'fail',
                    'issues': issues
                }
                total_score += score
                
                if score < 4:  # Critical failure
                    self.validation_results['errors'].extend(issues)
                elif score < 7:  # Warning
                    self.validation_results['warnings'].extend(issues)
                else:  # Good, but could be better
                    self.validation_results['improvements'].extend(issues)
                    
            except Exception as e:
                self.validation_results['errors'].append(f"Check {check_name} failed: {str(e)}")
                self.validation_results['checks'][check_name] = {
                    'score': 0,
                    'max_score': 10,
                    'status': 'error',
                    'issues': [f"Check failed: {str(e)}"]
                }
        
        # Calculate overall score and status
        self.validation_results['score'] = (total_score / max_score) * 100
        
        if self.validation_results['score'] >= 85:
            self.validation_results['overall_status'] = 'excellent'
        elif self.validation_results['score'] >= 70:
            self.validation_results['overall_status'] = 'good'
        elif self.validation_results['score'] >= 50:
            self.validation_results['overall_status'] = 'needs_improvement'
        else:
            self.validation_results['overall_status'] = 'poor'
            
        # In strict mode, fail if score is below 70
        if strict and self.validation_results['score'] < 70:
            self.validation_results['overall_status'] = 'failed_strict'
            
        return self.validation_results
        
    def _check_manifest_exists(self) -> Tuple[int, List[str]]:
        """Check if documentation manifest exists."""
        manifest_path = self.root / '.documentation' / 'manifest.json'
        
        if not manifest_path.exists():
            return 0, ["Documentation manifest (.documentation/manifest.json) does not exist"]
            
        return 10, []
        
    def _check_manifest_valid(self) -> Tuple[int, List[str]]:
        """Check if manifest is valid JSON with required structure."""
        manifest_path = self.root / '.documentation' / 'manifest.json'
        issues = []
        
        if not manifest_path.exists():
            return 0, ["Manifest does not exist"]
            
        try:
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
                
            required_keys = ['version', 'project', 'features', 'agent_instructions']
            missing_keys = [key for key in required_keys if key not in manifest]
            
            if missing_keys:
                issues.extend([f"Missing required key: {key}" for key in missing_keys])
                
            # Check feature structure
            if 'features' in manifest:
                for feature_name, feature_info in manifest['features'].items():
                    required_feature_keys = ['path', 'type', 'status', 'purpose']
                    missing_feature_keys = [key for key in required_feature_keys if key not in feature_info]
                    if missing_feature_keys:
                        issues.append(f"Feature {feature_name} missing keys: {missing_feature_keys}")
                        
            score = max(0, 10 - len(issues) * 2)
            return score, issues
            
        except json.JSONDecodeError as e:
            return 0, [f"Invalid JSON in manifest: {str(e)}"]
            
    def _check_agent_instructions_exist(self) -> Tuple[int, List[str]]:
        """Check if agent instructions file exists and is comprehensive."""
        instructions_path = self.root / '.agent-instructions.md'
        
        if not instructions_path.exists():
            return 0, ["Agent instructions file (.agent-instructions.md) does not exist"]
            
        try:
            content = instructions_path.read_text()
            
            required_sections = [
                'Understanding This Codebase',
                'Making Changes', 
                'Documentation Standards',
                'Memory System Integration',
                'Quality Gates'
            ]
            
            missing_sections = []
            for section in required_sections:
                if section.lower() not in content.lower():
                    missing_sections.append(section)
                    
            if missing_sections:
                score = max(3, 10 - len(missing_sections) * 2)
                return score, [f"Missing section: {section}" for section in missing_sections]
                
            # Check for code examples
            if '```' not in content:
                return 7, ["No code examples found in agent instructions"]
                
            return 10, []
            
        except Exception as e:
            return 0, [f"Error reading agent instructions: {str(e)}"]
            
    def _check_readme_coverage(self) -> Tuple[int, List[str]]:
        """Check README coverage for feature directories."""
        feature_dirs = [
            'ai/memory', 'ai/agents', 'ai/tools', 'ai/cli', 'ai/interface',
            'ai/integration', 'ai/loop', 'ai/monitor', 'ai/workflows',
            'ai/autonomous', 'ai/services', 'ai/system'
        ]
        
        missing_readmes = []
        incomplete_readmes = []
        
        for feature_dir in feature_dirs:
            dir_path = self.root / feature_dir
            if not dir_path.exists():
                continue
                
            readme_path = dir_path / 'README.md'
            if not readme_path.exists():
                missing_readmes.append(feature_dir)
            else:
                # Check README quality
                try:
                    content = readme_path.read_text()
                    required_sections = ['Purpose', 'Components', 'Usage', 'Dependencies', 'Testing']
                    missing_sections = [section for section in required_sections 
                                      if section.lower() not in content.lower()]
                    if missing_sections:
                        incomplete_readmes.append(f"{feature_dir}: missing {missing_sections}")
                except Exception as e:
                    incomplete_readmes.append(f"{feature_dir}: error reading README - {str(e)}")
        
        issues = []
        if missing_readmes:
            issues.extend([f"Missing README: {dir}" for dir in missing_readmes])
        if incomplete_readmes:
            issues.extend(incomplete_readmes)
            
        total_features = len([d for d in feature_dirs if (self.root / d).exists()])
        missing_count = len(missing_readmes) + len(incomplete_readmes)
        
        if total_features == 0:
            return 0, ["No feature directories found"]
            
        coverage_ratio = (total_features - missing_count) / total_features
        score = int(coverage_ratio * 10)
        
        return score, issues
        
    def _check_file_headers(self) -> Tuple[int, List[str]]:
        """Check file header documentation coverage."""
        python_files = list(self.root.rglob('*.py'))
        python_files = [f for f in python_files if not self._should_skip_file(f)]
        
        if not python_files:
            return 0, ["No Python files found"]
            
        missing_headers = []
        incomplete_headers = []
        
        for py_file in python_files:
            try:
                content = py_file.read_text(encoding='utf-8')
                rel_path = str(py_file.relative_to(self.root))
                
                if not self._has_file_header(content):
                    missing_headers.append(rel_path)
                elif not self._has_complete_header(content):
                    incomplete_headers.append(rel_path)
                    
            except Exception as e:
                incomplete_headers.append(f"{rel_path}: error reading - {str(e)}")
        
        total_files = len(python_files)
        missing_count = len(missing_headers) + len(incomplete_headers)
        
        coverage_ratio = (total_files - missing_count) / total_files
        score = int(coverage_ratio * 10)
        
        issues = []
        if missing_headers:
            issues.extend([f"Missing header: {f}" for f in missing_headers[:5]])  # Limit output
            if len(missing_headers) > 5:
                issues.append(f"...and {len(missing_headers) - 5} more files missing headers")
        if incomplete_headers:
            issues.extend([f"Incomplete header: {f}" for f in incomplete_headers[:5]])
            if len(incomplete_headers) > 5:
                issues.append(f"...and {len(incomplete_headers) - 5} more files with incomplete headers")
        
        return score, issues
        
    def _check_link_validation(self) -> Tuple[int, List[str]]:
        """Check for broken internal links in documentation."""
        doc_files = list(self.root.rglob('*.md'))
        broken_links = []
        
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        
        for doc_file in doc_files:
            try:
                content = doc_file.read_text()
                rel_path = str(doc_file.relative_to(self.root))
                
                for match in re.finditer(link_pattern, content):
                    link_text = match.group(1)
                    link_target = match.group(2)
                    
                    # Skip external links
                    if link_target.startswith(('http://', 'https://', 'mailto:')):
                        continue
                        
                    # Skip anchors for now (would need more sophisticated parsing)
                    if link_target.startswith('#'):
                        continue
                        
                    # Check if file exists
                    target_path = (doc_file.parent / link_target).resolve()
                    if not target_path.exists():
                        broken_links.append(f"{rel_path}: broken link to {link_target}")
                        
            except Exception as e:
                broken_links.append(f"{rel_path}: error checking links - {str(e)}")
        
        if not broken_links:
            return 10, []
            
        score = max(0, 10 - len(broken_links))
        return score, broken_links[:10]  # Limit output
        
    def _check_feature_documentation(self) -> Tuple[int, List[str]]:
        """Check that features have proper documentation structure."""
        manifest_path = self.root / '.documentation' / 'manifest.json'
        
        if not manifest_path.exists():
            return 0, ["Cannot check feature docs without manifest"]
            
        try:
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
                
            features = manifest.get('features', {})
            issues = []
            
            for feature_name, feature_info in features.items():
                feature_path = self.root / feature_info['path']
                
                # Check if feature directory exists
                if not feature_path.exists():
                    issues.append(f"Feature {feature_name} path does not exist: {feature_info['path']}")
                    continue
                    
                # Check for README
                readme_path = feature_path / 'README.md'
                if not readme_path.exists():
                    issues.append(f"Feature {feature_name} missing README.md")
                    
                # Check that documented files exist
                documented_files = feature_info.get('files', [])
                for file_info in documented_files:
                    if isinstance(file_info, dict):
                        file_path = self.root / file_info['path']
                    else:
                        file_path = self.root / file_info
                        
                    if not file_path.exists():
                        issues.append(f"Feature {feature_name} references non-existent file: {file_path}")
                        
            total_features = len(features)
            if total_features == 0:
                return 5, ["No features defined in manifest"]
                
            score = max(0, 10 - len(issues))
            return score, issues
            
        except Exception as e:
            return 0, [f"Error validating feature documentation: {str(e)}"]
            
    def _check_api_documentation(self) -> Tuple[int, List[str]]:
        """Check that public APIs are documented."""
        # This is a simplified check - in production would be more sophisticated
        python_files = [f for f in self.root.rglob('*.py') if not self._should_skip_file(f)]
        
        undocumented_apis = []
        
        for py_file in python_files:
            try:
                content = py_file.read_text()
                rel_path = str(py_file.relative_to(self.root))
                
                # Parse AST to find classes and functions
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                        # Skip private methods/classes
                        if node.name.startswith('_'):
                            continue
                            
                        # Check if it has a docstring
                        if not (node.body and isinstance(node.body[0], ast.Expr) and
                               isinstance(node.body[0].value, ast.Constant)):
                            undocumented_apis.append(f"{rel_path}: {type(node).__name__} {node.name}")
                            
            except Exception:
                # Skip files that can't be parsed
                continue
                
        if not undocumented_apis:
            return 10, []
            
        score = max(0, 10 - len(undocumented_apis) // 5)  # More lenient
        return score, undocumented_apis[:10]  # Limit output
        
    def _check_examples_runnable(self) -> Tuple[int, List[str]]:
        """Check that code examples are syntactically correct."""
        doc_files = list(self.root.rglob('*.md'))
        broken_examples = []
        
        python_code_pattern = r'```python\n(.*?)\n```'
        
        for doc_file in doc_files:
            try:
                content = doc_file.read_text()
                rel_path = str(doc_file.relative_to(self.root))
                
                for match in re.finditer(python_code_pattern, content, re.DOTALL):
                    code = match.group(1)
                    
                    # Skip examples that are clearly incomplete or pseudo-code
                    if '...' in code or 'TODO' in code or '# ...' in code:
                        continue
                        
                    try:
                        ast.parse(code)
                    except SyntaxError as e:
                        broken_examples.append(f"{rel_path}: syntax error in code example - {str(e)}")
                        
            except Exception:
                continue
                
        if not broken_examples:
            return 10, []
            
        score = max(0, 10 - len(broken_examples))
        return score, broken_examples[:5]  # Limit output
        
    def _check_orphan_files(self) -> Tuple[int, List[str]]:
        """Check for orphaned files not referenced anywhere."""
        # Load analysis if available
        analysis_path = self.root / 'docs' / 'documentation_gaps_analysis.json'
        
        if not analysis_path.exists():
            return 5, ["Cannot check orphans - run analyze_documentation_gaps.py first"]
            
        try:
            with open(analysis_path, 'r') as f:
                analysis = json.load(f)
                
            orphaned_files = analysis.get('gaps', {}).get('orphaned_files', [])
            
            if not orphaned_files:
                return 10, []
                
            issues = [f"Orphaned file: {item['file']}" for item in orphaned_files]
            score = max(0, 10 - len(orphaned_files))
            
            return score, issues[:10]  # Limit output
            
        except Exception as e:
            return 3, [f"Error checking orphaned files: {str(e)}"]
            
    def _check_documentation_freshness(self) -> Tuple[int, List[str]]:
        """Check that documentation is reasonably fresh."""
        key_docs = [
            'README.md',
            'docs/ARCHITECTURE.md',
            'docs/FEATURE_STATUS.md',
            '.agent-instructions.md'
        ]
        
        stale_docs = []
        now = datetime.now()
        
        for doc_path in key_docs:
            full_path = self.root / doc_path
            
            if not full_path.exists():
                stale_docs.append(f"Missing: {doc_path}")
                continue
                
            try:
                mtime = datetime.fromtimestamp(full_path.stat().st_mtime)
                days_old = (now - mtime).days
                
                if days_old > 30:  # Older than 30 days
                    stale_docs.append(f"Stale ({days_old} days): {doc_path}")
                    
            except Exception as e:
                stale_docs.append(f"Error checking {doc_path}: {str(e)}")
                
        if not stale_docs:
            return 10, []
            
        score = max(0, 10 - len(stale_docs) * 2)
        return score, stale_docs
        
    def _should_skip_file(self, path: Path) -> bool:
        """Check if file should be skipped in analysis."""
        skip_patterns = [
            '__pycache__', '.git', '.pytest_cache', 'build', 'dist',
            'node_modules', '.venv', 'venv', 'env', 'scaffolding'
        ]
        return any(pattern in str(path) for pattern in skip_patterns)
        
    def _has_file_header(self, content: str) -> bool:
        """Check if file has any header documentation."""
        return content.strip().startswith('"""') or content.strip().startswith("'''")
        
    def _has_complete_header(self, content: str) -> bool:
        """Check if file has complete header with required elements."""
        if not self._has_file_header(content):
            return False
            
        # Extract docstring
        lines = content.split('\n')
        docstring_lines = []
        in_docstring = False
        quote_type = None
        
        for line in lines:
            if not in_docstring:
                if line.strip().startswith('"""'):
                    quote_type = '"""'
                    in_docstring = True
                elif line.strip().startswith("'''"):
                    quote_type = "'''"
                    in_docstring = True
                if in_docstring:
                    docstring_lines.append(line)
            else:
                docstring_lines.append(line)
                if quote_type in line and line.strip() != quote_type:
                    break
                    
        docstring = '\n'.join(docstring_lines)
        
        # Check for required elements
        required_elements = ['@file', '@description']
        return all(element in docstring for element in required_elements)
        
    def print_results(self):
        """Print human-readable validation results."""
        results = self.validation_results
        
        print(f"\n📊 Documentation Validation Results")
        print(f"{'='*50}")
        print(f"Overall Status: {results['overall_status'].upper()}")
        print(f"Overall Score: {results['score']:.1f}/100")
        print(f"Timestamp: {results['timestamp']}")
        
        print(f"\n📋 Check Results:")
        for check_name, check_result in results['checks'].items():
            status_icon = {'pass': '✅', 'warn': '⚠️', 'fail': '❌', 'error': '💥'}[check_result['status']]
            print(f"{status_icon} {check_name}: {check_result['score']}/{check_result['max_score']}")
            
            if check_result['issues']:
                for issue in check_result['issues'][:3]:  # Show first 3 issues
                    print(f"    • {issue}")
                if len(check_result['issues']) > 3:
                    print(f"    • ...and {len(check_result['issues']) - 3} more issues")
        
        if results['errors']:
            print(f"\n❌ Critical Errors ({len(results['errors'])}):")
            for error in results['errors'][:5]:
                print(f"  • {error}")
                
        if results['warnings']:
            print(f"\n⚠️ Warnings ({len(results['warnings'])}):")
            for warning in results['warnings'][:5]:
                print(f"  • {warning}")
                
        if results['improvements']:
            print(f"\n💡 Improvement Opportunities ({len(results['improvements'])}):")
            for improvement in results['improvements'][:3]:
                print(f"  • {improvement}")
                
        # Recommendations
        print(f"\n🎯 Recommendations:")
        if results['score'] < 50:
            print("  • Focus on basic documentation coverage - add missing READMEs and file headers")
        elif results['score'] < 70:
            print("  • Improve documentation quality - add examples and fix broken links")
        elif results['score'] < 85:
            print("  • Polish documentation - ensure all APIs documented and examples runnable")
        else:
            print("  • Excellent documentation! Consider automation to maintain this quality")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate Fresh AI documentation")
    parser.add_argument('--strict', action='store_true', 
                       help='Fail if score is below 70%')
    parser.add_argument('--json', action='store_true',
                       help='Output results as JSON')
    parser.add_argument('--output', type=str,
                       help='Save results to file')
    
    args = parser.parse_args()
    
    validator = DocumentationValidator()
    results = validator.validate_all(strict=args.strict)
    
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        validator.print_results()
        
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n💾 Results saved to: {args.output}")
    
    # Exit with appropriate code
    if results['overall_status'] in ['failed_strict', 'poor']:
        sys.exit(1)
    elif results['overall_status'] == 'needs_improvement':
        sys.exit(2)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
