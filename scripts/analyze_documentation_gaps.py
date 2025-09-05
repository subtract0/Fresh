#!/usr/bin/env python3
"""
Documentation Gaps Analysis Script
Identifies missing documentation, orphaned files, and agent-readiness issues.
"""

import os
import ast
import json
from pathlib import Path
from typing import List, Dict, Set, Tuple
from datetime import datetime

class DocumentationAnalyzer:
    def __init__(self, root_path: str):
        self.root = Path(root_path)
        self.analysis = {
            'timestamp': datetime.now().isoformat(),
            'gaps': {
                'missing_readmes': [],
                'undocumented_files': [],
                'incomplete_headers': [],
                'orphaned_files': [],
                'broken_links': [],
                'missing_examples': []
            },
            'features': {},
            'connectivity': {},
            'metrics': {}
        }
        
    def analyze(self):
        """Run comprehensive documentation analysis."""
        print("🔍 Analyzing documentation gaps...")
        
        self._discover_features()
        self._check_readme_coverage()
        self._analyze_file_headers()
        self._find_orphaned_files()
        self._analyze_connectivity()
        self._calculate_metrics()
        
        return self.analysis
        
    def _discover_features(self):
        """Identify feature directories and modules."""
        features = {}
        
        # Pattern 1: Explicit feature directories
        feature_dirs = [
            'ai/memory', 'ai/agents', 'ai/tools', 'ai/cli', 'ai/interface',
            'ai/integration', 'ai/loop', 'ai/monitor', 'ai/workflows',
            'ai/autonomous', 'ai/services', 'ai/system'
        ]
        
        for feature_dir in feature_dirs:
            path = self.root / feature_dir
            if path.exists():
                features[feature_dir.replace('/', '_')] = {
                    'path': str(path),
                    'type': 'directory',
                    'files': list(path.rglob('*.py')),
                    'has_readme': (path / 'README.md').exists(),
                    'has_init': (path / '__init__.py').exists()
                }
                
        # Pattern 2: Root-level modules
        for py_file in self.root.glob('*.py'):
            if py_file.stem not in ['setup', '__init__']:
                features[f'root_{py_file.stem}'] = {
                    'path': str(py_file),
                    'type': 'file',
                    'files': [py_file],
                    'has_readme': False,
                    'has_init': False
                }
                
        self.analysis['features'] = features
        
    def _check_readme_coverage(self):
        """Check for missing READMEs in feature directories."""
        missing_readmes = []
        
        for feature_name, feature_info in self.analysis['features'].items():
            if feature_info['type'] == 'directory' and not feature_info['has_readme']:
                missing_readmes.append({
                    'feature': feature_name,
                    'path': feature_info['path'],
                    'file_count': len(feature_info['files'])
                })
                
        self.analysis['gaps']['missing_readmes'] = missing_readmes
        
    def _analyze_file_headers(self):
        """Check for proper file header documentation."""
        incomplete_headers = []
        undocumented_files = []
        
        for py_file in self.root.rglob('*.py'):
            if self._should_skip_file(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Check if file has any documentation
                if not self._has_documentation(content):
                    undocumented_files.append({
                        'file': str(py_file.relative_to(self.root)),
                        'size': len(content),
                        'functions': self._count_functions(content)
                    })
                    
                # Check header quality
                elif not self._has_complete_header(content):
                    incomplete_headers.append({
                        'file': str(py_file.relative_to(self.root)),
                        'missing': self._get_missing_header_elements(content)
                    })
                    
            except Exception as e:
                print(f"⚠️  Error analyzing {py_file}: {e}")
                
        self.analysis['gaps']['undocumented_files'] = undocumented_files
        self.analysis['gaps']['incomplete_headers'] = incomplete_headers
        
    def _find_orphaned_files(self):
        """Find files with no references or unclear purpose."""
        orphaned = []
        all_files = list(self.root.rglob('*.py'))
        
        for py_file in all_files:
            if self._should_skip_file(py_file):
                continue
                
            references = self._find_references_to_file(py_file, all_files)
            
            if len(references) == 0 and not self._is_entry_point(py_file):
                orphaned.append({
                    'file': str(py_file.relative_to(self.root)),
                    'reason': 'No references found',
                    'recommendation': self._recommend_orphan_action(py_file)
                })
                
        self.analysis['gaps']['orphaned_files'] = orphaned
        
    def _analyze_connectivity(self):
        """Analyze file connections and dependencies."""
        connectivity = {'nodes': [], 'edges': []}
        
        for py_file in self.root.rglob('*.py'):
            if self._should_skip_file(py_file):
                continue
                
            rel_path = str(py_file.relative_to(self.root))
            connectivity['nodes'].append({
                'id': rel_path,
                'type': self._classify_file_type(py_file),
                'feature': self._get_file_feature(py_file)
            })
            
            # Analyze imports
            imports = self._extract_imports(py_file)
            for imp in imports:
                if imp.startswith('.') or imp.startswith('ai.'):
                    connectivity['edges'].append({
                        'from': rel_path,
                        'to': self._resolve_import_path(imp, py_file),
                        'type': 'import'
                    })
                    
        self.analysis['connectivity'] = connectivity
        
    def _calculate_metrics(self):
        """Calculate documentation health metrics."""
        total_files = len(list(self.root.rglob('*.py'))) - len([f for f in self.root.rglob('*.py') if self._should_skip_file(f)])
        total_features = len(self.analysis['features'])
        
        metrics = {
            'total_files': total_files,
            'total_features': total_features,
            'documentation_coverage': {
                'files_documented': total_files - len(self.analysis['gaps']['undocumented_files']),
                'coverage_percentage': round(((total_files - len(self.analysis['gaps']['undocumented_files'])) / total_files) * 100, 1) if total_files > 0 else 0,
                'readme_coverage': sum(1 for f in self.analysis['features'].values() if f.get('has_readme', False)),
                'readme_percentage': round((sum(1 for f in self.analysis['features'].values() if f.get('has_readme', False)) / total_features) * 100, 1) if total_features > 0 else 0
            },
            'quality_issues': {
                'orphaned_files': len(self.analysis['gaps']['orphaned_files']),
                'incomplete_headers': len(self.analysis['gaps']['incomplete_headers']),
                'missing_readmes': len(self.analysis['gaps']['missing_readmes']),
                'broken_links': len(self.analysis['gaps']['broken_links'])
            },
            'agent_readiness_score': self._calculate_agent_readiness_score(total_files)
        }
        
        self.analysis['metrics'] = metrics
        
    def _should_skip_file(self, path: Path) -> bool:
        """Check if file should be skipped in analysis."""
        skip_patterns = [
            '__pycache__', '.git', '.pytest_cache', 'build', 'dist',
            'node_modules', '.venv', 'venv', 'env'
        ]
        return any(pattern in str(path) for pattern in skip_patterns) or path.name.startswith('.')
        
    def _has_documentation(self, content: str) -> bool:
        """Check if file has any form of documentation."""
        return '"""' in content or "'''" in content or content.strip().startswith('#')
        
    def _has_complete_header(self, content: str) -> bool:
        """Check if file has complete header documentation."""
        # Look for structured header with key elements
        return all(keyword in content[:500] for keyword in ['@file', '@description']) or \
               (content.strip().startswith('"""') and len(content.split('"""')[1].strip()) > 50)
               
    def _get_missing_header_elements(self, content: str) -> List[str]:
        """Identify missing header documentation elements."""
        missing = []
        if '@file' not in content[:500]:
            missing.append('file identification')
        if '@description' not in content[:500]:
            missing.append('description')
        if '@usage' not in content[:500] and 'example' not in content[:500].lower():
            missing.append('usage examples')
        return missing
        
    def _count_functions(self, content: str) -> int:
        """Count function definitions in file."""
        try:
            tree = ast.parse(content)
            return sum(1 for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))
        except:
            return content.count('def ')
            
    def _find_references_to_file(self, target_file: Path, all_files: List[Path]) -> List[str]:
        """Find files that reference the target file."""
        references = []
        target_module = str(target_file.relative_to(self.root)).replace('/', '.').replace('.py', '')
        
        for py_file in all_files:
            if py_file == target_file:
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if target_module in content or target_file.stem in content:
                        references.append(str(py_file.relative_to(self.root)))
            except:
                continue
                
        return references
        
    def _is_entry_point(self, py_file: Path) -> bool:
        """Check if file is an entry point."""
        entry_patterns = ['main.py', '__main__.py', 'cli.py', 'app.py', 'server.py']
        return py_file.name in entry_patterns or 'if __name__ == "__main__"' in py_file.read_text(errors='ignore')
        
    def _recommend_orphan_action(self, py_file: Path) -> str:
        """Recommend action for orphaned file."""
        try:
            content = py_file.read_text(errors='ignore')
            if 'def ' not in content and 'class ' not in content:
                return 'delete'
            elif 'test' in py_file.name.lower():
                return 'link_to_tests'
            else:
                return 'document_purpose'
        except:
            return 'investigate'
            
    def _classify_file_type(self, py_file: Path) -> str:
        """Classify file type based on content and location."""
        if 'test' in py_file.name:
            return 'test'
        elif py_file.name == '__init__.py':
            return 'package'
        elif 'cli' in str(py_file):
            return 'cli'
        elif 'agent' in str(py_file):
            return 'agent'
        elif 'tool' in str(py_file):
            return 'tool'
        elif 'memory' in str(py_file):
            return 'memory'
        else:
            return 'module'
            
    def _get_file_feature(self, py_file: Path) -> str:
        """Determine which feature a file belongs to."""
        path_parts = py_file.parts
        if 'ai' in path_parts:
            ai_index = path_parts.index('ai')
            if ai_index + 1 < len(path_parts):
                return path_parts[ai_index + 1]
        return 'root'
        
    def _extract_imports(self, py_file: Path) -> List[str]:
        """Extract import statements from Python file."""
        imports = []
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('import ') or line.startswith('from '):
                        imports.append(line.split()[1])
        except:
            pass
        return imports
        
    def _resolve_import_path(self, import_stmt: str, from_file: Path) -> str:
        """Resolve import statement to actual file path."""
        # Simplified resolution - would need more sophisticated logic for production
        return import_stmt.replace('.', '/')
        
    def _calculate_agent_readiness_score(self, total_files: int) -> float:
        """Calculate how ready the codebase is for autonomous agents."""
        if total_files == 0:
            return 0.0
            
        penalties = 0
        penalties += len(self.analysis['gaps']['undocumented_files']) * 2
        penalties += len(self.analysis['gaps']['orphaned_files']) * 3
        penalties += len(self.analysis['gaps']['missing_readmes']) * 1
        penalties += len(self.analysis['gaps']['incomplete_headers']) * 1
        
        max_possible_penalties = total_files * 3
        score = max(0, 100 - (penalties / max_possible_penalties * 100))
        
        return round(score, 1)

def main():
    analyzer = DocumentationAnalyzer('/Users/am/Code/Fresh')
    analysis = analyzer.analyze()
    
    # Save results
    output_file = Path('/Users/am/Code/Fresh/docs/documentation_gaps_analysis.json')
    with open(output_file, 'w') as f:
        json.dump(analysis, f, indent=2, default=str)
    
    # Print summary
    print(f"\n📊 Documentation Analysis Complete")
    print(f"📁 Total Files Analyzed: {analysis['metrics']['total_files']}")
    print(f"📝 Documentation Coverage: {analysis['metrics']['documentation_coverage']['coverage_percentage']}%")
    print(f"📋 README Coverage: {analysis['metrics']['documentation_coverage']['readme_percentage']}%")
    print(f"🤖 Agent Readiness Score: {analysis['metrics']['agent_readiness_score']}/100")
    
    print(f"\n⚠️  Critical Gaps:")
    print(f"   • Undocumented Files: {len(analysis['gaps']['undocumented_files'])}")
    print(f"   • Missing READMEs: {len(analysis['gaps']['missing_readmes'])}")
    print(f"   • Orphaned Files: {len(analysis['gaps']['orphaned_files'])}")
    print(f"   • Incomplete Headers: {len(analysis['gaps']['incomplete_headers'])}")
    
    print(f"\n💾 Full analysis saved to: {output_file}")
    
    return analysis

if __name__ == "__main__":
    main()
