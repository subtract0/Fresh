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

def perform_assessment(config):
    # Placeholder for actual assessment logic
    # Simulating some assessment results based on the config
    if 'criteria' not in config:
        raise ValueError("Configuration must contain 'criteria' key.")
    
    assessment_results = {
        "criteria": config['criteria'],
        "assessment": "passed" if config['criteria'] == "valid" else "failed",
        "details": "Assessment completed based on provided criteria."
    }
    return assessment_results

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file', required=True)
@click.pass_context
def technicalassessmentagent(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    TechnicalAssessmentAgent command.
    This command performs a technical assessment based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running TechnicalAssessmentAgent command...[/blue]")
        
        config_data = load_config(config)
        assessment_results = perform_assessment(config_data)
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(assessment_results, indent=2))
        elif output == 'table':
            table = Table(title=f"TechnicalAssessmentAgent Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in assessment_results.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in assessment_results.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ TechnicalAssessmentAgent completed successfully[/green]")
            
    except FileNotFoundError as fnf_error:
        console.print(f"[red]❌ Error: {str(fnf_error)}[/red]")
        ctx.exit(1)
    except ValueError as val_error:
        console.print(f"[red]❌ Error: {str(val_error)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ TechnicalAssessmentAgent failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["technicalassessmentagent"]