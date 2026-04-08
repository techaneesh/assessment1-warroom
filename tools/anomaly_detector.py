"""Tool 2: Anomaly Detector — detects anomalous data points using z-score analysis."""

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


@tool("detect_anomalies")
def detect_anomalies(metric_name: str, z_threshold: float = 2.0) -> str:
    """Detect anomalous data points in a metric's time series using z-score
    analysis against the pre-launch baseline.

    A data point is flagged as anomalous if its z-score exceeds the threshold
    (default 2.0 standard deviations from the pre-launch mean).

    Args:
        metric_name: Name of the metric field (e.g., 'crash_rate_pct',
            'api_latency_p95_ms', 'dau', 'support_tickets').
        z_threshold: Z-score threshold for anomaly detection (default 2.0).

    Returns:
        JSON string with list of anomalous data points, their z-scores, and direction.
    """
    logger.info(f"[TOOL:anomaly_detector] metric_name={metric_name}, z_threshold={z_threshold}")

    data = _load_metrics()
    metadata = data["metadata"]
    daily = data["daily_metrics"]

    pre_launch_days = set(metadata["pre_launch_days"])

    # Compute baseline from pre-launch data
    baseline_values = [d[metric_name] for d in daily if d["date"] in pre_launch_days and d.get(metric_name) is not None]

    if len(baseline_values) < 2:
        return json.dumps({"error": f"Insufficient pre-launch data for '{metric_name}' to compute baseline"})

    baseline_mean = statistics.mean(baseline_values)
    baseline_std = statistics.stdev(baseline_values)

    if baseline_std == 0:
        baseline_std = 0.001  # Avoid division by zero

    anomalies = []
    for entry in daily:
        value = entry.get(metric_name)
        if value is None:
            continue

        z_score = (value - baseline_mean) / baseline_std

        if abs(z_score) > z_threshold:
            direction = "spike" if z_score > 0 else "drop"
            anomalies.append({
                "date": entry["date"],
                "day_label": entry["day_label"],
                "value": round(value, 4),
                "z_score": round(z_score, 2),
                "direction": direction,
                "deviation_from_baseline": round(value - baseline_mean, 4),
            })

    result = {
        "metric_name": metric_name,
        "z_threshold": z_threshold,
        "baseline_mean": round(baseline_mean, 4),
        "baseline_std": round(baseline_std, 4),
        "total_data_points": len(daily),
        "anomalies_found": len(anomalies),
        "anomalies": anomalies,
    }

    logger.info(f"[TOOL:anomaly_detector] Found {len(anomalies)} anomalies for {metric_name}")
    return json.dumps(result, indent=2)
