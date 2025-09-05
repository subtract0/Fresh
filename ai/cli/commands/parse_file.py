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

def parse_file_logic(file_path: str, config: Optional[dict]):
    if not Path(file_path).exists():
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    
    # Simulate parsing logic
    with open(file_path, 'r') as f:
        data = f.read()
    
    # Here you would implement your actual parsing logic
    parsed_data = {
        "file_content": data,
        "config": config
    }
    
    return parsed_data

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.argument('file_path', type=click.Path(exists=True))
@click.pass_context
def parse_file(ctx, verbose: bool, output: str, config: Optional[str], file_path: str):
    """
    parse_file command.
    Parses the specified file and outputs the result in the desired format.
    """
    try:
        if verbose:
            console.print(f"[blue]Running parse_file command on {file_path}...[/blue]")
        
        config_data = load_config(config) if config else None
        result_data = parse_file_logic(file_path, config_data)
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"parse_file Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ parse_file completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ parse_file failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["parse_file"]