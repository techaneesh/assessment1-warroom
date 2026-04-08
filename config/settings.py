"""Central configuration for the War Room multi-agent system."""

import os
from pathlib import Path

# LLM Configuration
LLM_MODEL = "gemini/gemini-2.5-flash"
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"

# SLA / SLO Thresholds
SLA_THRESHOLDS = {
    "api_latency_p95_ms": {"max": 250, "label": "API Latency p95 (ms)", "unit": "ms"},
    "crash_rate_pct": {"max": 0.5, "label": "Crash Rate (%)", "unit": "%"},
    "payment_success_rate_pct": {"min": 98.0, "label": "Payment Success Rate (%)", "unit": "%"},
    "support_tickets": {"max": 60, "label": "Daily Support Tickets", "unit": "tickets/day"},
}

# Launch metadata
LAUNCH_DATE = "2026-04-03"
FEATURE_NAME = "Smart Workflow Builder"
ROLLOUT_PERCENTAGE = 30
