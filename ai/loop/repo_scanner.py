"""Repository Scanner for detecting issues in codebase.

This module scans the repository for various issues that agents can
autonomously fix, including TODOs, FIXMEs, failing tests, type errors,
and uncommitted changes.

Cross-references:
    - ADR-008: Autonomous Development Loop Architecture
    - Mother Agent: ai/agents/mother.py for task dispatch
    - Development Loop: ai/loop/dev_loop.py for task execution
"""
from __future__ import annotations
import re
import subprocess
import json
from enum import Enum
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Optional, Dict, Any
import fnmatch

from ai.utils.settings import TIMEOUT_SECONDS


class TaskType(Enum):
    """Types of tasks that can be detected."""
    TODO = "TODO"
    FIXME = "FIXME"
    FAILING_TEST = "FAILING_TEST"
    SYNTAX_ERROR = "SYNTAX_ERROR"
    TYPE_ERROR = "TYPE_ERROR"
    UNCOMMITTED = "UNCOMMITTED"


@dataclass
class Task:
    """Represents a task found in the repository."""
    type: TaskType
    description: str
    file_path: str
    line_number: int
    priority: int = 1
    context: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary for JSON serialization."""
        return {
            "type": self.type.value,
            "description": self.description,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "priority": self.priority,
            "context": self.context
        }
    
    def __eq__(self, other) -> bool:
        """Check equality based on core attributes."""
        if not isinstance(other, Task):
            return False
        return (
            self.type == other.type and
            self.description == other.description and
            self.file_path == other.file_path and
            self.line_number == other.line_number
        )


class RepoScanner:
    """Scans repository for issues that agents can fix."""
    
    DEFAULT_IGNORE_PATTERNS = [
        ".git", ".svn", ".hg",
        "node_modules", "__pycache__", ".pytest_cache",
        "*.pyc", "*.pyo", "*.egg-info",
        ".venv", "venv", "env",
        "dist", "build", ".tox",
        ".coverage", "htmlcov",
        ".mypy_cache", ".ruff_cache"
    ]
    
    def __init__(self, repo_path: str = ".", ignore_patterns: Optional[List[str]] = None):
        """Initialize scanner with repository path.
        
        Args:
            repo_path: Path to repository to scan
            ignore_patterns: Patterns to ignore during scanning
        """
        self.repo_path = Path(repo_path)
        self.ignore_patterns = ignore_patterns or self.DEFAULT_IGNORE_PATTERNS
    
    def scan(self) -> List[Task]:
        """Perform comprehensive repository scan.
        
        Returns:
            List of tasks found, prioritized by importance
        """
        tasks = []
        
        # Find TODOs and FIXMEs
        tasks.extend(self.find_todos())
        
        # Find failing tests
        tasks.extend(self.find_failing_tests())
        
        # Find type errors
        tasks.extend(self.find_type_errors())
        
        # Find uncommitted changes
        tasks.extend(self.parse_git_diff())
        
        # Prioritize and return
        return self.prioritize_tasks(tasks)
    
    def find_todos(self) -> List[Task]:
        """Find TODO and FIXME comments in code.
        
        Returns:
            List of TODO/FIXME tasks
        """
        tasks = []
        todo_pattern = re.compile(r'#\s*(TODO|FIXME):\s*(.+)', re.IGNORECASE)
        
        for file_path in self._find_source_files():
            if self._should_ignore(file_path):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                for line_num, line in enumerate(lines, 1):
                    match = todo_pattern.search(line)
                    if match:
                        task_type = match.group(1).upper()
                        description = f"{task_type}: {match.group(2).strip()}"
                        
                        # Get context (3 lines before and after)
                        start = max(0, line_num - 3)
                        end = min(len(lines), line_num + 2)
                        context = ''.join(lines[start:end])
                        
                        tasks.append(Task(
                            type=TaskType.TODO if task_type == "TODO" else TaskType.FIXME,
                            description=description,
                            file_path=str(file_path.relative_to(self.repo_path)),
                            line_number=line_num,
                            priority=2 if task_type == "FIXME" else 1,
                            context=context
                        ))
            except Exception:
                # Skip files that can't be read
                continue
        
        return tasks
    
    def find_failing_tests(self) -> List[Task]:
        """Find failing tests using pytest.
        
        Returns:
            List of failing test tasks
        """
        tasks = []
        
        try:
            # Run pytest with minimal output
            result = subprocess.run(
                ["poetry", "run", "pytest", "--tb=no", "-q", str(self.repo_path)],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
                timeout=30
            )
            
            if result.returncode != 0:
                # Parse pytest output for failures
                for line in result.stdout.split('\n'):
                    if 'FAILED' in line:
                        # Extract test name and file
                        parts = line.split('::')
                        if len(parts) >= 2:
                            file_path = parts[0].replace('FAILED ', '').strip()
                            test_name = parts[1].split(' ')[0] if ' ' in parts[1] else parts[1]
                            
                            tasks.append(Task(
                                type=TaskType.FAILING_TEST,
                                description=f"Failing test: {test_name}",
                                file_path=file_path,
                                line_number=1,  # Would need AST parsing for exact line
                                priority=3
                            ))
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # pytest not available or timed out
            pass
        except Exception:
            # Other errors - skip test detection
            pass
        
        return tasks
    
    def find_type_errors(self) -> List[Task]:
        """Find type errors using mypy.
        
        Returns:
            List of type error tasks
        """
        tasks = []
        
        try:
            # Run mypy
            result = subprocess.run(
                ["mypy", "--no-error-summary", "--no-color-output", str(self.repo_path)],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
                timeout=30
            )
            
            if result.returncode != 0:
                # Parse mypy output
                for line in result.stdout.split('\n'):
                    if ': error:' in line:
                        # Extract file, line, and error message
                        match = re.match(r'(.+):(\d+):\s*error:\s*(.+)', line)
                        if match:
                            file_path = match.group(1)
                            line_number = int(match.group(2))
                            error_msg = match.group(3)
                            
                            tasks.append(Task(
                                type=TaskType.TYPE_ERROR,
                                description=f"Type error: {error_msg}",
                                file_path=file_path,
                                line_number=line_number,
                                priority=4
                            ))
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # mypy not available or timed out
            pass
        except Exception:
            # Other errors - skip type checking
            pass
        
        return tasks
    
    def parse_git_diff(self) -> List[Task]:
        """Parse git diff for uncommitted changes.
        
        Returns:
            List of uncommitted change tasks
        """
        tasks = []
        
        try:
            # Get list of modified files
            result = subprocess.run(
                ["git", "diff", "--name-only"],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
                timeout=TIMEOUT_SECONDS
            )
            
            if result.returncode == 0 and result.stdout.strip():
                modified_files = result.stdout.strip().split('\n')
                
                for file_path in modified_files:
                    tasks.append(Task(
                        type=TaskType.UNCOMMITTED,
                        description=f"Uncommitted changes in {file_path}",
                        file_path=file_path,
                        line_number=1,
                        priority=1
                    ))
        except (subprocess.CalledProcessError, FileNotFoundError):
            # git not available or not a git repository
            pass
        
        return tasks
    
    def prioritize_tasks(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks by priority (highest first).
        
        Args:
            tasks: List of tasks to prioritize
            
        Returns:
            Sorted list of tasks
        """
        return sorted(tasks, key=lambda t: t.priority, reverse=True)
    
    def _find_source_files(self) -> List[Path]:
        """Find all source files in repository.
        
        Returns:
            List of source file paths
        """
        source_extensions = ['.py', '.js', '.ts', '.jsx', '.tsx', '.go', '.rs', '.java', '.c', '.cpp', '.h']
        files = []
        
        for ext in source_extensions:
            files.extend(self.repo_path.rglob(f'*{ext}'))
        
        return files
    
    def _should_ignore(self, file_path: Path) -> bool:
        """Check if file should be ignored based on patterns.
        
        Args:
            file_path: Path to check
            
        Returns:
            True if file should be ignored
        """
        path_str = str(file_path)
        
        for pattern in self.ignore_patterns:
            # Check if any part of the path matches the pattern
            if pattern in path_str:
                return True
            # Check glob patterns
            if fnmatch.fnmatch(path_str, pattern):
                return True
            # Check if any parent directory matches
            for parent in file_path.parents:
                if parent.name == pattern:
                    return True
        
        return False


# Module-level convenience functions

def scan_repository(repo_path: str = ".") -> List[Task]:
    """Scan repository for issues.
    
    Args:
        repo_path: Path to repository
        
    Returns:
        List of tasks found
    """
    scanner = RepoScanner(repo_path)
    return scanner.scan()


def find_todos(repo_path: str = ".") -> List[Task]:
    """Find TODO and FIXME comments.
    
    Args:
        repo_path: Path to repository
        
    Returns:
        List of TODO/FIXME tasks
    """
    scanner = RepoScanner(repo_path)
    return scanner.find_todos()


def find_failing_tests(repo_path: str = ".") -> List[Task]:
    """Find failing tests.
    
    Args:
        repo_path: Path to repository
        
    Returns:
        List of failing test tasks
    """
    scanner = RepoScanner(repo_path)
    return scanner.find_failing_tests()


def parse_git_diff(repo_path: str = ".") -> List[Task]:
    """Parse git diff for uncommitted changes.
    
    Args:
        repo_path: Path to repository
        
    Returns:
        List of uncommitted change tasks
    """
    scanner = RepoScanner(repo_path)
    return scanner.parse_git_diff()
