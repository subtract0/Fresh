import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import os

console = Console()

def load_config(config_path: str):
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    with open(config_path, 'r') as file:
        return json.load(file)

def validate_safety_logic(config):
    # Placeholder for actual validation logic
    # Here you would implement the actual safety validation logic based on the config
    if 'safety_criteria' not in config:
        raise ValueError("Configuration must include 'safety_criteria'")
    
    # Simulate validation result
    return {
        "is_safe": True,
        "issues": []
    }

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file', required=True)
@click.pass_context
def validate_safety(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    validate_safety command.
    Validates safety based on the provided configuration file.
    """
    try:
        if verbose:
            console.print(f"[blue]Running validate_safety command...[/blue]")
        
        config_data = load_config(config)
        validation_result = validate_safety_logic(config_data)
        
        result_data = {
            "feature": "validate_safety",
            "status": "success" if validation_result["is_safe"] else "failure",
            "issues": validation_result["issues"],
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"validate_safety Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ validate_safety completed successfully[/green]")
            
    except FileNotFoundError as fnf_error:
        console.print(f"[red]❌ validate_safety failed: {str(fnf_error)}[/red]")
        ctx.exit(1)
    except ValueError as val_error:
        console.print(f"[red]❌ validate_safety failed: {str(val_error)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ validate_safety failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["validate_safety"]