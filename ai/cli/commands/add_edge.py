import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import networkx as nx

console = Console()
graph = nx.Graph()

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.option('--source', required=True, help='Source node for the edge')
@click.option('--target', required=True, help='Target node for the edge')
@click.pass_context
def add_edge(ctx, verbose: bool, output: str, config: Optional[str], source: str, target: str):
    """
    Add an edge between two nodes in the graph.
    """
    try:
        if verbose:
            console.print(f"[blue]Running add_edge command...[/blue]")
        
        # Validate nodes
        if not source or not target:
            raise ValueError("Both source and target nodes must be provided.")
        
        # Add edge to the graph
        graph.add_edge(source, target)
        
        result_data = {
            "feature": "add_edge",
            "status": "success", 
            "message": f"Edge added between {source} and {target}",
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"add_edge Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ add_edge completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ add_edge failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["add_edge"]