import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import os

console = Console()


@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def save_to_file(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    save_to_file command.
    Saves data to a specified file format based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running save_to_file command...[/blue]")
        
        if config is None:
            raise ValueError("Configuration file must be provided.")
        
        with open(config, 'r') as config_file:
            config_data = json.load(config_file)

        output_file = config_data.get("output_file", "output.json")
        data_to_save = config_data.get("data", {})
        
        if not data_to_save:
            raise ValueError("No data found in configuration to save.")
        
        # Save data to the specified output format
        if output == 'json':
            with open(output_file, 'w') as f:
                json.dump(data_to_save, f, indent=2)
            result_message = f"Data saved to {output_file} in JSON format."
        
        elif output == 'table':
            table = Table(title="Saved Data")
            for key, value in data_to_save.items():
                table.add_column(str(key), style="cyan")
                table.add_row(str(value))
            console.print(table)
            result_message = f"Data displayed in table format."
        
        else:  # plain
            with open(output_file, 'w') as f:
                for key, value in data_to_save.items():
                    f.write(f"{key}: {value}\n")
            result_message = f"Data saved to {output_file} in plain text format."

        console.print(result_message)
        
        if verbose:
            console.print(f"[green]✅ save_to_file completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ save_to_file failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)


# Export command for CLI registration
__all__ = ["save_to_file"]