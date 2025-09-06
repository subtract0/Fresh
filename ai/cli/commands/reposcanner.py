import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import os

console = Console()

def scan_repository(repo_path: str) -> dict:
    # Simulate scanning a repository
    if not os.path.exists(repo_path):
        raise FileNotFoundError(f"Repository path '{repo_path}' does not exist.")
    
    # Example scan results
    return {
        "repository": repo_path,
        "files": len(os.listdir(repo_path)),
        "directories": sum(os.path.isdir(os.path.join(repo_path, name)) for name in os.listdir(repo_path)),
        "status": "scanned"
    }

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.argument('repo_path', type=click.Path(exists=True))
@click.pass_context
def reposcanner(ctx, verbose: bool, output: str, config: Optional[str], repo_path: str):
    """
    RepoScanner command.
    
    Scans the specified repository and provides analysis results.
    """
    try:
        if verbose:
            console.print(f"[blue]Running RepoScanner command on {repo_path}...[/blue]")
        
        # Load configuration if provided
        config_data = {}
        if config:
            with open(config, 'r') as f:
                config_data = json.load(f)
                if verbose:
                    console.print(f"[yellow]Loaded configuration: {config_data}[/yellow]")
        
        # Scan the repository
        result_data = scan_repository(repo_path)
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"RepoScanner Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ RepoScanner completed successfully[/green]")
            
    except FileNotFoundError as fnf_error:
        console.print(f"[red]❌ RepoScanner failed: {str(fnf_error)}[/red]")
        ctx.exit(1)
    except json.JSONDecodeError as json_error:
        console.print(f"[red]❌ Failed to parse configuration file: {str(json_error)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ RepoScanner failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["reposcanner"]