"""Utility to load mock data files."""

import json
from pathlib import Path


def load_metrics(data_dir: Path) -> dict:
    """Load metrics.json and return parsed data."""
    with open(data_dir / "metrics.json", "r") as f:
        return json.load(f)


def load_feedback(data_dir: Path) -> list[dict]:
    """Load user_feedback.json and return list of entries."""
    with open(data_dir / "user_feedback.json", "r") as f:
        return json.load(f)


def load_release_notes(data_dir: Path) -> str:
    """Load release_notes.md and return as string."""
    with open(data_dir / "release_notes.md", "r") as f:
        return f.read()
