import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import requests

console = Console()

@click.command()
@click.option('--agent-id', '-a', required=True, help='ID of the agent to retrieve')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def get_agent_by_id(ctx, agent_id: str, verbose: bool, output: str, config: Optional[str]):
    """
    Retrieve agent information by ID.
    """
    try:
        if verbose:
            console.print(f"[blue]Running get_agent_by_id command for agent ID: {agent_id}...[/blue]")
        
        # Load configuration if provided
        api_url = "http://api.example.com/agents"  # Replace with actual API URL
        if config:
            with open(config, 'r') as f:
                config_data = json.load(f)
                api_url = config_data.get("api_url", api_url)

        # Validate agent ID
        if not agent_id.isdigit():
            raise ValueError("Agent ID must be a numeric value.")
        
        # Make API request to get agent by ID
        response = requests.get(f"{api_url}/{agent_id}")
        response.raise_for_status()  # Raise an error for bad responses

        result_data = response.json()

        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"Agent Details for ID: {agent_id}")
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ get_agent_by_id completed successfully[/green]")
            
    except requests.HTTPError as http_err:
        console.print(f"[red]❌ HTTP error occurred: {str(http_err)}[/red]")
        ctx.exit(1)
    except ValueError as val_err:
        console.print(f"[red]❌ Value error: {str(val_err)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ get_agent_by_id failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["get_agent_by_id"]