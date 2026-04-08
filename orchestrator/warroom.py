"""War Room Orchestrator — assembles agents, tasks, and crew."""

from crewai import Crew, Task, Process, LLM
from pathlib import Path

from agents.data_analyst_agent import create_data_analyst_agent
from agents.marketing_agent import create_marketing_agent
from agents.risk_agent import create_risk_agent
from agents.engineering_agent import create_engineering_agent
from agents.customer_success_agent import create_customer_success_agent
from agents.pm_agent import create_pm_agent
from schemas.output_schema import LaunchDecisionOutput
from tools.metric_aggregator import aggregate_metrics
from tools.anomaly_detector import detect_anomalies
from tools.sentiment_analyzer import analyze_sentiment
from tools.trend_comparator import compare_trends
from tools.sla_checker import check_sla_compliance


def build_crew(llm: LLM, output_dir: Path) -> Crew:
    """Build the War Room crew with all agents, tasks, and context chains."""

    # --- Create Agents ---
    data_analyst = create_data_analyst_agent(
        llm=llm,
        tools=[aggregate_metrics, detect_anomalies, compare_trends],
    )

    marketing = create_marketing_agent(
        llm=llm,
        tools=[analyze_sentiment],
    )

    engineering = create_engineering_agent(
        llm=llm,
        tools=[aggregate_metrics, detect_anomalies, check_sla_compliance],
    )

    customer_success = create_customer_success_agent(
        llm=llm,
        tools=[analyze_sentiment, aggregate_metrics],
    )

    risk = create_risk_agent(
        llm=llm,
        tools=[detect_anomalies, check_sla_compliance, compare_trends],
    )

    pm = create_pm_agent(llm=llm)

    # --- Define Tasks ---
    task1_data_analysis = Task(
        description=(
            "Analyze all available launch metrics for the Smart Workflow Builder feature. "
            "You MUST use the tools provided to compute real statistics.\n\n"
            "Steps:\n"
            "1. Use the aggregate_metrics tool for EACH of these metrics: "
            "signup_conversion_pct, dau, d1_retention_pct, d7_retention_pct, "
            "crash_rate_pct, api_latency_p95_ms, payment_success_rate_pct, "
            "support_tickets, churn_cancellations\n"
            "2. Use the detect_anomalies tool on crash_rate_pct, api_latency_p95_ms, "
            "and support_tickets to identify spikes\n"
            "3. Use the compare_trends tool on at least 4 key metrics\n\n"
            "Provide a comprehensive quantitative assessment covering which metrics "
            "improved, which degraded, anomalies detected, and your confidence level."
        ),
        expected_output=(
            "A detailed quantitative report with: metric-by-metric analysis including "
            "exact pre/post numbers and percentage changes, anomaly list with dates, "
            "trend comparisons, and an overall data health assessment with confidence "
            "level (low/medium/high)."
        ),
        agent=data_analyst,
    )

    task2_sentiment = Task(
        description=(
            "Analyze all user feedback collected during the launch period.\n\n"
            "Steps:\n"
            "1. Use the analyze_sentiment tool with category='all' for overall distribution\n"
            "2. Use the analyze_sentiment tool with category='feature_related' for "
            "feature-specific feedback\n"
            "3. Use the analyze_sentiment tool with category='negative' for deep dive "
            "into complaints\n\n"
            "Identify: overall sentiment distribution, top 3 recurring complaints, "
            "top 3 positive signals, critical outliers (data loss, billing issues). "
            "Then assess brand risk and prepare communication guidance for three "
            "scenarios: proceed, pause, and rollback."
        ),
        expected_output=(
            "A sentiment analysis report with: distribution breakdown, top recurring "
            "issues with frequency, critical outlier flags, brand risk assessment "
            "(low/medium/high), and draft communication bullets for each scenario "
            "(proceed/pause/rollback)."
        ),
        agent=marketing,
        context=[task1_data_analysis],
    )

    task3_system_health = Task(
        description=(
            "Evaluate system reliability and infrastructure health.\n\n"
            "Steps:\n"
            "1. Use the check_sla_compliance tool with metric_name='all' to check "
            "all SLA thresholds\n"
            "2. Use the aggregate_metrics tool for crash_rate_pct and api_latency_p95_ms "
            "to see post-launch trends\n"
            "3. Use the detect_anomalies tool on api_latency_p95_ms\n\n"
            "Assess: severity levels (P0-P3) for each technical issue, estimated "
            "time-to-fix, whether infrastructure can handle 100% rollout, and "
            "technical prerequisites before expanding."
        ),
        expected_output=(
            "A system health report with: SLA compliance status, severity classification "
            "of technical issues (P0-P3), estimated time-to-fix per issue, infrastructure "
            "readiness for full rollout, and prerequisites before expanding."
        ),
        agent=engineering,
        context=[task1_data_analysis],
    )

    task4_customer_impact = Task(
        description=(
            "Assess the impact of the launch on customer success metrics.\n\n"
            "Steps:\n"
            "1. Use the analyze_sentiment tool with category='negative' to understand "
            "pain points\n"
            "2. Use the aggregate_metrics tool for support_tickets and churn_cancellations\n\n"
            "Evaluate: support team capacity (current vs baseline volume), churn risk "
            "for paid customers, impact by segment (free vs paid vs enterprise), and "
            "CSAT risk if rollout continues or expands."
        ),
        expected_output=(
            "A customer impact report with: support capacity analysis, churn risk "
            "assessment with projected numbers, segment-level impact analysis, "
            "and recommended customer success actions."
        ),
        agent=customer_success,
        context=[task1_data_analysis, task2_sentiment],
    )

    task5_risk_assessment = Task(
        description=(
            "You are the devil's advocate. Review ALL prior analyses and challenge "
            "their conclusions.\n\n"
            "Steps:\n"
            "1. Use the check_sla_compliance tool to independently verify SLA claims\n"
            "2. Use the detect_anomalies tool on d1_retention_pct and churn_cancellations\n"
            "3. Use the compare_trends tool on d7_retention_pct and payment_success_rate_pct\n\n"
            "Specifically:\n"
            "- Identify any optimistic bias in the reports\n"
            "- List risks that have been underweighted\n"
            "- Challenge any assumption stated as fact\n"
            "- Consider compounding risks\n"
            "- Identify what data is MISSING\n"
            "- Produce a formal risk register with top 5 risks ranked by severity"
        ),
        expected_output=(
            "A risk assessment with: challenges to prior conclusions, a risk register "
            "with top 5 risks (each with severity, likelihood, mitigation, owner), "
            "list of missing data, worst-case scenario, and conditions under which "
            "rollback becomes mandatory."
        ),
        agent=risk,
        context=[task1_data_analysis, task2_sentiment, task3_system_health, task4_customer_impact],
    )

    task6_pm_decision = Task(
        description=(
            "As the Product Manager, synthesize ALL prior analyses to make the final "
            "launch decision.\n\n"
            "Your decision must be one of:\n"
            "- PROCEED: continue expanding to 60% then 100% rollout\n"
            "- PAUSE: hold at 30%, fix critical issues, reassess in 48 hours\n"
            "- ROLL_BACK: revert the feature entirely\n\n"
            "Your output MUST include:\n"
            "1. decision: PROCEED, PAUSE, or ROLL_BACK\n"
            "2. decision_timestamp: current ISO timestamp\n"
            "3. feature_name: Smart Workflow Builder\n"
            "4. rollout_percentage: 30\n"
            "5. rationale: with summary, key_drivers list, metric_references, and feedback_summary\n"
            "6. risk_register: list of risk items with id, title, severity, likelihood, "
            "description, metric_evidence, mitigation, owner\n"
            "7. action_plan: list of action items with id, action, owner, timeline, priority\n"
            "8. communication_plan: list with audience, channel, message_summary, timing\n"
            "9. confidence: score (0-1), level, key_uncertainties, would_increase_confidence\n"
            "10. next_review: ISO timestamp for next war room meeting\n"
            "11. dissenting_opinions: any disagreements from agents\n\n"
            "Reference SPECIFIC metrics and feedback in your rationale. Be honest about "
            "uncertainty in your confidence score."
        ),
        expected_output=(
            "A complete JSON object matching the LaunchDecisionOutput schema with all "
            "required fields populated based on evidence from prior analyses."
        ),
        agent=pm,
        context=[
            task1_data_analysis,
            task2_sentiment,
            task3_system_health,
            task4_customer_impact,
            task5_risk_assessment,
        ],
        output_pydantic=LaunchDecisionOutput,
    )

    # --- Assemble Crew ---
    crew = Crew(
        agents=[data_analyst, marketing, engineering, customer_success, risk, pm],
        tasks=[
            task1_data_analysis,
            task2_sentiment,
            task3_system_health,
            task4_customer_impact,
            task5_risk_assessment,
            task6_pm_decision,
        ],
        process=Process.sequential,
        verbose=True,
        output_log_file=str(output_dir / "warroom_trace.log"),
    )

    return crew
