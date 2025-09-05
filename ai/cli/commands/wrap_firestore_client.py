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
def wrap_firestore_client(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    wrap_firestore_client command.
    This command initializes a Firestore client and performs basic operations.
    """
    try:
        if verbose:
            console.print(f"[blue]Running wrap_firestore_client command...[/blue]")
        
        # Load configuration
        if config:
            with open(config, 'r') as f:
                config_data = json.load(f)
            cred = credentials.Certificate(config_data['service_account_key'])
            firebase_admin.initialize_app(cred)
        else:
            raise ValueError("Configuration file is required.")

        db = firestore.client()
        
        # Example operation: Fetching collections
        collections = db.collections()
        collection_names = [collection.id for collection in collections]

        result_data = {
            "feature": "wrap_firestore_client",
            "status": "success", 
            "message": "Firestore client initialized and collections fetched.",
            "collections": collection_names,
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"wrap_firestore_client Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ wrap_firestore_client completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ wrap_firestore_client failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["wrap_firestore_client"]