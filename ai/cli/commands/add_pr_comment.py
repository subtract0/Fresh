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
@click.option('--pr-url', required=True, help='URL of the pull request')
@click.option('--comment', required=True, help='Comment to add to the pull request')
@click.pass_context
def add_pr_comment(ctx, verbose: bool, output: str, config: Optional[str], pr_url: str, comment: str):
    """
    Add a comment to a pull request.
    
    :param pr_url: URL of the pull request to comment on
    :param comment: The comment text to add
    """
    try:
        if verbose:
            console.print(f"[blue]Running add_pr_comment command...[/blue]")
        
        # Load configuration if provided
        headers = {}
        if config:
            with open(config, 'r') as f:
                config_data = json.load(f)
                headers['Authorization'] = f"token {config_data.get('token')}"
        
        # Validate inputs
        if not pr_url.startswith("http"):
            raise ValueError("Invalid pull request URL.")
        
        # Prepare the API request
        response = requests.post(f"{pr_url}/comments", json={"body": comment}, headers=headers)
        
        if response.status_code == 201:
            result_data = {
                "feature": "add_pr_comment",
                "status": "success", 
                "message": "Comment added successfully",
                "config_used": config,
                "verbose": verbose
            }
        else:
            raise Exception(f"Failed to add comment: {response.text}")
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"add_pr_comment Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ add_pr_comment completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ add_pr_comment failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["add_pr_comment"]