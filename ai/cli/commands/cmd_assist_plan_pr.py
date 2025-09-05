import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import os

console = Console()

def load_config(config_path: str):
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    with open(config_path, 'r') as file:
        return json.load(file)

def process_assist_plan(data):
    # Placeholder for actual business logic
    # Here you would implement the logic to process the assist plan
    return {
        "processed": True,
        "details": "Assist plan processed successfully."
    }

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def cmd_assist_plan_pr(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    cmd_assist_plan_pr command.
    
    This command processes an assist plan based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running cmd_assist_plan_pr command...[/blue]")
        
        config_data = {}
        if config:
            config_data = load_config(config)

        # Process the assist plan
        result = process_assist_plan(config_data)

        result_data = {
            "feature": "cmd_assist_plan_pr",
            "status": "success", 
            "message": result["details"],
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"cmd_assist_plan_pr Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ cmd_assist_plan_pr completed successfully[/green]")
            
    except FileNotFoundError as fnf_error:
        console.print(f"[red]❌ cmd_assist_plan_pr failed: {str(fnf_error)}[/red]")
        ctx.exit(1)
    except json.JSONDecodeError as json_error:
        console.print(f"[red]❌ cmd_assist_plan_pr failed: Invalid JSON in configuration file - {str(json_error)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ cmd_assist_plan_pr failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["cmd_assist_plan_pr"]