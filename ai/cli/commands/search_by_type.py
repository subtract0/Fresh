import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import os

console = Console()

def load_config(config_path: str):
    if config_path and Path(config_path).exists():
        with open(config_path, 'r') as f:
            return json.load(f)
    return {}

def search_files_by_type(search_type: str, directory: str):
    results = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(search_type):
                results.append(os.path.join(root, file))
    return results

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.option('--type', '-t', required=True, help='File type to search for (e.g., .txt, .py)')
@click.option('--directory', '-d', default='.', help='Directory to search in')
@click.pass_context
def search_by_type(ctx, verbose: bool, output: str, config: Optional[str], type: str, directory: str):
    """
    Search for files by type in a specified directory.
    """
    try:
        if verbose:
            console.print(f"[blue]Running search_by_type command...[/blue]")
        
        config_data = load_config(config)
        search_type = type.strip()
        
        if not search_type.startswith('.'):
            search_type = '.' + search_type
        
        if verbose:
            console.print(f"[yellow]Searching for files of type: {search_type} in directory: {directory}[/yellow]")
        
        results = search_files_by_type(search_type, directory)
        
        if not results:
            result_data = {
                "feature": "search_by_type",
                "status": "no_results", 
                "message": f"No files found for type {search_type} in {directory}",
                "config_used": config_data,
                "verbose": verbose
            }
        else:
            result_data = {
                "feature": "search_by_type",
                "status": "success", 
                "files": results,
                "config_used": config_data,
                "verbose": verbose
            }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"search_by_type Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                if isinstance(value, list):
                    value = ', '.join(value)
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                if isinstance(value, list):
                    value = ', '.join(value)
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ search_by_type completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ search_by_type failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["search_by_type"]