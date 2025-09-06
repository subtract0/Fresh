import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import os

console = Console()

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def cmd_scaffold_new(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    cmd_scaffold_new command.
    
    This command scaffolds a new feature based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running cmd_scaffold_new command...[/blue]")
        
        # Load configuration if provided
        config_data = {}
        if config:
            with open(config, 'r') as f:
                config_data = json.load(f)
                if verbose:
                    console.print(f"[yellow]Loaded configuration: {config_data}[/yellow]")

        # Validate configuration
        if 'feature_name' not in config_data:
            raise ValueError("Configuration must include 'feature_name'.")

        feature_name = config_data['feature_name']
        output_dir = config_data.get('output_dir', '.')

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Simulate scaffolding process
        feature_path = Path(output_dir) / feature_name
        if feature_path.exists():
            raise FileExistsError(f"Feature '{feature_name}' already exists at '{feature_path}'.")

        feature_path.mkdir(parents=True)
        (feature_path / '__init__.py').touch()
        (feature_path / f"{feature_name}.py").write_text(f"# {feature_name} feature implementation\n")

        result_data = {
            "feature": feature_name,
            "status": "success", 
            "message": f"Feature '{feature_name}' scaffolded successfully.",
            "config_used": config_data,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"cmd_scaffold_new Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ cmd_scaffold_new completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ cmd_scaffold_new failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["cmd_scaffold_new"]