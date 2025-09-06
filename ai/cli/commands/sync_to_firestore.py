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
def sync_to_firestore(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    sync_to_firestore command.
    Sync data to Firestore based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running sync_to_firestore command...[/blue]")
        
        if not config:
            raise ValueError("Configuration file must be provided.")
        
        with open(config, 'r') as f:
            config_data = json.load(f)

        cred = credentials.Certificate(config_data['firebase_credentials'])
        firebase_admin.initialize_app(cred)
        db = firestore.client()

        data_to_sync = config_data.get('data_to_sync', {})
        if not data_to_sync:
            raise ValueError("No data to sync found in the configuration.")

        for collection, documents in data_to_sync.items():
            for doc_id, doc_data in documents.items():
                db.collection(collection).document(doc_id).set(doc_data)

        result_data = {
            "feature": "sync_to_firestore",
            "status": "success", 
            "message": "Data synced to Firestore successfully",
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"sync_to_firestore Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ sync_to_firestore completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ sync_to_firestore failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["sync_to_firestore"]