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

def find_files_in_directory(directory: str, search_term: str):
    matches = []
    for root, _, files in os.walk(directory):
        for file in files:
            if search_term in file:
                matches.append(Path(root) / file)
    return matches

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.option('--search', '-s', required=True, help='Search term for files')
@click.pass_context
def where(ctx, verbose: bool, output: str, config: Optional[str], search: str):
    """
    where command to find files containing the search term.
    """
    try:
        if verbose:
            console.print(f"[blue]Running where command with search term: {search}...[/blue]")
        
        config_data = {}
        if config:
            config_data = load_config(config)

        search_directory = config_data.get("search_directory", ".")
        if not os.path.isdir(search_directory):
            raise ValueError(f"Search directory '{search_directory}' does not exist.")

        found_files = find_files_in_directory(search_directory, search)

        result_data = {
            "feature": "where",
            "status": "success" if found_files else "no_results", 
            "files": found_files,
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"where Results")
            table.add_column("File Path", style="cyan")
            
            for file in found_files:
                table.add_row(str(file))
            
            console.print(table)
        else:  # plain
            if found_files:
                for file in found_files:
                    console.print(f"Found: {file}")
            else:
                console.print("No files found.")

        if verbose:
            console.print(f"[green]✅ where completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ where failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["where"]