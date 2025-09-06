import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import os

console = Console()

def count_tokens_in_message(message: str) -> int:
    return len(message.split())

def load_config(config_path: str) -> dict:
    with open(config_path, 'r') as file:
        return json.load(file)

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def count_messages_tokens(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    count_messages_tokens command.
    Counts the tokens in messages provided in the configuration file.
    """
    try:
        if verbose:
            console.print(f"[blue]Running count_messages_tokens command...[/blue]")
        
        if config is None:
            raise ValueError("Configuration file must be provided.")
        
        config_data = load_config(config)
        
        if 'messages' not in config_data:
            raise ValueError("Configuration must contain 'messages' key.")
        
        total_tokens = sum(count_tokens_in_message(message) for message in config_data['messages'])
        
        result_data = {
            "feature": "count_messages_tokens",
            "status": "success", 
            "total_tokens": total_tokens,
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"count_messages_tokens Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ count_messages_tokens completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ count_messages_tokens failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["count_messages_tokens"]