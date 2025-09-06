import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import openai
import os

console = Console()

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def track_openai_call(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    track_openai_call command.
    This command tracks OpenAI API calls and logs the results.
    """
    try:
        if verbose:
            console.print(f"[blue]Running track_openai_call command...[/blue]")
        
        # Load configuration if provided
        api_key = None
        if config:
            with open(config, 'r') as f:
                config_data = json.load(f)
                api_key = config_data.get("api_key")
                if not api_key:
                    raise ValueError("API key not found in configuration file.")
        else:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("API key must be provided either via config file or environment variable.")

        openai.api_key = api_key
        
        # Example OpenAI API call (modify as needed)
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello, how can I track OpenAI calls?"}]
        )
        
        result_data = {
            "feature": "track_openai_call",
            "status": "success", 
            "response": response,
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"track_openai_call Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ track_openai_call completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ track_openai_call failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["track_openai_call"]