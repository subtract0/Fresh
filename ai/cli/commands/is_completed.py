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

def check_completion(feature: str, config: dict) -> dict:
    # Simulate checking if a feature is completed based on the config
    if feature in config:
        return {"feature": feature, "completed": config[feature].get("completed", False)}
    return {"feature": feature, "completed": False}

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), required=True, help='Configuration file')
@click.option('--feature', type=str, required=True, help='Feature to check completion status')
@click.pass_context
def is_completed(ctx, verbose: bool, output: str, config: Optional[str], feature: str):
    """
    Check if a specific feature is completed based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running is_completed command for feature: {feature}...[/blue]")
        
        # Load configuration
        config_data = load_config(config)
        
        # Check if the feature is completed
        result = check_completion(feature, config_data)
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result, indent=2))
        elif output == 'table':
            table = Table(title=f"Completion Status for {feature}")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ is_completed completed successfully[/green]")
            
    except FileNotFoundError:
        console.print(f"[red]❌ Configuration file not found: {config}[/red]")
        ctx.exit(1)
    except json.JSONDecodeError:
        console.print(f"[red]❌ Error decoding JSON from configuration file: {config}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ is_completed failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["is_completed"]