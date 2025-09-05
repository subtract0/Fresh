import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import yaml

console = Console()

def load_config(config_path: str):
    if config_path.endswith('.json'):
        with open(config_path, 'r') as f:
            return json.load(f)
    elif config_path.endswith('.yaml') or config_path.endswith('.yml'):
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    else:
        raise ValueError("Unsupported config file format. Use JSON or YAML.")

def analyze_agent_types(config):
    # Placeholder for actual analysis logic
    # This should be replaced with the real implementation
    return {
        "agent_types": ["Type A", "Type B", "Type C"],
        "analysis_result": "Analysis completed successfully."
    }

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def agenttypeanalysis(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    AgentTypeAnalysis command.
    Analyzes agent types based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running AgentTypeAnalysis command...[/blue]")
        
        if config:
            config_data = load_config(config)
        else:
            raise ValueError("Configuration file is required.")

        analysis_result = analyze_agent_types(config_data)

        result_data = {
            "feature": "AgentTypeAnalysis",
            "status": "success", 
            "message": analysis_result["analysis_result"],
            "agent_types": analysis_result["agent_types"],
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"AgentTypeAnalysis Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ AgentTypeAnalysis completed successfully[/green]")
            
    except ValueError as ve:
        console.print(f"[red]❌ Error: {str(ve)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ AgentTypeAnalysis failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["agenttypeanalysis"]