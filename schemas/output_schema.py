"""Pydantic models for the structured launch decision output."""

from pydantic import BaseModel, Field
from typing import Literal


class MetricReference(BaseModel):
    metric_name: str
    pre_launch_avg: float
    post_launch_avg: float
    change_pct: float
    assessment: Literal["improving", "degrading", "stable", "critical"]


class FeedbackSummary(BaseModel):
    total_entries: int
    positive_pct: float
    negative_pct: float
    neutral_pct: float
    top_issues: list[str]
    top_praise: list[str]
    critical_flags: list[str]


class Rationale(BaseModel):
    summary: str = Field(description="1-3 sentence summary of the decision rationale")
    key_drivers: list[str] = Field(description="Top 3-5 factors driving the decision")
    metric_references: list[MetricReference] = Field(description="Key metrics referenced")
    feedback_summary: FeedbackSummary


class RiskItem(BaseModel):
    id: str = Field(description="e.g., RISK-001")
    title: str
    severity: Literal["critical", "high", "medium", "low"]
    likelihood: Literal["high", "medium", "low"]
    description: str
    metric_evidence: str
    mitigation: str
    owner: str


class ActionItem(BaseModel):
    id: str = Field(description="e.g., ACT-001")
    action: str
    owner: str
    timeline: str = Field(description="e.g., 'within 4 hours', 'within 24 hours'")
    priority: Literal["P0", "P1", "P2"]


class CommunicationItem(BaseModel):
    audience: str = Field(description="e.g., engineering, support, executives, customers, public")
    channel: str = Field(description="e.g., Slack, email, in-app banner, status page")
    message_summary: str
    timing: str


class ConfidenceAssessment(BaseModel):
    score: float = Field(ge=0.0, le=1.0, description="Confidence score from 0.0 to 1.0")
    level: Literal["low", "medium", "high"]
    key_uncertainties: list[str]
    would_increase_confidence: list[str]


class LaunchDecisionOutput(BaseModel):
    """Final structured output of the War Room decision."""
    decision: Literal["PROCEED", "PAUSE", "ROLL_BACK"]
    decision_timestamp: str
    feature_name: str
    rollout_percentage: int
    rationale: Rationale
    risk_register: list[RiskItem]
    action_plan: list[ActionItem]
    communication_plan: list[CommunicationItem]
    confidence: ConfidenceAssessment
    next_review: str = Field(description="When to reconvene, e.g., 2026-04-09T10:00:00Z")
    dissenting_opinions: list[str] = Field(description="Any agent disagreements for transparency")
