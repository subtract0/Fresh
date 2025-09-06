import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import yaml

console = Console()

def load_config(config_path: str):
    if config_path.endswith('.json'):
        with open(config_path, 'r') as f:
            return json.load(f)
    elif config_path.endswith('.yaml') or config_path.endswith('.yml'):
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    else:
        raise ValueError("Unsupported config file format. Use JSON or YAML.")

def perform_tracked_query(config: dict):
    # Simulate a tracked query operation based on the provided configuration
    if 'query' not in config:
        raise ValueError("Configuration must include a 'query' key.")
    
    # Here you would implement the actual logic for the tracked query
    # For demonstration, we return a mock result
    return {
        "query": config['query'],
        "result": "mock_result_data",
        "status": "success"
    }

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file', required=True)
@click.pass_context
def trackedquery(ctx, verbose: bool, output: str, config: str):
    """
    TrackedQuery command.
    
    Executes a tracked query based on the provided configuration file.
    """
    try:
        if verbose:
            console.print(f"[blue]Running TrackedQuery command...[/blue]")
        
        config_data = load_config(config)
        
        result_data = perform_tracked_query(config_data)
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"TrackedQuery Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ TrackedQuery completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ TrackedQuery failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["trackedquery"]