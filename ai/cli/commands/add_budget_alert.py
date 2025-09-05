import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import jsonschema
from jsonschema import validate

console = Console()

# Define the schema for budget alert
budget_alert_schema = {
    "type": "object",
    "properties": {
        "amount": {"type": "number"},
        "category": {"type": "string"},
        "alert_type": {"type": "string", "enum": ["above", "below"]},
        "message": {"type": "string"}
    },
    "required": ["amount", "category", "alert_type", "message"]
}

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.option('--amount', type=float, required=True, help='Budget alert amount')
@click.option('--category', type=str, required=True, help='Budget category')
@click.option('--alert_type', type=click.Choice(['above', 'below']), required=True, help='Alert type')
@click.option('--message', type=str, required=True, help='Alert message')
@click.pass_context
def add_budget_alert(ctx, verbose: bool, output: str, config: Optional[str], amount: float, category: str, alert_type: str, message: str):
    """
    Add a budget alert.
    """
    try:
        if verbose:
            console.print(f"[blue]Running add_budget_alert command...[/blue]")
        
        # Create budget alert data
        budget_alert_data = {
            "amount": amount,
            "category": category,
            "alert_type": alert_type,
            "message": message
        }
        
        # Validate the budget alert data against the schema
        validate(instance=budget_alert_data, schema=budget_alert_schema)

        # Here you would typically save the budget alert to a database or a file
        # For demonstration, we will just return the data
        result_data = {
            "feature": "add_budget_alert",
            "status": "success", 
            "message": "Budget alert added successfully",
            "data": budget_alert_data,
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"add_budget_alert Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ add_budget_alert completed successfully[/green]")
            
    except jsonschema.exceptions.ValidationError as ve:
        console.print(f"[red]❌ Validation error: {ve.message}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ add_budget_alert failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["add_budget_alert"]