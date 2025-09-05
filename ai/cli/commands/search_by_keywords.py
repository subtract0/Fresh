import click
from typing import Optional, List
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import os

console = Console()

def load_config(config_path: str) -> dict:
    if config_path and os.path.exists(config_path):
        with open(config_path, 'r') as file:
            return json.load(file)
    return {}

def search_keywords_in_data(keywords: List[str], data: List[dict]) -> List[dict]:
    results = []
    for item in data:
        if any(keyword.lower() in item.get('description', '').lower() for keyword in keywords):
            results.append(item)
    return results

def get_sample_data() -> List[dict]:
    return [
        {"id": 1, "description": "This is a sample item with keyword one."},
        {"id": 2, "description": "Another item with keyword two."},
        {"id": 3, "description": "This item does not match."},
        {"id": 4, "description": "Keyword one and two are here."},
    ]

@click.command()
@click.option('--keywords', '-k', multiple=True, required=True, help='Keywords to search for')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def search_by_keywords(ctx, keywords: List[str], verbose: bool, output: str, config: Optional[str]):
    """
    Search for items by keywords in their descriptions.
    """
    try:
        if verbose:
            console.print(f"[blue]Running search_by_keywords command with keywords: {', '.join(keywords)}...[/blue]")
        
        config_data = load_config(config)
        sample_data = get_sample_data()  # Replace with actual data source
        results = search_keywords_in_data(keywords, sample_data)
        
        if not results:
            result_data = {
                "feature": "search_by_keywords",
                "status": "no_results", 
                "message": "No items found matching the keywords.",
                "config_used": config_data,
                "keywords": keywords
            }
        else:
            result_data = {
                "feature": "search_by_keywords",
                "status": "success",
                "results": results,
                "config_used": config_data,
                "keywords": keywords
            }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"search_by_keywords Results")
            table.add_column("ID", style="cyan")
            table.add_column("Description", style="magenta")
            
            for item in results:
                table.add_row(str(item['id']), item['description'])
            
            console.print(table)
        else:  # plain
            for item in results:
                console.print(f"ID: {item['id']}, Description: {item['description']}")
        
        if verbose:
            console.print(f"[green]✅ search_by_keywords completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ search_by_keywords failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["search_by_keywords"]