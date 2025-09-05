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

def process_document(config: dict):
    # Simulated document processing logic
    if 'documents' not in config:
        raise ValueError("Configuration must contain 'documents' key.")
    documents = config['documents']
    processed_documents = [{"name": doc, "status": "processed"} for doc in documents]
    return processed_documents

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file', required=True)
@click.pass_context
def document(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    document command to process documents based on a configuration file.
    """
    try:
        if verbose:
            console.print(f"[blue]Running document command...[/blue]")
        
        config_data = load_config(config)
        processed_data = process_document(config_data)
        
        result_data = {
            "feature": "document",
            "status": "success", 
            "processed_documents": processed_data,
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"Document Processing Results")
            table.add_column("Document Name", style="cyan")
            table.add_column("Status", style="magenta")
            
            for doc in processed_data:
                table.add_row(doc["name"], doc["status"])
            
            console.print(table)
        else:  # plain
            for doc in processed_data:
                console.print(f"{doc['name']}: {doc['status']}")
        
        if verbose:
            console.print(f"[green]✅ Document processing completed successfully[/green]")
            
    except FileNotFoundError as fnf_error:
        console.print(f"[red]❌ document failed: {str(fnf_error)}[/red]")
        ctx.exit(1)
    except ValueError as val_error:
        console.print(f"[red]❌ document failed: {str(val_error)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ document failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["document"]