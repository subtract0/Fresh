import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import openai

console = Console()

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def track_openai_streaming_call(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    track_openai_streaming_call command.
    This command tracks the OpenAI streaming call and outputs the results.
    """
    try:
        if verbose:
            console.print(f"[blue]Running track_openai_streaming_call command...[/blue]")
        
        # Load configuration if provided
        if config:
            with open(config, 'r') as f:
                config_data = json.load(f)
                openai.api_key = config_data.get("api_key")
        else:
            console.print(f"[red]❌ Configuration file is required.[/red]")
            ctx.exit(1)

        # Validate API key
        if not openai.api_key:
            console.print(f"[red]❌ API key is missing in the configuration.[/red]")
            ctx.exit(1)

        # Call OpenAI API with streaming
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello, how can I help you?"}],
            stream=True
        )

        result_data = {
            "feature": "track_openai_streaming_call",
            "status": "success",
            "responses": []
        }

        for chunk in response:
            if 'choices' in chunk:
                result_data["responses"].append(chunk['choices'][0]['delta'].get('content', ''))

        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"track_openai_streaming_call Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                if isinstance(value, list):
                    value = "\n".join(value)
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                if isinstance(value, list):
                    value = "\n".join(value)
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ track_openai_streaming_call completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ track_openai_streaming_call failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["track_openai_streaming_call"]