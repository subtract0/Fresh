import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import os

console = Console()

def load_config(config_path: str):
    if config_path and Path(config_path).exists():
        with open(config_path, 'r') as f:
            return json.load(f)
    return {}

def get_emoji_status():
    # Example implementation of status retrieval
    return {
        "online": "😊",
        "offline": "😞",
        "busy": "😤",
        "away": "😴"
    }

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def get_status_emoji(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    get_status_emoji command.
    Retrieves the status emojis for various states.
    """
    try:
        if verbose:
            console.print(f"[blue]Running get_status_emoji command...[/blue]")
        
        config_data = load_config(config)
        emoji_status = get_emoji_status()
        
        result_data = {
            "feature": "get_status_emoji",
            "status": "success", 
            "emojis": emoji_status,
            "config_used": config_data,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"get_status_emoji Results")
            table.add_column("Status", style="cyan")
            table.add_column("Emoji", style="magenta")
            
            for key, value in emoji_status.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in emoji_status.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ get_status_emoji completed successfully[/green]")
            
    except FileNotFoundError as fnf_error:
        console.print(f"[red]❌ Configuration file not found: {str(fnf_error)}[/red]")
        ctx.exit(1)
    except json.JSONDecodeError as json_error:
        console.print(f"[red]❌ Error parsing JSON configuration: {str(json_error)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ get_status_emoji failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["get_status_emoji"]