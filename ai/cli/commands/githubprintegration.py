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
def githubprintegration(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    GitHubPRIntegration command.
    
    This command integrates with GitHub to manage pull requests based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running GitHubPRIntegration command...[/blue]")
        
        if config is None:
            raise ValueError("Configuration file must be provided.")
        
        with open(config, 'r') as f:
            config_data = json.load(f)
        
        repo = config_data.get("repository")
        token = config_data.get("token")
        
        if not repo or not token:
            raise ValueError("Repository and token must be specified in the configuration file.")
        
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        response = requests.get(f"https://api.github.com/repos/{repo}/pulls", headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"Failed to fetch pull requests: {response.status_code} - {response.text}")
        
        pull_requests = response.json()
        
        result_data = {
            "feature": "GitHubPRIntegration",
            "status": "success", 
            "pull_requests": pull_requests,
            "config_used": config,
            "verbose": verbose
        }
        
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"GitHubPRIntegration Results")
            table.add_column("PR Number", style="cyan")
            table.add_column("Title", style="magenta")
            table.add_column("State", style="green")
            
            for pr in pull_requests:
                table.add_row(str(pr['number']), pr['title'], pr['state'])
            
            console.print(table)
        else:  # plain
            for pr in pull_requests:
                console.print(f"PR #{pr['number']}: {pr['title']} - State: {pr['state']}")
        
        if verbose:
            console.print(f"[green]✅ GitHubPRIntegration completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ GitHubPRIntegration failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["githubprintegration"]