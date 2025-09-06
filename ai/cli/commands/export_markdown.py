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

def export_to_markdown(data: dict, output_path: str):
    with open(output_path, 'w') as f:
        for key, value in data.items():
            f.write(f"## {key}\n\n{value}\n\n")

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain', 'markdown']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def export_markdown(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    export_markdown command.
    Exports data in various formats including markdown.
    """
    try:
        if verbose:
            console.print(f"[blue]Running export_markdown command...[/blue]")
        
        config_data = {}
        if config:
            config_data = load_config(config)
            if verbose:
                console.print(f"[yellow]Loaded configuration from {config}[/yellow]")

        # Sample data to export
        result_data = {
            "feature": "export_markdown",
            "status": "success", 
            "message": "Export completed successfully",
            "config_used": config_data,
            "verbose": verbose
        }

        output_path = Path("exported_data.md")
        export_to_markdown(result_data, output_path)

        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"export_markdown Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        elif output == 'plain':
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        elif output == 'markdown':
            console.print(f"[green]Markdown exported to {output_path}[/green]")

        if verbose:
            console.print(f"[green]✅ export_markdown completed successfully[/green]")
            
    except FileNotFoundError as fnf_error:
        console.print(f"[red]❌ Configuration file not found: {str(fnf_error)}[/red]")
        ctx.exit(1)
    except json.JSONDecodeError as json_error:
        console.print(f"[red]❌ Error decoding JSON from config: {str(json_error)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ export_markdown failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["export_markdown"]