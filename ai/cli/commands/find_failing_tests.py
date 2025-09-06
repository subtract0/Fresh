import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import unittest

console = Console()

def discover_tests(test_directory: str):
    loader = unittest.TestLoader()
    suite = loader.discover(test_directory)
    return suite

def find_failing_tests_in_suite(suite):
    failing_tests = []
    for test_case in suite:
        for test in test_case:
            result = unittest.TextTestRunner().run(test)
            if not result.wasSuccessful():
                failing_tests.append(str(test))
    return failing_tests

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def find_failing_tests(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    find_failing_tests command.
    This command discovers and runs tests in the specified directory,
    reporting any that fail.
    """
    try:
        if verbose:
            console.print(f"[blue]Running find_failing_tests command...[/blue]")
        
        if config is None:
            console.print(f"[red]❌ Configuration file is required.[/red]")
            ctx.exit(1)

        config_path = Path(config)
        if not config_path.is_file():
            console.print(f"[red]❌ Configuration file does not exist: {config}[/red]")
            ctx.exit(1)

        with open(config_path) as f:
            config_data = json.load(f)

        test_directory = config_data.get("test_directory")
        if not test_directory:
            console.print(f"[red]❌ 'test_directory' not found in configuration.[/red]")
            ctx.exit(1)

        suite = discover_tests(test_directory)
        failing_tests = find_failing_tests_in_suite(suite)

        result_data = {
            "feature": "find_failing_tests",
            "status": "completed",
            "failing_tests": failing_tests,
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"find_failing_tests Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ find_failing_tests completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ find_failing_tests failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["find_failing_tests"]