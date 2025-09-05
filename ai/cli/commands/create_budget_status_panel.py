import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import yaml

console = Console()

def load_config(config_path: str):
    if config_path.endswith('.json'):
        with open(config_path, 'r') as f:
            return json.load(f)
    elif config_path.endswith('.yaml') or config_path.endswith('.yml'):
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    else:
        raise ValueError("Unsupported configuration file format. Use JSON or YAML.")

def validate_budget_data(budget_data):
    if 'budget' not in budget_data or not isinstance(budget_data['budget'], (int, float)):
        raise ValueError("Invalid budget data: 'budget' key is required and must be a number.")
    if 'expenses' not in budget_data or not isinstance(budget_data['expenses'], list):
        raise ValueError("Invalid budget data: 'expenses' key is required and must be a list.")

def calculate_budget_status(budget_data):
    total_expenses = sum(expense.get('amount', 0) for expense in budget_data['expenses'])
    remaining_budget = budget_data['budget'] - total_expenses
    return {
        "total_budget": budget_data['budget'],
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
def create_budget_status_panel(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    create_budget_status_panel command.
    Generates a budget status panel based on provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running create_budget_status_panel command...[/blue]")
        
        if not config:
            raise ValueError("Configuration file is required.")
        
        budget_data = load_config(config)
        validate_budget_data(budget_data)
        result_data = calculate_budget_status(budget_data)

        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"Budget Status Panel Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ create_budget_status_panel completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ create_budget_status_panel failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["create_budget_status_panel"]