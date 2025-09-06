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
def sync_with_firestore(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    sync_with_firestore command.
    Syncs local data with Firestore database.
    """
    try:
        if verbose:
            console.print(f"[blue]Running sync_with_firestore command...[/blue]")
        
        if not config:
            raise ValueError("Configuration file is required.")
        
        with open(config) as f:
            config_data = json.load(f)
        
        cred = credentials.Certificate(config_data['firebase_credentials'])
        firebase_admin.initialize_app(cred)
        db = firestore.client()

        local_data_path = Path(config_data['local_data_path'])
        if not local_data_path.exists():
            raise FileNotFoundError(f"Local data path '{local_data_path}' does not exist.")
        
        with open(local_data_path) as f:
            local_data = json.load(f)

        for doc_id, data in local_data.items():
            db.collection(config_data['firestore_collection']).document(doc_id).set(data)

        result_data = {
            "feature": "sync_with_firestore",
            "status": "success", 
            "message": "Data synced successfully",
            "config_used": config,
            "verbose": verbose
        }
        
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"sync_with_firestore Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ sync_with_firestore completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ sync_with_firestore failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["sync_with_firestore"]