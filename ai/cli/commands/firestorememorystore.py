import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import firebase_admin
from firebase_admin import credentials, firestore

console = Console()

# Initialize Firestore
def initialize_firestore(config_path: str):
    cred = credentials.Certificate(config_path)
    firebase_admin.initialize_app(cred)
    return firestore.client()

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def firestorememorystore(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    FirestoreMemoryStore command.
    This command interacts with Firestore to store and retrieve data.
    """
    try:
        if verbose:
            console.print(f"[blue]Running FirestoreMemoryStore command...[/blue]")
        
        if not config:
            raise ValueError("Configuration file is required.")
        
        firestore_client = initialize_firestore(config)
        
        # Example operation: Fetching data from a Firestore collection
        collection_name = 'your_collection_name'  # Replace with your collection name
        docs = firestore_client.collection(collection_name).stream()
        
        result_data = {
            "feature": "FirestoreMemoryStore",
            "status": "success", 
            "data": [doc.to_dict() for doc in docs],
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"FirestoreMemoryStore Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ FirestoreMemoryStore completed successfully[/green]")
            
    except ValueError as ve:
        console.print(f"[red]❌ FirestoreMemoryStore failed: {str(ve)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ FirestoreMemoryStore failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["firestorememorystore"]