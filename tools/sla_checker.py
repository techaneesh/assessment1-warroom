"""Tool 5: SLA Checker — checks current metric values against SLA/SLO thresholds."""

import json
import logging
from pathlib import Path

from crewai.tools import tool

logger = logging.getLogger("warroom")

_DATA_DIR: Path = Path("data")

# SLA thresholds — documented and accessible
SLA_THRESHOLDS = {
    "api_latency_p95_ms": {"max": 250, "label": "API Latency p95", "unit": "ms"},
    "crash_rate_pct": {"max": 0.5, "label": "Crash Rate", "unit": "%"},
    "payment_success_rate_pct": {"min": 98.0, "label": "Payment Success Rate", "unit": "%"},
    "support_tickets": {"max": 60, "label": "Daily Support Tickets", "unit": "tickets/day"},
}


def set_data_dir(path: Path):
    global _DATA_DIR
    _DATA_DIR = path


def _load_metrics() -> dict:
    with open(_DATA_DIR / "metrics.json", "r") as f:
        return json.load(f)


@tool("check_sla_compliance")
def check_sla_compliance(metric_name: str = "all") -> str:
    """Check current (latest) metric values against predefined SLA/SLO thresholds.

    Thresholds:
    - API Latency p95: must be < 250ms
    - Crash Rate: must be < 0.5%
    - Payment Success Rate: must be >= 98.0%
    - Support Tickets: must be < 60/day

    Args:
        metric_name: Specific metric to check, or 'all' to check all SLA metrics.

    Returns:
        JSON string with pass/fail status for each metric, current value,
        threshold, and breach severity.
    """
    logger.info(f"[TOOL:sla_checker] metric_name={metric_name}")

    data = _load_metrics()
    latest = data["daily_metrics"][-1]  # Most recent day

    metrics_to_check = {}
    if metric_name == "all":
        metrics_to_check = SLA_THRESHOLDS
    elif metric_name in SLA_THRESHOLDS:
        metrics_to_check = {metric_name: SLA_THRESHOLDS[metric_name]}
    else:
        return json.dumps({"error": f"No SLA threshold defined for '{metric_name}'. Available: {list(SLA_THRESHOLDS.keys())}"})

    results = []
    breaches = 0

    for name, threshold in metrics_to_check.items():
        current_value = latest.get(name)
        if current_value is None:
            results.append({"metric": name, "status": "no_data"})
            continue

        if "max" in threshold:
            passed = current_value <= threshold["max"]
            threshold_desc = f"<= {threshold['max']}"
            breach_amount = current_value - threshold["max"] if not passed else 0
        else:
            passed = current_value >= threshold["min"]
            threshold_desc = f">= {threshold['min']}"
            breach_amount = threshold["min"] - current_value if not passed else 0

        if not passed:
            breaches += 1
            if "max" in threshold:
                breach_severity_pct = (breach_amount / threshold["max"]) * 100
            else:
                breach_severity_pct = (breach_amount / threshold["min"]) * 100
        else:
            breach_severity_pct = 0

        results.append({
            "metric": name,
            "label": threshold["label"],
            "current_value": round(current_value, 4),
            "threshold": threshold_desc,
            "unit": threshold["unit"],
            "status": "PASS" if passed else "BREACH",
            "breach_amount": round(breach_amount, 4) if not passed else 0,
            "breach_severity_pct": round(breach_severity_pct, 1),
        })

    output = {
        "check_date": latest["date"],
        "total_metrics_checked": len(results),
        "breaches": breaches,
        "all_clear": breaches == 0,
        "results": results,
    }

    logger.info(f"[TOOL:sla_checker] {breaches}/{len(results)} SLA breaches detected")
    return json.dumps(output, indent=2)
