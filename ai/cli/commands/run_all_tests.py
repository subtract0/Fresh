import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import unittest

console = Console()

def discover_and_run_tests(test_dir: str):
    loader = unittest.TestLoader()
    suite = loader.discover(test_dir)
    runner = unittest.TextTestRunner()
    result = runner.run(suite)
    return result

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def run_all_tests(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    run_all_tests command.
    This command discovers and runs all unit tests in the specified directory.
    """
    try:
        if verbose:
            console.print(f"[blue]Running run_all_tests command...[/blue]")
        
        if config:
            with open(config, 'r') as f:
                config_data = json.load(f)
                test_dir = config_data.get("test_directory", ".")
        else:
            test_dir = "."

        if not Path(test_dir).exists():
            raise ValueError(f"Test directory '{test_dir}' does not exist.")

        result = discover_and_run_tests(test_dir)

        result_data = {
            "feature": "run_all_tests",
            "status": "success" if result.wasSuccessful() else "failure",
            "total_tests": result.testsRun,
            "failures": len(result.failures),
            "errors": len(result.errors),
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"run_all_tests Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ run_all_tests completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ run_all_tests failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["run_all_tests"]