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

def run_sync_logic(config):
    # Placeholder for the actual synchronization logic
    # Simulating a successful run
    return {
        "sync_status": "success",
        "details": "Data synchronized successfully.",
        "config": config
    }

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def run_sync_agent(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    run_sync_agent command.
    
    This command runs the synchronization agent based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running run_sync_agent command...[/blue]")
        
        if not config:
            raise ValueError("Configuration file is required.")
        
        config_data = load_config(config)
        
        if verbose:
            console.print(f"[yellow]Loaded configuration: {config_data}[/yellow]")
        
        result_data = run_sync_logic(config_data)
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"run_sync_agent Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ run_sync_agent completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ run_sync_agent failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["run_sync_agent"]