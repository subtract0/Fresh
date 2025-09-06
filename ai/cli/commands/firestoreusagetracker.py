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
def firestoreusagetracker(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    FirestoreUsageTracker command.
    This command tracks Firestore usage based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running FirestoreUsageTracker command...[/blue]")
        
        if config is None:
            raise ValueError("Configuration file is required.")
        
        with open(config, 'r') as f:
            config_data = json.load(f)
        
        cred = credentials.Certificate(config_data['firebase_credentials'])
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        
        usage_data = {}
        collections = db.collections()
        
        for collection in collections:
            docs = collection.stream()
            usage_data[collection.id] = sum(1 for _ in docs)
        
        result_data = {
            "feature": "FirestoreUsageTracker",
            "status": "success", 
            "usage_data": usage_data,
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"FirestoreUsageTracker Results")
            table.add_column("Collection", style="cyan")
            table.add_column("Document Count", style="magenta")
            
            for collection, count in usage_data.items():
                table.add_row(collection, str(count))
            
            console.print(table)
        else:  # plain
            for collection, count in usage_data.items():
                console.print(f"{collection}: {count} documents")
        
        if verbose:
            console.print(f"[green]✅ FirestoreUsageTracker completed successfully[/green]")
            
    except FileNotFoundError:
        console.print(f"[red]❌ Configuration file not found: {config}[/red]")
        ctx.exit(1)
    except ValueError as ve:
        console.print(f"[red]❌ Value error: {str(ve)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ FirestoreUsageTracker failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["firestoreusagetracker"]