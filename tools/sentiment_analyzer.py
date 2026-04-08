"""Tool 3: Sentiment Analyzer — classifies and summarizes user feedback."""

import json
import logging
from collections import Counter
from pathlib import Path

from crewai.tools import tool

logger = logging.getLogger("warroom")

_DATA_DIR: Path = Path("data")


def set_data_dir(path: Path):
    global _DATA_DIR
    _DATA_DIR = path


def _load_feedback() -> list[dict]:
    with open(_DATA_DIR / "user_feedback.json", "r") as f:
        return json.load(f)


# Common keywords to look for in feedback
ISSUE_KEYWORDS = {
    "crash": ["crash", "crashed", "crashing"],
    "slow": ["slow", "loading", "laggy", "takes forever", "load time"],
    "lost_work": ["lost", "disappeared", "gone", "deleted", "corrupted"],
    "error_messages": ["error", "error message", "weird error", "confusing error"],
    "billing": ["charged", "billing", "refund", "duplicate charge"],
}


def _extract_themes(entries: list[dict]) -> list[dict]:
    """Extract recurring themes from feedback text."""
    theme_counts = {}
    theme_examples = {}

    for entry in entries:
        text_lower = entry["text"].lower()
        for theme, keywords in ISSUE_KEYWORDS.items():
            if any(kw in text_lower for kw in keywords):
                theme_counts[theme] = theme_counts.get(theme, 0) + 1
                if theme not in theme_examples:
                    theme_examples[theme] = entry["text"]

    themes = []
    for theme, count in sorted(theme_counts.items(), key=lambda x: -x[1]):
        themes.append({
            "theme": theme,
            "count": count,
            "example": theme_examples[theme],
        })
    return themes


@tool("analyze_sentiment")
def analyze_sentiment(category: str = "all") -> str:
    """Analyze user feedback entries and return sentiment distribution,
    recurring themes, critical issues, and representative quotes.

    Args:
        category: Filter by 'all', 'positive', 'negative', 'neutral',
            or 'feature_related' (only feedback about the launched feature).

    Returns:
        JSON string with sentiment analysis results including distribution,
        top themes, critical issues, and sample quotes.
    """
    logger.info(f"[TOOL:sentiment_analyzer] category={category}")

    feedback = _load_feedback()

    # Filter by category
    if category == "feature_related":
        entries = [f for f in feedback if f.get("feature_related", False)]
    elif category in ("positive", "negative", "neutral"):
        entries = [f for f in feedback if f["sentiment"] == category]
    else:
        entries = feedback

    total = len(entries)
    if total == 0:
        return json.dumps({"error": f"No feedback found for category '{category}'"})

    # Sentiment distribution
    sentiment_counts = Counter(e["sentiment"] for e in entries)
    distribution = {
        "positive": sentiment_counts.get("positive", 0),
        "negative": sentiment_counts.get("negative", 0),
        "neutral": sentiment_counts.get("neutral", 0),
        "positive_pct": round(sentiment_counts.get("positive", 0) / total * 100, 1),
        "negative_pct": round(sentiment_counts.get("negative", 0) / total * 100, 1),
        "neutral_pct": round(sentiment_counts.get("neutral", 0) / total * 100, 1),
    }

    # Source distribution
    source_counts = dict(Counter(e["source"] for e in entries))

    # User segment distribution
    segment_counts = dict(Counter(e["user_segment"] for e in entries))

    # Extract themes from negative feedback
    negative_entries = [e for e in entries if e["sentiment"] == "negative"]
    themes = _extract_themes(negative_entries)

    # Critical issues (flagged by keywords suggesting severity)
    critical_keywords = ["urgent", "data loss", "deleted", "corrupted", "charged twice", "duplicate charge", "blocking"]
    critical_issues = []
    for entry in entries:
        text_lower = entry["text"].lower()
        if any(kw in text_lower for kw in critical_keywords):
            critical_issues.append({
                "id": entry["id"],
                "text": entry["text"],
                "user_segment": entry["user_segment"],
                "source": entry["source"],
            })

    # Sample quotes per sentiment
    sample_quotes = {}
    for sentiment in ["positive", "negative", "neutral"]:
        sentiment_entries = [e for e in entries if e["sentiment"] == sentiment]
        sample_quotes[sentiment] = [e["text"] for e in sentiment_entries[:3]]

    result = {
        "category_filter": category,
        "total_entries": total,
        "sentiment_distribution": distribution,
        "source_distribution": source_counts,
        "user_segment_distribution": segment_counts,
        "top_negative_themes": themes,
        "critical_issues": critical_issues,
        "critical_issue_count": len(critical_issues),
        "sample_quotes": sample_quotes,
    }

    logger.info(f"[TOOL:sentiment_analyzer] {total} entries, {distribution['negative_pct']}% negative, {len(critical_issues)} critical")
    return json.dumps(result, indent=2)
