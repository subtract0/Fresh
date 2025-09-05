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
        raise ValueError("Unsupported config file format. Use JSON or YAML.")

def validate_config(config):
    if 'features' not in config:
        raise ValueError("Configuration must contain 'features' key.")

def check_feature_logic(config):
    features = config.get('features', [])
    results = {}
    for feature in features:
        # Simulate feature checking logic
        results[feature] = {
            "status": "enabled" if feature in ["feature1", "feature2"] else "disabled",
            "message": f"{feature} is {'enabled' if feature in ['feature1', 'feature2'] else 'disabled'}"
        }
    return results

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def check_feature(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    check_feature command.
    This command checks the status of features defined in the configuration file.
    """
    try:
        if verbose:
            console.print(f"[blue]Running check_feature command...[/blue]")
        
        if not config:
            raise ValueError("Configuration file must be provided.")
        
        config_data = load_config(config)
        validate_config(config_data)
        
        results = check_feature_logic(config_data)
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(results, indent=2))
        elif output == 'table':
            table = Table(title=f"check_feature Results")
            table.add_column("Feature", style="cyan")
            table.add_column("Status", style="magenta")
            table.add_column("Message", style="green")
            
            for feature, result in results.items():
                table.add_row(feature, result["status"], result["message"])
            
            console.print(table)
        else:  # plain
            for feature, result in results.items():
                console.print(f"{feature}: {result['status']} - {result['message']}")
        
        if verbose:
            console.print(f"[green]✅ check_feature completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ check_feature failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["check_feature"]