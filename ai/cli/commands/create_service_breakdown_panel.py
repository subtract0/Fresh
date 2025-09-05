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

def validate_config(config):
    required_keys = ['service_name', 'breakdown_details']
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required config key: {key}")

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def create_service_breakdown_panel(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    create_service_breakdown_panel command.
    This command generates a service breakdown panel based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running create_service_breakdown_panel command...[/blue]")
        
        config_data = {}
        if config:
            config_data = load_config(config)
            validate_config(config_data)

        # Simulate service breakdown generation
        breakdown = {
            "service_name": config_data.get('service_name', 'Default Service'),
            "breakdown_details": config_data.get('breakdown_details', [])
        }
        
        result_data = {
            "feature": "create_service_breakdown_panel",
            "status": "success", 
            "breakdown": breakdown,
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"create_service_breakdown_panel Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ create_service_breakdown_panel completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ create_service_breakdown_panel failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["create_service_breakdown_panel"]