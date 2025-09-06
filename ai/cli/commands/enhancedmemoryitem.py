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

def process_enhanced_memory_item(config: dict):
    # Simulate processing logic based on the configuration
    if 'memory_items' not in config:
        raise ValueError("Configuration must contain 'memory_items' key.")
    
    memory_items = config['memory_items']
    processed_items = [{"item": item, "status": "processed"} for item in memory_items]
    return processed_items

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file', required=True)
@click.pass_context
def enhancedmemoryitem(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    EnhancedMemoryItem command.
    Processes memory items based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running EnhancedMemoryItem command...[/blue]")
        
        config_data = load_config(config)
        processed_data = process_enhanced_memory_item(config_data)
        
        result_data = {
            "feature": "EnhancedMemoryItem",
            "status": "success", 
            "processed_items": processed_data,
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"EnhancedMemoryItem Results")
            table.add_column("Item", style="cyan")
            table.add_column("Status", style="magenta")
            
            for item in processed_data:
                table.add_row(item['item'], item['status'])
            
            console.print(table)
        else:  # plain
            for item in processed_data:
                console.print(f"Item: {item['item']}, Status: {item['status']}")
        
        if verbose:
            console.print(f"[green]✅ EnhancedMemoryItem completed successfully[/green]")
            
    except FileNotFoundError as fnf_error:
        console.print(f"[red]❌ EnhancedMemoryItem failed: {str(fnf_error)}[/red]")
        ctx.exit(1)
    except ValueError as val_error:
        console.print(f"[red]❌ EnhancedMemoryItem failed: {str(val_error)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ EnhancedMemoryItem failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["enhancedmemoryitem"]