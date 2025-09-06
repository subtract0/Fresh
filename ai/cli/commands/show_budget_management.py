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

def validate_budget_data(budget_data):
    if not isinstance(budget_data, dict):
        raise ValueError("Budget data must be a dictionary.")
    if 'total_budget' not in budget_data or 'expenses' not in budget_data:
        raise ValueError("Budget data must contain 'total_budget' and 'expenses'.")

def calculate_budget_status(budget_data):
    total_budget = budget_data['total_budget']
    total_expenses = sum(budget_data['expenses'].values())
    remaining_budget = total_budget - total_expenses
    return {
        "total_budget": total_budget,
        "total_expenses": total_expenses,
        "remaining_budget": remaining_budget,
        "status": "under_budget" if remaining_budget >= 0 else "over_budget"
    }

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def show_budget_management(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    show_budget_management command.
    Displays budget management information based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running show_budget_management command...[/blue]")
        
        if not config:
            raise ValueError("Configuration file must be provided.")
        
        budget_data = load_config(config)
        validate_budget_data(budget_data)
        budget_status = calculate_budget_status(budget_data)
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(budget_status, indent=2))
        elif output == 'table':
            table = Table(title=f"Budget Management Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in budget_status.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in budget_status.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ show_budget_management completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ show_budget_management failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["show_budget_management"]