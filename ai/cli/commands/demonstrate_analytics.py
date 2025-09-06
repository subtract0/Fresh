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

def perform_analytics(config):
    # Placeholder for actual analytics logic
    # Simulating some analytics results based on the config
    if 'data' not in config:
        raise ValueError("Configuration must include 'data' key.")
    
    data = config['data']
    # Simulate processing data
    processed_data = {"count": len(data), "average": sum(data) / len(data) if data else 0}
    
    return processed_data

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def demonstrate_analytics(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    demonstrate_analytics command.
    This command performs analytics based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running demonstrate_analytics command...[/blue]")
        
        if not config:
            raise ValueError("Configuration file must be provided.")
        
        config_data = load_config(config)
        
        if verbose:
            console.print(f"[yellow]Loaded configuration: {json.dumps(config_data, indent=2)}[/yellow]")
        
        result_data = perform_analytics(config_data)
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"demonstrate_analytics Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ demonstrate_analytics completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ demonstrate_analytics failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["demonstrate_analytics"]