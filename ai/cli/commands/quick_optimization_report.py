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

def perform_optimization(config):
    # Placeholder for optimization logic
    # Simulate optimization process
    if 'parameters' not in config:
        raise ValueError("Configuration must contain 'parameters' key.")
    
    # Example optimization result
    return {
        "optimized_value": sum(config['parameters']),
        "status": "success",
        "details": "Optimization completed successfully."
    }

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def quick_optimization_report(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    quick_optimization_report command.
    Generates a quick optimization report based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running quick_optimization_report command...[/blue]")
        
        if not config:
            raise ValueError("Configuration file must be provided.")
        
        config_data = load_config(config)
        
        optimization_result = perform_optimization(config_data)
        
        result_data = {
            "feature": "quick_optimization_report",
            "status": optimization_result["status"], 
            "message": optimization_result["details"],
            "config_used": config,
            "optimized_value": optimization_result["optimized_value"],
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"quick_optimization_report Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ quick_optimization_report completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ quick_optimization_report failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["quick_optimization_report"]