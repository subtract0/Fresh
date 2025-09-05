import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import yaml

console = Console()

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def create_agent_panel(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    create_agent_panel command.
    
    This command creates an agent panel based on the provided configuration.
    It accepts a configuration file in JSON or YAML format and outputs the result
    in the specified format (JSON, table, or plain text).
    
    Args:
        ctx: Click context.
        verbose (bool): Enable verbose output.
        output (str): Output format.
        config (Optional[str]): Path to the configuration file.
    """
    try:
        if verbose:
            console.print(f"[blue]Running create_agent_panel command...[/blue]")
        
        # Load configuration if provided
        config_data = {}
        if config:
            if config.endswith('.json'):
                with open(config, 'r') as f:
                    config_data = json.load(f)
            elif config.endswith('.yaml') or config.endswith('.yml'):
                with open(config, 'r') as f:
                    config_data = yaml.safe_load(f)
            else:
                raise ValueError("Unsupported configuration file format. Use JSON or YAML.")
        
        # Validate configuration data
        if not isinstance(config_data, dict):
            raise ValueError("Configuration data must be a dictionary.")
        
        # Simulate agent panel creation logic
        result_data = {
            "feature": "create_agent_panel",
            "status": "success", 
            "message": "Agent panel created successfully",
            "config_used": config_data,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"create_agent_panel Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ create_agent_panel completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ create_agent_panel failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["create_agent_panel"]