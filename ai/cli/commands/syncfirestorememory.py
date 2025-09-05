import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import firebase_admin
from firebase_admin import credentials, firestore

console = Console()

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def syncfirestorememory(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    SyncFirestoreMemory command.
    Syncs data from Firestore to in-memory storage.
    """
    try:
        if verbose:
            console.print(f"[blue]Running SyncFirestoreMemory command...[/blue]")
        
        if config is None:
            raise ValueError("Configuration file must be provided.")
        
        # Load configuration
        with open(config, 'r') as f:
            config_data = json.load(f)
        
        # Initialize Firestore
        cred = credentials.Certificate(config_data['firebase_credentials'])
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        
        # Fetch data from Firestore
        collection_name = config_data.get('collection_name')
        if not collection_name:
            raise ValueError("Collection name must be specified in the configuration.")
        
        docs = db.collection(collection_name).stream()
        data = {doc.id: doc.to_dict() for doc in docs}
        
        # Output results based on format
        result_data = {
            "feature": "SyncFirestoreMemory",
            "status": "success", 
            "message": "Data synced successfully",
            "data": data,
            "config_used": config,
            "verbose": verbose
        }
        
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"SyncFirestoreMemory Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ SyncFirestoreMemory completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ SyncFirestoreMemory failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["syncfirestorememory"]