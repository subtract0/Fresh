import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json

console = Console()


@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def analyze_file_sizes(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    analyze_file_sizes command.
    Analyzes file sizes in the specified directory and outputs the results.
    """
    try:
        if verbose:
            console.print(f"[blue]Running analyze_file_sizes command...[/blue]")
        
        # Load configuration if provided
        directory = Path(config) if config else Path.cwd()
        if not directory.is_dir():
            raise ValueError(f"The specified path '{directory}' is not a valid directory.")
        
        file_sizes = {}
        for file in directory.glob('*'):
            if file.is_file():
                file_sizes[file.name] = file.stat().st_size
        
        result_data = {
            "feature": "analyze_file_sizes",
            "status": "success", 
            "file_sizes": file_sizes,
            "config_used": str(directory),
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"analyze_file_sizes Results")
            table.add_column("File Name", style="cyan")
            table.add_column("Size (bytes)", style="magenta")
            
            for file_name, size in file_sizes.items():
                table.add_row(file_name, str(size))
            
            console.print(table)
        else:  # plain
            for file_name, size in file_sizes.items():
                console.print(f"{file_name}: {size} bytes")
        
        if verbose:
            console.print(f"[green]✅ analyze_file_sizes completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ analyze_file_sizes failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)


# Export command for CLI registration
__all__ = ["analyze_file_sizes"]