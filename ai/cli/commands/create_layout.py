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
@click.pass_context
def create_layout(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    create_layout command.
    This command creates a layout based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running create_layout command...[/blue]")
        
        # Load configuration if provided
        layout_config = {}
        if config:
            with open(config, 'r') as f:
                layout_config = json.load(f)
                if verbose:
                    console.print(f"[yellow]Loaded configuration from {config}[/yellow]")
        
        # Validate configuration
        if not layout_config.get('layout_name'):
            raise ValueError("Configuration must include 'layout_name'.")

        # Simulate layout creation logic
        layout_name = layout_config['layout_name']
        layout_path = Path(f"./layouts/{layout_name}")
        layout_path.mkdir(parents=True, exist_ok=True)

        result_data = {
            "feature": "create_layout",
            "status": "success", 
            "message": f"Layout '{layout_name}' created successfully.",
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"create_layout Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ create_layout completed successfully[/green]")
            
    except FileNotFoundError as fnf_error:
        console.print(f"[red]❌ create_layout failed: Configuration file not found: {str(fnf_error)}[/red]")
        ctx.exit(1)
    except json.JSONDecodeError as json_error:
        console.print(f"[red]❌ create_layout failed: Invalid JSON in configuration file: {str(json_error)}[/red]")
        ctx.exit(1)
    except ValueError as value_error:
        console.print(f"[red]❌ create_layout failed: {str(value_error)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ create_layout failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["create_layout"]