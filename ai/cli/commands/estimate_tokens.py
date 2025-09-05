import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import os

console = Console()

def load_config(config_path: str):
    with open(config_path, 'r') as f:
        return json.load(f)

def estimate_token_cost(prompt: str, model: str, tokens_per_prompt: int, cost_per_token: float) -> float:
    total_tokens = tokens_per_prompt + len(prompt.split())
    return total_tokens * cost_per_token

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.option('--prompt', required=True, help='The prompt for which to estimate tokens')
@click.pass_context
def estimate_tokens(ctx, verbose: bool, output: str, config: Optional[str], prompt: str):
    """
    estimate_tokens command.
    
    Estimates the token usage and cost for a given prompt based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running estimate_tokens command...[/blue]")
        
        if config is None:
            raise ValueError("Configuration file is required.")
        
        config_data = load_config(config)
        
        model = config_data.get('model', 'default_model')
        tokens_per_prompt = config_data.get('tokens_per_prompt', 0)
        cost_per_token = config_data.get('cost_per_token', 0.0)

        if tokens_per_prompt <= 0 or cost_per_token < 0:
            raise ValueError("Invalid token or cost values in configuration.")
        
        estimated_cost = estimate_token_cost(prompt, model, tokens_per_prompt, cost_per_token)
        
        result_data = {
            "feature": "estimate_tokens",
            "status": "success", 
            "estimated_cost": estimated_cost,
            "model": model,
            "prompt_length": len(prompt.split()),
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"estimate_tokens Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ estimate_tokens completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ estimate_tokens failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["estimate_tokens"]