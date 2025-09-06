import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import yaml

console = Console()

def load_config(config_path: str):
    with open(config_path, 'r') as file:
        if config_path.endswith('.json'):
            return json.load(file)
        elif config_path.endswith('.yaml') or config_path.endswith('.yml'):
            return yaml.safe_load(file)
        else:
            raise ValueError("Unsupported config file format. Use JSON or YAML.")

def execute_workflow(config):
    # Simulate workflow execution logic
    if 'workflow' not in config:
        raise ValueError("Configuration must contain 'workflow' key.")
    
    # Here you would implement the actual workflow execution logic
    return {
        "workflow_name": config['workflow'],
        "status": "success",
        "details": "Workflow executed successfully."
    }

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file', required=True)
@click.pass_context
def workflowexecution(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    WorkflowExecution command.
    Executes a workflow based on the provided configuration file.
    """
    try:
        if verbose:
            console.print(f"[blue]Running WorkflowExecution command...[/blue]")
        
        config_data = load_config(config)
        
        result_data = execute_workflow(config_data)
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"WorkflowExecution Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ WorkflowExecution completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ WorkflowExecution failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["workflowexecution"]