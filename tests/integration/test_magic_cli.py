"""
Integration tests for the Magic Command CLI interface.
"""

import pytest
import tempfile
import shutil
import subprocess
from pathlib import Path
from click.testing import CliRunner

from ai.cli.magic_cli import cli


class TestMagicCLI:
    """Test the CLI interface for magic commands."""
    
    @pytest.fixture
    def temp_repo(self):
        """Create temporary repository for testing."""
        temp_dir = Path(tempfile.mkdtemp())
        
        # Initialize as git repo
        subprocess.run(["git", "init"], cwd=temp_dir, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=temp_dir, check=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=temp_dir, check=True)
        
        # Create test files
        (temp_dir / "src").mkdir()
        (temp_dir / "src" / "__init__.py").write_text("")
        (temp_dir / "src" / "calculator.py").write_text('''
def add(a, b):
    return a + b

def divide(a, b):
    return a / b  # Bug: division by zero not handled

# TODO: Add input validation
''')
        
        # Initial commit
        subprocess.run(["git", "add", "."], cwd=temp_dir, check=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=temp_dir, check=True)
        
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_cli_fix_command(self, temp_repo):
        """Test the CLI fix command."""
        runner = CliRunner()
        
        with runner.isolated_filesystem():
            # Change to temp repo
            result = runner.invoke(cli, [
                '--directory', str(temp_repo),
                'fix', 'division by zero in calculator'
            ])
            
            assert result.exit_code == 0
            assert "Success!" in result.output
            assert "division by zero" in result.output.lower()
    
    def test_cli_add_command(self, temp_repo):
        """Test the CLI add command."""
        runner = CliRunner()
        
        result = runner.invoke(cli, [
            '--directory', str(temp_repo),
            'add', 'input validation for calculator functions'
        ])
        
        assert result.exit_code == 0
        assert "Success!" in result.output
        assert "validation" in result.output.lower()
    
    def test_cli_test_command(self, temp_repo):
        """Test the CLI test command."""
        runner = CliRunner()
        
        result = runner.invoke(cli, [
            '--directory', str(temp_repo),
            'test', 'comprehensive tests for calculator'
        ])
        
        assert result.exit_code == 0
        assert "Success!" in result.output
        assert "test" in result.output.lower()
    
    def test_cli_refactor_command(self, temp_repo):
        """Test the CLI refactor command."""
        runner = CliRunner()
        
        result = runner.invoke(cli, [
            '--directory', str(temp_repo),
            'refactor', 'extract validation logic'
        ])
        
        assert result.exit_code == 0
        assert "Success!" in result.output
        assert "refactor" in result.output.lower()
    
    def test_cli_status_command(self, temp_repo):
        """Test the CLI status command."""
        runner = CliRunner()
        
        result = runner.invoke(cli, [
            '--directory', str(temp_repo),
            'status'
        ])
        
        assert result.exit_code == 0
        assert "Fresh AI Status" in result.output
        assert str(temp_repo) in result.output
    
    def test_cli_memory_command(self, temp_repo):
        """Test the CLI memory command."""
        runner = CliRunner()
        
        # First run a command to create memory
        runner.invoke(cli, [
            '--directory', str(temp_repo),
            'fix', 'division by zero'
        ])
        
        # Then check memory
        result = runner.invoke(cli, [
            '--directory', str(temp_repo),
            'memory'
        ])
        
        assert result.exit_code == 0
        assert "Fresh AI Memory" in result.output
    
    def test_cli_verbose_mode(self, temp_repo):
        """Test verbose mode shows progress."""
        runner = CliRunner()
        
        result = runner.invoke(cli, [
            '--directory', str(temp_repo),
            '--verbose',
            'fix', 'division by zero'
        ])
        
        assert result.exit_code == 0
        assert "PARSING" in result.output or "SCANNING" in result.output
        assert "Working directory:" in result.output
    
    def test_cli_invalid_directory(self):
        """Test error handling for invalid directory."""
        runner = CliRunner()
        
        result = runner.invoke(cli, [
            '--directory', '/nonexistent/directory',
            'fix', 'something'
        ])
        
        assert result.exit_code == 2  # Click parameter validation error
    
    def test_cli_non_git_directory(self):
        """Test error handling for non-git directory."""
        runner = CliRunner()
        
        with runner.isolated_filesystem():
            # Create a non-git directory
            temp_dir = Path("test_dir")
            temp_dir.mkdir()
            
            result = runner.invoke(cli, [
                '--directory', str(temp_dir),
                'fix', 'something'
            ])
            
            assert result.exit_code == 1
            assert "not a git repository" in result.output
    
    def test_cli_error_handling(self, temp_repo):
        """Test error handling for unclear commands."""
        runner = CliRunner()
        
        result = runner.invoke(cli, [
            '--directory', str(temp_repo),
            'fix', 'make it better'
        ])
        
        assert result.exit_code == 0  # Should succeed but indicate unclear
        assert "Failed!" in result.output or "unclear" in result.output.lower()
    
    def test_cli_help_commands(self):
        """Test help is displayed correctly."""
        runner = CliRunner()
        
        # Test main help
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert "Fresh AI" in result.output
        assert "fix" in result.output
        assert "add" in result.output
        assert "test" in result.output
        assert "refactor" in result.output
        
        # Test command-specific help
        result = runner.invoke(cli, ['fix', '--help'])
        assert result.exit_code == 0
        assert "Fix issues described in natural language" in result.output
        assert "Examples:" in result.output


class TestMagicCLIIntegration:
    """Test CLI integration with the existing system."""
    
    @pytest.fixture 
    def integration_repo(self):
        """Create a more complex repository."""
        temp_dir = Path(tempfile.mkdtemp())
        
        # Initialize git repo
        subprocess.run(["git", "init"], cwd=temp_dir, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=temp_dir, check=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=temp_dir, check=True)
        
        # Create realistic project structure
        (temp_dir / "src").mkdir()
        (temp_dir / "src" / "api").mkdir()
        (temp_dir / "tests").mkdir()
        
        (temp_dir / "src" / "__init__.py").write_text("")
        (temp_dir / "src" / "api" / "__init__.py").write_text("")
        (temp_dir / "src" / "api" / "auth.py").write_text('''
import hashlib

def hash_password(password):
    # TODO: Add salt for security
    return hashlib.md5(password.encode()).hexdigest()

def verify_password(password, hash):
    return hash_password(password) == hash
''')
        
        (temp_dir / "tests" / "__init__.py").write_text("")
        
        # Initial commit
        subprocess.run(["git", "add", "."], cwd=temp_dir, check=True)
        subprocess.run(["git", "commit", "-m", "Initial project"], cwd=temp_dir, check=True)
        
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_end_to_end_workflow(self, integration_repo):
        """Test complete CLI workflow: fix → test → status."""
        runner = CliRunner()
        
        # Step 1: Fix security issue
        result = runner.invoke(cli, [
            '--directory', str(integration_repo),
            '--verbose',
            'fix', 'security vulnerabilities in authentication'
        ])
        
        assert result.exit_code == 0
        assert "Success!" in result.output
        
        # Step 2: Add tests
        result = runner.invoke(cli, [
            '--directory', str(integration_repo),
            'test', 'tests for authentication security'
        ])
        
        assert result.exit_code == 0
        assert "Success!" in result.output
        
        # Step 3: Check status
        result = runner.invoke(cli, [
            '--directory', str(integration_repo),
            'status'
        ])
        
        assert result.exit_code == 0
        assert "Commands executed:" in result.output
    
    def test_memory_persistence_across_commands(self, integration_repo):
        """Test that memory persists across CLI commands."""
        runner = CliRunner()
        
        # Run first command
        runner.invoke(cli, [
            '--directory', str(integration_repo),
            'fix', 'password hashing security'
        ])
        
        # Check memory
        result = runner.invoke(cli, [
            '--directory', str(integration_repo),
            'memory'
        ])
        
        assert "magic_command" in result.output
        assert "password" in result.output.lower() or "hashing" in result.output.lower()
        
        # Run second command - should benefit from memory
        result = runner.invoke(cli, [
            '--directory', str(integration_repo),
            '--verbose',
            'fix', 'security in authentication'
        ])
        
        assert result.exit_code == 0
        # Should show pattern usage in verbose mode
        # assert "patterns" in result.output.lower()
