# DevDojo configuration — paths/constants only, no secrets (none needed).
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CURRICULUM_DIR = BASE_DIR / "curriculum"
DATA_DIR = BASE_DIR / "data"
PROGRESS_PATH = DATA_DIR / "progress.json"

APP_PORT = int(os.environ.get("DEVDOJO_PORT", "5057"))

# Local AI only (workspace ADR-011). No cloud LLMs, no API keys.
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5:7b-instruct")
OLLAMA_TIMEOUT_SECONDS = int(os.environ.get("OLLAMA_TIMEOUT_SECONDS", "120"))

TRACKS = {
    "stack": "Your Stack — how your projects work",
    "claude-code": "Claude Code — agents, skills, workflow",
    "grow": "Grow — practices to adopt next",
    "agents": "Agents — design, build, and ship AI agents",
}
