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

def fetch_data_from_firestore(db):
    try:
        docs = db.collection('your_collection_name').stream()
        return {doc.id: doc.to_dict() for doc in docs}
    except Exception as e:
        raise RuntimeError(f"Error fetching data from Firestore: {str(e)}")

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def enhancedfirestorememorystore(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    EnhancedFirestoreMemoryStore command.
    Fetches data from Firestore and displays it in the specified format.
    """
    try:
        if not config:
            raise ValueError("Configuration file must be provided.")
        
        if verbose:
            console.print(f"[blue]Running EnhancedFirestoreMemoryStore command...[/blue]")
        
        db = initialize_firestore(config)
        result_data = fetch_data_from_firestore(db)
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"EnhancedFirestoreMemoryStore Results")
            table.add_column("Document ID", style="cyan")
            table.add_column("Data", style="magenta")
            
            for doc_id, data in result_data.items():
                table.add_row(doc_id, json.dumps(data))
            
            console.print(table)
        else:  # plain
            for doc_id, data in result_data.items():
                console.print(f"{doc_id}: {data}")
        
        if verbose:
            console.print(f"[green]✅ EnhancedFirestoreMemoryStore completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ EnhancedFirestoreMemoryStore failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["enhancedfirestorememorystore"]