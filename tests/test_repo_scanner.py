"""Tests for Repository Scanner that detects issues in codebase.

The scanner identifies TODOs, FIXMEs, failing tests, and other issues
that agents can autonomously fix.
"""
from __future__ import annotations
import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch
import subprocess

from ai.loop.repo_scanner import (
    RepoScanner, 
    Task,
    TaskType,
    scan_repository,
    find_todos,
    find_failing_tests,
    parse_git_diff
)


class TestRepoScanner:
    """Test Repository Scanner functionality."""
    
    def test_scanner_initialization(self):
        """Test scanner can be initialized with repo path."""
        scanner = RepoScanner(repo_path=".")
        
        assert scanner is not None
        assert scanner.repo_path == Path(".")
    
    def test_find_todos_in_files(self, tmp_path):
        """Test finding TODO and FIXME comments in code."""
        # Create test files with TODOs
        test_file = tmp_path / "test.py"
        test_file.write_text("""
def example():
    # TODO: Implement this function
    pass
    
# FIXME: This is broken  # Test data for scanner
def broken():
    return None
""")
        
        scanner = RepoScanner(repo_path=tmp_path)
        tasks = scanner.find_todos()
        
        assert len(tasks) == 2
        assert any(t.description == "TODO: Implement this function" for t in tasks)
        assert any("FIXME: This is broken" in t.description for t in tasks)  # Allow for partial match
        # Check task types - one TODO, one FIXME
        task_types = [t.type for t in tasks]
        assert TaskType.TODO in task_types
        assert TaskType.FIXME in task_types
    
    def test_find_failing_tests(self, tmp_path):
        """Test detection of failing tests."""
        # Create a failing test file
        test_file = tmp_path / "test_example.py"
        test_file.write_text("""
def test_failing():
    assert 1 == 2  # This will fail
    
def test_passing():
    assert 1 == 1  # This will pass
""")
        
        scanner = RepoScanner(repo_path=tmp_path)
        
        # Mock pytest output
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                returncode=1,
                stdout="FAILED test_example.py::test_failing - AssertionError"
            )
            
            tasks = scanner.find_failing_tests()
        
        assert len(tasks) >= 1
        assert tasks[0].type == TaskType.FAILING_TEST
        assert "test_failing" in tasks[0].description
    
    def test_parse_git_diff(self, tmp_path):
        """Test parsing git diff for uncommitted changes."""
        scanner = RepoScanner(repo_path=tmp_path)
        
        # Mock git diff output
        diff_output = """
diff --git a/module.py b/module.py
index abc123..def456 100644
--- a/module.py
+++ b/module.py
@@ -1,3 +1,3 @@
 def function():
-    return "old"
+    return "new"  # TODO: Review this change
"""
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                returncode=0,
                stdout=diff_output,
                stderr=""
            )
            
            tasks = scanner.parse_git_diff()
        
        assert len(tasks) >= 1
        assert any(t.type == TaskType.UNCOMMITTED for t in tasks)
    
    def test_scan_repository_comprehensive(self, tmp_path):
        """Test comprehensive repository scanning."""
        # Create test repository structure
        (tmp_path / "src").mkdir()
        (tmp_path / "tests").mkdir()
        
        # Add file with TODO
        src_file = tmp_path / "src" / "app.py"
        src_file.write_text("# TODO: Add authentication\nclass App: pass")
        
        # Add failing test
        test_file = tmp_path / "tests" / "test_app.py"
        test_file.write_text("def test_app():\n    assert False")
        
        scanner = RepoScanner(repo_path=tmp_path)
        
        # Mock subprocess calls
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
            
            tasks = scanner.scan()
        
        assert len(tasks) >= 1
        assert any(t.type == TaskType.TODO for t in tasks)
    
    def test_task_priority_ordering(self):
        """Test that tasks are ordered by priority."""
        scanner = RepoScanner(repo_path=".")
        
        tasks = [
            Task(type=TaskType.TODO, description="Low priority", 
                 file_path="file.py", line_number=1, priority=1),
            Task(type=TaskType.FAILING_TEST, description="High priority",
                 file_path="test.py", line_number=1, priority=3),
            Task(type=TaskType.SYNTAX_ERROR, description="Critical",
                 file_path="error.py", line_number=1, priority=5),
        ]
        
        sorted_tasks = scanner.prioritize_tasks(tasks)
        
        assert sorted_tasks[0].priority == 5
        assert sorted_tasks[1].priority == 3
        assert sorted_tasks[2].priority == 1
    
    def test_task_to_dict(self):
        """Test Task serialization to dictionary."""
        task = Task(
            type=TaskType.TODO,
            description="Implement feature",
            file_path="module.py",
            line_number=42,
            priority=2,
            context="def feature():\n    # TODO: Implement feature"
        )
        
        task_dict = task.to_dict()
        
        assert task_dict["type"] == "TODO"
        assert task_dict["description"] == "Implement feature"
        assert task_dict["file_path"] == "module.py"
        assert task_dict["line_number"] == 42
        assert task_dict["priority"] == 2
        assert "context" in task_dict
    
    def test_ignore_patterns(self, tmp_path):
        """Test that scanner respects ignore patterns."""
        # Create files in ignored directories
        (tmp_path / "node_modules").mkdir()
        (tmp_path / "node_modules" / "lib.js").write_text("// TODO: Ignored")
        
        (tmp_path / ".git").mkdir()
        (tmp_path / ".git" / "config").write_text("# TODO: Also ignored")
        
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "app.py").write_text("# TODO: Should be found")
        
        scanner = RepoScanner(
            repo_path=tmp_path,
            ignore_patterns=["node_modules", ".git", "__pycache__", "*.pyc"]
        )
        
        tasks = scanner.find_todos()
        
        assert len(tasks) == 1
        assert tasks[0].description == "TODO: Should be found"
    
    def test_find_type_errors(self, tmp_path):
        """Test detection of type errors using mypy or similar."""
        test_file = tmp_path / "typed.py"
        test_file.write_text("""
def add(a: int, b: int) -> int:
    return a + b

result = add("1", "2")  # Type error
""")
        
        scanner = RepoScanner(repo_path=tmp_path)
        
        # Mock mypy output
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                returncode=1,
                stdout="typed.py:5: error: Argument 1 to \"add\" has incompatible type \"str\"; expected \"int\""
            )
            
            tasks = scanner.find_type_errors()
        
        assert len(tasks) >= 1
        assert tasks[0].type == TaskType.TYPE_ERROR
        assert "incompatible type" in tasks[0].description
    
    def test_scanner_with_no_issues(self, tmp_path):
        """Test scanner with clean repository."""
        # Create clean file
        clean_file = tmp_path / "clean.py"
        clean_file.write_text("""
def perfect_function():
    '''A function with no issues.'''
    return 42
""")
        
        scanner = RepoScanner(repo_path=tmp_path)
        tasks = scanner.scan()
        
        assert len(tasks) == 0
    
    def test_scan_repository_function(self, tmp_path):
        """Test the module-level scan_repository function."""
        # Create test file
        test_file = tmp_path / "app.py"
        test_file.write_text("# TODO: Test this\nprint('hello')")
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
            
            tasks = scan_repository(str(tmp_path))
        
        assert isinstance(tasks, list)
        assert all(isinstance(t, Task) for t in tasks)


class TestTask:
    """Test the Task data structure."""
    
    def test_task_creation(self):
        """Test creating a Task."""
        task = Task(
            type=TaskType.TODO,
            description="Implement feature",
            file_path="module.py",
            line_number=10,
            priority=2
        )
        
        assert task.type == TaskType.TODO
        assert task.description == "Implement feature"
        assert task.file_path == "module.py"
        assert task.line_number == 10
        assert task.priority == 2
    
    def test_task_type_enum(self):
        """Test TaskType enumeration."""
        assert TaskType.TODO.value == "TODO"
        assert TaskType.FIXME.value == "FIXME"
        assert TaskType.FAILING_TEST.value == "FAILING_TEST"
        assert TaskType.SYNTAX_ERROR.value == "SYNTAX_ERROR"
        assert TaskType.TYPE_ERROR.value == "TYPE_ERROR"
        assert TaskType.UNCOMMITTED.value == "UNCOMMITTED"
    
    def test_task_equality(self):
        """Test Task equality comparison."""
        task1 = Task(
            type=TaskType.TODO,
            description="Same task",
            file_path="file.py",
            line_number=1
        )
        
        task2 = Task(
            type=TaskType.TODO,
            description="Same task",
            file_path="file.py",
            line_number=1
        )
        
        assert task1 == task2
    
    def test_task_with_context(self):
        """Test Task with code context."""
        task = Task(
            type=TaskType.TODO,
            description="Fix this",
            file_path="app.py",
            line_number=5,
            context="def broken():\n    # TODO: Fix this\n    return None"
        )
        
        assert task.context is not None
        assert "TODO: Fix this" in task.context


class TestModuleFunctions:
    """Test module-level convenience functions."""
    
    def test_find_todos_function(self, tmp_path):
        """Test module-level find_todos function."""
        test_file = tmp_path / "test.py"
        test_file.write_text("# TODO: Test todo")
        
        tasks = find_todos(str(tmp_path))
        
        assert len(tasks) >= 1
        assert tasks[0].type == TaskType.TODO
    
    def test_find_failing_tests_function(self):
        """Test module-level find_failing_tests function."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                returncode=1,
                stdout="FAILED test_example.py::test_fail"
            )
            
            tasks = find_failing_tests(".")
        
        assert isinstance(tasks, list)
    
    def test_parse_git_diff_function(self):
        """Test module-level parse_git_diff function."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                returncode=0,
                stdout="diff --git a/file.py b/file.py"
            )
            
            tasks = parse_git_diff(".")
        
        assert isinstance(tasks, list)