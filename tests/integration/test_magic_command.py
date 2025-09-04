"""
Integration tests for Phase 2: The Magic Command
Tests the unified CLI interface that delivers immediate value.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch

from ai.cli.magic import MagicCommand
from ai.memory.intelligent_store import IntelligentMemoryStore


class TestMagicCommand:
    """Test the unified magic command interface."""
    
    @pytest.fixture
    def temp_repo(self):
        """Create temporary repository for testing."""
        temp_dir = Path(tempfile.mkdtemp())
        
        # Initialize as git repo
        import subprocess
        subprocess.run(["git", "init"], cwd=temp_dir, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=temp_dir, check=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=temp_dir, check=True)
        
        # Create test files with issues
        (temp_dir / "src").mkdir()
        (temp_dir / "src" / "__init__.py").write_text("")
        (temp_dir / "src" / "calculator.py").write_text('''
def add(a, b):
    return a + b

def divide(a, b):
    return a / b  # Bug: division by zero not handled

def multiply(a, b):
    return a * b

# TODO: Add input validation
''')
        
        (temp_dir / "tests").mkdir() 
        (temp_dir / "tests" / "__init__.py").write_text("")
        # No actual tests yet - this is what magic command should fix
        
        # Initial commit
        subprocess.run(["git", "add", "."], cwd=temp_dir, check=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=temp_dir, check=True)
        
        yield temp_dir
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def magic_command(self, temp_repo):
        """Create MagicCommand instance."""
        memory_store = IntelligentMemoryStore()
        return MagicCommand(
            working_directory=str(temp_repo),
            memory_store=memory_store
        )
    
    def test_fix_command_identifies_issue(self, magic_command, temp_repo):
        """Test that 'fresh fix' can identify and fix issues."""
        # Test command: fresh fix "the divide function crashes"
        
        with patch.object(magic_command, '_show_progress') as mock_progress:
            result = magic_command.fix("the divide function crashes")
            
            assert result['success'] == True
            assert result['issue_identified'] == True
            assert 'division by zero' in result['description'].lower()
            
            # Should have shown progress
            assert mock_progress.call_count > 0
            
            # Should have created a fix
            assert 'solution' in result
            assert 'files_changed' in result
    
    def test_add_command_creates_feature(self, magic_command, temp_repo):
        """Test that 'fresh add' can add new features."""
        # Test command: fresh add "input validation for calculator functions"
        
        result = magic_command.add("input validation for calculator functions")
        
        assert result['success'] == True
        assert result['feature_added'] == True
        assert 'validation' in result['description'].lower()
        
        # Should have identified where to add the feature
        assert 'files_changed' in result
        assert len(result['files_changed']) > 0
    
    def test_test_command_adds_tests(self, magic_command, temp_repo):
        """Test that 'fresh test' can add comprehensive tests."""
        # Test command: fresh test "add unit tests for calculator functions" 
        
        result = magic_command.test("add unit tests for calculator functions")
        
        assert result['success'] == True
        assert result['tests_added'] == True
        
        # Should have created test files
        assert 'files_changed' in result
        test_files = [f for f in result['files_changed'] if 'test' in f.lower()]
        assert len(test_files) > 0
    
    def test_refactor_command_improves_code(self, magic_command, temp_repo):
        """Test that 'fresh refactor' can improve code structure."""
        # Test command: fresh refactor "extract validation logic to separate module"
        
        result = magic_command.refactor("extract validation logic to separate module")
        
        assert result['success'] == True
        assert result['refactored'] == True
        
        # Should have created new files or modified existing ones
        assert 'files_changed' in result
        assert len(result['files_changed']) > 0
    
    def test_command_with_progress_tracking(self, magic_command, temp_repo):
        """Test that commands show progress updates."""
        progress_updates = []
        
        def capture_progress(update):
            progress_updates.append(update)
        
        magic_command.on_progress = capture_progress
        
        result = magic_command.fix("division by zero error")
        
        # Should have received multiple progress updates
        assert len(progress_updates) >= 3
        
        # Should show key phases
        phases = [update.get('phase') for update in progress_updates]
        expected_phases = ['scanning', 'analyzing', 'generating', 'validating']
        for phase in expected_phases[:3]:  # At least first 3 phases
            assert any(phase in p for p in phases if p)
    
    def test_command_uses_memory_patterns(self, magic_command, temp_repo):
        """Test that commands use memory to improve over time."""
        memory_store = magic_command.memory_store
        
        # Add a successful pattern to memory
        memory_store.write(
            content="Successfully fixed division by zero by adding if b == 0 check",
            tags=["pattern", "division", "validation", "success"]
        )
        
        # Run command that should benefit from this pattern
        result = magic_command.fix("division by zero in calculator")
        
        assert result['success'] == True
        assert result.get('used_patterns') == True
        
        # Should have found the pattern in memory
        assert 'pattern_confidence' in result
        assert result['pattern_confidence'] > 0.5
    
    def test_command_creates_pr(self, magic_command, temp_repo):
        """Test that commands can create pull requests.""" 
        with patch.object(magic_command, '_create_pull_request') as mock_pr:
            mock_pr.return_value = {
                'pr_number': 42,
                'pr_url': 'https://github.com/test/repo/pull/42',
                'status': 'created'
            }
            
            result = magic_command.fix("division by zero", create_pr=True)
            
            assert result['success'] == True
            assert result['pr_created'] == True
            assert result['pr_number'] == 42
            assert 'github.com' in result['pr_url']
    
    def test_command_error_handling(self, magic_command, temp_repo):
        """Test that commands handle errors gracefully."""
        # Test with invalid/unclear instruction
        result = magic_command.fix("make it better somehow")
        
        # Should not crash, but should indicate unclear instruction
        assert 'error' in result or result.get('success') == False
        assert 'unclear' in str(result).lower() or 'specific' in str(result).lower()
    
    def test_natural_language_parsing(self, magic_command, temp_repo):
        """Test that commands can parse natural language instructions."""
        test_cases = [
            ("fix the bug in divide function", {"action": "fix", "target": "divide function", "type": "bug"}),
            ("add error handling to all math operations", {"action": "add", "feature": "error handling", "scope": "math operations"}),
            ("write tests for the calculator module", {"action": "test", "target": "calculator module"}),
            ("refactor validation logic into utils", {"action": "refactor", "what": "validation logic", "where": "utils"})
        ]
        
        for instruction, expected in test_cases:
            parsed = magic_command._parse_instruction(instruction)
            
            assert parsed.action == expected['action']
            # Check that key elements are identified
            for key, value in expected.items():
                if key != 'action':
                    assert value.lower() in str(parsed).lower()


class TestMagicCommandIntegration:
    """Test magic command integration with real workflows."""
    
    @pytest.fixture
    def integration_repo(self):
        """Create a more complex repository for integration testing."""
        temp_dir = Path(tempfile.mkdtemp())
        
        # Initialize git repo
        import subprocess
        subprocess.run(["git", "init"], cwd=temp_dir, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=temp_dir, check=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=temp_dir, check=True)
        
        # Create a more realistic project structure
        (temp_dir / "src").mkdir()
        (temp_dir / "src" / "api").mkdir()
        (temp_dir / "src" / "models").mkdir()
        (temp_dir / "tests").mkdir()
        
        # API with authentication issues
        (temp_dir / "src" / "api" / "__init__.py").write_text("")
        (temp_dir / "src" / "api" / "auth.py").write_text('''
import hashlib

def hash_password(password):
    # TODO: Add salt for security
    return hashlib.md5(password.encode()).hexdigest()

def verify_password(password, hash):
    return hash_password(password) == hash

# Missing: rate limiting, input validation
''')
        
        # Models with type issues
        (temp_dir / "src" / "models" / "__init__.py").write_text("")
        (temp_dir / "src" / "models" / "user.py").write_text('''
class User:
    def __init__(self, username, email):
        self.username = username  # No validation
        self.email = email        # No email validation
        
    def to_dict(self):
        return {
            "username": self.username,
            "email": self.email
        }
        
    # Missing: type hints, validation methods
''')
        
        # Minimal tests
        (temp_dir / "tests" / "__init__.py").write_text("")
        (temp_dir / "tests" / "test_auth.py").write_text('''
# Placeholder test file - no actual tests yet
''')
        
        # Requirements
        (temp_dir / "requirements.txt").write_text("flask==2.3.3\npytest==7.4.2\n")
        
        # Initial commit
        subprocess.run(["git", "add", "."], cwd=temp_dir, check=True)
        subprocess.run(["git", "commit", "-m", "Initial project setup"], cwd=temp_dir, check=True)
        
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_comprehensive_security_fix(self, integration_repo):
        """Test fixing multiple security issues in one command."""
        magic_command = MagicCommand(
            working_directory=str(integration_repo),
            memory_store=IntelligentMemoryStore()
        )
        
        # Command to fix security issues
        result = magic_command.fix("security vulnerabilities in authentication")
        
        assert result['success'] == True
        assert 'security' in result['description'].lower()
        
        # Should have identified multiple issues
        issues = result.get('issues_found', [])
        assert len(issues) >= 2  # MD5 hashing, no salt, etc.
        
        # Should propose comprehensive fixes
        assert 'salt' in str(result).lower() or 'bcrypt' in str(result).lower()
        assert 'validation' in str(result).lower()
    
    def test_add_comprehensive_testing(self, integration_repo):
        """Test adding comprehensive test suite."""
        magic_command = MagicCommand(
            working_directory=str(integration_repo),
            memory_store=IntelligentMemoryStore()
        )
        
        result = magic_command.test("create comprehensive test suite for the API")
        
        assert result['success'] == True
        assert result.get('tests_added') == True
        
        # Should have created multiple test files
        files_changed = result.get('files_changed', [])
        test_files = [f for f in files_changed if 'test' in f]
        assert len(test_files) >= 2  # auth tests, model tests, etc.
    
    def test_end_to_end_workflow(self, integration_repo):
        """Test complete workflow: fix → test → refactor."""
        magic_command = MagicCommand(
            working_directory=str(integration_repo),
            memory_store=IntelligentMemoryStore()
        )
        
        # Step 1: Fix security issues
        fix_result = magic_command.fix("authentication security issues")
        assert fix_result['success'] == True
        
        # Step 2: Add tests for the fixes
        test_result = magic_command.test("add tests for authentication security")
        assert test_result['success'] == True
        
        # Step 3: Refactor if needed
        refactor_result = magic_command.refactor("improve code organization")
        assert refactor_result['success'] == True
        
        # Memory should have recorded all actions
        memories = magic_command.memory_store.query(tags=["magic_command"], limit=10)
        assert len(memories) >= 3  # One for each step
