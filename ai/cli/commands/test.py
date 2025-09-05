import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import os

console = Console()

def load_config(config_path: str):
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    with open(config_path, 'r') as file:
        return json.load(file)

def run_tests(config):
    # Placeholder for actual test logic
    # Simulating test results based on configuration
    results = []
    for feature in config.get("features", []):
        results.append({
            "feature": feature,
            "status": "passed" if feature.get("enabled", False) else "skipped",
            "message": f"Test for {feature['name']} executed."
        })
    return results

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file', required=True)
@click.pass_context
def test(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    Run tests based on the provided configuration file.
    """
    try:
        if verbose:
            console.print(f"[blue]Running test command...[/blue]")
        
        config_data = load_config(config)
        
        if verbose:
            console.print(f"[blue]Loaded configuration: {json.dumps(config_data, indent=2)}[/blue]")
        
        results = run_tests(config_data)
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(results, indent=2))
        elif output == 'table':
            table = Table(title=f"Test Results")
            table.add_column("Feature", style="cyan")
            table.add_column("Status", style="magenta")
            table.add_column("Message", style="green")
            
            for result in results:
                table.add_row(result["feature"], result["status"], result["message"])
            
            console.print(table)
        else:  # plain
            for result in results:
                console.print(f"Feature: {result['feature']}, Status: {result['status']}, Message: {result['message']}")
        
        if verbose:
            console.print(f"[green]✅ Test completed successfully[/green]")
            
    except FileNotFoundError as fnf_error:
        console.print(f"[red]❌ Configuration error: {str(fnf_error)}[/red]")
        ctx.exit(1)
    except json.JSONDecodeError as json_error:
        console.print(f"[red]❌ JSON error: {str(json_error)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ Test failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["test"]