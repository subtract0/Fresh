from __future__ import annotations
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from ai.memory.store import set_memory_store, InMemoryMemoryStore
from ai.tools.memory_tools import WriteMemory
from ai.tools.next_steps import GenerateNextSteps
from ai.tools.mcp_client import DiscoverMCPServers


def _run(cmd: list[str], cwd: Path | None = None) -> tuple[int, str]:
    try:
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False)
        return result.returncode, result.stdout + result.stderr
    except Exception as e:
        return 1, str(e)


def ask_and_implement(request: str, branch_prefix: str = "auto-feature") -> Dict[str, Any]:
    """High-level interface: user describes what they want, agents plan and implement.
    
    Creates a feature branch to avoid conflicts with parallel work.
    Returns a summary with branch name, plan, and next steps.
    """
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    branch_name = f"{branch_prefix}-{timestamp}"
    
    # Ensure isolated memory for this planning session
    set_memory_store(InMemoryMemoryStore())
    
    # Write user request to memory
    WriteMemory(content=f"user request: {request}", tags=["feature", "user-request"]).run()  # type: ignore
    
    # Create feature branch (conflict-safe)
    code, out = _run(["git", "checkout", "-b", branch_name])
    if code != 0:
        return {"error": f"Failed to create branch {branch_name}: {out}"}
    
    # Discover available MCP capabilities
    mcp_servers = DiscoverMCPServers().run()  # type: ignore
    WriteMemory(content=f"available MCP servers: {len(mcp_servers)} servers with tools for browser, research, docs, shell", tags=["feature", "mcp"]).run()  # type: ignore
    
    # Generate implementation plan
    plan_steps = GenerateNextSteps(limit=5, tags=["feature"]).run()  # type: ignore
    WriteMemory(content=f"implementation plan: {plan_steps.strip()}", tags=["feature", "planning"]).run()  # type: ignore
    
    return {
        "request": request,
        "branch": branch_name,
        "mcp_servers": len(mcp_servers),
        "plan": plan_steps.strip(),
        "status": "branch created, ready for implementation",
        "next": "Agents will implement on this branch to avoid conflicts"
    }


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        request = " ".join(sys.argv[1:])
        result = ask_and_implement(request)
        import json
        print(json.dumps(result, indent=2))
    else:
        print("Usage: python -m ai.interface.ask_implement 'your request here'")
