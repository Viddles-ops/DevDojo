# Jett Marketing Agent configuration — paths/constants only, no secrets (none needed).
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Where aggregate stats exports live. Point this at the OSKA pipeline's
# Gold-layer export folder on your machine (NEVER Bronze/Silver — PHI stops
# at Bronze). Ships pointing at bundled fictional sample data so the app
# runs out of the box.
GOLD_DIR = Path(os.environ.get("OSKA_GOLD_DIR", str(BASE_DIR / "sample_gold")))

ASSETS_DIR = BASE_DIR / "assets"
LOGO_PATH = ASSETS_DIR / "jett_logo.png"  # optional; wordmark used if absent

APP_PORT = int(os.environ.get("JETT_MARKETING_PORT", "5058"))

# Local AI only (workspace ADR-011). No cloud LLMs, no API keys.
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5:7b-instruct")
OLLAMA_TIMEOUT_SECONDS = int(os.environ.get("OLLAMA_TIMEOUT_SECONDS", "120"))

# Small-cell suppression: metrics computed over fewer than this many
# records are excluded from customer-facing documents.
MIN_CELL_SIZE = 11
