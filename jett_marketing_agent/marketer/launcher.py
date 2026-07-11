"""Bootstrap-and-launch for the Jett Marketing Agent. Stdlib only — runs
with ANY Python, even the wrong project's venv, and always uses this
project's own .venv (same pattern as DevDojo's tutor/launcher.py).

    python -m marketer.launcher     (or just .\\run.ps1)
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VENV_DIR = ROOT / ".venv"
VENV_PY = (
    VENV_DIR / "Scripts" / "python.exe" if os.name == "nt" else VENV_DIR / "bin" / "python"
)


def ensure_venv() -> None:
    if not VENV_PY.exists():
        print("First run — creating the agent's virtual environment (.venv)...")
        subprocess.run([sys.executable, "-m", "venv", str(VENV_DIR)], check=True)
    subprocess.run(
        [str(VENV_PY), "-m", "pip", "install", "-q", "-r", str(ROOT / "requirements.txt")],
        check=True,
    )


def launch() -> None:
    ensure_venv()
    port = os.environ.get("JETT_MARKETING_PORT", "5058")
    print(f"Starting Jett Marketing Agent -> http://localhost:{port}   (Ctrl+C to stop)")
    subprocess.run([str(VENV_PY), str(ROOT / "app.py")], cwd=ROOT)


if __name__ == "__main__":
    launch()
