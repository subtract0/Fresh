import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import yaml

console = Console()

def validate_config(config_path: str) -> dict:
    if not Path(config_path).is_file():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    with open(config_path, 'r') as file:
        if config_path.endswith('.json'):
            return json.load(file)
        elif config_path.endswith('.yaml') or config_path.endswith('.yml'):
            return yaml.safe_load(file)
        else:
            raise ValueError("Unsupported configuration file format. Use JSON or YAML.")

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def workflowsyntaxerror(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    WorkflowSyntaxError command.
    Validates workflow syntax based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running WorkflowSyntaxError command...[/blue]")
        
        config_data = {}
        if config:
            config_data = validate_config(config)
            if verbose:
                console.print(f"[yellow]Using configuration: {config_data}[/yellow]")

        # Simulate workflow syntax validation logic
        # Here you would implement the actual validation logic
        is_valid = True  # Placeholder for actual validation result
        if not is_valid:
            raise ValueError("Workflow syntax is invalid based on the provided configuration.")

        result_data = {
            "feature": "WorkflowSyntaxError",
            "status": "success", 
            "message": "Workflow syntax is valid.",
            "config_used": config_data,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"WorkflowSyntaxError Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ WorkflowSyntaxError completed successfully[/green]")
            
    except FileNotFoundError as fnf_error:
        console.print(f"[red]❌ WorkflowSyntaxError failed: {str(fnf_error)}[/red]")
        ctx.exit(1)
    except ValueError as val_error:
        console.print(f"[red]❌ WorkflowSyntaxError failed: {str(val_error)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ WorkflowSyntaxError failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["workflowsyntaxerror"]