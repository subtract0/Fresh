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

def search_capabilities(query: str, config: dict):
    # Simulated search logic based on the configuration
    results = []
    for capability in config.get("capabilities", []):
        if query.lower() in capability.lower():
            results.append(capability)
    return results

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.option('--query', '-q', required=True, help='Search query for capabilities')
@click.pass_context
def demonstrate_search_capabilities(ctx, verbose: bool, output: str, config: Optional[str], query: str):
    """
    demonstrate_search_capabilities command.
    This command searches for capabilities based on a query and outputs the results.
    """
    try:
        if verbose:
            console.print(f"[blue]Running demonstrate_search_capabilities command...[/blue]")
        
        if config:
            config_data = load_config(config)
        else:
            raise ValueError("Configuration file must be provided.")

        results = search_capabilities(query, config_data)

        if not results:
            result_data = {
                "feature": "demonstrate_search_capabilities",
                "status": "no_results", 
                "message": "No capabilities found matching the query.",
                "query": query,
                "config_used": config,
                "verbose": verbose
            }
        else:
            result_data = {
                "feature": "demonstrate_search_capabilities",
                "status": "success", 
                "results": results,
                "query": query,
                "config_used": config,
                "verbose": verbose
            }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"demonstrate_search_capabilities Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                if isinstance(value, list):
                    value = ', '.join(value)
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                if isinstance(value, list):
                    value = ', '.join(value)
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ demonstrate_search_capabilities completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ demonstrate_search_capabilities failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["demonstrate_search_capabilities"]