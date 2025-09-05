import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import pkg_resources

console = Console()


@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def cmd_version(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    cmd_version command to display the version of the application and its features.
    """
    try:
        if verbose:
            console.print(f"[blue]Running cmd_version command...[/blue]")
        
        # Load configuration if provided
        config_data = {}
        if config:
            with open(config, 'r') as f:
                config_data = json.load(f)

        # Get version information
        version_info = {
            "version": pkg_resources.get_distribution("your_package_name").version,
            "features": ["feature1", "feature2", "feature3"],  # Replace with actual features
            "config_used": config_data,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(version_info, indent=2))
        elif output == 'table':
            table = Table(title=f"cmd_version Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in version_info.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in version_info.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ cmd_version completed successfully[/green]")
            
    except FileNotFoundError as fnf_error:
        console.print(f"[red]❌ Configuration file not found: {str(fnf_error)}[/red]")
        ctx.exit(1)
    except json.JSONDecodeError as json_error:
        console.print(f"[red]❌ Error decoding JSON from configuration file: {str(json_error)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ cmd_version failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)


# Export command for CLI registration
__all__ = ["cmd_version"]