import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import firebase_admin
from firebase_admin import credentials, firestore

console = Console()

def initialize_firestore(config_path: str):
    cred = credentials.Certificate(config_path)
    firebase_admin.initialize_app(cred)
    return firestore.client()

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def get_firestore_memories(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    get_firestore_memories command.
    Fetches memories from Firestore and displays them in the specified format.
    """
    try:
        if verbose:
            console.print(f"[blue]Running get_firestore_memories command...[/blue]")
        
        if not config:
            raise ValueError("Configuration file is required.")
        
        db = initialize_firestore(config)
        memories_ref = db.collection('memories')
        memories = memories_ref.stream()

        result_data = []
        for memory in memories:
            result_data.append(memory.to_dict())

        if not result_data:
            raise ValueError("No memories found in Firestore.")

        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"get_firestore_memories Results")
            table.add_column("ID", style="cyan")
            table.add_column("Memory", style="magenta")
            
            for memory in result_data:
                table.add_row(str(memory.get('id', 'N/A')), str(memory.get('content', 'N/A')))
            
            console.print(table)
        else:  # plain
            for memory in result_data:
                console.print(f"ID: {memory.get('id', 'N/A')}, Memory: {memory.get('content', 'N/A')}")
        
        if verbose:
            console.print(f"[green]✅ get_firestore_memories completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ get_firestore_memories failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["get_firestore_memories"]