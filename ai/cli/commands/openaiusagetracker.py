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
    with open(config_path, 'r') as f:
        return json.load(f)

def fetch_usage_data(api_key: str):
    # Simulated API call to fetch usage data
    if not api_key:
        raise ValueError("API key is required to fetch usage data.")
    # Here you would implement the actual API call to OpenAI
    return {
        "total_usage": 12345,
        "usage_by_model": {
            "gpt-3.5-turbo": 5000,
            "gpt-4": 7345
        }
    }

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def openaiusagetracker(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    OpenAIUsageTracker command.
    Fetch and display usage statistics from OpenAI API.
    """
    try:
        if verbose:
            console.print(f"[blue]Running OpenAIUsageTracker command...[/blue]")
        
        config_data = load_config(config) if config else {}
        api_key = config_data.get("api_key")
        
        usage_data = fetch_usage_data(api_key)
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(usage_data, indent=2))
        elif output == 'table':
            table = Table(title=f"OpenAI Usage Tracker Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in usage_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in usage_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ OpenAIUsageTracker completed successfully[/green]")
            
    except FileNotFoundError as fnf_error:
        console.print(f"[red]❌ Error: {str(fnf_error)}[/red]")
        ctx.exit(1)
    except ValueError as val_error:
        console.print(f"[red]❌ Error: {str(val_error)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ OpenAIUsageTracker failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["openaiusagetracker"]