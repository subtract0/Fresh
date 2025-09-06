from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import date

import click
from rich.console import Console
from rich.table import Table

console = Console()


def load_config(config_path: str | Path) -> Dict[str, Any]:
    """Load configuration from a JSON file.

    Parameters
    ----------
    config_path: str | Path
        Path to the JSON configuration file.

    Returns
    -------
    Dict[str, Any]
        Parsed JSON configuration.

    Raises
    ------
    ValueError
        If reading the file or parsing JSON fails.
    """
    try:
        path = Path(config_path).expanduser().resolve()
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")
        if not path.is_file():
            raise IsADirectoryError(f"Expected a file but got directory: {path}")

        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
            if not isinstance(data, dict):
                raise ValueError("Configuration root must be a JSON object")
            return data
    except (json.JSONDecodeError, FileNotFoundError, IsADirectoryError, ValueError) as err:
        raise ValueError(f"Failed to load configuration: {err}") from err
    except Exception as err:  # pragma: no cover
        raise ValueError(f"Unexpected error loading configuration: {err}") from err


def _validate_header_data(header: Dict[str, Any]) -> None:
    """Validate the header dictionary.

    Ensures all required keys exist and values are strings.

    Raises
    ------
    ValueError
        If validation fails.
    """
    required_keys = ("title", "author", "date")
    missing = [k for k in required_keys if k not in header]
    if missing:
        raise ValueError(f"Header missing required fields: {', '.join(missing)}")

    for key, value in header.items():
        if not isinstance(value, str):
            raise ValueError(f"Header field '{key}' must be a string, got {type(value).__name__}")
        if value.strip() == "":
            raise ValueError(f"Header field '{key}' cannot be empty")


def create_header_logic(config: Optional[Dict[str, Any]], verbose: bool) -> Dict[str, Any]:
    """Business logic for creating a header.

    Parameters
    ----------
    config: dict | None
        Configuration dictionary; can override default header values.
    verbose: bool
        Flag to enable verbose console output.

    Returns
    -------
    Dict[str, Any]
        Result dictionary containing header and status information.
    """
    config = config or {}
    if not isinstance(config, dict):
        raise ValueError("Config must be a dictionary if provided")

    header: Dict[str, str] = {
        "title": str(config.get("title", "Default Title")),
        "author": str(config.get("author", "Unknown Author")),
        "date": str(config.get("date", date.today().isoformat())),
    }

    # Validate the header structure
    _validate_header_data(header)

    if verbose:
        console.print(f"[blue]Header created with title: '{header['title']}'[/blue]")

    return {
        "feature": "create_header",
        "status": "success",
        "header": header,
        "config_used": config,
    }


@click.command("create_header", help="Create a header for documentation or files.")
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose output.",
    show_default=True,
)
@click.option(
    "--output",
    "-o",
    type=click.Choice(["json", "table", "plain"], case_sensitive=False),
    default="table",
    help="Choose the output format.",
    show_default=True,
)
@click.option(
    "--config",
    type=click.Path(exists=True, dir_okay=False, readable=True, path_type=Path),
    help="Path to a JSON configuration file.",
)
@click.pass_context
def create_header(
    ctx: click.Context,
    verbose: bool,
    output: str,
    config: Optional[Path],
) -> None:
    """
    Create a header for documentation or files based on the provided configuration.

    The command can read configuration overrides from a JSON file and prints the resulting
    header in one of the supported formats (json, table, plain).
    """
    try:
        if verbose:
            console.print("[blue]Running create_header command...[/blue]")

        config_data: Optional[Dict[str, Any]] = None
        if config:
            config_data = load_config(config)

        result_data = create_header_logic(config_data, verbose)

        # Output results in requested format
        if output.lower() == "json":
            console.print_json(json.dumps(result_data, indent=2))
        elif output.lower() == "table":
            table = Table(title="create_header Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")

            for key, value in result_data.items():
                if isinstance(value, dict):
                    value = json.dumps(value, indent=2)
                table.add_row(str(key), str(value))
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")

        if verbose:
            console.print("[green]✅ create_header completed successfully[/green]")

    except Exception as err:  # pragma: no cover
        console.print(f"[red]❌ create_header failed: {err}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)


# Export command for CLI registration
__all__ = ["create_header"]