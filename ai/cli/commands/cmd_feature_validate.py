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

def validate_feature(config):
    # Placeholder for actual validation logic
    if 'feature_name' not in config:
        raise ValueError("Configuration must contain 'feature_name'.")
    return {
        "feature": config['feature_name'],
        "status": "validated",
        "message": "Feature validation successful."
    }

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def cmd_feature_validate(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    cmd_feature_validate command.
    
    Validates the feature based on the provided configuration file.
    """
    try:
        if verbose:
            console.print(f"[blue]Running cmd_feature_validate command...[/blue]")
        
        if not config:
            raise ValueError("Configuration file is required.")
        
        config_data = load_config(config)
        result_data = validate_feature(config_data)
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"cmd_feature_validate Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ cmd_feature_validate completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ cmd_feature_validate failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["cmd_feature_validate"]