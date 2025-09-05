import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
from fpdf import FPDF

console = Console()

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Export PDF Report', 0, 1, 'C')

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def export_pdf(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    export_pdf command.
    Exports data to a PDF file based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running export_pdf command...[/blue]")
        
        if config is None:
            raise ValueError("Configuration file must be provided.")
        
        config_path = Path(config)
        if not config_path.is_file():
            raise FileNotFoundError(f"Configuration file '{config}' does not exist.")
        
        with open(config_path) as f:
            config_data = json.load(f)

        pdf = PDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        for key, value in config_data.items():
            pdf.cell(200, 10, f"{key}: {value}", ln=True)

        output_file = config_path.with_suffix('.pdf')
        pdf.output(str(output_file))

        result_data = {
            "feature": "export_pdf",
            "status": "success", 
            "message": f"PDF exported successfully to {output_file}",
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"export_pdf Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ export_pdf completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ export_pdf failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["export_pdf"]