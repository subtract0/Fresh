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

def process_memory_learning_patterns(config):
    # Placeholder for actual logic
    # Simulating processing based on configuration
    if 'patterns' not in config:
        raise ValueError("Configuration must contain 'patterns' key.")
    
    patterns = config['patterns']
    results = [{"pattern": pattern, "status": "processed"} for pattern in patterns]
    return results

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def memorylearningpatterns(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    MemoryLearningPatterns command.
    Processes memory learning patterns based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running MemoryLearningPatterns command...[/blue]")
        
        if config:
            config_data = load_config(config)
        else:
            raise ValueError("Configuration file must be provided.")

        result_data = process_memory_learning_patterns(config_data)
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"MemoryLearningPatterns Results")
            table.add_column("Pattern", style="cyan")
            table.add_column("Status", style="magenta")
            
            for item in result_data:
                table.add_row(item['pattern'], item['status'])
            
            console.print(table)
        else:  # plain
            for item in result_data:
                console.print(f"Pattern: {item['pattern']}, Status: {item['status']}")
        
        if verbose:
            console.print(f"[green]✅ MemoryLearningPatterns completed successfully[/green]")
            
    except FileNotFoundError as fnf_error:
        console.print(f"[red]❌ MemoryLearningPatterns failed: {str(fnf_error)}[/red]")
        ctx.exit(1)
    except ValueError as val_error:
        console.print(f"[red]❌ MemoryLearningPatterns failed: {str(val_error)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ MemoryLearningPatterns failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["memorylearningpatterns"]