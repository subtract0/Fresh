import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import os

console = Console()

class MemoryItem:
    def __init__(self, config_path: str):
        """
        Initialize the MemoryItem with the given configuration path.

        :param config_path: Path to the configuration file.
        """
        self.config_path = config_path
        self.load_config()

    def load_config(self):
        """
        Load the configuration from the specified file.

        Raises:
            FileNotFoundError: If the configuration file does not exist.
            json.JSONDecodeError: If the configuration file is not valid JSON.
        """
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        with open(self.config_path, 'r') as file:
            self.config = json.load(file)

    def process_memory_item(self):
        """
        Process the memory item based on the loaded configuration.

        :return: A dictionary containing the processing result.
        """
        # Simulate processing logic
        return {
            "feature": "MemoryItem",
            "status": "success",
            "message": "MemoryItem processed successfully",
            "config": self.config
        }

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), required=True, help='Configuration file')
@click.pass_context
def memoryitem(ctx, verbose: bool, output: str, config: str):
    """
    MemoryItem command.
    Processes memory items based on the provided configuration.

    :param ctx: Click context.
    :param verbose: Flag to enable verbose output.
    :param output: Desired output format.
    :param config: Path to the configuration file.
    """
    try:
        if verbose:
            console.print(f"[blue]Running MemoryItem command...[/blue]")
        
        memory_item = MemoryItem(config)
        result_data = memory_item.process_memory_item()
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"MemoryItem Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ MemoryItem completed successfully[/green]")
            
    except FileNotFoundError as fnf_error:
        console.print(f"[red]❌ MemoryItem failed: {str(fnf_error)}[/red]")
        ctx.exit(1)
    except json.JSONDecodeError as json_error:
        console.print(f"[red]❌ JSON decoding error: {str(json_error)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ MemoryItem failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["memoryitem"]