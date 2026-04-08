"""Tools for the War Room multi-agent system."""

from tools.metric_aggregator import aggregate_metrics, set_data_dir as set_metric_dir
from tools.anomaly_detector import detect_anomalies, set_data_dir as set_anomaly_dir
from tools.sentiment_analyzer import analyze_sentiment, set_data_dir as set_sentiment_dir
from tools.trend_comparator import compare_trends, set_data_dir as set_trend_dir
from tools.sla_checker import check_sla_compliance, set_data_dir as set_sla_dir


def configure_data_dir(data_dir):
    """Set data directory for all tools."""
    set_metric_dir(data_dir)
    set_anomaly_dir(data_dir)
    set_sentiment_dir(data_dir)
    set_trend_dir(data_dir)
    set_sla_dir(data_dir)


__all__ = [
    "aggregate_metrics",
    "detect_anomalies",
    "analyze_sentiment",
    "compare_trends",
    "check_sla_compliance",
    "configure_data_dir",
]
