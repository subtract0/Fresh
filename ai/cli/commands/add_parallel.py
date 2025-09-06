import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import concurrent.futures

console = Console()

def add_numbers_parallel(numbers):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(sum, numbers))
    return results

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.argument('numbers', nargs=-1, type=int)
@click.pass_context
def add_parallel(ctx, verbose: bool, output: str, config: Optional[str], numbers: tuple):
    """
    add_parallel command to sum numbers in parallel.
    
    This command takes a list of integers and sums them using parallel processing.
    """
    try:
        if verbose:
            console.print(f"[blue]Running add_parallel command with numbers: {numbers}...[/blue]")
        
        if not numbers:
            raise ValueError("No numbers provided for addition.")
        
        # Prepare numbers for parallel addition
        chunk_size = 2  # Adjust chunk size as needed
        number_chunks = [numbers[i:i + chunk_size] for i in range(0, len(numbers), chunk_size)]
        
        result_data = {
            "feature": "add_parallel",
            "status": "success", 
            "result": add_numbers_parallel(number_chunks),
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"add_parallel Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ add_parallel completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ add_parallel failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["add_parallel"]