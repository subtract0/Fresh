import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import firebase_admin
from firebase_admin import credentials, firestore

console = Console()

class TrackedFirestoreClient:
    def __init__(self, config_path: str):
        self.config = self.load_config(config_path)
        self.db = self.initialize_firestore()

    def load_config(self, config_path: str):
        with open(config_path, 'r') as file:
            return json.load(file)

    def initialize_firestore(self):
        cred = credentials.Certificate(self.config['firebase_credentials'])
        firebase_admin.initialize_app(cred)
        return firestore.client()

    def get_data(self, collection_name: str):
        try:
            collection_ref = self.db.collection(collection_name)
            docs = collection_ref.stream()
            return {doc.id: doc.to_dict() for doc in docs}
        except Exception as e:
            raise RuntimeError(f"Failed to fetch data from Firestore: {str(e)}")

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file', required=True)
@click.option('--collection', type=str, help='Firestore collection name', required=True)
@click.pass_context
def trackedfirestoreclient(ctx, verbose: bool, output: str, config: str, collection: str):
    """
    TrackedFirestoreClient command.
    Fetches data from a specified Firestore collection.
    """
    try:
        if verbose:
            console.print(f"[blue]Running TrackedFirestoreClient command...[/blue]")
        
        client = TrackedFirestoreClient(config)
        result_data = client.get_data(collection)

        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"TrackedFirestoreClient Results")
            table.add_column("Document ID", style="cyan")
            table.add_column("Data", style="magenta")
            
            for doc_id, data in result_data.items():
                table.add_row(doc_id, json.dumps(data))
            
            console.print(table)
        else:  # plain
            for doc_id, data in result_data.items():
                console.print(f"{doc_id}: {data}")
        
        if verbose:
            console.print(f"[green]✅ TrackedFirestoreClient completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ TrackedFirestoreClient failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["trackedfirestoreclient"]