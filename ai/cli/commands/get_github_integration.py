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
def get_github_integration(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    get_github_integration command.
    
    Fetches GitHub integration details based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running get_github_integration command...[/blue]")
        
        if config is None:
            raise ValueError("Configuration file must be provided.")
        
        with open(config, 'r') as f:
            config_data = json.load(f)
        
        github_token = config_data.get("github_token")
        if not github_token:
            raise ValueError("GitHub token is missing in the configuration.")
        
        response = requests.get("https://api.github.com/user", headers={"Authorization": f"token {github_token}"})
        
        if response.status_code != 200:
            raise Exception(f"Failed to fetch GitHub integration: {response.text}")
        
        result_data = {
            "feature": "get_github_integration",
            "status": "success", 
            "data": response.json(),
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"get_github_integration Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                if key == "data":
                    for k, v in value.items():
                        table.add_row(str(k), str(v))
                else:
                    table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                if key == "data":
                    for k, v in value.items():
                        console.print(f"{k}: {v}")
                else:
                    console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ get_github_integration completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ get_github_integration failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)


# Export command for CLI registration
__all__ = ["get_github_integration"]