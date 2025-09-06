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
@click.argument('feature_name', type=str)
@click.argument('approval_status', type=click.Choice(['approved', 'rejected']))
@click.pass_context
def add_human_approval(ctx, verbose: bool, output: str, config: Optional[str], feature_name: str, approval_status: str):
    """
    Add human approval for a specific feature.
    
    FEATURE_NAME: The name of the feature to approve or reject.
    APPROVAL_STATUS: The status of the approval (approved or rejected).
    """
    try:
        if verbose:
            console.print(f"[blue]Running add_human_approval command for feature '{feature_name}'...[/blue]")
        
        if not feature_name:
            raise ValueError("Feature name cannot be empty.")
        
        if approval_status not in ['approved', 'rejected']:
            raise ValueError("Approval status must be either 'approved' or 'rejected'.")

        # Load configuration if provided
        config_data = {}
        if config:
            with open(config, 'r') as f:
                config_data = json.load(f)

        # Simulate saving the approval status (this would be replaced with actual logic)
        approval_record = {
            "feature": feature_name,
            "status": approval_status,
            "config_used": config_data,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(approval_record, indent=2))
        elif output == 'table':
            table = Table(title=f"add_human_approval Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in approval_record.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in approval_record.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ add_human_approval completed successfully for feature '{feature_name}'[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ add_human_approval failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["add_human_approval"]