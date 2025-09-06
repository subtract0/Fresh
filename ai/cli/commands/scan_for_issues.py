import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import os

console = Console()

def validate_config_file(ctx, param, value):
    if value and not Path(value).is_file():
        raise click.BadParameter(f"Configuration file '{value}' does not exist.")
    return value

def load_config(config_path: str):
    with open(config_path, 'r') as f:
        return json.load(f)

def scan_for_issues_logic(config):
    # Placeholder for actual scanning logic
    issues = []
    # Simulate scanning logic
    if config.get("check_for_issues"):
        issues.append({"issue": "Example issue found", "severity": "low"})
    return issues

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), callback=validate_config_file, 
              help='Configuration file')
@click.pass_context
def scan_for_issues(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    scan_for_issues command.
    Scans for issues based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running scan_for_issues command...[/blue]")
        
        config_data = {}
        if config:
            config_data = load_config(config)

        issues = scan_for_issues_logic(config_data)

        result_data = {
            "feature": "scan_for_issues",
            "status": "success" if issues else "no_issues_found",
            "issues": issues,
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"scan_for_issues Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                if isinstance(value, list):
                    value = ', '.join([str(issue) for issue in value])
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                if isinstance(value, list):
                    value = ', '.join([str(issue) for issue in value])
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ scan_for_issues completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ scan_for_issues failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["scan_for_issues"]