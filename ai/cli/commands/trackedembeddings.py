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

def process_tracked_embeddings(config):
    # Placeholder for actual TrackedEmbeddings processing logic
    # This should be replaced with the actual implementation
    return {
        "embedding_size": config.get("embedding_size", 128),
        "num_layers": config.get("num_layers", 2),
        "learning_rate": config.get("learning_rate", 0.001),
        "status": "success",
        "message": "TrackedEmbeddings processed successfully"
    }

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def trackedembeddings(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    TrackedEmbeddings command.
    This command processes tracked embeddings based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running TrackedEmbeddings command...[/blue]")
        
        if config is None:
            raise ValueError("Configuration file must be provided.")
        
        config_data = load_config(config)
        
        if verbose:
            console.print(f"[yellow]Loaded configuration: {config_data}[/yellow]")
        
        result_data = process_tracked_embeddings(config_data)
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"TrackedEmbeddings Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ TrackedEmbeddings completed successfully[/green]")
            
    except FileNotFoundError:
        console.print(f"[red]❌ Configuration file not found: {config}[/red]")
        ctx.exit(1)
    except ValueError as ve:
        console.print(f"[red]❌ Value error: {str(ve)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ TrackedEmbeddings failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["trackedembeddings"]