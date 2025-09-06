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
def create_firestore_memory_store(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    create_firestore_memory_store command.
    This command initializes a Firestore memory store based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running create_firestore_memory_store command...[/blue]")
        
        if config is None:
            raise ValueError("Configuration file must be provided.")
        
        with open(config, 'r') as f:
            config_data = json.load(f)

        # Initialize Firestore
        cred = credentials.Certificate(config_data['service_account_key'])
        firebase_admin.initialize_app(cred)
        db = firestore.client()

        # Create a Firestore collection and document
        collection_name = config_data.get('collection_name', 'default_collection')
        document_data = config_data.get('document_data', {})
        
        if not document_data:
            raise ValueError("Document data must be provided in the configuration.")

        db.collection(collection_name).add(document_data)

        result_data = {
            "feature": "create_firestore_memory_store",
            "status": "success", 
            "message": "Firestore memory store created successfully",
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"create_firestore_memory_store Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ create_firestore_memory_store completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ create_firestore_memory_store failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["create_firestore_memory_store"]