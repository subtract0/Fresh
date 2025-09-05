import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import yaml

console = Console()

def load_config(config_path: str):
    if config_path.endswith('.json'):
        with open(config_path, 'r') as f:
            return json.load(f)
    elif config_path.endswith('.yaml') or config_path.endswith('.yml'):
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    else:
        raise ValueError("Unsupported config file format. Use JSON or YAML.")

def call_mcp_logic(config):
    # Simulated business logic for call_mcp
    if not config.get("endpoint"):
        raise ValueError("Configuration must include 'endpoint'.")
    
    # Simulate a successful call to an external service
    response = {
        "data": "Sample response from MCP",
        "status": "success"
    }
    return response

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def call_mcp(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    call_mcp command.
    This command interacts with the MCP service based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running call_mcp command...[/blue]")
        
        if config:
            config_data = load_config(config)
        else:
            raise ValueError("Configuration file is required.")
        
        result_data = call_mcp_logic(config_data)
        
        # Prepare output data
        output_data = {
            "feature": "call_mcp",
            "status": "success",
            "response": result_data,
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(output_data, indent=2))
        elif output == 'table':
            table = Table(title=f"call_mcp Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in output_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in output_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ call_mcp completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ call_mcp failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["call_mcp"]