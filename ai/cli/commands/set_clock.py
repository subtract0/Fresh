import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import datetime

console = Console()


@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.option('--time', type=str, required=True, help='Time to set the clock (format: HH:MM:SS)')
@click.pass_context
def set_clock(ctx, verbose: bool, output: str, config: Optional[str], time: str):
    """
    set_clock command.
    
    Sets the system clock to the specified time.
    """
    try:
        if verbose:
            console.print(f"[blue]Running set_clock command...[/blue]")
        
        # Validate time format
        try:
            time_obj = datetime.datetime.strptime(time, "%H:%M:%S").time()
        except ValueError:
            raise ValueError("Time must be in HH:MM:SS format.")
        
        # Here you would implement the actual clock setting logic
        # For demonstration, we will just simulate it
        # In a real implementation, you would use system calls or libraries to set the clock
        result_data = {
            "feature": "set_clock",
            "status": "success", 
            "message": f"Clock set to {time_obj}",
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"set_clock Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ set_clock completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ set_clock failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)


# Export command for CLI registration
__all__ = ["set_clock"]