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
def get_github_workflows(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    get_github_workflows command.
    Fetches GitHub workflows from the specified repository.
    """
    try:
        if verbose:
            console.print(f"[blue]Running get_github_workflows command...[/blue]")
        
        if config is None:
            raise ValueError("Configuration file must be provided.")
        
        with open(config) as f:
            config_data = json.load(f)
        
        repo = config_data.get("repository")
        token = config_data.get("token")
        
        if not repo or not token:
            raise ValueError("Repository and token must be specified in the configuration file.")
        
        url = f"https://api.github.com/repos/{repo}/actions/workflows"
        headers = {"Authorization": f"token {token}"}
        
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"Failed to fetch workflows: {response.status_code} - {response.text}")
        
        workflows = response.json().get("workflows", [])
        
        result_data = {
            "feature": "get_github_workflows",
            "status": "success", 
            "workflows": workflows,
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"get_github_workflows Results")
            table.add_column("Workflow ID", style="cyan")
            table.add_column("Name", style="magenta")
            table.add_column("State", style="green")
            
            for workflow in workflows:
                table.add_row(str(workflow['id']), workflow['name'], workflow['state'])
            
            console.print(table)
        else:  # plain
            console.print(f"Workflows: {len(workflows)} found.")
            for workflow in workflows:
                console.print(f"ID: {workflow['id']}, Name: {workflow['name']}, State: {workflow['state']}")
        
        if verbose:
            console.print(f"[green]✅ get_github_workflows completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ get_github_workflows failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)


# Export command for CLI registration
__all__ = ["get_github_workflows"]