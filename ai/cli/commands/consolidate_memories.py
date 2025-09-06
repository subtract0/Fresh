import click
from typing import Optional, List, Any, Dict
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import hashlib
import gzip
from datetime import datetime

console = Console()

def load_config(config_path: str) -> dict:
    """Load configuration from a JSON file."""
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            if not isinstance(data, dict):
                raise RuntimeError("Configuration file must contain a JSON object at top level.")
            return data
    except Exception as e:
        raise RuntimeError(f"Failed to load configuration: {str(e)}")

def _normalize_text(text: str) -> str:
    return " ".join(text.strip().split())

def _hash_text(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def _read_json_file(path: Path) -> List[Any]:
    with path.open('r', encoding='utf-8') as f:
        data = json.load(f)
        if isinstance(data, list):
            return data
        else:
            return [data]

def _read_jsonl_file(path: Path) -> List[Any]:
    items = []
    with path.open('r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                items.append(json.loads(line))
            except Exception:
                items.append(line)
    return items

def _read_text_file(path: Path) -> List[str]:
    with path.open('r', encoding='utf-8') as f:
        content = f.read()
        paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
        if paragraphs:
            return paragraphs
        else:
            return [l.strip() for l in content.splitlines() if l.strip()]

def _extract_text_from_obj(obj: Any) -> Optional[str]:
    if obj is None:
        return None
    if isinstance(obj, str):
        return obj
    if isinstance(obj, dict):
        for key in ("text", "content", "note", "memo", "message", "body"):
            if key in obj and isinstance(obj[key], str):
                return obj[key]
        try:
            return json.dumps(obj, ensure_ascii=False)
        except Exception:
            return None
    try:
        return str(obj)
    except Exception:
        return None

def write_output_file(output_path: Path, data: Dict[str, Any], compress: bool) -> Path:
    if compress:
        out_path = output_path.with_suffix(output_path.suffix + ".gz")
        with gzip.open(out_path, 'wt', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    else:
        out_path = output_path
        with out_path.open('w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    return out_path

def consolidate_memory_logic(config: Optional[dict], verbose: bool) -> dict:
    start_ts = datetime.utcnow().isoformat() + "Z"
    if verbose:
        console.print(f"[blue]Starting memory consolidation: {start_ts}[/blue]")

    try:
        memory_dir = Path(config.get("memory_dir")) if config and config.get("memory_dir") else Path.cwd() / "memories"
        if not memory_dir.exists():
            if config and config.get("create_if_missing", False):
                memory_dir.mkdir(parents=True, exist_ok=True)
                if verbose:
                    console.print(f"[yellow]Created missing memory directory at {memory_dir}[/yellow]")
            else:
                message = f"Memory directory does not exist: {memory_dir}"
                if verbose:
                    console.print(f"[red]{message}[/red]")
                return {
                    "feature": "consolidate_memories",
                    "status": "no_data",
                    "message": message,
                    "config_used": config,
                    "timestamp": start_ts
                }

        file_patterns = config.get("file_patterns") if config else None
        supported_exts = [".json", ".jsonl", ".txt", ".md", ".log"]
        files: List[Path] = []
        if file_patterns and isinstance(file_patterns, list) and file_patterns:
            for pattern in file_patterns:
                files.extend(sorted(memory_dir.glob(pattern)))
        else:
            for ext in supported_exts:
                files.extend(sorted(memory_dir.glob(f"*{ext}")))
            if not files:
                files = sorted([p for p in memory_dir.iterdir() if p.is_file()])

        if verbose:
            console.print(f"[blue]Discovered {len(files)} files to scan in {memory_dir}[/blue]")

        total_items_found = 0
        seen_hashes = {}
        entries = []
        for file_path in files:
            try:
                if verbose:
                    console.print(f"[blue]Processing file: {file_path}[/blue]")
                if file_path.suffix.lower() == ".json":
                    raw_items = _read_json_file(file_path)
                elif file_path.suffix.lower() == ".jsonl":
                    raw_items = _read_jsonl_file(file_path)
                else:
                    raw_items = _read_text_file(file_path)
                for raw in raw_items:
                    text = _extract_text_from_obj(raw)
                    if not text:
                        continue
                    norm = _normalize_text(text)
                    if not norm:
                        continue
                    total_items_found += 1
                    h = _hash_text(norm)
                    if h in seen_hashes:
                        seen_hashes[h]["sources"].append(str(file_path))
                        seen_hashes[h]["count"] += 1
                        continue
                    entry = {
                        "id": h[:12],
                        "hash": h,
                        "text": norm if verbose else (norm if len(norm) < 1000 else norm[:1000] + "…"),
                        "sources": [str(file_path)],
                    }
                    seen_hashes[h] = {"entry": entry, "sources": [str(file_path)], "count": 1}
                    entries.append(entry)
            except Exception as e:
                if verbose:
                    console.print(f"[red]Failed to process file {file_path}: {e}[/red]")

        unique_count = len(entries)
        duplicates_removed = total_items_found - unique_count

        if verbose:
            console.print(f"[green]Found {total_items_found} items; {unique_count} unique; {duplicates_removed} duplicates removed.[/green]")

        if config and config.get("summarize", True):
            for e in entries:
                txt = e.get("text", "")
                if len(txt) > 400:
                    e["excerpt"] = txt[:400] + "…"
                else:
                    e["excerpt"] = txt

        output_dir = Path(config.get("output_dir")) if config and config.get("output_dir") else memory_dir
        output_dir.mkdir(parents=True, exist_ok=True)
        filename = config.get("output_filename") if config and config.get("output_filename") else "consolidated_memories.json"
        output_path = output_dir / filename
        compress = bool(config.get("compress", False))

        output_payload = {
            "generated_at": start_ts,
            "total_files_scanned": len(files),
            "total_items_found": total_items_found,
            "unique_items": unique_count,
            "duplicates_removed": duplicates_removed,
            "entries": entries if config and config.get("include_entries", False) else [{"id": e["id"], "excerpt": e.get("excerpt", e.get("text", "")), "sources": e.get("sources", [])} for e in entries],
            "config_used": config or {}
        }

        out_file = write_output_file(output_path, output_payload, compress)

        result = {
            "feature": "consolidate_memories",
            "status": "success",
            "message": "Memory consolidation completed successfully",
            "total_files_scanned": len(files),
            "total_items_found": total_items_found,
            "unique_items": unique_count,
            "duplicates_removed": duplicates_removed,
            "output_file": str(out_file),
            "timestamp": start_ts,
            "config_used": config or {}
        }

        if verbose:
            console.print(f"[green]Wrote consolidated output to {out_file}[/green]")

        return result

    except Exception as e:
        raise RuntimeError(f"Error during consolidation: {str(e)}")

@click.command(help="Consolidate and optimize memory data based on the provided configuration.")
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format (json, table, plain)')
@click.option('--config', '-c', type=click.Path(exists=True), help='Path to configuration JSON file')
@click.pass_context
def consolidate_memories(ctx, verbose: bool, output: str, config: Optional[str]):
    try:
        config_data = None
        if config:
            config_data = load_config(config)
            if verbose:
                console.print(f"[blue]Loaded configuration from {config}[/blue]")

        result_data = consolidate_memory_logic(config_data, verbose)

        if output == 'json':
            console.print_json(json.dumps(result_data, ensure_ascii=False, indent=2))
        elif output == 'table':
            table = Table(title=f"consolidate_memories Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")

            keys_to_show = ["feature", "status", "message", "total_files_scanned", "total_items_found",
                            "unique_items", "duplicates_removed", "output_file", "timestamp"]
            for key in keys_to_show:
                if key in result_data:
                    table.add_row(str(key), str(result_data.get(key)))
            console.print(table)
        else:
            for key, value in result_data.items():
                console.print(f"{key}: {value}")

        if verbose:
            console.print(f"[green]✅ consolidate_memories completed successfully[/green]")

    except Exception as e:
        console.print(f"[red]❌ consolidate_memories failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["consolidate_memories"]