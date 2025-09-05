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

def optimize_costs(config):
    # Placeholder for actual cost optimization logic
    # This should be replaced with the real implementation
    if 'costs' not in config:
        raise ValueError("Configuration must contain 'costs' key.")
    
    optimized_costs = {k: v * 0.9 for k, v in config['costs'].items()}  # Example optimization
    return optimized_costs

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def costoptimizer(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    CostOptimizer command.
    This command optimizes costs based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running CostOptimizer command...[/blue]")
        
        if not config:
            raise ValueError("Configuration file must be provided.")
        
        config_data = load_config(config)
        
        optimized_costs = optimize_costs(config_data)
        
        result_data = {
            "feature": "CostOptimizer",
            "status": "success", 
            "optimized_costs": optimized_costs,
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"CostOptimizer Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ CostOptimizer completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ CostOptimizer failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["costoptimizer"]