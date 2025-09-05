import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import os

console = Console()

def load_config(config_path: str):
    with open(config_path, 'r') as f:
        return json.load(f)

def validate_config(config):
    required_keys = ['database', 'batch_size']
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required config key: {key}")

def perform_tracked_write_batch(config, verbose):
    # Simulate writing to a database or batch processing
    if verbose:
        console.print(f"[blue]Using database: {config['database']}[/blue]")
        console.print(f"[blue]Batch size: {config['batch_size']}[/blue]")
    
    # Simulated processing logic
    processed_items = config.get('items', [])
    if not processed_items:
        raise ValueError("No items to process in the configuration.")
    
    return {
        "processed_count": len(processed_items),
        "status": "success",
        "message": "Batch processed successfully."
    }

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file', required=True)
@click.pass_context
def trackedwritebatch(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    TrackedWriteBatch command.
    Processes a batch of items based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running TrackedWriteBatch command...[/blue]")
        
        config_data = load_config(config)
        validate_config(config_data)
        
        result_data = perform_tracked_write_batch(config_data, verbose)
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"TrackedWriteBatch Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ TrackedWriteBatch completed successfully[/green]")
            
    except FileNotFoundError:
        console.print(f"[red]❌ Configuration file not found: {config}[/red]")
        ctx.exit(1)
    except ValueError as ve:
        console.print(f"[red]❌ Configuration error: {str(ve)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ TrackedWriteBatch failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["trackedwritebatch"]