#!/usr/bin/env python3
"""
Feature Inventory and Validation System

Implements the self-documenting loop by:
1. Scanning codebase for all features and their implementation status
2. Validating each feature meets quality criteria
3. Identifying features not properly hooked up
4. Generating comprehensive feature documentation
5. Ensuring no feature bloat and proper test coverage

This is a core implementation of the "Self-Documenting Loop" rule.
"""

import ast
import json
import sys
from pathlib import Path
from typing import Dict, List, Set, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import inspect
import importlib.util
import subprocess
import re
from datetime import datetime


@dataclass
class Feature:
    """Represents a feature in the codebase."""
    name: str
    module_path: str
    class_name: Optional[str]
    function_name: Optional[str]
    description: str
    implemented: bool
    hooked_up: bool
    tested: bool
    necessary: bool
    cli_accessible: bool
    api_accessible: bool
    dependencies: List[str]
    test_files: List[str]
    documentation: List[str]
    quality_score: float
    issues: List[str]
    

@dataclass
class FeatureInventory:
    """Complete inventory of codebase features."""
    total_features: int
    implemented_features: int
    hooked_up_features: int
    tested_features: int
    unnecessary_features: int
    cli_features: int
    api_features: int
    features: List[Feature]
    quality_summary: Dict[str, Any]
    issues: List[str]
    recommendations: List[str]
    generated_at: str


class FeatureScanner:
    """Scans codebase to identify and validate features."""
    
    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.features: List[Feature] = []
        self.cli_endpoints: Set[str] = set()
        self.api_endpoints: Set[str] = set()
        self.test_files: Dict[str, List[str]] = {}
        self.documentation_files: Dict[str, List[str]] = {}
        
    def scan_codebase(self) -> FeatureInventory:
        """Perform complete feature scan and validation."""
        print("🔍 Starting comprehensive feature scan...")
        
        # Phase 1: Discover features
        self._discover_features()
        
        # Phase 2: Analyze CLI and API hooks
        self._analyze_endpoints()
        
        # Phase 3: Map test coverage
        self._map_test_coverage()
        
        # Phase 4: Map documentation
        self._map_documentation()
        
        # Phase 5: Validate each feature
        self._validate_features()
        
        # Phase 6: Generate inventory
        inventory = self._generate_inventory()
        
        print(f"✅ Feature scan complete: {len(self.features)} features analyzed")
        return inventory
    
    def _discover_features(self):
        """Discover all features by scanning Python modules."""
        print("  📂 Discovering features in codebase...")
        
        # Scan all Python files in key directories
        key_dirs = ['ai/', 'scripts/']
        
        for dir_name in key_dirs:
            dir_path = self.root_path / dir_name
            if dir_path.exists():
                self._scan_directory(dir_path)
    
    def _scan_directory(self, directory: Path):
        """Recursively scan directory for Python features."""
        for py_file in directory.rglob("*.py"):
            if "__pycache__" in str(py_file) or "test_" in py_file.name:
                continue
                
            try:
                self._analyze_python_file(py_file)
            except Exception as e:
                print(f"⚠️  Error analyzing {py_file}: {e}")
    
    def _analyze_python_file(self, file_path: Path):
        """Analyze a Python file for features."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            tree = ast.parse(content)
            relative_path = file_path.relative_to(self.root_path)
            
            # Look for classes and functions that represent features
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    self._analyze_class(node, str(relative_path), content)
                elif isinstance(node, ast.FunctionDef):
                    if not node.name.startswith('_'):  # Skip private functions
                        self._analyze_function(node, str(relative_path), content)
                        
        except Exception as e:
            print(f"⚠️  Error parsing {file_path}: {e}")
    
    def _analyze_class(self, node: ast.ClassDef, file_path: str, content: str):
        """Analyze a class to determine if it's a feature."""
        class_name = node.name
        
        # Skip test classes and private classes
        if class_name.startswith('Test') or class_name.startswith('_'):
            return
            
        # Get docstring
        description = ast.get_docstring(node) or f"Class {class_name}"
        
        # Determine if this is a significant feature
        if self._is_significant_feature(class_name, description, node):
            feature = Feature(
                name=f"{class_name}",
                module_path=file_path,
                class_name=class_name,
                function_name=None,
                description=description.split('\n')[0] if description else f"Class {class_name}",
                implemented=True,  # If class exists, it's implemented
                hooked_up=False,   # Will be determined later
                tested=False,      # Will be determined later
                necessary=True,    # Will be validated later
                cli_accessible=False,  # Will be determined later
                api_accessible=False,  # Will be determined later
                dependencies=[],
                test_files=[],
                documentation=[],
                quality_score=0.0,
                issues=[]
            )
            self.features.append(feature)
    
    def _analyze_function(self, node: ast.FunctionDef, file_path: str, content: str):
        """Analyze a function to determine if it's a feature."""
        func_name = node.name
        
        # Skip special methods and test functions
        if func_name.startswith('__') or func_name.startswith('test_'):
            return
            
        # Get docstring
        description = ast.get_docstring(node) or f"Function {func_name}"
        
        # Determine if this is a significant feature
        if self._is_significant_feature(func_name, description, node):
            feature = Feature(
                name=f"{func_name}",
                module_path=file_path,
                class_name=None,
                function_name=func_name,
                description=description.split('\n')[0] if description else f"Function {func_name}",
                implemented=True,  # If function exists, it's implemented
                hooked_up=False,   # Will be determined later
                tested=False,      # Will be determined later
                necessary=True,    # Will be validated later
                cli_accessible=False,  # Will be determined later
                api_accessible=False,  # Will be determined later
                dependencies=[],
                test_files=[],
                documentation=[],
                quality_score=0.0,
                issues=[]
            )
            self.features.append(feature)
    
    def _is_significant_feature(self, name: str, description: str, node: ast.AST) -> bool:
        """Determine if a class/function represents a significant feature."""
        # Skip utility functions and internal helpers
        if any(skip in name.lower() for skip in ['helper', 'util', 'internal', '_private']):
            return False
            
        # Look for feature indicators
        feature_indicators = [
            'agent', 'loop', 'memory', 'tool', 'command', 'scanner', 
            'engine', 'controller', 'monitor', 'store', 'manager',
            'processor', 'analyzer', 'generator', 'validator'
        ]
        
        if any(indicator in name.lower() for indicator in feature_indicators):
            return True
            
        # Check if it has substantial implementation
        if isinstance(node, ast.ClassDef):
            method_count = len([n for n in node.body if isinstance(n, ast.FunctionDef)])
            return method_count >= 2
        elif isinstance(node, ast.FunctionDef):
            # Check if function has substantial body
            return len(node.body) >= 3
            
        return False
    
    def _analyze_endpoints(self):
        """Analyze CLI and API endpoints to see what features are hooked up."""
        print("  🔌 Analyzing endpoint hooks...")
        
        # Analyze CLI endpoints
        cli_file = self.root_path / "ai" / "cli" / "fresh.py"
        if cli_file.exists():
            self._analyze_cli_endpoints(cli_file)
        
        # Update features with hook status
        for feature in self.features:
            feature.cli_accessible = feature.name in self.cli_endpoints or \
                                   (feature.function_name and feature.function_name in self.cli_endpoints) or \
                                   (feature.class_name and feature.class_name in self.cli_endpoints)
            
            # A feature is "hooked up" if it's accessible through some interface
            feature.hooked_up = feature.cli_accessible or feature.api_accessible
    
    def _analyze_cli_endpoints(self, cli_file: Path):
        """Extract CLI command endpoints from the CLI module."""
        try:
            with open(cli_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for command functions and class imports
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                # Look for function definitions that start with 'cmd_'
                if isinstance(node, ast.FunctionDef) and node.name.startswith('cmd_'):
                    command_name = node.name.replace('cmd_', '')
                    self.cli_endpoints.add(command_name)
                
                # Look for imports that might be CLI accessible
                elif isinstance(node, ast.ImportFrom):
                    if node.names:
                        for alias in node.names:
                            self.cli_endpoints.add(alias.name)
                            
        except Exception as e:
            print(f"⚠️  Error analyzing CLI endpoints: {e}")
    
    def _map_test_coverage(self):
        """Map test files to features."""
        print("  🧪 Mapping test coverage...")
        
        test_dirs = ['tests/']
        
        for test_dir in test_dirs:
            test_path = self.root_path / test_dir
            if test_path.exists():
                self._scan_test_directory(test_path)
        
        # Update features with test information
        for feature in self.features:
            feature.test_files = self.test_files.get(feature.name, [])
            feature.tested = len(feature.test_files) > 0
    
    def _scan_test_directory(self, test_dir: Path):
        """Scan test directory for test files."""
        for test_file in test_dir.rglob("test_*.py"):
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract tested features from test file
                tested_features = self._extract_tested_features(content, test_file.name)
                
                for feature_name in tested_features:
                    if feature_name not in self.test_files:
                        self.test_files[feature_name] = []
                    self.test_files[feature_name].append(str(test_file.relative_to(self.root_path)))
                    
            except Exception as e:
                print(f"⚠️  Error analyzing test file {test_file}: {e}")
    
    def _extract_tested_features(self, content: str, filename: str) -> List[str]:
        """Extract feature names that are being tested."""
        features = []
        
        # Look for imports and class names being tested
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                # Look for imports
                if isinstance(node, ast.ImportFrom):
                    if node.names:
                        for alias in node.names:
                            features.append(alias.name)
                
                # Look for test class names
                elif isinstance(node, ast.ClassDef) and node.name.startswith('Test'):
                    # Extract feature name from test class name
                    feature_name = node.name.replace('Test', '')
                    if feature_name:
                        features.append(feature_name)
                        
        except:
            pass
            
        # Also extract from filename
        if filename.startswith('test_'):
            base_name = filename.replace('test_', '').replace('.py', '')
            features.append(base_name.replace('_', ''))
            
        return features
    
    def _map_documentation(self):
        """Map documentation files to features."""
        print("  📚 Mapping documentation...")
        
        doc_dirs = ['docs/', '.cursor/rules/']
        
        for doc_dir in doc_dirs:
            doc_path = self.root_path / doc_dir
            if doc_path.exists():
                self._scan_doc_directory(doc_path)
        
        # Update features with documentation information
        for feature in self.features:
            feature.documentation = self.documentation_files.get(feature.name, [])
    
    def _scan_doc_directory(self, doc_dir: Path):
        """Scan documentation directory."""
        for doc_file in doc_dir.rglob("*.md"):
            try:
                with open(doc_file, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                
                # Check which features are mentioned in this doc
                for feature in self.features:
                    if feature.name.lower() in content:
                        if feature.name not in self.documentation_files:
                            self.documentation_files[feature.name] = []
                        self.documentation_files[feature.name].append(str(doc_file.relative_to(self.root_path)))
                        
            except Exception as e:
                print(f"⚠️  Error analyzing doc file {doc_file}: {e}")
    
    def _validate_features(self):
        """Validate each feature against quality criteria."""
        print("  ✅ Validating feature quality and necessity...")
        
        for feature in self.features:
            self._validate_single_feature(feature)
    
    def _validate_single_feature(self, feature: Feature):
        """Validate a single feature against all criteria."""
        issues = []
        quality_score = 1.0  # Start with perfect score
        
        # Check if properly implemented
        if not feature.implemented:
            issues.append("Feature is declared but not implemented")
            quality_score -= 0.3
        
        # Check if hooked up
        if not feature.hooked_up:
            issues.append("Feature is not accessible through any interface (CLI/API)")
            quality_score -= 0.2
        
        # Check if tested
        if not feature.tested:
            issues.append("Feature lacks test coverage")
            quality_score -= 0.2
        
        # Check documentation
        if not feature.documentation:
            issues.append("Feature lacks documentation")
            quality_score -= 0.1
        
        # Validate necessity (heuristic check)
        if not self._is_feature_necessary(feature):
            issues.append("Feature may not be necessary - consider removal")
            feature.necessary = False
            quality_score -= 0.2
        
        feature.issues = issues
        feature.quality_score = max(0.0, quality_score)
    
    def _is_feature_necessary(self, feature: Feature) -> bool:
        """Determine if feature is necessary using heuristics."""
        # Features that are hooked up and tested are likely necessary
        if feature.hooked_up and feature.tested:
            return True
        
        # Core features (based on naming) are likely necessary
        core_indicators = ['memory', 'agent', 'loop', 'safety', 'cli']
        if any(indicator in feature.name.lower() for indicator in core_indicators):
            return True
        
        # Features with good documentation are likely necessary
        if len(feature.documentation) >= 2:
            return True
        
        # Otherwise, mark as potentially unnecessary
        return False
    
    def _generate_inventory(self) -> FeatureInventory:
        """Generate comprehensive feature inventory."""
        print("  📊 Generating feature inventory...")
        
        total = len(self.features)
        implemented = sum(1 for f in self.features if f.implemented)
        hooked_up = sum(1 for f in self.features if f.hooked_up)
        tested = sum(1 for f in self.features if f.tested)
        unnecessary = sum(1 for f in self.features if not f.necessary)
        cli_accessible = sum(1 for f in self.features if f.cli_accessible)
        api_accessible = sum(1 for f in self.features if f.api_accessible)
        
        # Calculate quality metrics
        avg_quality = sum(f.quality_score for f in self.features) / total if total > 0 else 0.0
        high_quality = sum(1 for f in self.features if f.quality_score >= 0.8)
        
        quality_summary = {
            "average_quality_score": round(avg_quality, 2),
            "high_quality_features": high_quality,
            "features_with_issues": sum(1 for f in self.features if f.issues),
            "coverage_metrics": {
                "implementation_coverage": round(implemented / total * 100, 1) if total > 0 else 0,
                "hookup_coverage": round(hooked_up / total * 100, 1) if total > 0 else 0,
                "test_coverage": round(tested / total * 100, 1) if total > 0 else 0
            }
        }
        
        # Generate recommendations
        recommendations = self._generate_recommendations()
        
        # Collect all issues
        all_issues = []
        for feature in self.features:
            for issue in feature.issues:
                all_issues.append(f"{feature.name}: {issue}")
        
        return FeatureInventory(
            total_features=total,
            implemented_features=implemented,
            hooked_up_features=hooked_up,
            tested_features=tested,
            unnecessary_features=unnecessary,
            cli_features=cli_accessible,
            api_features=api_accessible,
            features=self.features,
            quality_summary=quality_summary,
            issues=all_issues,
            recommendations=recommendations,
            generated_at=datetime.now().isoformat()
        )
    
    def _generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        # Analyze patterns
        unhooked = [f for f in self.features if not f.hooked_up and f.implemented]
        untested = [f for f in self.features if not f.tested and f.implemented]
        unnecessary = [f for f in self.features if not f.necessary]
        
        if unhooked:
            recommendations.append(f"Hook up {len(unhooked)} unconnected features to CLI/API interfaces")
        
        if untested:
            recommendations.append(f"Add test coverage for {len(untested)} untested features")
        
        if unnecessary:
            recommendations.append(f"Review and consider removing {len(unnecessary)} potentially unnecessary features")
        
        if len(self.features) > 50:
            recommendations.append("Consider consolidating features to reduce complexity")
        
        return recommendations


def generate_feature_documentation(inventory: FeatureInventory, output_path: Path):
    """Generate comprehensive feature documentation."""
    print("📝 Generating feature documentation...")
    
    content = f"""# Feature Inventory Report

**Generated**: {inventory.generated_at}
**Total Features**: {inventory.total_features}

## Summary

| Metric | Count | Percentage |
|--------|-------|------------|
| Total Features | {inventory.total_features} | 100% |
| Implemented | {inventory.implemented_features} | {inventory.quality_summary['coverage_metrics']['implementation_coverage']}% |
| Hooked Up (Accessible) | {inventory.hooked_up_features} | {inventory.quality_summary['coverage_metrics']['hookup_coverage']}% |
| Tested | {inventory.tested_features} | {inventory.quality_summary['coverage_metrics']['test_coverage']}% |
| CLI Accessible | {inventory.cli_features} | {round(inventory.cli_features/inventory.total_features*100, 1) if inventory.total_features > 0 else 0}% |
| API Accessible | {inventory.api_features} | {round(inventory.api_features/inventory.total_features*100, 1) if inventory.total_features > 0 else 0}% |
| Potentially Unnecessary | {inventory.unnecessary_features} | {round(inventory.unnecessary_features/inventory.total_features*100, 1) if inventory.total_features > 0 else 0}% |

## Quality Metrics

- **Average Quality Score**: {inventory.quality_summary['average_quality_score']}/1.0
- **High Quality Features** (≥0.8): {inventory.quality_summary['high_quality_features']}
- **Features with Issues**: {inventory.quality_summary['features_with_issues']}

## Recommendations

"""
    
    for i, rec in enumerate(inventory.recommendations, 1):
        content += f"{i}. {rec}\n"
    
    content += f"""

## Feature Details

### 🔴 Critical Issues (Features Not Hooked Up)

"""
    
    unhooked = [f for f in inventory.features if not f.hooked_up and f.implemented]
    if unhooked:
        for feature in sorted(unhooked, key=lambda x: x.quality_score):
            content += f"- **{feature.name}** (`{feature.module_path}`)\n"
            content += f"  - Description: {feature.description}\n"
            content += f"  - Quality Score: {feature.quality_score}\n"
            content += f"  - Issues: {', '.join(feature.issues)}\n\n"
    else:
        content += "✅ All implemented features are properly hooked up!\n\n"
    
    content += """### 🟡 Missing Test Coverage

"""
    
    untested = [f for f in inventory.features if not f.tested and f.implemented and f.hooked_up]
    if untested:
        for feature in sorted(untested, key=lambda x: x.quality_score):
            content += f"- **{feature.name}** (`{feature.module_path}`)\n"
            content += f"  - CLI Accessible: {'✅' if feature.cli_accessible else '❌'}\n"
            content += f"  - API Accessible: {'✅' if feature.api_accessible else '❌'}\n\n"
    else:
        content += "✅ All hooked-up features have test coverage!\n\n"
    
    content += """### 🟠 Potentially Unnecessary Features

"""
    
    unnecessary = [f for f in inventory.features if not f.necessary]
    if unnecessary:
        for feature in sorted(unnecessary, key=lambda x: x.quality_score):
            content += f"- **{feature.name}** (`{feature.module_path}`)\n"
            content += f"  - Hooked Up: {'✅' if feature.hooked_up else '❌'}\n"
            content += f"  - Tested: {'✅' if feature.tested else '❌'}\n"
            content += f"  - Quality Score: {feature.quality_score}\n\n"
    else:
        content += "✅ All features appear to be necessary!\n\n"
    
    content += """### ✅ High Quality Features

"""
    
    high_quality = [f for f in inventory.features if f.quality_score >= 0.8]
    for feature in sorted(high_quality, key=lambda x: x.quality_score, reverse=True):
        content += f"- **{feature.name}** (`{feature.module_path}`) - Score: {feature.quality_score}\n"
        content += f"  - Hooked Up: {'✅' if feature.hooked_up else '❌'}\n"
        content += f"  - Tested: {'✅' if feature.tested else '❌'}\n"
        if feature.documentation:
            content += f"  - Documented in: {', '.join(feature.documentation)}\n"
        content += "\n"
    
    content += """

---

## All Features (Alphabetical)

"""
    
    for feature in sorted(inventory.features, key=lambda x: x.name.lower()):
        status_icons = []
        if feature.implemented:
            status_icons.append("💻")
        if feature.hooked_up:
            status_icons.append("🔌")
        if feature.tested:
            status_icons.append("🧪")
        if feature.documentation:
            status_icons.append("📚")
        if not feature.necessary:
            status_icons.append("❓")
        
        content += f"### {' '.join(status_icons)} {feature.name}\n\n"
        content += f"**Module**: `{feature.module_path}`\n\n"
        content += f"**Description**: {feature.description}\n\n"
        content += f"**Quality Score**: {feature.quality_score}/1.0\n\n"
        
        if feature.issues:
            content += f"**Issues**:\n"
            for issue in feature.issues:
                content += f"- {issue}\n"
            content += "\n"
        
        content += f"**Status**:\n"
        content += f"- Implemented: {'✅' if feature.implemented else '❌'}\n"
        content += f"- CLI Accessible: {'✅' if feature.cli_accessible else '❌'}\n"
        content += f"- API Accessible: {'✅' if feature.api_accessible else '❌'}\n"
        content += f"- Tested: {'✅' if feature.tested else '❌'}\n"
        content += f"- Necessary: {'✅' if feature.necessary else '❓'}\n"
        
        if feature.test_files:
            content += f"- Test Files: {', '.join(feature.test_files)}\n"
        
        if feature.documentation:
            content += f"- Documentation: {', '.join(feature.documentation)}\n"
        
        content += "\n---\n\n"
    
    # Write documentation
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Feature documentation written to {output_path}")


def main():
    """Main function to run feature inventory."""
    root_path = Path(__file__).parent.parent
    
    print(f"🚀 Starting Feature Inventory System")
    print(f"📍 Root Path: {root_path}")
    
    # Create scanner and run analysis
    scanner = FeatureScanner(root_path)
    inventory = scanner.scan_codebase()
    
    # Save JSON inventory
    json_path = root_path / "docs" / "feature_inventory.json"
    json_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(asdict(inventory), f, indent=2, default=str)
    
    print(f"💾 JSON inventory saved to {json_path}")
    
    # Generate human-readable documentation
    doc_path = root_path / "docs" / "FEATURE_INVENTORY.md"
    generate_feature_documentation(inventory, doc_path)
    
    # Print summary
    print(f"\n📊 FEATURE INVENTORY SUMMARY")
    print(f"{'='*50}")
    print(f"Total Features: {inventory.total_features}")
    print(f"Implemented: {inventory.implemented_features} ({inventory.quality_summary['coverage_metrics']['implementation_coverage']}%)")
    print(f"Hooked Up: {inventory.hooked_up_features} ({inventory.quality_summary['coverage_metrics']['hookup_coverage']}%)")
    print(f"Tested: {inventory.tested_features} ({inventory.quality_summary['coverage_metrics']['test_coverage']}%)")
    print(f"Average Quality: {inventory.quality_summary['average_quality_score']}/1.0")
    print(f"{'='*50}")
    
    if inventory.issues:
        print(f"\n🚨 CRITICAL ISSUES TO ADDRESS:")
        for issue in inventory.issues[:10]:  # Show top 10 issues
            print(f"  - {issue}")
        if len(inventory.issues) > 10:
            print(f"  ... and {len(inventory.issues) - 10} more issues")
    
    if inventory.recommendations:
        print(f"\n💡 RECOMMENDATIONS:")
        for rec in inventory.recommendations:
            print(f"  - {rec}")
    
    # Return exit code based on quality
    if inventory.quality_summary['average_quality_score'] < 0.7:
        print(f"\n❌ Quality below threshold (0.7). Address issues before adding new features.")
        return 1
    else:
        print(f"\n✅ Feature inventory complete. Quality acceptable.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
