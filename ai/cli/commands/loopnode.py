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

def validate_config(config):
    if 'iterations' not in config or not isinstance(config['iterations'], int):
        raise ValueError("Configuration must include 'iterations' as an integer.")
    if 'loop_message' not in config or not isinstance(config['loop_message'], str):
        raise ValueError("Configuration must include 'loop_message' as a string.")

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def loopnode(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    LoopNode command.
    Executes a loop based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running LoopNode command...[/blue]")
        
        if config:
            config_data = load_config(config)
            validate_config(config_data)
            iterations = config_data['iterations']
            loop_message = config_data['loop_message']
        else:
            raise ValueError("Configuration file is required.")

        results = []
        for i in range(iterations):
            results.append(f"{loop_message} - Iteration {i + 1}")

        result_data = {
            "feature": "LoopNode",
            "status": "success", 
            "results": results,
            "config_used": config,
            "verbose": verbose
        }
        
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"LoopNode Results")
            table.add_column("Iteration", style="cyan")
            table.add_column("Message", style="magenta")
            
            for i, message in enumerate(results):
                table.add_row(str(i + 1), message)
            
            console.print(table)
        else:  # plain
            for i, message in enumerate(results):
                console.print(f"Iteration {i + 1}: {message}")
        
        if verbose:
            console.print(f"[green]✅ LoopNode completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ LoopNode failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["loopnode"]