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

def analyze_cost_breakdown(config: dict):
    # Placeholder for actual cost breakdown analysis logic
    # This should be replaced with real analysis based on the configuration
    return {
        "total_cost": 1000,
        "breakdown": {
            "item_a": 400,
            "item_b": 600
        }
    }

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file', required=True)
@click.pass_context
def get_cost_breakdown_analysis(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    get_cost_breakdown_analysis command.
    Analyzes cost breakdown based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running get_cost_breakdown_analysis command...[/blue]")
        
        config_data = load_config(config)
        
        if verbose:
            console.print(f"[yellow]Loaded configuration: {config_data}[/yellow]")
        
        result_data = analyze_cost_breakdown(config_data)
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"get_cost_breakdown_analysis Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        table.add_row(f"{key}.{sub_key}", str(sub_value))
                else:
                    table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        console.print(f"{key}.{sub_key}: {sub_value}")
                else:
                    console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ get_cost_breakdown_analysis completed successfully[/green]")
            
    except FileNotFoundError:
        console.print(f"[red]❌ Configuration file not found: {config}[/red]")
        ctx.exit(1)
    except yaml.YAMLError as e:
        console.print(f"[red]❌ Error parsing configuration file: {str(e)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ get_cost_breakdown_analysis failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["get_cost_breakdown_analysis"]