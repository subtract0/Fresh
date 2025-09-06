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

def execute_agent_logic(config):
    # Placeholder for actual agent execution logic
    # Simulating some processing based on the config
    if 'agent_name' not in config:
        raise ValueError("Configuration must include 'agent_name'")
    
    return {
        "agent_name": config['agent_name'],
        "execution_time": "5s",
        "status": "success",
        "details": "Agent executed successfully."
    }

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file', required=True)
@click.pass_context
def agentexecutionmonitor(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    AgentExecutionMonitor command.
    Monitors the execution of agents based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running AgentExecutionMonitor command...[/blue]")
        
        config_data = load_config(config)
        result_data = execute_agent_logic(config_data)
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"AgentExecutionMonitor Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ AgentExecutionMonitor completed successfully[/green]")
            
    except FileNotFoundError as fnf_error:
        console.print(f"[red]❌ Error: {str(fnf_error)}[/red]")
        ctx.exit(1)
    except ValueError as val_error:
        console.print(f"[red]❌ Configuration Error: {str(val_error)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ AgentExecutionMonitor failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["agentexecutionmonitor"]