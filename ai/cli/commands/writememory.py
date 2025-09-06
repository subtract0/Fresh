import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import os

console = Console()

def load_config(config_path: str):
    with open(config_path, 'r') as file:
        return json.load(file)

def write_memory(data: dict):
    memory_file = Path("memory.json")
    if memory_file.exists():
        with open(memory_file, 'r+') as file:
            existing_data = json.load(file)
            existing_data.update(data)
            file.seek(0)
            json.dump(existing_data, file, indent=2)
    else:
        with open(memory_file, 'w') as file:
            json.dump(data, file, indent=2)

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def writememory(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    WriteMemory command.
    Writes data to memory based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running WriteMemory command...[/blue]")
        
        if config:
            config_data = load_config(config)
        else:
            console.print(f"[red]❌ Configuration file is required.[/red]")
            ctx.exit(1)

        if not isinstance(config_data, dict):
            console.print(f"[red]❌ Configuration file must contain a valid JSON object.[/red]")
            ctx.exit(1)

        write_memory(config_data)

        result_data = {
            "feature": "WriteMemory",
            "status": "success", 
            "message": "Memory written successfully",
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"WriteMemory Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ WriteMemory completed successfully[/green]")
            
    except FileNotFoundError as e:
        console.print(f"[red]❌ Configuration file not found: {str(e)}[/red]")
        ctx.exit(1)
    except json.JSONDecodeError as e:
        console.print(f"[red]❌ Error decoding JSON: {str(e)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ WriteMemory failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["writememory"]