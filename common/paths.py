from __future__ import annotations

import platform
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / 'data'
TEST_DOCS_DIR = REPO_ROOT / 'test_docs'
RUNTIME_DIR = REPO_ROOT / 'runtime'

for path in (DATA_DIR, TEST_DOCS_DIR, RUNTIME_DIR):
    path.mkdir(parents=True, exist_ok=True)


def data_path(*parts):
    """Always use this to get data files. Never hardcode 'data/...' strings."""
    return DATA_DIR.joinpath(*parts)


def runtime_path(*parts):
    """Always use this to get runtime artifacts. Never hardcode 'runtime/...' strings."""
    return RUNTIME_DIR.joinpath(*parts)


# ==================== Cross-platform helpers (NEW) ====================

def get_venv_python() -> Path:
    """
    Return the correct python executable inside the project .venv.

    Why:
    - Windows: .venv\\Scripts\\python.exe
    - Linux/macOS: .venv/bin/python
    - All future scripts / CLI / pipeline must call this instead of writing
      .\.venv\Scripts\python.exe or ./.venv/bin/python directly.
    - This is the #1 source of "works on my machine" cross-platform breakage.
    """
    if platform.system() == "Windows":
        return REPO_ROOT / ".venv" / "Scripts" / "python.exe"
    else:
        return REPO_ROOT / ".venv" / "bin" / "python"


def get_platform_aware_command(base_cmd: str, *args: str) -> list[str]:
    """
    Build a command list that works without shell quoting nightmares.

    Usage:
        cmd = get_platform_aware_command("python", "-m", "research_core.qlib_lab.cli", "init")
        # then subprocess.run(cmd, ...)

    Why:
    - Avoids having to write different commands in .sh vs .ps1 vs docs.
    - All orchestration code should go through this.
    """
    if base_cmd in ("python", "python3"):
        return [str(get_venv_python())] + list(args)
    return [base_cmd] + list(args)


def ensure_cross_platform() -> None:
    """
    Call this early in any entrypoint script (run_pipeline.py, cli, tests, etc.).

    Why:
    - Forces consistent path usage from day one.
    - Can later be extended to set PYTHONPATH, warn if not inside venv,
      normalize os.sep, etc.
    - Makes the entire research flow "clone → run python script → works"
      instead of "clone → fix 17 platform-specific commands".
    """
    # Future: we can add auto PYTHONPATH injection or venv activation hints here.
    pass


def get_repo_root() -> Path:
    """Convenience accessor so nobody does Path(__file__).parents[...] manually."""
    return REPO_ROOT
