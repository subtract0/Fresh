import click
from typing import Optional, List, Dict, Any
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
from datetime import datetime, timezone

console = Console()

def _load_json_file(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    return json.loads(text)

def _parse_timestamp(value) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, (int, float)):
        try:
            return datetime.fromtimestamp(float(value), tz=timezone.utc)
        except Exception:
            return None
    if isinstance(value, str):
        s = value.strip()
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        try:
            return datetime.fromisoformat(s)
        except Exception:
            fmts = [
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%d",
            ]
            for f in fmts:
                try:
                    return datetime.strptime(s, f).replace(tzinfo=timezone.utc)
                except Exception:
                    continue
    return None

def _collect_events_from_dir(dir_path: Path) -> List[Dict[str, Any]]:
    events: List[Dict[str, Any]] = []
    for p in sorted(dir_path.glob("*.json")):
        try:
            data = _load_json_file(p)
            if isinstance(data, list):
                events.extend(data)
            elif isinstance(data, dict):
                if "events" in data and isinstance(data["events"], list):
                    events.extend(data["events"])
                else:
                    events.append(data)
        except Exception:
            continue
    return events

@click.command(help="Retrieve recent events and manage timelines. Reads events from a JSON file or directory. Use --config to point to a JSON config with 'events_file' or 'events_dir'.")
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file (JSON)')
@click.pass_context
def get_recent_events(ctx, verbose: bool, output: str, config: Optional[str]):
    try:
        if verbose:
            console.print(f"[blue]Running get_recent_events command...[/blue]")

        cfg = {}
        if config:
            cfg_path = Path(config)
            try:
                cfg = _load_json_file(cfg_path)
                if not isinstance(cfg, dict):
                    raise ValueError("Configuration file must contain a JSON object at top level.")
            except Exception as e:
                console.print(f"[red]Failed to read config file {config}: {e}[/red]")
                ctx.exit(1)

        events: List[Dict[str, Any]] = []
        events_file = None
        events_dir = None
        default_limit = 20

        if isinstance(cfg.get("events_file"), str):
            events_file = Path(cfg["events_file"]).expanduser()
        if isinstance(cfg.get("events_dir"), str):
            events_dir = Path(cfg["events_dir"]).expanduser()
        if isinstance(cfg.get("default_limit"), int):
            default_limit = max(1, cfg["default_limit"])

        if events_file and events_file.exists():
            try:
                data = _load_json_file(events_file)
                if isinstance(data, list):
                    events = data
                elif isinstance(data, dict):
                    if "events" in data and isinstance(data["events"], list):
                        events = data["events"]
                    else:
                        events = [data]
                else:
                    raise ValueError("Events file JSON must be an object or array.")
            except Exception as e:
                console.print(f"[red]Failed to read events_file {events_file}: {e}[/red]")
                ctx.exit(1)
        elif events_dir and events_dir.exists() and events_dir.is_dir():
            events = _collect_events_from_dir(events_dir)
        else:
            cwd_file = Path.cwd() / "events.json"
            home_file = Path.home() / ".motheragent" / "events.json"
            cwd_dir = Path.cwd() / "events"
            home_dir = Path.home() / ".motheragent" / "events"
            if cwd_file.exists():
                try:
                    data = _load_json_file(cwd_file)
                    if isinstance(data, list):
                        events = data
                    elif isinstance(data, dict) and "events" in data and isinstance(data["events"], list):
                        events = data["events"]
                    else:
                        events = [data]
                    events_file = cwd_file
                except Exception as e:
                    console.print(f"[red]Failed to read {cwd_file}: {e}[/red]")
                    ctx.exit(1)
            elif home_file.exists():
                try:
                    data = _load_json_file(home_file)
                    if isinstance(data, list):
                        events = data
                    elif isinstance(data, dict) and "events" in data and isinstance(data["events"], list):
                        events = data["events"]
                    else:
                        events = [data]
                    events_file = home_file
                except Exception as e:
                    console.print(f"[red]Failed to read {home_file}: {e}[/red]")
                    ctx.exit(1)
            elif cwd_dir.exists() and cwd_dir.is_dir():
                events = _collect_events_from_dir(cwd_dir)
                events_dir = cwd_dir
            elif home_dir.exists() and home_dir.is_dir():
                events = _collect_events_from_dir(home_dir)
                events_dir = home_dir
            else:
                if verbose:
                    console.print("[yellow]No events file or directory found in defaults. Returning empty result.[/yellow]")
                result_data = {
                    "feature": "get_recent_events",
                    "status": "ok",
                    "events": [],
                    "config_used": str(config) if config else None,
                    "source": None,
                    "limit": default_limit,
                    "verbose": verbose,
                    "message": "No events found"
                }
                if output == 'json':
                    console.print_json(json.dumps(result_data, default=str))
                elif output == 'table':
                    table = Table(title="get_recent_events Results")
                    table.add_column("Property", style="cyan")
                    table.add_column("Value", style="magenta")
                    for key, value in result_data.items():
                        table.add_row(str(key), str(value))
                    console.print(table)
                else:
                    for key, value in result_data.items():
                        console.print(f"{key}: {value}")
                if verbose:
                    console.print(f"[green]✅ get_recent_events completed successfully[/green]")
                return result_data

        normalized: List[Dict[str, Any]] = []
        for idx, ev in enumerate(events):
            if not isinstance(ev, dict):
                ev_obj = {"id": f"evt-{idx}", "raw": ev}
            else:
                ev_obj = dict(ev)
            if "id" not in ev_obj:
                ev_obj["id"] = ev_obj.get("uuid") or ev_obj.get("event_id") or f"evt-{idx}"
            ts_raw = ev_obj.get("timestamp") or ev_obj.get("time") or ev_obj.get("created_at")
            ts_dt = _parse_timestamp(ts_raw)
            if ts_dt is None:
                ts_dt = datetime.now(timezone.utc)
            ev_obj["_parsed_time"] = ts_dt
            if "type" not in ev_obj:
                ev_obj["type"] = ev_obj.get("event_type") or "generic"
            if "message" not in ev_obj:
                for k in ("msg", "description", "body", "text"):
                    if k in ev_obj:
                        ev_obj["message"] = ev_obj[k]
                        break
                else:
                    ev_obj["message"] = ev_obj.get("summary") or ""
            normalized.append(ev_obj)

        normalized.sort(key=lambda e: e.get("_parsed_time") or datetime.min.replace(tzinfo=timezone.utc), reverse=True)

        limit = cfg.get("default_limit", default_limit)
        try:
            limit = int(limit)
        except Exception:
            limit = default_limit
        limit = max(1, limit)

        recent = normalized[:limit]

        out_events = []
        for e in recent:
            ts = e.get("_parsed_time")
            ts_iso = ts.isoformat() if isinstance(ts, datetime) else None
            out_events.append({
                "id": e.get("id"),
                "timestamp": ts_iso,
                "type": e.get("type"),
                "message": e.get("message"),
                "raw": {k: v for k, v in e.items() if k not in ("_parsed_time", "message")}
            })

        source_desc = None
        if events_file:
            source_desc = str(events_file)
        elif events_dir:
            source_desc = str(events_dir)

        result_data = {
            "feature": "get_recent_events",
            "status": "ok",
            "events": out_events,
            "total_found": len(normalized),
            "returned": len(out_events),
            "config_used": str(config) if config else None,
            "source": source_desc,
            "limit": limit,
            "verbose": verbose
        }

        if output == 'json':
            console.print_json(json.dumps(result_data, default=str))
        elif output == 'table':
            table = Table(title="Recent Events")
            table.add_column("ID", style="cyan", overflow="fold")
            table.add_column("Timestamp", style="green")
            table.add_column("Type", style="magenta")
            table.add_column("Message", style="white", overflow="fold")
            for ev in out_events:
                table.add_row(
                    str(ev.get("id", "")),
                    str(ev.get("timestamp", "")),
                    str(ev.get("type", "")),
                    str(ev.get("message", ""))[:200]
                )
            console.print(table)
            meta = Table(title="Summary", show_header=False)
            meta.add_column("Property", style="cyan")
            meta.add_column("Value", style="magenta")
            meta.add_row("Total Found", str(result_data["total_found"]))
            meta.add_row("Returned", str(result_data["returned"]))
            meta.add_row("Source", str(result_data["source"]))
            meta.add_row("Config Used", str(result_data["config_used"]))
            console.print(meta)
        else:
            for ev in out_events:
                console.print(f"[{ev.get('timestamp')}] ({ev.get('type')}) {ev.get('id')}: {ev.get('message')}")
            console.print(f"\nTotal Found: {result_data['total_found']}, Returned: {result_data['returned']}, Source: {result_data['source']}")

        if verbose:
            console.print(f"[green]✅ get_recent_events completed successfully[/green]")

        return result_data

    except Exception as e:
        console.print(f"[red]❌ get_recent_events failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["get_recent_events"]