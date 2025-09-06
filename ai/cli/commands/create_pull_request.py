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
def create_pull_request(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    Create a pull request in the specified repository.
    
    This command allows you to create a pull request by providing necessary details
    through a configuration file or command-line options.
    """
    try:
        if verbose:
            console.print(f"[blue]Running create_pull_request command...[/blue]")
        
        # Load configuration if provided
        if config:
            with open(config, 'r') as f:
                config_data = json.load(f)
        else:
            console.print(f"[red]❌ Configuration file not provided or invalid.[/red]")
            ctx.exit(1)

        # Validate required fields in config
        required_fields = ['repo', 'title', 'body', 'head', 'base']
        for field in required_fields:
            if field not in config_data:
                console.print(f"[red]❌ Missing required field in config: {field}[/red]")
                ctx.exit(1)

        # Prepare the pull request data
        pr_data = {
            "title": config_data['title'],
            "body": config_data['body'],
            "head": config_data['head'],
            "base": config_data['base']
        }

        # Make the API request to create the pull request
        response = requests.post(
            f"https://api.github.com/repos/{config_data['repo']}/pulls",
            json=pr_data,
            headers={"Authorization": f"token {config_data.get('token')}"}
        )

        if response.status_code == 201:
            result_data = {
                "feature": "create_pull_request",
                "status": "success",
                "message": "Pull request created successfully",
                "url": response.json().get('html_url'),
                "config_used": config,
                "verbose": verbose
            }
        else:
            result_data = {
                "feature": "create_pull_request",
                "status": "failure",
                "message": response.json().get('message', 'Unknown error'),
                "config_used": config,
                "verbose": verbose
            }

        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"create_pull_request Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ create_pull_request completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ create_pull_request failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["create_pull_request"]