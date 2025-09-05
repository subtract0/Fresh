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

def cleanup_agents(config):
    completed_agents_dir = config.get("completed_agents_directory", "completed_agents")
    if not os.path.exists(completed_agents_dir):
        raise FileNotFoundError(f"Directory '{completed_agents_dir}' does not exist.")
    
    cleaned_agents = []
    for filename in os.listdir(completed_agents_dir):
        file_path = os.path.join(completed_agents_dir, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
            cleaned_agents.append(filename)
    
    return cleaned_agents

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def cleanup_completed_agents(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    cleanup_completed_agents command.
    Cleans up completed agents from the specified directory.
    """
    try:
        if verbose:
            console.print(f"[blue]Running cleanup_completed_agents command...[/blue]")
        
        if config is None:
            raise ValueError("Configuration file must be provided.")
        
        config_data = load_config(config)
        cleaned_agents = cleanup_agents(config_data)
        
        result_data = {
            "feature": "cleanup_completed_agents",
            "status": "success", 
            "message": f"Cleaned up {len(cleaned_agents)} agents.",
            "cleaned_agents": cleaned_agents,
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"cleanup_completed_agents Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ cleanup_completed_agents completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ cleanup_completed_agents failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["cleanup_completed_agents"]