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

def generate_report_logic(config: dict):
    # Simulate report generation logic
    report_data = {
        "total_items": 100,
        "successful_items": 95,
        "failed_items": 5,
        "details": [
            {"item": "Item 1", "status": "success"},
            {"item": "Item 2", "status": "success"},
            {"item": "Item 3", "status": "failure"},
        ]
    }
    return report_data

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def generate_report(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    generate_report command.
    Generates a report based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running generate_report command...[/blue]")
        
        if config:
            config_data = load_config(config)
        else:
            console.print(f"[red]❌ Configuration file is required.[/red]")
            ctx.exit(1)

        report_data = generate_report_logic(config_data)

        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(report_data, indent=2))
        elif output == 'table':
            table = Table(title=f"generate_report Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in report_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in report_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ generate_report completed successfully[/green]")
            
    except FileNotFoundError as fnf_error:
        console.print(f"[red]❌ Configuration file not found: {str(fnf_error)}[/red]")
        ctx.exit(1)
    except yaml.YAMLError as yaml_error:
        console.print(f"[red]❌ Error parsing configuration file: {str(yaml_error)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ generate_report failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["generate_report"]