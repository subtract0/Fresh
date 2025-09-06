import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import yaml

console = Console()

def load_config(config_path: str):
    if config_path.endswith('.json'):
        with open(config_path, 'r') as f:
            return json.load(f)
    elif config_path.endswith('.yaml') or config_path.endswith('.yml'):
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    else:
        raise ValueError("Unsupported configuration file format. Use JSON or YAML.")

def perform_assist_scan(config):
    # Placeholder for actual scan logic
    # Simulating scan results
    return {
        "scan_results": [
            {"item": "feature_1", "status": "enabled"},
            {"item": "feature_2", "status": "disabled"},
        ],
        "summary": {
            "total": 2,
            "enabled": 1,
            "disabled": 1
        }
    }

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def cmd_assist_scan(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    cmd_assist_scan command.
    Scans features based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running cmd_assist_scan command...[/blue]")
        
        if config:
            config_data = load_config(config)
        else:
            config_data = {}

        scan_results = perform_assist_scan(config_data)

        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(scan_results, indent=2))
        elif output == 'table':
            table = Table(title=f"cmd_assist_scan Results")
            table.add_column("Item", style="cyan")
            table.add_column("Status", style="magenta")
            
            for result in scan_results["scan_results"]:
                table.add_row(result["item"], result["status"])
            
            console.print(table)
            summary = scan_results["summary"]
            console.print(f"Total: {summary['total']}, Enabled: {summary['enabled']}, Disabled: {summary['disabled']}")
        else:  # plain
            for result in scan_results["scan_results"]:
                console.print(f"{result['item']}: {result['status']}")
            summary = scan_results["summary"]
            console.print(f"Total: {summary['total']}, Enabled: {summary['enabled']}, Disabled: {summary['disabled']}")
        
        if verbose:
            console.print(f"[green]✅ cmd_assist_scan completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ cmd_assist_scan failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["cmd_assist_scan"]