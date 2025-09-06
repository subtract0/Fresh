import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import yaml

console = Console()

def load_config(config_path: str):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def normalize_tag_logic(data):
    # Placeholder for normalization logic
    return {key: value.strip().lower() for key, value in data.items()}

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def normalize_tag(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    normalize_tag command.
    Normalizes tags based on provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running normalize_tag command...[/blue]")
        
        config_data = {}
        if config:
            config_data = load_config(config)
            if verbose:
                console.print(f"[yellow]Loaded configuration: {config_data}[/yellow]")

        # Simulate data to normalize
        data_to_normalize = {
            "Tag1": "  Example Tag  ",
            "Tag2": "Another Tag  ",
            "Tag3": "  Yet Another Tag  "
        }

        normalized_data = normalize_tag_logic(data_to_normalize)

        result_data = {
            "feature": "normalize_tag",
            "status": "success", 
            "normalized_data": normalized_data,
            "config_used": config_data,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"normalize_tag Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ normalize_tag completed successfully[/green]")
            
    except FileNotFoundError as fnf_error:
        console.print(f"[red]❌ Configuration file not found: {str(fnf_error)}[/red]")
        ctx.exit(1)
    except yaml.YAMLError as yaml_error:
        console.print(f"[red]❌ Error parsing YAML configuration: {str(yaml_error)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ normalize_tag failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["normalize_tag"]