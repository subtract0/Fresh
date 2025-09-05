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
def patch_enhanced_firestore(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    patch_enhanced_firestore command.
    This command patches documents in Firestore with the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running patch_enhanced_firestore command...[/blue]")
        
        if not config:
            raise ValueError("Configuration file is required.")
        
        with open(config, 'r') as f:
            config_data = json.load(f)

        cred = credentials.Certificate(config_data['firebase_credentials'])
        firebase_admin.initialize_app(cred)
        db = firestore.client()

        collection_name = config_data.get('collection')
        document_id = config_data.get('document_id')
        updates = config_data.get('updates')

        if not collection_name or not document_id or not updates:
            raise ValueError("Collection name, document ID, and updates must be provided in the configuration.")

        doc_ref = db.collection(collection_name).document(document_id)
        doc_ref.update(updates)

        result_data = {
            "feature": "patch_enhanced_firestore",
            "status": "success", 
            "message": "Document patched successfully",
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"patch_enhanced_firestore Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ patch_enhanced_firestore completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ patch_enhanced_firestore failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["patch_enhanced_firestore"]