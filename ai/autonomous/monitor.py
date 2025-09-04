"""
Codebase Monitor for Autonomous Loop
Continuously monitors codebase health and quality metrics.
"""

import os
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json
import re

from ai.memory.intelligent_store import IntelligentMemoryStore


@dataclass
class CodeMetrics:
    """Represents code quality metrics."""
    timestamp: datetime
    total_lines: int
    code_lines: int
    comment_lines: int
    blank_lines: int
    files_count: int
    test_coverage: float
    complexity_average: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "total_lines": self.total_lines,
            "code_lines": self.code_lines,
            "comment_lines": self.comment_lines,
            "blank_lines": self.blank_lines,
            "files_count": self.files_count,
            "test_coverage": self.test_coverage,
            "complexity_average": self.complexity_average
        }


@dataclass
class IssueReport:
    """Represents a discovered code issue."""
    type: str
    severity: str
    file: str
    line: Optional[int]
    description: str
    details: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "severity": self.severity,
            "file": self.file,
            "line": self.line,
            "description": self.description,
            "details": self.details
        }


class CodebaseMonitor:
    """
    Continuously monitors codebase health and quality metrics.
    Identifies issues, patterns, and improvement opportunities.
    """
    
    def __init__(self, working_directory: str, memory_store: Optional[IntelligentMemoryStore] = None):
        self.working_directory = Path(working_directory)
        self.memory_store = memory_store or IntelligentMemoryStore()
        
        # Monitoring configuration
        self.config = {
            "file_extensions": [".py", ".js", ".ts", ".java", ".cpp", ".c", ".h"],
            "ignore_patterns": [
                ".git/", "__pycache__/", ".pytest_cache/", "node_modules/",
                ".venv/", "venv/", "build/", "dist/"
            ],
            "max_complexity": 10,
            "min_test_coverage": 80.0
        }
        
        # Track historical metrics
        self.metrics_history: List[CodeMetrics] = []
        
    def comprehensive_scan(self) -> Dict[str, Any]:
        """
        Perform comprehensive codebase scan.
        
        Returns:
            Dictionary containing scan results including issues and metrics
        """
        scan_results = {
            "timestamp": datetime.now().isoformat(),
            "issues": [],
            "metrics": None,
            "patterns": [],
            "health_score": 0.0
        }
        
        try:
            # Collect current metrics
            metrics = self.collect_metrics()
            scan_results["metrics"] = metrics.to_dict() if metrics else None
            
            # Scan for various types of issues
            issues = []
            
            # Security issues
            security_issues = self._scan_security_issues()
            issues.extend(security_issues)
            
            # Quality issues
            quality_issues = self._scan_quality_issues()
            issues.extend(quality_issues)
            
            # Performance issues
            performance_issues = self._scan_performance_issues()
            issues.extend(performance_issues)
            
            # Test coverage issues
            test_issues = self._scan_test_issues()
            issues.extend(test_issues)
            
            # TODO items
            todo_issues = self._scan_todo_items()
            issues.extend(todo_issues)
            
            scan_results["issues"] = [issue.to_dict() for issue in issues]
            
            # Analyze patterns
            patterns = self.analyze_patterns()
            scan_results["patterns"] = patterns
            
            # Calculate health score
            health_score = self._calculate_health_score(issues, metrics)
            scan_results["health_score"] = health_score
            
        except Exception as e:
            scan_results["error"] = str(e)
        
        return scan_results
    
    def collect_metrics(self) -> Optional[CodeMetrics]:
        """Collect current code metrics."""
        try:
            total_lines = 0
            code_lines = 0
            comment_lines = 0
            blank_lines = 0
            files_count = 0
            
            # Count lines in source files
            for ext in self.config["file_extensions"]:
                for file_path in self.working_directory.rglob(f"*{ext}"):
                    if self._should_ignore_file(file_path):
                        continue
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = f.readlines()
                            
                        files_count += 1
                        total_lines += len(lines)
                        
                        for line in lines:
                            stripped = line.strip()
                            if not stripped:
                                blank_lines += 1
                            elif stripped.startswith('#') or stripped.startswith('//'):
                                comment_lines += 1
                            else:
                                code_lines += 1
                    except:
                        continue
            
            # Get test coverage if available
            test_coverage = self._get_test_coverage()
            
            # Calculate average complexity (simplified)
            complexity_average = self._calculate_average_complexity()
            
            metrics = CodeMetrics(
                timestamp=datetime.now(),
                total_lines=total_lines,
                code_lines=code_lines,
                comment_lines=comment_lines,
                blank_lines=blank_lines,
                files_count=files_count,
                test_coverage=test_coverage,
                complexity_average=complexity_average
            )
            
            # Store in history
            self.metrics_history.append(metrics)
            
            # Store in memory
            try:
                self.memory_store.write(
                    content=f"Code metrics collected: {files_count} files, {total_lines} lines",
                    tags=["monitoring", "metrics", "codebase"]
                )
            except:
                pass
            
            return metrics
            
        except Exception as e:
            print(f"Error collecting metrics: {e}")
            return None
    
    def analyze_patterns(self) -> List[Dict[str, Any]]:
        """Analyze code patterns and anti-patterns."""
        patterns = []
        
        try:
            # Detect recurring issues
            recurring_patterns = self._detect_recurring_issues()
            patterns.extend(recurring_patterns)
            
            # Detect architectural patterns
            arch_patterns = self._detect_architectural_patterns()
            patterns.extend(arch_patterns)
            
            # Detect naming patterns
            naming_patterns = self._detect_naming_patterns()
            patterns.extend(naming_patterns)
            
        except Exception as e:
            patterns.append({
                "type": "error",
                "description": f"Pattern analysis failed: {e}"
            })
        
        return patterns
    
    def detect_regressions(self) -> List[Dict[str, Any]]:
        """Detect performance or quality regressions."""
        regressions = []
        
        if len(self.metrics_history) < 2:
            return regressions
        
        try:
            current = self.metrics_history[-1]
            previous = self.metrics_history[-2]
            
            # Check test coverage regression
            if current.test_coverage < previous.test_coverage - 5.0:
                regressions.append({
                    "type": "test_coverage_regression",
                    "severity": "medium",
                    "description": f"Test coverage decreased from {previous.test_coverage:.1f}% to {current.test_coverage:.1f}%",
                    "current": current.test_coverage,
                    "previous": previous.test_coverage
                })
            
            # Check complexity regression
            if current.complexity_average > previous.complexity_average + 2.0:
                regressions.append({
                    "type": "complexity_regression",
                    "severity": "medium",
                    "description": f"Average complexity increased from {previous.complexity_average:.1f} to {current.complexity_average:.1f}",
                    "current": current.complexity_average,
                    "previous": previous.complexity_average
                })
            
        except Exception as e:
            regressions.append({
                "type": "error",
                "description": f"Regression detection failed: {e}"
            })
        
        return regressions
    
    def _scan_security_issues(self) -> List[IssueReport]:
        """Scan for security issues."""
        issues = []
        
        try:
            # Common security patterns to check
            security_patterns = [
                (r'hashlib\.md5|hashlib\.sha1', "Weak cryptographic hash function"),
                (r'random\.random\(\)', "Insecure random number generation"),
                (r'eval\(|exec\(', "Dangerous code execution"),
                (r'pickle\.loads?', "Insecure deserialization"),
                (r'subprocess\..*shell=True', "Shell injection risk"),
            ]
            
            for file_path in self.working_directory.rglob("*.py"):
                if self._should_ignore_file(file_path):
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        lines = content.split('\n')
                    
                    for i, line in enumerate(lines, 1):
                        for pattern, description in security_patterns:
                            if re.search(pattern, line):
                                issues.append(IssueReport(
                                    type="security",
                                    severity="high",
                                    file=str(file_path.relative_to(self.working_directory)),
                                    line=i,
                                    description=description,
                                    details={"pattern": pattern, "code": line.strip()}
                                ))
                                
                except:
                    continue
                    
        except Exception as e:
            issues.append(IssueReport(
                type="security",
                severity="low",
                file="",
                line=None,
                description=f"Security scan failed: {e}",
                details={}
            ))
        
        return issues
    
    def _scan_quality_issues(self) -> List[IssueReport]:
        """Scan for code quality issues."""
        issues = []
        
        try:
            # Quality patterns to check
            quality_patterns = [
                (r'^.{120,}', "Line too long (>120 characters)"),
                (r'\t', "Tab character used instead of spaces"),
                (r'print\(|console\.log\(', "Debug print statement left in code"),
                (r'# TODO:?\s*$', "Empty TODO comment"),
                (r'def\s+\w+\([^)]*\):\s*$', "Empty function definition"),
            ]
            
            for file_path in self.working_directory.rglob("*.py"):
                if self._should_ignore_file(file_path):
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                    
                    for i, line in enumerate(lines, 1):
                        for pattern, description in quality_patterns:
                            if re.search(pattern, line):
                                issues.append(IssueReport(
                                    type="quality",
                                    severity="medium",
                                    file=str(file_path.relative_to(self.working_directory)),
                                    line=i,
                                    description=description,
                                    details={"pattern": pattern, "code": line.strip()}
                                ))
                                
                except:
                    continue
                    
        except Exception as e:
            pass
        
        return issues
    
    def _scan_performance_issues(self) -> List[IssueReport]:
        """Scan for performance issues."""
        issues = []
        
        try:
            # Performance patterns to check
            perf_patterns = [
                (r'for\s+\w+\s+in\s+range\(len\(', "Inefficient loop pattern"),
                (r'\.append\(.*\)\s*$', "List append in loop (potential performance issue)"),
                (r'time\.sleep\(\d+\)', "Long sleep call"),
            ]
            
            for file_path in self.working_directory.rglob("*.py"):
                if self._should_ignore_file(file_path):
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                    
                    for i, line in enumerate(lines, 1):
                        for pattern, description in perf_patterns:
                            if re.search(pattern, line):
                                issues.append(IssueReport(
                                    type="performance",
                                    severity="medium",
                                    file=str(file_path.relative_to(self.working_directory)),
                                    line=i,
                                    description=description,
                                    details={"pattern": pattern, "code": line.strip()}
                                ))
                                
                except:
                    continue
                    
        except Exception as e:
            pass
        
        return issues
    
    def _scan_test_issues(self) -> List[IssueReport]:
        """Scan for testing issues."""
        issues = []
        
        try:
            # Count test files vs source files
            source_files = 0
            test_files = 0
            
            for file_path in self.working_directory.rglob("*.py"):
                if self._should_ignore_file(file_path):
                    continue
                
                if "test" in file_path.name.lower():
                    test_files += 1
                else:
                    source_files += 1
            
            # Check test-to-source ratio
            if source_files > 0:
                test_ratio = test_files / source_files
                if test_ratio < 0.5:
                    issues.append(IssueReport(
                        type="test_coverage",
                        severity="medium",
                        file="",
                        line=None,
                        description=f"Low test-to-source ratio: {test_ratio:.2f}",
                        details={"test_files": test_files, "source_files": source_files}
                    ))
                    
        except Exception as e:
            pass
        
        return issues
    
    def _scan_todo_items(self) -> List[IssueReport]:
        """Scan for TODO items."""
        issues = []
        
        try:
            todo_pattern = r'#\s*TODO:?\s*(.+)'
            
            for file_path in self.working_directory.rglob("*.py"):
                if self._should_ignore_file(file_path):
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                    
                    for i, line in enumerate(lines, 1):
                        match = re.search(todo_pattern, line)
                        if match:
                            todo_text = match.group(1).strip()
                            issues.append(IssueReport(
                                type="todo",
                                severity="low",
                                file=str(file_path.relative_to(self.working_directory)),
                                line=i,
                                description=f"TODO: {todo_text}",
                                details={"todo_text": todo_text}
                            ))
                            
                except:
                    continue
                    
        except Exception as e:
            pass
        
        return issues
    
    def _should_ignore_file(self, file_path: Path) -> bool:
        """Check if file should be ignored."""
        file_str = str(file_path)
        
        for pattern in self.config["ignore_patterns"]:
            if pattern in file_str:
                return True
        
        return False
    
    def _get_test_coverage(self) -> float:
        """Get test coverage if available."""
        try:
            # Try to run coverage if available
            result = subprocess.run(
                ["poetry", "run", "pytest", "--cov-report=json", "--cov=.", "-q"],
                cwd=self.working_directory,
                capture_output=True,
                timeout=60
            )
            
            if result.returncode == 0:
                # Try to read coverage.json
                coverage_file = self.working_directory / "coverage.json"
                if coverage_file.exists():
                    with open(coverage_file) as f:
                        data = json.load(f)
                        return data.get("totals", {}).get("percent_covered", 0.0)
        except:
            pass
        
        return 0.0
    
    def _calculate_average_complexity(self) -> float:
        """Calculate average cyclomatic complexity (simplified)."""
        # Simple heuristic based on control flow keywords
        complexity_keywords = ['if', 'elif', 'else', 'for', 'while', 'try', 'except', 'finally']
        
        total_complexity = 0
        file_count = 0
        
        try:
            for file_path in self.working_directory.rglob("*.py"):
                if self._should_ignore_file(file_path):
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read().lower()
                    
                    file_complexity = 1  # Base complexity
                    for keyword in complexity_keywords:
                        file_complexity += content.count(f' {keyword} ')
                        file_complexity += content.count(f'\t{keyword} ')
                        file_complexity += content.count(f'\n{keyword} ')
                    
                    total_complexity += file_complexity
                    file_count += 1
                    
                except:
                    continue
        except:
            pass
        
        return total_complexity / file_count if file_count > 0 else 0.0
    
    def _calculate_health_score(self, issues: List[IssueReport], metrics: Optional[CodeMetrics]) -> float:
        """Calculate overall codebase health score (0.0 to 1.0)."""
        score = 1.0
        
        # Penalize based on issue severity
        for issue in issues:
            if issue.severity == "critical":
                score -= 0.1
            elif issue.severity == "high":
                score -= 0.05
            elif issue.severity == "medium":
                score -= 0.02
            elif issue.severity == "low":
                score -= 0.01
        
        # Penalize based on metrics
        if metrics:
            if metrics.test_coverage < self.config["min_test_coverage"]:
                score -= 0.2
            
            if metrics.complexity_average > self.config["max_complexity"]:
                score -= 0.1
        
        return max(0.0, score)
    
    def _detect_recurring_issues(self) -> List[Dict[str, Any]]:
        """Detect recurring issues or patterns."""
        patterns = []
        
        try:
            # This would analyze historical data to find recurring issues
            # For now, just placeholder
            patterns.append({
                "type": "recurring_pattern",
                "description": "Pattern analysis placeholder",
                "confidence": 0.5
            })
        except:
            pass
        
        return patterns
    
    def _detect_architectural_patterns(self) -> List[Dict[str, Any]]:
        """Detect architectural patterns."""
        patterns = []
        
        try:
            # Analyze directory structure and imports
            # This is a simplified implementation
            directories = set()
            for file_path in self.working_directory.rglob("*.py"):
                if not self._should_ignore_file(file_path):
                    directories.add(file_path.parent.name)
            
            if len(directories) > 5:
                patterns.append({
                    "type": "architecture",
                    "description": "Complex directory structure detected",
                    "details": {"directory_count": len(directories)}
                })
        except:
            pass
        
        return patterns
    
    def _detect_naming_patterns(self) -> List[Dict[str, Any]]:
        """Detect naming patterns and inconsistencies."""
        patterns = []
        
        try:
            # Simple naming convention checks
            snake_case_files = 0
            camel_case_files = 0
            
            for file_path in self.working_directory.rglob("*.py"):
                if self._should_ignore_file(file_path):
                    continue
                
                filename = file_path.stem
                if '_' in filename:
                    snake_case_files += 1
                elif any(c.isupper() for c in filename[1:]):
                    camel_case_files += 1
            
            if snake_case_files > 0 and camel_case_files > 0:
                patterns.append({
                    "type": "naming_inconsistency",
                    "description": "Mixed naming conventions detected",
                    "details": {"snake_case": snake_case_files, "camel_case": camel_case_files}
                })
        except:
            pass
        
        return patterns
