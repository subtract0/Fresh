import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import subprocess
import os

console = Console()


@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.argument('branch_name', required=True)
@click.pass_context
def create_feature_branch(ctx, verbose: bool, output: str, config: Optional[str], branch_name: str):
    """
    create_feature_branch command.
    
    This command creates a new feature branch in the current git repository.
    
    :param branch_name: The name of the feature branch to create.
    """
    try:
        if verbose:
            console.print(f"[blue]Running create_feature_branch command...[/blue]")
        
        # Validate branch name
        if not branch_name:
            raise ValueError("Branch name cannot be empty.")
        
        # Load configuration if provided
        config_data = {}
        if config:
            with open(config, 'r') as f:
                config_data = json.load(f)
        
        # Create the feature branch
        subprocess.run(['git', 'checkout', '-b', branch_name], check=True)
        
        result_data = {
            "feature": "create_feature_branch",
            "status": "success", 
            "message": f"Feature branch '{branch_name}' created successfully.",
            "config_used": config_data,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"create_feature_branch Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ create_feature_branch completed successfully[/green]")
            
    except subprocess.CalledProcessError as e:
        console.print(f"[red]❌ create_feature_branch failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ create_feature_branch failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)


# Export command for CLI registration
__all__ = ["create_feature_branch"]