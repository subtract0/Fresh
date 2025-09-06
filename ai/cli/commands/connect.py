import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import socket
import jsonschema
from jsonschema import validate

console = Console()

# JSON schema for configuration validation
config_schema = {
    "type": "object",
    "properties": {
        "host": {"type": "string"},
        "port": {"type": "integer"},
        "timeout": {"type": "integer"}
    },
    "required": ["host", "port"]
}

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def connect(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    Connect to a server using the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running connect command...[/blue]")
        
        # Load and validate configuration
        if config:
            with open(config, 'r') as f:
                config_data = json.load(f)
                validate(instance=config_data, schema=config_schema)
        else:
            raise ValueError("Configuration file is required.")

        host = config_data['host']
        port = config_data['port']
        timeout = config_data.get('timeout', 5)

        # Attempt to connect to the server
        with socket.create_connection((host, port), timeout=timeout) as sock:
            result_data = {
                "feature": "connect",
                "status": "success", 
                "message": f"Connected to {host}:{port}",
                "config_used": config,
                "verbose": verbose
            }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"connect Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ connect completed successfully[/green]")
            
    except jsonschema.exceptions.ValidationError as ve:
        console.print(f"[red]❌ Configuration validation failed: {str(ve)}[/red]")
        ctx.exit(1)
    except socket.error as se:
        console.print(f"[red]❌ Connection failed: {str(se)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ connect failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["connect"]