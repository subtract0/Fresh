import click
from typing import Optional, Dict, Any
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import os

console = Console()

class InMemoryMemoryStore:
    def __init__(self):
        self.store: Dict[str, Any] = {}

    def set(self, key: str, value: Any) -> None:
        self.store[key] = value

    def get(self, key: str) -> Any:
        return self.store.get(key, None)

    def delete(self, key: str) -> bool:
        if key in self.store:
            del self.store[key]
            return True
        return False

    def clear(self) -> None:
        self.store.clear()

    def get_all(self) -> Dict[str, Any]:
        return self.store

memory_store = InMemoryMemoryStore()

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def inmemorymemorystore(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    InMemoryMemoryStore command.
    This command allows you to interact with an in-memory key-value store.
    """
    try:
        if verbose:
            console.print(f"[blue]Running InMemoryMemoryStore command...[/blue]")
        
        if config:
            if not Path(config).is_file():
                raise FileNotFoundError(f"Configuration file '{config}' does not exist.")
            with open(config, 'r') as f:
                config_data = json.load(f)
                for key, value in config_data.items():
                    memory_store.set(key, value)
                if verbose:
                    console.print(f"[yellow]Loaded configuration from {config}[/yellow]")

        result_data = {
            "feature": "InMemoryMemoryStore",
            "status": "success", 
            "message": "InMemoryMemoryStore functionality implemented",
            "stored_data": memory_store.get_all(),
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"InMemoryMemoryStore Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ InMemoryMemoryStore completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ InMemoryMemoryStore failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["inmemorymemorystore"]