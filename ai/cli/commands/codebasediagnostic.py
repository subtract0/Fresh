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
    with open(config_path, 'r') as file:
        return json.load(file)

def perform_diagnostic(config: dict):
    # Simulated diagnostic logic
    issues = []
    if 'required_key' not in config:
        issues.append("Missing 'required_key' in configuration.")
    return issues

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), callback=validate_config_file, 
              help='Configuration file')
@click.pass_context
def codebasediagnostic(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    CodebaseDiagnostic command.
    This command performs diagnostics on the codebase based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running CodebaseDiagnostic command...[/blue]")
        
        config_data = {}
        if config:
            config_data = load_config(config)
            if verbose:
                console.print(f"[yellow]Loaded configuration from {config}[/yellow]")
        
        issues = perform_diagnostic(config_data)
        
        result_data = {
            "feature": "CodebaseDiagnostic",
            "status": "completed" if not issues else "issues_found", 
            "issues": issues,
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"CodebaseDiagnostic Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ CodebaseDiagnostic completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ CodebaseDiagnostic failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["codebasediagnostic"]