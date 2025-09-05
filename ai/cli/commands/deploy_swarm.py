import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import subprocess
import os

console = Console()


@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def deploy_swarm(ctx, verbose: bool, output: Optional[str], config: Optional[str]):
    """
    deploy_swarm command.
    
    Deploys a Docker Swarm cluster based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running deploy_swarm command...[/blue]")
        
        if config is None:
            raise ValueError("Configuration file must be provided.")
        
        config_path = Path(config)
        if not config_path.is_file():
            raise FileNotFoundError(f"Configuration file '{config}' does not exist.")
        
        with open(config_path) as f:
            swarm_config = json.load(f)

        # Validate configuration
        if 'services' not in swarm_config:
            raise ValueError("Invalid configuration: 'services' key is missing.")
        
        # Deploy the swarm using Docker CLI
        for service, details in swarm_config['services'].items():
            command = ["docker", "service", "create", "--name", service]
            if 'image' in details:
                command.append(details['image'])
            if 'replicas' in details:
                command.extend(["--replicas", str(details['replicas'])])
            if 'env' in details:
                for env_var in details['env']:
                    command.extend(["--env", env_var])
            if verbose:
                console.print(f"[yellow]Executing command: {' '.join(command)}[/yellow]")
            subprocess.run(command, check=True)

        result_data = {
            "feature": "deploy_swarm",
            "status": "success", 
            "message": "Swarm deployed successfully",
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"deploy_swarm Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ deploy_swarm completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ deploy_swarm failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)


# Export command for CLI registration
__all__ = ["deploy_swarm"]