import json
import platform
import subprocess
import shutil
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict

import click
from rich.console import Console
from rich.table import Table

console = Console()

def _load_config(config_path: Optional[str]) -> Dict:
    if not config_path:
        return {}
    try:
        path = Path(config_path).expanduser().resolve()
        with path.open("r", encoding="utf-8") as fp:
            return json.load(fp)
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Failed to load configuration file: {exc}") from exc

def _detect_sync_command() -> Optional[str]:
    system = platform.system().lower()
    if system in {"linux", "darwin"}:
        if shutil.which("timedatectl"):
            return "timedatectl"
        if shutil.which("ntpdate"):
            return "ntpdate"
        if shutil.which("sntp"):
            return "sntp"
    elif system == "windows":
        if shutil.which("w32tm"):
            return "w32tm"
    return None

def _validate_ntp_server(ntp_server: str) -> bool:
    if not ntp_server or not isinstance(ntp_server, str):
        return False
    ntp_server = ntp_server.strip()
    ipv4_re = re.compile(r"^(25[0-5]|2[0-4]\d|1?\d{1,2})(\.(25[0-5]|2[0-4]\d|1?\d{1,2})){3}$")
    if ipv4_re.match(ntp_server):
        return True
    ipv6_re = re.compile(r"^([0-9a-fA-F:]+)$")
    if ipv6_re.match(ntp_server) and ":" in ntp_server:
        return True
    hostname_re = re.compile(r"^(?=.{1,253}$)(?:[A-Za-z0-9](?:[A-Za-z0-9\-]{0,61}[A-Za-z0-9])?)(?:\.(?:[A-Za-z0-9](?:[A-Za-z0-9\-]{0,61}[A-Za-z0-9])?))*\.?$")
    if hostname_re.match(ntp_server):
        return True
    return False

def _sync_time(command: str, ntp_server: str, verbose: bool) -> Dict:
    start_time = datetime.utcnow()
    system = platform.system().lower()
    cmd = None
    if command == "timedatectl":
        cmd = ["timedatectl", "set-ntp", "true"]
    elif command == "ntpdate":
        cmd = ["ntpdate", "-u", ntp_server]
    elif command == "sntp":
        cmd = ["sntp", "-s", ntp_server]
    elif command == "w32tm":
        cmd = ["w32tm", "/resync"]
    else:
        raise RuntimeError("Unsupported command for time synchronization.")
    if verbose:
        console.print(f"[blue]Executing: {' '.join(cmd)}[/blue]")
    try:
        completed = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
        )
        status = "success"
        message = "Time synchronization completed successfully."
    except FileNotFoundError:
        completed = subprocess.CompletedProcess(cmd, returncode=1, stdout="", stderr="Command not found.")
        status = "failed"
        message = f"Time synchronization failed: Command '{cmd[0]}' not found."
    except subprocess.CalledProcessError as exc:
        completed = exc
        status = "failed"
        stderr = (getattr(exc, "stderr", "") or "").strip()
        stdout = (getattr(exc, "stdout", "") or "").strip()
        message = f"Time synchronization failed (returncode={exc.returncode})."
        if verbose and stderr:
            message += f" stderr: {stderr}"
        elif verbose and stdout:
            message += f" stdout: {stdout}"
    except Exception as exc:
        completed = subprocess.CompletedProcess(cmd, returncode=1, stdout="", stderr=str(exc))
        status = "failed"
        message = f"Unexpected error during synchronization: {exc}"
    end_time = datetime.utcnow()
    return {
        "command": " ".join(cmd),
        "returncode": getattr(completed, "returncode", 1),
        "stdout": (getattr(completed, "stdout", "") or "").strip(),
        "stderr": (getattr(completed, "stderr", "") or "").strip(),
        "status": status,
        "message": message,
        "start_time_utc": start_time.isoformat(timespec="seconds") + "Z",
        "end_time_utc": end_time.isoformat(timespec="seconds") + "Z",
        "duration_seconds": (end_time - start_time).total_seconds(),
    }

@click.command(help="Reset the system clock and synchronize time with an NTP server.")
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option(
    '--output',
    '-o',
    type=click.Choice(['json', 'table', 'plain']),
    default='table',
    help='Output format',
)
@click.option(
    '--config',
    type=click.Path(exists=True),
    help='Path to configuration JSON file',
)
@click.option(
    '--ntp-server',
    default=None,
    help='Override NTP server (e.g., pool.ntp.org)',
)
@click.pass_context
def reset_to_system_clock(
    ctx,
    verbose: bool,
    output: str,
    config: Optional[str],
    ntp_server: Optional[str],
):
    api_mode = False
    try:
        if isinstance(ctx, click.Context) and isinstance(ctx.obj, dict) and ctx.obj.get("api", False):
            api_mode = True
        if verbose and not api_mode:
            console.print("[blue]Running reset_to_system_clock command...[/blue]")
        config_data = _load_config(config)
        ntp_srv = (ntp_server if ntp_server is not None else config_data.get("ntp_server", "pool.ntp.org")) or "pool.ntp.org"
        if ntp_srv and not _validate_ntp_server(ntp_srv):
            raise RuntimeError(f"Invalid NTP server provided: '{ntp_srv}'")
        command = _detect_sync_command()
        if command is None:
            raise RuntimeError(
                "No suitable time synchronization command found on this system."
            )
        if command == "timedatectl" and os.name != "nt":
            try:
                if hasattr(os, "geteuid") and os.geteuid() != 0:
                    if verbose and not api_mode:
                        console.print("[yellow]Warning: timedatectl may require root privileges to change system time.[/yellow]")
            except Exception:
                pass
        sync_result = _sync_time(command, ntp_srv, verbose)
        result_data = {
            "feature": "reset_to_system_clock",
            "command_used": command,
            "ntp_server": ntp_srv,
            "status": sync_result["status"],
            "message": sync_result["message"],
            "details": {
                key: value
                for key, value in sync_result.items()
                if key not in {"status", "message"}
            },
        }
        if api_mode:
            return result_data
        if output == 'json':
            console.print_json(data=json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title="reset_to_system_clock Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            for key, value in result_data.items():
                if isinstance(value, dict):
                    table.add_row(str(key), json.dumps(value, indent=2))
                else:
                    table.add_row(str(key), str(value))
            console.print(table)
        else:
            for key, value in result_data.items():
                if isinstance(value, dict):
                    console.print(f"{key}: {json.dumps(value, indent=2)}")
                else:
                    console.print(f"{key}: {value}")
        if result_data["status"] != "success":
            if verbose:
                console.print(f"[red]❌ reset_to_system_clock encountered errors[/red]")
            ctx.exit(1)
        if verbose:
            console.print("[green]✅ reset_to_system_clock completed successfully[/green]")
    except Exception as e:
        error_payload = {
            "feature": "reset_to_system_clock",
            "status": "failed",
            "message": str(e),
        }
        if api_mode:
            return error_payload
        console.print(f"[red]❌ reset_to_system_clock failed: {e}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["reset_to_system_clock"]