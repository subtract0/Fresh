import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import os

console = Console()

def load_config(config_path: str):
    with open(config_path, 'r') as file:
        return json.load(file)

def detect_regressions_logic(config):
    # Placeholder for actual regression detection logic
    # This should be replaced with the actual implementation
    if 'regression_threshold' not in config:
        raise ValueError("Configuration must include 'regression_threshold'")
    
    # Simulated regression detection result
    return {
        "detected_regressions": [
            {"feature": "feature_a", "regression_value": 0.1},
            {"feature": "feature_b", "regression_value": 0.2}
        ],
        "threshold": config['regression_threshold']
    }

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file', required=True)
@click.pass_context
def detect_regressions(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    detect_regressions command.
    This command detects regressions based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running detect_regressions command...[/blue]")
        
        config_data = load_config(config)
        
        if verbose:
            console.print(f"[blue]Loaded configuration: {config_data}[/blue]")
        
        result = detect_regressions_logic(config_data)
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result, indent=2))
        elif output == 'table':
            table = Table(title=f"detect_regressions Results")
            table.add_column("Feature", style="cyan")
            table.add_column("Regression Value", style="magenta")
            table.add_column("Threshold", style="yellow")
            
            for regression in result["detected_regressions"]:
                table.add_row(regression["feature"], str(regression["regression_value"]), str(result["threshold"]))
            
            console.print(table)
        else:  # plain
            console.print("Detected Regressions:")
            for regression in result["detected_regressions"]:
                console.print(f"{regression['feature']}: {regression['regression_value']} (Threshold: {result['threshold']})")
        
        if verbose:
            console.print(f"[green]✅ detect_regressions completed successfully[/green]")
            
    except FileNotFoundError:
        console.print(f"[red]❌ Configuration file not found: {config}[/red]")
        ctx.exit(1)
    except json.JSONDecodeError:
        console.print(f"[red]❌ Error decoding JSON from configuration file: {config}[/red]")
        ctx.exit(1)
    except ValueError as ve:
        console.print(f"[red]❌ Configuration error: {str(ve)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ detect_regressions failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["detect_regressions"]