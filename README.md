# Assessment 1: Product Launch War Room

A multi-agent system that simulates a cross-functional "war room" during a product launch. The system analyzes a mock dashboard (metrics + user feedback) and produces a structured **Proceed / Pause / Roll Back** decision with a concise action plan.

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    SEQUENTIAL CREW                            │
│                                                              │
│  Task 1: Data Analyst Agent                                  │
│     │  Tools: aggregate_metrics, detect_anomalies,           │
│     │         compare_trends                                 │
│     ▼                                                        │
│  Task 2: Marketing/Comms Agent                               │
│     │  Tools: analyze_sentiment                              │
│     ▼                                                        │
│  Task 3: Engineering/SRE Agent (bonus)                       │
│     │  Tools: aggregate_metrics, detect_anomalies,           │
│     │         check_sla_compliance                           │
│     ▼                                                        │
│  Task 4: Customer Success Agent (bonus)                      │
│     │  Tools: analyze_sentiment, aggregate_metrics           │
│     ▼                                                        │
│  Task 5: Risk/Critic Agent                                   │
│     │  Tools: detect_anomalies, check_sla_compliance,        │
│     │         compare_trends                                 │
│     ▼                                                        │
│  Task 6: Product Manager Agent (Decision Maker)              │
│     │  No tools — synthesizes all prior context              │
│     │  Output: Structured JSON (Pydantic validated)          │
│     ▼                                                        │
│  ┌──────────────────────────────┐                            │
│  │  output/launch_decision.json │                            │
│  └──────────────────────────────┘                            │
└──────────────────────────────────────────────────────────────┘
```

### Agent Roles

| # | Agent | Role | Tools Used |
|---|-------|------|-----------|
| 1 | **Data Analyst** | Quantitative metrics analysis | aggregate_metrics, detect_anomalies, compare_trends |
| 2 | **Marketing/Comms** | Sentiment analysis & communication plans | analyze_sentiment |
| 3 | **Engineering/SRE** *(bonus)* | System health & infrastructure readiness | aggregate_metrics, detect_anomalies, check_sla_compliance |
| 4 | **Customer Success** *(bonus)* | Churn risk & support capacity | analyze_sentiment, aggregate_metrics |
| 5 | **Risk/Critic** | Devil's advocate — challenges all assumptions | detect_anomalies, check_sla_compliance, compare_trends |
| 6 | **Product Manager** | Final decision maker (Proceed/Pause/Roll Back) | None (structured output only) |

### Tools (5 custom tools, all called programmatically)

| Tool | Description |
|------|-------------|
| `aggregate_metrics` | Computes mean, median, std, min/max, % change for any metric |
| `detect_anomalies` | Z-score anomaly detection against pre-launch baseline |
| `analyze_sentiment` | Classifies feedback, extracts themes, identifies critical issues |
| `compare_trends` | Pre vs post launch comparison with slopes and direction |
| `check_sla_compliance` | Checks latest values against SLA thresholds |

## Setup

### Prerequisites
- Python 3.10+
- A Google AI API key ([Get one here](https://aistudio.google.com/apikey))

### Installation

```bash
# Clone the repository
git clone <repo-url>
cd assessment1-warroom

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure API key
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

## Running the System

```bash
python main.py
```

The system will:
1. Load mock dashboard data (metrics, feedback, release notes)
2. Run 6 agents sequentially, each using tools to analyze the data
3. Produce a structured JSON decision
4. Save output files to `output/`

### Expected runtime: 2-5 minutes (depends on API response times)

## Output

### Final Decision (`output/launch_decision.json`)

```json
{
  "decision": "PAUSE",
  "rationale": { ... },
  "risk_register": [ ... ],
  "action_plan": [ ... ],
  "communication_plan": [ ... ],
  "confidence": { "score": 0.72, ... },
  "next_review": "2026-04-08T10:00:00Z"
}
```

### Trace Log (`output/warroom_trace.log`)

Contains the complete execution trace including:
- Each agent's reasoning process
- Every tool call with arguments and results
- Task completions and handoffs between agents

To read the trace log:
```bash
# View full trace
cat output/warroom_trace.log

# Filter for tool calls only
grep "TOOL:" output/warroom_trace.log

# Filter for a specific agent
grep "Data Analyst" output/warroom_trace.log
```

## Mock Data

The system uses realistic mock data that tells an ambiguous launch story:

- **Metrics** (`data/metrics.json`): 10-day time series with 10 metrics (6 pre-launch + 4 post-launch)
- **User Feedback** (`data/user_feedback.json`): 35 entries with mixed sentiment
- **Release Notes** (`data/release_notes.md`): Feature description and known issues

### Scenario
PurpleMerit launched "Smart Workflow Builder" at 30% rollout. Growth metrics (signups, DAU) are up, but quality metrics (crash rate, latency, retention) are degraded — creating a genuine decision dilemma.

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_API_KEY` | Yes | Google AI API key for Gemini 2.5 Flash |

## Technology Stack

- **Python 3.12** — Programming language
- **CrewAI** — Multi-agent orchestration framework
- **Google Gemini 2.5 Flash** — LLM for agent reasoning
- **Pydantic v2** — Structured output validation
