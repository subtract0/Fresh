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
def githubintegration(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    GitHubIntegration command.
    
    This command integrates with GitHub to perform various operations
    based on the provided configuration file.
    """
    try:
        if verbose:
            console.print(f"[blue]Running GitHubIntegration command...[/blue]")
        
        if config is None:
            raise ValueError("Configuration file must be provided.")
        
        with open(config, 'r') as f:
            config_data = json.load(f)
        
        if 'token' not in config_data or 'repo' not in config_data:
            raise ValueError("Configuration must include 'token' and 'repo' fields.")
        
        token = config_data['token']
        repo = config_data['repo']
        
        headers = {'Authorization': f'token {token}'}
        response = requests.get(f'https://api.github.com/repos/{repo}', headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"Failed to fetch repository data: {response.status_code} - {response.text}")
        
        repo_data = response.json()
        
        result_data = {
            "feature": "GitHubIntegration",
            "status": "success", 
            "repo_name": repo_data.get('name'),
            "repo_url": repo_data.get('html_url'),
            "description": repo_data.get('description'),
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"GitHubIntegration Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ GitHubIntegration completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ GitHubIntegration failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["githubintegration"]