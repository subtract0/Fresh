import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import os
import hashlib

console = Console()

def calculate_file_hash(file_path: str) -> str:
    """Calculate the SHA256 hash of a file."""
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()

def load_config(config_path: str) -> dict:
    """Load configuration from a JSON file."""
    with open(config_path, 'r') as f:
        return json.load(f)

def monitor_codebase(directory: str, previous_hashes: dict) -> dict:
    """Monitor the codebase for changes."""
    current_hashes = {}
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            current_hashes[file_path] = calculate_file_hash(file_path)

    changes = {
        "modified": [],
        "added": [],
        "removed": []
    }

    for file_path, current_hash in current_hashes.items():
        if file_path not in previous_hashes:
            changes["added"].append(file_path)
        elif previous_hashes[file_path] != current_hash:
            changes["modified"].append(file_path)

    for file_path in previous_hashes.keys():
        if file_path not in current_hashes:
            changes["removed"].append(file_path)

    return changes

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def codebasemonitor(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    CodebaseMonitor command.
    Monitors a codebase for changes based on a configuration file.
    """
    try:
        if verbose:
            console.print(f"[blue]Running CodebaseMonitor command...[/blue]")
        
        if not config:
            raise ValueError("Configuration file is required.")

        config_data = load_config(config)
        directory = config_data.get("directory")
        if not directory or not Path(directory).is_dir():
            raise ValueError("Invalid or missing 'directory' in configuration.")

        previous_hashes = config_data.get("hashes", {})
        changes = monitor_codebase(directory, previous_hashes)

        # Output results based on format
        result_data = {
            "feature": "CodebaseMonitor",
            "status": "success",
            "changes": changes,
            "config_used": config,
            "verbose": verbose
        }

        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"CodebaseMonitor Results")
            table.add_column("Change Type", style="cyan")
            table.add_column("Files", style="magenta")

            for change_type, files in changes.items():
                table.add_row(change_type.capitalize(), ', '.join(files) if files else 'None')
            
            console.print(table)
        else:  # plain
            for change_type, files in changes.items():
                console.print(f"{change_type.capitalize()}: {', '.join(files) if files else 'None'}")
        
        if verbose:
            console.print(f"[green]✅ CodebaseMonitor completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ CodebaseMonitor failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["codebasemonitor"]