import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import os

console = Console()

def load_config(config_path: str):
    with open(config_path, 'r') as file:
        return json.load(file)

def validate_config(config):
    required_keys = ['integrations']
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required key in configuration: {key}")

def get_integration_examples(config):
    integrations = config.get('integrations', [])
    if not integrations:
        raise ValueError("No integrations found in configuration.")
    return integrations

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def show_integration_examples(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    show_integration_examples command.
    Displays integration examples based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running show_integration_examples command...[/blue]")
        
        if not config:
            raise ValueError("Configuration file must be provided.")
        
        config_data = load_config(config)
        validate_config(config_data)
        integration_examples = get_integration_examples(config_data)
        
        result_data = {
            "feature": "show_integration_examples",
            "status": "success", 
            "examples": integration_examples,
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"show_integration_examples Results")
            table.add_column("Integration", style="cyan")
            table.add_column("Details", style="magenta")
            
            for example in integration_examples:
                table.add_row(example.get('name', 'N/A'), example.get('details', 'N/A'))
            
            console.print(table)
        else:  # plain
            for example in integration_examples:
                console.print(f"Integration: {example.get('name', 'N/A')}, Details: {example.get('details', 'N/A')}")
        
        if verbose:
            console.print(f"[green]✅ show_integration_examples completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ show_integration_examples failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["show_integration_examples"]