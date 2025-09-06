import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import os
import time

console = Console()

def load_config(config_path: str):
    with open(config_path, 'r') as f:
        return json.load(f)

def record_metrics(metrics: dict, output_path: str):
    with open(output_path, 'a') as f:
        json.dump(metrics, f)
        f.write('\n')

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def record_execution_metrics(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    record_execution_metrics command.
    Records execution metrics based on provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running record_execution_metrics command...[/blue]")
        
        if config:
            config_data = load_config(config)
        else:
            raise ValueError("Configuration file is required.")

        start_time = time.time()
        
        # Simulate execution metrics collection
        metrics = {
            "execution_time": time.time() - start_time,
            "status": "success",
            "config_used": config_data,
            "verbose": verbose
        }

        output_path = config_data.get("output_path", "execution_metrics.json")
        record_metrics(metrics, output_path)

        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(metrics, indent=2))
        elif output == 'table':
            table = Table(title=f"record_execution_metrics Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in metrics.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in metrics.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ record_execution_metrics completed successfully[/green]")
            
    except FileNotFoundError as e:
        console.print(f"[red]❌ Configuration file not found: {str(e)}[/red]")
        ctx.exit(1)
    except json.JSONDecodeError as e:
        console.print(f"[red]❌ Error parsing configuration file: {str(e)}[/red]")
        ctx.exit(1)
    except ValueError as e:
        console.print(f"[red]❌ Value error: {str(e)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ record_execution_metrics failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["record_execution_metrics"]