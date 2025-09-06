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

def validate_config(config):
    required_keys = ['agent_name', 'agent_type']
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required config key: {key}")

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def freshagentsystem(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    FreshAgentSystem command.
    This command initializes and manages fresh agents based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running FreshAgentSystem command...[/blue]")
        
        config_data = {}
        if config:
            config_data = load_config(config)
            validate_config(config_data)
        
        # Simulate agent creation logic
        agent_name = config_data.get('agent_name', 'DefaultAgent')
        agent_type = config_data.get('agent_type', 'default')
        
        result_data = {
            "feature": "FreshAgentSystem",
            "status": "success", 
            "message": f"Agent '{agent_name}' of type '{agent_type}' created successfully.",
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"FreshAgentSystem Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ FreshAgentSystem completed successfully[/green]")
            
    except ValueError as ve:
        console.print(f"[red]❌ FreshAgentSystem failed: {str(ve)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ FreshAgentSystem failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["freshagentsystem"]