import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import shutil
import os

console = Console()

def validate_config(config_path: str) -> dict:
    if not Path(config_path).is_file():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    with open(config_path, 'r') as file:
        try:
            config = json.load(file)
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in configuration file: {config_path}")
    return config

def backup_memory_store(config: dict) -> str:
    backup_dir = config.get("backup_directory", "backups")
    os.makedirs(backup_dir, exist_ok=True)
    source_dir = config.get("source_directory")
    
    if not source_dir or not Path(source_dir).is_dir():
        raise ValueError(f"Source directory not specified or does not exist in config: {source_dir}")
    
    backup_path = Path(backup_dir) / f"backup_{int(os.path.getmtime(source_dir))}.zip"
    shutil.make_archive(backup_path.stem, 'zip', source_dir)
    
    return str(backup_path)

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file', required=True)
@click.pass_context
def backupmemorystore(ctx, verbose: bool, output: str, config: str):
    """
    BackupMemoryStore command.
    Backs up the memory store based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running BackupMemoryStore command...[/blue]")
        
        config_data = validate_config(config)
        backup_path = backup_memory_store(config_data)
        
        result_data = {
            "feature": "BackupMemoryStore",
            "status": "success", 
            "message": "Backup completed successfully",
            "backup_path": backup_path,
            "config_used": config,
            "verbose": verbose
        }
        
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"BackupMemoryStore Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ BackupMemoryStore completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ BackupMemoryStore failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["backupmemorystore"]