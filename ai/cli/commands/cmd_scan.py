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

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def cmd_scan(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    cmd_scan command.
    
    Scans the system based on the provided configuration and outputs the results.
    """
    try:
        if verbose:
            console.print(f"[blue]Running cmd_scan command...[/blue]")
        
        config_data = {}
        if config:
            config_data = load_config(config)
            if verbose:
                console.print(f"[yellow]Loaded configuration: {config_data}[/yellow]")

        # Simulated scan logic
        scan_results = {
            "scanned_items": len(config_data.get('items', [])),
            "status": "success",
            "details": "Scan completed successfully."
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(scan_results, indent=2))
        elif output == 'table':
            table = Table(title=f"cmd_scan Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in scan_results.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in scan_results.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ cmd_scan completed successfully[/green]")
            
    except FileNotFoundError:
        console.print(f"[red]❌ Configuration file not found: {config}[/red]")
        ctx.exit(1)
    except ValueError as ve:
        console.print(f"[red]❌ Error: {str(ve)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ cmd_scan failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["cmd_scan"]