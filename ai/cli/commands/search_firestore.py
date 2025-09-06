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
@click.option('--query', type=str, required=True, help='Search query for Firestore')
@click.pass_context
def search_firestore(ctx, verbose: bool, output: str, config: Optional[str], query: str):
    """
    search_firestore command.
    
    Searches Firestore based on the provided query.
    """
    try:
        if verbose:
            console.print(f"[blue]Running search_firestore command...[/blue]")
        
        if not config:
            raise ValueError("Configuration file is required.")
        
        db = initialize_firestore(config)
        
        # Perform Firestore search
        results = db.collection('your_collection_name').where('your_field_name', '==', query).get()
        
        if not results:
            raise ValueError("No results found for the given query.")
        
        result_data = [{"id": doc.id, **doc.to_dict()} for doc in results]
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"search_firestore Results")
            table.add_column("ID", style="cyan")
            for key in result_data[0].keys():
                if key != 'id':
                    table.add_column(key, style="magenta")
            
            for item in result_data:
                row = [item['id']] + [item[key] for key in item if key != 'id']
                table.add_row(*map(str, row))
            
            console.print(table)
        else:  # plain
            for item in result_data:
                console.print(f"ID: {item['id']}")
                for key, value in item.items():
                    if key != 'id':
                        console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ search_firestore completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ search_firestore failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["search_firestore"]