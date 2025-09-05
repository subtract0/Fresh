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
    with open(config_path, 'r') as f:
        return json.load(f)

def generate_report(config: dict):
    # Simulate report generation based on the configuration
    report_data = {
        "total_features": len(config.get("features", [])),
        "enabled_features": [feature for feature in config.get("features", []) if feature.get("enabled", False)],
        "disabled_features": [feature for feature in config.get("features", []) if not feature.get("enabled", False)],
    }
    return report_data

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file', required=True)
@click.pass_context
def cmd_assist_report(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    cmd_assist_report command.
    Generates a report based on the provided configuration file.
    """
    try:
        if verbose:
            console.print(f"[blue]Running cmd_assist_report command...[/blue]")
        
        config_data = load_config(config)
        report_data = generate_report(config_data)

        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(report_data, indent=2))
        elif output == 'table':
            table = Table(title=f"cmd_assist_report Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in report_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in report_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ cmd_assist_report completed successfully[/green]")
            
    except FileNotFoundError as fnf_error:
        console.print(f"[red]❌ Error: {str(fnf_error)}[/red]")
        ctx.exit(1)
    except json.JSONDecodeError as json_error:
        console.print(f"[red]❌ JSON Decode Error: {str(json_error)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ cmd_assist_report failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["cmd_assist_report"]