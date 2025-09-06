import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import os

console = Console()

def analyze_directory(directory: Path) -> dict:
    purpose_keywords = {
        "images": ["jpg", "png", "gif"],
        "documents": ["pdf", "docx", "txt"],
        "videos": ["mp4", "avi", "mov"],
        "music": ["mp3", "wav", "flac"],
    }
    
    purpose_count = {key: 0 for key in purpose_keywords.keys()}
    
    for item in directory.iterdir():
        if item.is_file():
            ext = item.suffix[1:].lower()  # Get file extension
            for purpose, extensions in purpose_keywords.items():
                if ext in extensions:
                    purpose_count[purpose] += 1
    
    return purpose_count

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.argument('directory', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.pass_context
def infer_directory_purpose(ctx, verbose: bool, output: str, config: Optional[str], directory: str):
    """
    infer_directory_purpose command.
    
    Analyzes the specified directory to infer its purpose based on file types.
    """
    try:
        if verbose:
            console.print(f"[blue]Running infer_directory_purpose command on {directory}...[/blue]")
        
        directory_path = Path(directory)
        result_data = analyze_directory(directory_path)
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"infer_directory_purpose Results")
            table.add_column("Purpose", style="cyan")
            table.add_column("Count", style="magenta")
            
            for purpose, count in result_data.items():
                table.add_row(purpose, str(count))
            
            console.print(table)
        else:  # plain
            for purpose, count in result_data.items():
                console.print(f"{purpose}: {count}")
        
        if verbose:
            console.print(f"[green]✅ infer_directory_purpose completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ infer_directory_purpose failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["infer_directory_purpose"]