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
        raise ValueError("Unsupported config file format. Use JSON or YAML.")

def perform_comprehensive_scan(config):
    # Placeholder for actual scan logic
    # Simulating scan results
    return {
        "scan_results": [
            {"item": "feature_1", "status": "ok"},
            {"item": "feature_2", "status": "warning"},
            {"item": "feature_3", "status": "error"},
        ],
        "summary": {
            "total": 3,
            "ok": 1,
            "warning": 1,
            "error": 1
        }
    }

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def comprehensive_scan(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    comprehensive_scan command.
    Scans the system based on the provided configuration and outputs the results.
    """
    try:
        if verbose:
            console.print(f"[blue]Running comprehensive_scan command...[/blue]")
        
        if config is None:
            raise ValueError("Configuration file must be provided.")
        
        config_data = load_config(config)
        
        if verbose:
            console.print(f"[blue]Loaded configuration: {json.dumps(config_data, indent=2)}[/blue]")
        
        result_data = perform_comprehensive_scan(config_data)
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"comprehensive_scan Results")
            table.add_column("Item", style="cyan")
            table.add_column("Status", style="magenta")
            
            for result in result_data["scan_results"]:
                table.add_row(result["item"], result["status"])
            
            console.print(table)
            summary = result_data["summary"]
            console.print(f"Total: {summary['total']}, OK: {summary['ok']}, Warning: {summary['warning']}, Error: {summary['error']}")
        else:  # plain
            for result in result_data["scan_results"]:
                console.print(f"{result['item']}: {result['status']}")
            summary = result_data["summary"]
            console.print(f"Total: {summary['total']}, OK: {summary['ok']}, Warning: {summary['warning']}, Error: {summary['error']}")
        
        if verbose:
            console.print(f"[green]✅ comprehensive_scan completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ comprehensive_scan failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["comprehensive_scan"]