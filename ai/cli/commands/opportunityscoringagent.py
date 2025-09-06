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

def calculate_opportunity_score(data):
    # Placeholder for actual scoring logic
    # This should be replaced with the real scoring algorithm
    return {"score": sum(data.values()) / len(data)}

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def opportunityscoringagent(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    OpportunityScoringAgent command.
    This command calculates opportunity scores based on provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running OpportunityScoringAgent command...[/blue]")
        
        if config is None:
            raise ValueError("Configuration file must be provided.")

        config_data = load_config(config)
        
        if verbose:
            console.print(f"[yellow]Loaded configuration: {config_data}[/yellow]")

        # Assuming config_data contains the necessary data for scoring
        result = calculate_opportunity_score(config_data)

        result_data = {
            "feature": "OpportunityScoringAgent",
            "status": "success", 
            "score": result["score"],
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"OpportunityScoringAgent Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ OpportunityScoringAgent completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ OpportunityScoringAgent failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["opportunityscoringagent"]