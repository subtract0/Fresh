import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import os

console = Console()

def analyze_file(file_path: Path) -> dict:
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            lines = content.splitlines()
            return {
                "file": str(file_path),
                "line_count": len(lines),
                "word_count": sum(len(line.split()) for line in lines),
                "char_count": len(content)
            }
    except Exception as e:
        return {
            "file": str(file_path),
            "error": str(e)
        }

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def analyze_all_files(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    Analyze all files in the specified directory.
    """
    try:
        if verbose:
            console.print(f"[blue]Running analyze_all_files command...[/blue]")
        
        if config:
            with open(config, 'r') as config_file:
                config_data = json.load(config_file)
                directory = Path(config_data.get("directory", "."))
        else:
            directory = Path(".")

        if not directory.is_dir():
            raise ValueError(f"The specified path '{directory}' is not a directory.")

        results = []
        for file_path in directory.glob('*'):
            if file_path.is_file():
                result = analyze_file(file_path)
                results.append(result)

        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(results, indent=2))
        elif output == 'table':
            table = Table(title=f"analyze_all_files Results")
            table.add_column("File", style="cyan")
            table.add_column("Lines", style="magenta")
            table.add_column("Words", style="magenta")
            table.add_column("Chars", style="magenta")
            table.add_column("Error", style="red")

            for result in results:
                table.add_row(
                    result.get("file", ""),
                    str(result.get("line_count", "")),
                    str(result.get("word_count", "")),
                    str(result.get("char_count", "")),
                    result.get("error", "")
                )
            console.print(table)
        else:  # plain
            for result in results:
                console.print(f"File: {result.get('file', '')}")
                console.print(f"  Lines: {result.get('line_count', '')}")
                console.print(f"  Words: {result.get('word_count', '')}")
                console.print(f"  Chars: {result.get('char_count', '')}")
                if "error" in result:
                    console.print(f"  Error: {result['error']}")
        
        if verbose:
            console.print(f"[green]✅ analyze_all_files completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ analyze_all_files failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["analyze_all_files"]