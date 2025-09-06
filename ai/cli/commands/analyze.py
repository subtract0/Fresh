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

def analyze_data(config, verbose):
    # Placeholder for actual analysis logic
    if verbose:
        console.print(f"[blue]Analyzing data with config: {config}[/blue]")
    
    # Simulated analysis result
    analysis_result = {
        "total_items": 100,
        "processed_items": 95,
        "errors": 5
    }
    return analysis_result

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def analyze(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    analyze command.
    Analyzes data based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running analyze command...[/blue]")
        
        if config is None:
            raise ValueError("Configuration file is required.")
        
        config_data = load_config(config)
        
        result_data = analyze_data(config_data, verbose)
        result_data["config_used"] = config
        result_data["verbose"] = verbose
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"analyze Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ analyze completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ analyze failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["analyze"]