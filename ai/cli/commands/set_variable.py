import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import os

console = Console()

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.option('--key', required=True, help='Variable key to set')
@click.option('--value', required=True, help='Variable value to set')
@click.pass_context
def set_variable(ctx, verbose: bool, output: str, config: Optional[str], key: str, value: str):
    """
    Set a variable in the configuration.
    
    This command allows you to set a variable in the specified configuration file.
    """
    try:
        if verbose:
            console.print(f"[blue]Running set_variable command...[/blue]")
        
        if config:
            config_path = Path(config)
            if not config_path.is_file():
                raise FileNotFoundError(f"Configuration file '{config}' does not exist.")
            
            with open(config_path, 'r') as f:
                config_data = json.load(f)
        else:
            config_data = {}

        # Set the variable
        config_data[key] = value

        # Write back to the configuration file
        with open(config_path, 'w') as f:
            json.dump(config_data, f, indent=2)

        result_data = {
            "feature": "set_variable",
            "status": "success", 
            "message": f"Variable '{key}' set to '{value}'",
            "config_used": str(config_path),
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"set_variable Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ set_variable completed successfully[/green]")
            
    except FileNotFoundError as fnf_error:
        console.print(f"[red]❌ Error: {str(fnf_error)}[/red]")
        ctx.exit(1)
    except json.JSONDecodeError:
        console.print(f"[red]❌ Error: Configuration file is not valid JSON.[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ set_variable failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["set_variable"]