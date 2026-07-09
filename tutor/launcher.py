"""Bootstrap-and-launch for DevDojo. Stdlib only — runs with ANY Python,
even the wrong project's venv, and always uses DevDojo's own .venv.

    python -m tutor.launcher     (or just .\\run.ps1)

Creates .venv on first run, installs requirements, starts the app.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VENV_DIR = ROOT / ".venv"
VENV_PY = VENV_DIR / "Scripts" / "python.exe"


def ensure_venv() -> None:
    if not VENV_PY.exists():
        print("First run — creating DevDojo's virtual environment (.venv)...")
        subprocess.run([sys.executable, "-m", "venv", str(VENV_DIR)], check=True)
    subprocess.run(
        [str(VENV_PY), "-m", "pip", "install", "-q", "-r", str(ROOT / "requirements.txt")],
        check=True,
    )


def launch() -> None:
    ensure_venv()
    print("Starting DevDojo -> http://localhost:5057   (Ctrl+C to stop)")
    subprocess.run([str(VENV_PY), str(ROOT / "app.py")], cwd=ROOT)


if __name__ == "__main__":
    launch()
