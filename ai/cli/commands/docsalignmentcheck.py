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

def validate_config(config):
    required_keys = ['source_documents', 'target_documents']
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required config key: {key}")

def check_docs_alignment(source_docs, target_docs):
    # Placeholder for actual alignment checking logic
    # This should compare source and target documents and return results
    return {
        "aligned": True,
        "details": "All documents are aligned."
    }

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def docsalignmentcheck(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    DocsAlignmentCheck command.
    This command checks the alignment of documents based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running DocsAlignmentCheck command...[/blue]")
        
        if not config:
            raise ValueError("Configuration file must be provided.")
        
        config_data = load_config(config)
        validate_config(config_data)

        source_docs = config_data['source_documents']
        target_docs = config_data['target_documents']
        
        alignment_result = check_docs_alignment(source_docs, target_docs)
        
        result_data = {
            "feature": "DocsAlignmentCheck",
            "status": "success", 
            "alignment_result": alignment_result,
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"DocsAlignmentCheck Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ DocsAlignmentCheck completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ DocsAlignmentCheck failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["docsalignmentcheck"]