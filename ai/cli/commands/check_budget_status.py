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

def check_budget_status_logic(config):
    # Simulated budget check logic
    budget = config.get("budget", 0)
    expenses = config.get("expenses", 0)
    remaining_budget = budget - expenses
    status = "under_budget" if remaining_budget >= 0 else "over_budget"
    
    return {
        "budget": budget,
        "expenses": expenses,
        "remaining_budget": remaining_budget,
        "status": status
    }

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file', required=True)
@click.pass_context
def check_budget_status(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    check_budget_status command.
    This command checks the budget status based on the provided configuration file.
    """
    try:
        if verbose:
            console.print(f"[blue]Running check_budget_status command...[/blue]")
        
        config_data = load_config(config)
        
        if 'budget' not in config_data or 'expenses' not in config_data:
            raise ValueError("Configuration must contain 'budget' and 'expenses' fields.")
        
        result_data = check_budget_status_logic(config_data)
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"check_budget_status Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ check_budget_status completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ check_budget_status failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["check_budget_status"]