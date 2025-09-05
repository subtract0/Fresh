import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import os

console = Console()

def load_config(config_path: str):
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    with open(config_path, 'r') as file:
        return json.load(file)

def process_documents(config):
    # Simulated processing of documents based on the configuration
    if 'documents' not in config:
        raise ValueError("Configuration must contain 'documents' key.")
    processed_data = []
    for doc in config['documents']:
        processed_data.append({
            "id": doc.get("id"),
            "status": "processed",
            "content": doc.get("content", "")
        })
    return processed_data

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file', required=True)
@click.pass_context
def trackeddocumentsnapshot(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    TrackedDocumentSnapshot command.
    Processes documents based on the provided configuration file.
    """
    try:
        if verbose:
            console.print(f"[blue]Running TrackedDocumentSnapshot command...[/blue]")
        
        config_data = load_config(config)
        result_data = process_documents(config_data)
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"TrackedDocumentSnapshot Results")
            table.add_column("Document ID", style="cyan")
            table.add_column("Status", style="magenta")
            table.add_column("Content", style="green")
            
            for item in result_data:
                table.add_row(str(item["id"]), str(item["status"]), str(item["content"]))
            
            console.print(table)
        else:  # plain
            for item in result_data:
                console.print(f"Document ID: {item['id']}, Status: {item['status']}, Content: {item['content']}")
        
        if verbose:
            console.print(f"[green]✅ TrackedDocumentSnapshot completed successfully[/green]")
            
    except FileNotFoundError as fnf_error:
        console.print(f"[red]❌ TrackedDocumentSnapshot failed: {str(fnf_error)}[/red]")
        ctx.exit(1)
    except ValueError as val_error:
        console.print(f"[red]❌ TrackedDocumentSnapshot failed: {str(val_error)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ TrackedDocumentSnapshot failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["trackeddocumentsnapshot"]