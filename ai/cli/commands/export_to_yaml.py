import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import yaml

console = Console()

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def export_to_yaml(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    export_to_yaml command.
    Exports data to YAML format based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running export_to_yaml command...[/blue]")
        
        if config is None:
            raise ValueError("Configuration file must be provided.")
        
        config_path = Path(config)
        if not config_path.is_file():
            raise FileNotFoundError(f"Configuration file '{config}' does not exist.")
        
        with open(config_path, 'r') as file:
            config_data = yaml.safe_load(file)
        
        # Here you would implement the logic to process the config_data and prepare the export
        # For demonstration, we will just return the loaded config data
        result_data = {
            "feature": "export_to_yaml",
            "status": "success", 
            "message": "Export completed successfully",
            "config_used": config_data,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"export_to_yaml Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ export_to_yaml completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ export_to_yaml failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["export_to_yaml"]