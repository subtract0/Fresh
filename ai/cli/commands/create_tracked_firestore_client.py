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
def create_tracked_firestore_client(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    create_tracked_firestore_client command.
    This command initializes a Firestore client with tracking capabilities.
    """
    try:
        if verbose:
            console.print(f"[blue]Running create_tracked_firestore_client command...[/blue]")
        
        if config is None:
            raise ValueError("Configuration file must be provided.")
        
        # Load configuration
        with open(config, 'r') as f:
            config_data = json.load(f)
        
        # Validate configuration
        if 'firebase_credentials' not in config_data:
            raise ValueError("Configuration must include 'firebase_credentials'.")
        
        # Initialize Firestore client
        cred = credentials.Certificate(config_data['firebase_credentials'])
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        
        # Example operation: Create a tracked document
        doc_ref = db.collection('tracked_clients').add({
            'status': 'active',
            'created_at': firestore.SERVER_TIMESTAMP
        })
        
        result_data = {
            "feature": "create_tracked_firestore_client",
            "status": "success", 
            "message": "Firestore client created and tracked document added.",
            "document_id": doc_ref.id,
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"create_tracked_firestore_client Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ create_tracked_firestore_client completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ create_tracked_firestore_client failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["create_tracked_firestore_client"]