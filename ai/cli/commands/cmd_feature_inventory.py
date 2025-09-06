import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import os

console = Console()

def load_config(config_path: str):
    with open(config_path, 'r') as f:
        return json.load(f)

def validate_config(config):
    required_keys = ['features']
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required key in config: {key}")

def get_feature_inventory(config):
    features = config.get('features', [])
    return [{"feature": feature, "status": "available"} for feature in features]

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def cmd_feature_inventory(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    cmd_feature_inventory command.
    This command retrieves and displays the feature inventory based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running cmd_feature_inventory command...[/blue]")
        
        if not config:
            raise ValueError("Configuration file must be provided.")
        
        config_data = load_config(config)
        validate_config(config_data)
        
        feature_inventory = get_feature_inventory(config_data)
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(feature_inventory, indent=2))
        elif output == 'table':
            table = Table(title=f"Feature Inventory Results")
            table.add_column("Feature", style="cyan")
            table.add_column("Status", style="magenta")
            
            for item in feature_inventory:
                table.add_row(item['feature'], item['status'])
            
            console.print(table)
        else:  # plain
            for item in feature_inventory:
                console.print(f"{item['feature']}: {item['status']}")
        
        if verbose:
            console.print(f"[green]✅ cmd_feature_inventory completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ cmd_feature_inventory failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["cmd_feature_inventory"]