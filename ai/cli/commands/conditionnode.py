import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import yaml

console = Console()

def load_config(config_path: str):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def validate_conditions(conditions):
    if not isinstance(conditions, dict):
        raise ValueError("Conditions must be a dictionary.")
    for key, value in conditions.items():
        if not isinstance(key, str) or not isinstance(value, (str, bool)):
            raise ValueError(f"Invalid condition: {key} -> {value}")

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def conditionnode(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    ConditionNode command.
    This command evaluates conditions based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running ConditionNode command...[/blue]")
        
        conditions = {}
        if config:
            config_data = load_config(config)
            conditions = config_data.get('conditions', {})
            validate_conditions(conditions)
        
        # Simulate condition evaluation
        results = {key: (value if isinstance(value, bool) else value.lower() == 'true') for key, value in conditions.items()}
        
        result_data = {
            "feature": "ConditionNode",
            "status": "success", 
            "results": results,
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"ConditionNode Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in results.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in results.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ ConditionNode completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ ConditionNode failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["conditionnode"]