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
def build(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    build command.
    
    This command builds the project based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running build command...[/blue]")
        
        # Validate configuration file
        if config:
            with open(config, 'r') as f:
                config_data = json.load(f)
                if not isinstance(config_data, dict):
                    raise ValueError("Configuration file must contain a valid JSON object.")
        else:
            config_data = {}

        # Simulate build logic
        build_directory = config_data.get("build_directory", "build")
        os.makedirs(build_directory, exist_ok=True)

        # Here you would add the actual build logic (e.g., compiling code, packaging)
        # For demonstration, we will just create a dummy file
        with open(os.path.join(build_directory, 'build_output.txt'), 'w') as f:
            f.write("Build completed successfully.")

        result_data = {
            "feature": "build",
            "status": "success", 
            "message": "Build functionality implemented successfully.",
            "config_used": config,
            "verbose": verbose,
            "output_directory": build_directory
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"Build Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ Build completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ Build failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["build"]