import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import firebase_admin
from firebase_admin import credentials, firestore

console = Console()

def initialize_firestore(config_path: str):
    cred = credentials.Certificate(config_path)
    firebase_admin.initialize_app(cred)
    return firestore.client()

def get_firestore_stats_data(db):
    collections = db.collections()
    stats = {}
    for collection in collections:
        docs = collection.stream()
        stats[collection.id] = len(list(docs))
    return stats

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def get_firestore_stats(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    get_firestore_stats command.
    Retrieves statistics from Firestore collections.
    """
    try:
        if verbose:
            console.print(f"[blue]Running get_firestore_stats command...[/blue]")
        
        if not config:
            raise ValueError("Configuration file is required.")
        
        db = initialize_firestore(config)
        stats_data = get_firestore_stats_data(db)
        
        result_data = {
            "feature": "get_firestore_stats",
            "status": "success", 
            "data": stats_data,
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"get_firestore_stats Results")
            table.add_column("Collection", style="cyan")
            table.add_column("Document Count", style="magenta")
            
            for collection, count in stats_data.items():
                table.add_row(collection, str(count))
            
            console.print(table)
        else:  # plain
            for collection, count in stats_data.items():
                console.print(f"{collection}: {count}")
        
        if verbose:
            console.print(f"[green]✅ get_firestore_stats completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ get_firestore_stats failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["get_firestore_stats"]