"""Tool 4: Trend Comparator — compares pre-launch vs post-launch trends."""

import json
import logging
import statistics
from pathlib import Path

from crewai.tools import tool

logger = logging.getLogger("warroom")

_DATA_DIR: Path = Path("data")


def set_data_dir(path: Path):
    global _DATA_DIR
    _DATA_DIR = path


def _load_metrics() -> dict:
    with open(_DATA_DIR / "metrics.json", "r") as f:
        return json.load(f)


def _compute_slope(values: list[float]) -> float:
    """Compute simple linear regression slope."""
    n = len(values)
    if n < 2:
        return 0.0
    x_values = list(range(n))
    x_mean = statistics.mean(x_values)
    y_mean = statistics.mean(values)

    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, values))
    denominator = sum((x - x_mean) ** 2 for x in x_values)

    if denominator == 0:
        return 0.0
    return numerator / denominator


@tool("compare_trends")
def compare_trends(metric_name: str) -> str:
    """Compare pre-launch vs post-launch trends for a specific metric.

    Computes averages, slopes (linear regression), absolute and percentage
    change, and classifies the trend direction as improving, degrading, or stable.

    Args:
        metric_name: Name of the metric field (e.g., 'dau', 'crash_rate_pct',
            'api_latency_p95_ms', 'signup_conversion_pct', 'd1_retention_pct',
            'payment_success_rate_pct', 'support_tickets', 'churn_cancellations').

    Returns:
        JSON string with pre vs post comparison including averages, slopes,
        percentage change, and trend direction.
    """
    logger.info(f"[TOOL:trend_comparator] metric_name={metric_name}")

    data = _load_metrics()
    metadata = data["metadata"]
    daily = data["daily_metrics"]

    pre_launch_days = set(metadata["pre_launch_days"])
    post_launch_days = set(metadata["post_launch_days"])

    pre_values = [d[metric_name] for d in daily if d["date"] in pre_launch_days and d.get(metric_name) is not None]
    post_values = [d[metric_name] for d in daily if d["date"] in post_launch_days and d.get(metric_name) is not None]

    if not pre_values or not post_values:
        return json.dumps({"error": f"Insufficient data for '{metric_name}' in one or both periods"})

    pre_avg = statistics.mean(pre_values)
    post_avg = statistics.mean(post_values)
    abs_change = post_avg - pre_avg
    pct_change = ((post_avg - pre_avg) / abs(pre_avg) * 100) if pre_avg != 0 else 0.0

    pre_slope = _compute_slope(pre_values)
    post_slope = _compute_slope(post_values)

    # Classify direction (5% threshold for "stable")
    if abs(pct_change) < 5:
        direction = "stable"
    elif pct_change > 0:
        direction = "increasing"
    else:
        direction = "decreasing"

    # Determine if the change is positive or negative for the business
    # Higher is worse for: crash_rate, latency, support_tickets, churn
    worse_when_higher = {"crash_rate_pct", "api_latency_p95_ms", "support_tickets", "churn_cancellations"}
    if metric_name in worse_when_higher:
        assessment = "degrading" if pct_change > 5 else ("improving" if pct_change < -5 else "stable")
    else:
        assessment = "improving" if pct_change > 5 else ("degrading" if pct_change < -5 else "stable")

    result = {
        "metric_name": metric_name,
        "pre_launch": {
            "average": round(pre_avg, 4),
            "slope_per_day": round(pre_slope, 4),
            "data_points": len(pre_values),
            "first": round(pre_values[0], 4),
            "last": round(pre_values[-1], 4),
        },
        "post_launch": {
            "average": round(post_avg, 4),
            "slope_per_day": round(post_slope, 4),
            "data_points": len(post_values),
            "first": round(post_values[0], 4),
            "last": round(post_values[-1], 4),
        },
        "comparison": {
            "absolute_change": round(abs_change, 4),
            "percentage_change": round(pct_change, 2),
            "direction": direction,
            "business_assessment": assessment,
        },
    }

    logger.info(f"[TOOL:trend_comparator] {metric_name}: {pct_change:+.1f}% change, assessment={assessment}")
    return json.dumps(result, indent=2)
