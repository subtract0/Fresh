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
@click.option('--document', required=True, help='Document ID to patch')
@click.option('--data', required=True, type=click.File('r'), help='JSON file with data to patch')
@click.pass_context
def patch_firestore_store(ctx, verbose: bool, output: str, config: Optional[str], document: str, data: str):
    """
    patch_firestore_store command.
    Patches a Firestore document with the provided data.
    """
    try:
        if verbose:
            console.print(f"[blue]Running patch_firestore_store command...[/blue]")
        
        # Initialize Firestore
        db = initialize_firestore(config)
        
        # Load data from JSON file
        patch_data = json.load(data)
        
        # Validate document ID and data
        if not isinstance(patch_data, dict):
            raise ValueError("Patch data must be a JSON object.")
        
        # Patch the document
        doc_ref = db.collection('your_collection_name').document(document)
        doc_ref.set(patch_data, merge=True)
        
        result_data = {
            "feature": "patch_firestore_store",
            "status": "success", 
            "message": f"Document {document} patched successfully.",
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"patch_firestore_store Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ patch_firestore_store completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ patch_firestore_store failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["patch_firestore_store"]