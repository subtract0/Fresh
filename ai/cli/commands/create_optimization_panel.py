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
        raise ValueError("Unsupported config file format. Please use JSON or YAML.")

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def create_optimization_panel(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    create_optimization_panel command.
    This command creates an optimization panel based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running create_optimization_panel command...[/blue]")
        
        config_data = {}
        if config:
            config_data = load_config(config)
            if verbose:
                console.print(f"[yellow]Loaded configuration: {config_data}[/yellow]")

        # Simulate optimization panel creation logic
        optimization_results = {
            "optimization_parameters": config_data.get("parameters", {}),
            "status": "success",
            "message": "Optimization panel created successfully"
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(optimization_results, indent=2))
        elif output == 'table':
            table = Table(title=f"create_optimization_panel Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in optimization_results.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in optimization_results.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ create_optimization_panel completed successfully[/green]")
            
    except ValueError as ve:
        console.print(f"[red]❌ create_optimization_panel failed: {str(ve)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ create_optimization_panel failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["create_optimization_panel"]