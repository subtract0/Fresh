import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import os

console = Console()

def load_config(config_path: str):
    with open(config_path, 'r') as f:
        return json.load(f)

def validate_event_data(event_data):
    required_fields = ['event_name', 'timestamp', 'user_id']
    for field in required_fields:
        if field not in event_data:
            raise ValueError(f"Missing required field: {field}")

def record_event_to_file(event_data, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, f"{event_data['event_name']}_{event_data['timestamp']}.json")
    with open(file_path, 'w') as f:
        json.dump(event_data, f, indent=2)

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.option('--event-name', required=True, help='Name of the event to record')
@click.option('--timestamp', required=True, help='Timestamp of the event')
@click.option('--user-id', required=True, help='User ID associated with the event')
@click.pass_context
def record_event(ctx, verbose: bool, output: str, config: Optional[str], event_name: str, timestamp: str, user_id: str):
    """
    record_event command to log events with details.
    """
    try:
        if verbose:
            console.print(f"[blue]Running record_event command...[/blue]")
        
        config_data = {}
        if config:
            config_data = load_config(config)
            if verbose:
                console.print(f"[yellow]Loaded configuration from {config}[/yellow]")

        event_data = {
            "event_name": event_name,
            "timestamp": timestamp,
            "user_id": user_id,
            "config_used": config_data
        }

        validate_event_data(event_data)
        output_dir = config_data.get('output_directory', './events')
        record_event_to_file(event_data, output_dir)

        result_data = {
            "feature": "record_event",
            "status": "success", 
            "message": "Event recorded successfully",
            "event_data": event_data
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"record_event Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ record_event completed successfully[/green]")
            
    except ValueError as ve:
        console.print(f"[red]❌ Validation error: {str(ve)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ record_event failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["record_event"]