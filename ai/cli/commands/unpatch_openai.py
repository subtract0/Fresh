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

def unpatch_openai_logic(config):
    # Simulate unpatching logic
    if 'openai' in config.get('features', []):
        config['features'].remove('openai')
        return {"status": "success", "message": "OpenAI unpatched successfully"}
    else:
        return {"status": "error", "message": "OpenAI feature not found in configuration"}

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file', required=True)
@click.pass_context
def unpatch_openai(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    unpatch_openai command.
    This command removes the OpenAI feature from the configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running unpatch_openai command...[/blue]")
        
        # Load configuration
        config_data = load_config(config)
        
        # Execute unpatch logic
        result = unpatch_openai_logic(config_data)
        
        # Save updated configuration
        with open(config, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        # Prepare result data
        result_data = {
            "feature": "unpatch_openai",
            "status": result["status"],
            "message": result["message"],
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"unpatch_openai Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ unpatch_openai completed successfully[/green]")
            
    except FileNotFoundError:
        console.print(f"[red]❌ Configuration file not found: {config}[/red]")
        ctx.exit(1)
    except json.JSONDecodeError:
        console.print(f"[red]❌ Failed to parse configuration file: {config}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ unpatch_openai failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["unpatch_openai"]