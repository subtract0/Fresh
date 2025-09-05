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
def patch_firestore_memory(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    patch_firestore_memory command.
    This command patches Firestore memory based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running patch_firestore_memory command...[/blue]")
        
        if config is None:
            raise ValueError("Configuration file must be provided.")

        # Load configuration
        with open(config, 'r') as f:
            config_data = json.load(f)

        # Initialize Firestore
        cred = credentials.Certificate(config_data['firebase_credentials'])
        firebase_admin.initialize_app(cred)
        db = firestore.client()

        # Patch Firestore memory
        for collection, updates in config_data['patches'].items():
            for doc_id, data in updates.items():
                db.collection(collection).document(doc_id).set(data, merge=True)

        result_data = {
            "feature": "patch_firestore_memory",
            "status": "success", 
            "message": "Firestore memory patched successfully",
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"patch_firestore_memory Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ patch_firestore_memory completed successfully[/green]")
            
    except FileNotFoundError:
        console.print(f"[red]❌ Configuration file not found: {config}[/red]")
        ctx.exit(1)
    except json.JSONDecodeError:
        console.print(f"[red]❌ Error decoding JSON from configuration file: {config}[/red]")
        ctx.exit(1)
    except ValueError as ve:
        console.print(f"[red]❌ Value error: {str(ve)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ patch_firestore_memory failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["patch_firestore_memory"]