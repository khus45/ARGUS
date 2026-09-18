"""Vercel Python Function entrypoint for the ARGUS FastAPI application."""

import sys
from pathlib import Path

# Vercel can execute a Python function with ``api/`` as its import directory.
# Add the repository root explicitly so the shared backend package resolves in
# both local and serverless runtimes.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.main import app  # noqa: E402

__all__ = ["app"]
