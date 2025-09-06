import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import pandas as pd

console = Console()

def load_config(config_path: str):
    with open(config_path, 'r') as file:
        return json.load(file)

def generate_feature_matrix_logic(config):
    # Placeholder for actual feature matrix generation logic
    # Here we simulate generating a feature matrix based on the config
    features = config.get("features", [])
    data = {feature: [1, 2, 3] for feature in features}  # Dummy data
    return pd.DataFrame(data)

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file', required=True)
@click.pass_context
def generate_feature_matrix(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    generate_feature_matrix command.
    Generates a feature matrix based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running generate_feature_matrix command...[/blue]")
        
        # Load configuration
        config_data = load_config(config)
        
        # Generate feature matrix
        feature_matrix = generate_feature_matrix_logic(config_data)
        
        # Prepare result data
        result_data = {
            "feature": "generate_feature_matrix",
            "status": "success", 
            "message": "Feature matrix generated successfully",
            "config_used": config_data,
            "verbose": verbose,
            "feature_matrix": feature_matrix.to_dict(orient='records')
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"generate_feature_matrix Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                if isinstance(value, list):
                    value = json.dumps(value)
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                if isinstance(value, list):
                    value = json.dumps(value)
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ generate_feature_matrix completed successfully[/green]")
            
    except FileNotFoundError:
        console.print(f"[red]❌ Configuration file not found: {config}[/red]")
        ctx.exit(1)
    except json.JSONDecodeError:
        console.print(f"[red]❌ Error decoding JSON from configuration file: {config}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ generate_feature_matrix failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["generate_feature_matrix"]