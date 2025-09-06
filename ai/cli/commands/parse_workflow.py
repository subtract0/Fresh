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
        raise ValueError("Unsupported configuration file format. Use JSON or YAML.")

def validate_config(config):
    required_keys = ['input_file', 'output_file']
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required configuration key: {key}")

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def parse_workflow(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    parse_workflow command.
    Parses the workflow based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running parse_workflow command...[/blue]")
        
        if config:
            config_data = load_config(config)
            validate_config(config_data)
        else:
            raise ValueError("Configuration file is required.")

        # Simulate parsing workflow logic
        result_data = {
            "feature": "parse_workflow",
            "status": "success", 
            "message": "Workflow parsed successfully",
            "config_used": config_data,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"parse_workflow Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ parse_workflow completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ parse_workflow failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["parse_workflow"]