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
def patch_openai(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    patch_openai command.
    
    This command integrates with OpenAI's API to apply patches based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running patch_openai command...[/blue]")
        
        if config is None:
            raise ValueError("Configuration file must be provided.")
        
        with open(config, 'r') as f:
            config_data = json.load(f)

        api_key = config_data.get("api_key")
        if not api_key:
            raise ValueError("API key not found in configuration.")

        endpoint = config_data.get("endpoint", "https://api.openai.com/v1/patch")
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = config_data.get("payload")
        if not payload:
            raise ValueError("Payload not found in configuration.")

        response = requests.patch(endpoint, headers=headers, json=payload)
        
        if response.status_code != 200:
            raise Exception(f"API request failed with status code {response.status_code}: {response.text}")

        result_data = {
            "feature": "patch_openai",
            "status": "success", 
            "message": "Patch applied successfully",
            "response": response.json(),
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"patch_openai Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ patch_openai completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ patch_openai failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["patch_openai"]