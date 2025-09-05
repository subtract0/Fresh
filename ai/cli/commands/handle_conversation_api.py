import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import requests

console = Console()

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def handle_conversation_api(ctx, verbose: bool, output: Optional[str], config: Optional[str]):
    """
    handle_conversation_api command.
    
    This command interacts with the conversation API to handle conversations.
    """
    try:
        if verbose:
            console.print(f"[blue]Running handle_conversation_api command...[/blue]")
        
        # Load configuration if provided
        api_url = "https://api.example.com/conversation"  # Replace with actual API endpoint
        headers = {}
        
        if config:
            with open(config, 'r') as f:
                config_data = json.load(f)
                api_url = config_data.get("api_url", api_url)
                headers = config_data.get("headers", {})
        
        # Make API request
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()  # Raise an error for bad responses
        
        result_data = response.json()
        result_data["feature"] = "handle_conversation_api"
        result_data["config_used"] = config
        result_data["verbose"] = verbose
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"handle_conversation_api Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ handle_conversation_api completed successfully[/green]")
            
    except requests.exceptions.RequestException as e:
        console.print(f"[red]❌ handle_conversation_api failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)
    except json.JSONDecodeError as e:
        console.print(f"[red]❌ JSON decoding failed: {str(e)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ handle_conversation_api failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["handle_conversation_api"]