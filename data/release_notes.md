# Release Notes: Smart Workflow Builder v1.0

## Release Date: April 3, 2026
## Rollout: Staged — 30% of active users

### Overview
The Smart Workflow Builder is a new drag-and-drop visual automation tool that allows users to create, manage, and execute multi-step workflows without writing code. Users can connect various service integrations (Slack, Email, CRM, APIs) through a visual canvas.

### Key Features
- **Visual Canvas Editor**: Drag-and-drop interface for building workflows
- **Pre-built Templates**: 15 starter templates (Lead Nurture, Onboarding, Support Escalation, etc.)
- **Conditional Branching**: If/else logic nodes for complex automation flows
- **API Integration Nodes**: Connect to 20+ third-party services
- **Scheduling**: Cron-based triggers and time-delay nodes
- **Real-time Preview**: Test workflows before activating them

### Known Issues
1. **Memory leak with complex workflows**: Workflows with more than 15 nodes may cause increased memory usage in the browser. The engineering team is investigating and a fix is expected within 1 week.

2. **Elevated API latency**: The workflow execution engine is causing higher-than-expected p95 latency across all API endpoints. Currently under investigation. Believed to be related to the new workflow state persistence layer.

3. **Crash on save (partially fixed)**: A crash occurred when saving workflows with certain node configurations. A hotfix was deployed on April 4 (v1.0.1) that reduced crash frequency by approximately 60%, but some edge cases remain.

4. **Slow initial load**: The workflow editor canvas takes 5-10 seconds to load on first access due to asset bundle size. Optimization planned for v1.1.

### Rollout Plan
- **Phase 1 (Current)**: 30% of users — collect feedback and monitor metrics
- **Phase 2 (Planned April 10)**: 60% of users — if Phase 1 metrics meet thresholds
- **Phase 3 (Planned April 17)**: 100% of users — full GA release

### Success Criteria for Phase 2 Expansion
- Crash rate < 0.5%
- API latency p95 < 250ms
- D1 retention within 5% of baseline
- Support ticket volume < 1.5x baseline
- Feature adoption completion rate > 40%
