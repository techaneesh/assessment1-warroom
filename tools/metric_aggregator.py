"""Tool 1: Metric Aggregator — computes summary statistics for any metric."""

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


@tool("aggregate_metrics")
def aggregate_metrics(metric_name: str, period: str = "all") -> str:
    """Compute summary statistics (mean, median, min, max, std, latest value,
    percent change from pre to post launch) for a given metric.

    Args:
        metric_name: Name of the metric field (e.g., 'dau', 'crash_rate_pct',
            'api_latency_p95_ms', 'signup_conversion_pct', 'd1_retention_pct',
            'd7_retention_pct', 'payment_success_rate_pct', 'support_tickets',
            'churn_cancellations', 'feature_adoption_start_pct',
            'feature_adoption_complete_pct').
        period: One of 'pre_launch', 'post_launch', or 'all'.

    Returns:
        JSON string with computed statistics.
    """
    logger.info(f"[TOOL:metric_aggregator] metric_name={metric_name}, period={period}")

    data = _load_metrics()
    metadata = data["metadata"]
    daily = data["daily_metrics"]

    pre_launch_days = set(metadata["pre_launch_days"])
    post_launch_days = set(metadata["post_launch_days"])

    if period == "pre_launch":
        entries = [d for d in daily if d["date"] in pre_launch_days]
    elif period == "post_launch":
        entries = [d for d in daily if d["date"] in post_launch_days]
    else:
        entries = daily

    values = [d[metric_name] for d in entries if d.get(metric_name) is not None]

    if not values:
        result = {"error": f"No data found for metric '{metric_name}' in period '{period}'"}
        return json.dumps(result)

    mean_val = statistics.mean(values)
    median_val = statistics.median(values)
    stdev_val = statistics.stdev(values) if len(values) > 1 else 0.0

    result = {
        "metric_name": metric_name,
        "period": period,
        "count": len(values),
        "mean": round(mean_val, 4),
        "median": round(median_val, 4),
        "min": round(min(values), 4),
        "max": round(max(values), 4),
        "std": round(stdev_val, 4),
        "latest": round(values[-1], 4),
    }

    # Compute pre-to-post change if period is "all" or "post_launch"
    pre_values = [d[metric_name] for d in daily if d["date"] in pre_launch_days and d.get(metric_name) is not None]
    post_values = [d[metric_name] for d in daily if d["date"] in post_launch_days and d.get(metric_name) is not None]

    if pre_values and post_values:
        pre_avg = statistics.mean(pre_values)
        post_avg = statistics.mean(post_values)
        if pre_avg != 0:
            pct_change = ((post_avg - pre_avg) / abs(pre_avg)) * 100
        else:
            pct_change = 0.0
        result["pre_launch_avg"] = round(pre_avg, 4)
        result["post_launch_avg"] = round(post_avg, 4)
        result["pct_change_post_vs_pre"] = round(pct_change, 2)

    logger.info(f"[TOOL:metric_aggregator] Result: mean={result['mean']}, latest={result['latest']}")
    return json.dumps(result, indent=2)
