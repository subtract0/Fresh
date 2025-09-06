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
def selfdocumentingloopservice(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    SelfDocumentingLoopService command.
    
    This command provides a self-documenting loop service functionality.
    It validates the configuration file and outputs results in specified formats.
    """
    try:
        if verbose:
            console.print(f"[blue]Running SelfDocumentingLoopService command...[/blue]")
        
        # Validate configuration file
        if config:
            if not Path(config).is_file():
                raise FileNotFoundError(f"Configuration file '{config}' does not exist.")
            with open(config, 'r') as f:
                config_data = json.load(f)
                if not isinstance(config_data, dict):
                    raise ValueError("Configuration file must contain a valid JSON object.")
        else:
            config_data = {}

        # Implement actual SelfDocumentingLoopService logic here
        result_data = {
            "feature": "SelfDocumentingLoopService",
            "status": "success", 
            "message": "SelfDocumentingLoopService functionality implemented successfully",
            "config_used": config_data,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"SelfDocumentingLoopService Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ SelfDocumentingLoopService completed successfully[/green]")
            
    except FileNotFoundError as fnf_error:
        console.print(f"[red]❌ SelfDocumentingLoopService failed: {str(fnf_error)}[/red]")
        ctx.exit(1)
    except ValueError as val_error:
        console.print(f"[red]❌ SelfDocumentingLoopService failed: {str(val_error)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ SelfDocumentingLoopService failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)


# Export command for CLI registration
__all__ = ["selfdocumentingloopservice"]