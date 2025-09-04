"""
CLI interface for the Magic Command system.
Integrates with the existing Fresh CLI to provide natural language commands.
"""

import os
import sys
import click
import traceback
from pathlib import Path
from typing import Optional

from ai.cli.magic import MagicCommand
from ai.memory.intelligent_store import IntelligentMemoryStore


def show_progress(update):
    """Show progress updates to user."""
    phase = update.get('phase', '')
    message = update.get('message', '')
    
    if phase:
        click.echo(f"🔄 [{phase.upper()}] {message}")
    else:
        click.echo(f"ℹ️  {message}")


def show_result(result):
    """Display result of magic command."""
    if result['success']:
        click.echo("✅ Success!")
        click.echo(f"📝 {result['description']}")
        
        if 'files_changed' in result and result['files_changed']:
            click.echo(f"📁 Files changed: {len(result['files_changed'])}")
            for file in result['files_changed'][:5]:  # Show first 5
                click.echo(f"   • {file}")
            if len(result['files_changed']) > 5:
                click.echo(f"   ... and {len(result['files_changed']) - 5} more")
        
        if result.get('pr_created'):
            click.echo(f"🔗 Pull Request: {result['pr_url']}")
        
        if result.get('used_patterns'):
            confidence = result.get('pattern_confidence', 0)
            click.echo(f"🧠 Used learned patterns (confidence: {confidence:.1%})")
    
    else:
        click.echo("❌ Failed!")
        click.echo(f"💔 {result.get('error', 'Unknown error')}")
        
        if 'suggestion' in result:
            click.echo(f"💡 Suggestion: {result['suggestion']}")


@click.group(name='fresh')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.option('--directory', '-d', type=click.Path(exists=True, file_okay=False), 
              help='Working directory (defaults to current directory)')
@click.pass_context
def cli(ctx, verbose, directory):
    """Fresh AI - Natural language development commands."""
    # Ensure context dict exists
    ctx.ensure_object(dict)
    
    # Set working directory
    working_dir = directory or os.getcwd()
    ctx.obj['working_dir'] = Path(working_dir).resolve()
    ctx.obj['verbose'] = verbose
    
    # Initialize memory store and magic command
    try:
        memory_store = IntelligentMemoryStore()
        magic_command = MagicCommand(
            working_directory=str(ctx.obj['working_dir']),
            memory_store=memory_store,
            on_progress=show_progress if verbose else None
        )
        ctx.obj['magic_command'] = magic_command
        
        if verbose:
            click.echo(f"🏠 Working directory: {ctx.obj['working_dir']}")
            click.echo(f"🧠 Memory store: {type(memory_store).__name__}")
        
    except ValueError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        if verbose:
            click.echo(f"❌ Unexpected error: {e}", err=True)
            traceback.print_exc()
        else:
            click.echo(f"❌ Error initializing Fresh: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('description')
@click.option('--pr', is_flag=True, help='Create pull request with changes')
@click.pass_context
def fix(ctx, description: str, pr: bool):
    """Fix issues described in natural language.
    
    Examples:
        fresh fix "division by zero in calculator"
        fresh fix "security vulnerabilities in authentication"
        fresh fix "the user login crashes on invalid input"
    """
    magic_command = ctx.obj['magic_command']
    verbose = ctx.obj['verbose']
    
    try:
        if verbose:
            click.echo(f"🔧 Fixing: {description}")
            
        result = magic_command.fix(description, create_pr=pr)
        show_result(result)
        
    except Exception as e:
        if verbose:
            click.echo(f"❌ Error during fix: {e}", err=True)
            traceback.print_exc()
        else:
            click.echo(f"❌ Fix failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('description')
@click.option('--pr', is_flag=True, help='Create pull request with changes')
@click.pass_context
def add(ctx, description: str, pr: bool):
    """Add new features described in natural language.
    
    Examples:
        fresh add "input validation for user forms"
        fresh add "email notifications for new orders"
        fresh add "caching layer for database queries"
    """
    magic_command = ctx.obj['magic_command']
    verbose = ctx.obj['verbose']
    
    try:
        if verbose:
            click.echo(f"➕ Adding: {description}")
            
        result = magic_command.add(description, create_pr=pr)
        show_result(result)
        
    except Exception as e:
        if verbose:
            click.echo(f"❌ Error during add: {e}", err=True)
            traceback.print_exc()
        else:
            click.echo(f"❌ Add failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('description')
@click.option('--pr', is_flag=True, help='Create pull request with changes')
@click.pass_context
def test(ctx, description: str, pr: bool):
    """Add tests described in natural language.
    
    Examples:
        fresh test "comprehensive tests for user authentication"
        fresh test "edge case tests for payment processing"
        fresh test "integration tests for API endpoints"
    """
    magic_command = ctx.obj['magic_command']
    verbose = ctx.obj['verbose']
    
    try:
        if verbose:
            click.echo(f"🧪 Testing: {description}")
            
        result = magic_command.test(description, create_pr=pr)
        show_result(result)
        
    except Exception as e:
        if verbose:
            click.echo(f"❌ Error during test: {e}", err=True)
            traceback.print_exc()
        else:
            click.echo(f"❌ Test failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('description')
@click.option('--pr', is_flag=True, help='Create pull request with changes')
@click.pass_context
def refactor(ctx, description: str, pr: bool):
    """Refactor code as described in natural language.
    
    Examples:
        fresh refactor "extract validation logic into separate module"
        fresh refactor "consolidate database connection handling"
        fresh refactor "improve error handling throughout the API"
    """
    magic_command = ctx.obj['magic_command']
    verbose = ctx.obj['verbose']
    
    try:
        if verbose:
            click.echo(f"🔄 Refactoring: {description}")
            
        result = magic_command.refactor(description, create_pr=pr)
        show_result(result)
        
    except Exception as e:
        if verbose:
            click.echo(f"❌ Error during refactor: {e}", err=True)
            traceback.print_exc()
        else:
            click.echo(f"❌ Refactor failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def status(ctx):
    """Show status of the Fresh AI system."""
    magic_command = ctx.obj['magic_command']
    verbose = ctx.obj['verbose']
    
    click.echo("🤖 Fresh AI Status")
    click.echo(f"📍 Working directory: {ctx.obj['working_dir']}")
    click.echo(f"🧠 Memory store: {type(magic_command.memory_store).__name__}")
    
    # Check git status
    try:
        import subprocess
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=ctx.obj['working_dir'],
            capture_output=True,
            text=True,
            check=True
        )
        
        if result.stdout.strip():
            changes = len(result.stdout.strip().split('\n'))
            click.echo(f"🔄 Uncommitted changes: {changes} files")
        else:
            click.echo("✅ Working directory clean")
    except:
        click.echo("⚠️  Could not check git status")
    
    # Show memory statistics
    try:
        memories = magic_command.memory_store.query(tags=["magic_command"], limit=100)
        click.echo(f"📚 Commands executed: {len(memories)}")
        
        # Show recent commands if verbose
        if verbose and memories:
            click.echo("\n📜 Recent commands:")
            for mem in memories[:5]:
                click.echo(f"   • {mem.content[:80]}...")
    except:
        click.echo("⚠️  Could not access memory statistics")


@cli.command()
@click.pass_context
def memory(ctx):
    """Show and manage Fresh AI memory."""
    magic_command = ctx.obj['magic_command']
    
    try:
        memories = magic_command.memory_store.query(tags=[], limit=50)
        
        click.echo(f"🧠 Fresh AI Memory ({len(memories)} items)")
        click.echo()
        
        # Group by tags
        tag_counts = {}
        for mem in memories:
            tags = getattr(mem, 'tags', [])
            for tag in tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        if tag_counts:
            click.echo("📊 Memory by category:")
            for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True):
                click.echo(f"   {tag}: {count}")
        
        click.echo()
        click.echo("💭 Recent memories:")
        for i, mem in enumerate(memories[:10], 1):
            content = mem.content[:100] + "..." if len(mem.content) > 100 else mem.content
            click.echo(f"   {i}. {content}")
            
    except Exception as e:
        click.echo(f"❌ Could not access memory: {e}", err=True)


if __name__ == '__main__':
    cli()
