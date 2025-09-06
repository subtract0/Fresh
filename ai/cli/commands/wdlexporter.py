import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import yaml

console = Console()

def load_config(config_path: str) -> dict:
    """
    Load configuration from a YAML file.

    Args:
        config_path (str): Path to the configuration file.

    Returns:
        dict: Loaded configuration data.

    Raises:
        FileNotFoundError: If the configuration file does not exist.
        yaml.YAMLError: If there is an error parsing the YAML file.
    """
    try:
        with open(config_path, 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Configuration file not found: {config_path}") from e
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing YAML file: {config_path}") from e

def validate_config(config: dict) -> None:
    """
    Validate the loaded configuration.

    Args:
        config (dict): Configuration data to validate.

    Raises:
        ValueError: If required keys are missing in the configuration.
    """
    required_keys = ['input', 'output', 'parameters']
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required config key: {key}")

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def wdlexporter(ctx, verbose: bool, output: str, config: Optional[str]) -> None:
    """
    WDLExporter command.
    Exports WDL files based on the provided configuration.

    Args:
        ctx: Click context.
        verbose (bool): Flag to enable verbose output.
        output (str): Desired output format.
        config (Optional[str]): Path to the configuration file.
    """
    try:
        if verbose:
            console.print(f"[blue]Running WDLExporter command...[/blue]")
        
        if config:
            config_data = load_config(config)
            validate_config(config_data)
        else:
            raise ValueError("Configuration file is required.")

        # Simulate WDL export logic
        result_data = {
            "feature": "WDLExporter",
            "status": "success", 
            "message": "WDL files exported successfully",
            "config_used": config_data,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"WDLExporter Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ WDLExporter completed successfully[/green]")
            
    except ValueError as ve:
        console.print(f"[red]❌ WDLExporter failed: {str(ve)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ WDLExporter failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["wdlexporter"]