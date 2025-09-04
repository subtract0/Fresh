"""
Integration of Product CLI Commands into Fresh CLI

This module adds the product-driven development commands to the main Fresh CLI.
"""
from ai.cli.product_commands import product_cli

def add_product_commands_to_cli(main_cli):
    """Add product commands to the main CLI."""
    main_cli.add_command(product_cli)
    
def register_product_commands():
    """Register product commands with the main Fresh CLI."""
    from ai.cli.fresh import cli
    add_product_commands_to_cli(cli)
