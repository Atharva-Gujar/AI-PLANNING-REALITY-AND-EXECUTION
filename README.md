# PLANNING, REALITY, AND EXECUTION

A comprehensive AI agent framework for real-world operational planning with constraint validation, scenario simulation, tool monitoring, and intelligent human approvals.

## Overview

Most planning agents fail because they ignore reality. This project implements four critical agents that bridge the gap between planning and execution:

1. **Constraint Reasoning Agent** - Gates all plans against real-world constraints
2. **Strategic Scenario Simulator** - Makes planning non-naive through multi-path simulation
3. **Tool Reliability & Drift Agent** - Prevents silent system degradation
4. **Human-in-the-Loop Decision Agent** - Makes approvals intelligent and usable

## Why These Agents Matter

### 🚫 Constraint Reasoning Agent
**Most planning agents fail because this is missing.**

Without constraint validation, plans are fantasy. This agent validates every plan against:
- **Time constraints**: Deadlines, duration limits
- **Budget constraints**: Cost limits, resource availability
- **Permission constraints**: Access rights, authorization levels
- **Regulatory constraints**: Compliance requirements, legal boundaries

### 🎯 Strategic Scenario Simulator
**Now planning becomes non-naive.**

Simulates multiple paths through plans with:
- **Multi-path simulation**: Monte Carlo and deterministic path exploration
- **Second-order effects**: Cascading consequences of actions
- **Risk-weighted outcomes**: Probability-adjusted value calculation

### 🔧 Tool Reliability & Drift Agent
**This is mandatory before real-world ops.**

Monitors system health to prevent silent rot:
- **API failure rates**: Track success/error rates over time
- **Data drift**: Detect changes in data schemas and distributions
- **Scraper decay**: Monitor web scraping reliability
- **Performance degradation**: Alert on response time increases

### 👤 Human-in-the-Loop Decision Agent
**This is the difference between annoying and usable AI.**

Intelligent approval system that learns:
- **When to ask**: Auto-approval rules based on risk and history
- **Who to ask**: Select approvers by expertise, authority, and availability
- **How much context to show**: Adapt detail level to approver preferences

## Installation

```bash
# Clone or download the project
cd "PLANNING REALITY AND EXECUTION"

# No external dependencies required - uses Python standard library only
python --version  # Requires Python 3.7+
```

## Quick Start

### 1. Constraint Reasoning

```python
from constraint_reasoning_agent import (
    ConstraintReasoningAgent, Constraint, Plan,
    ConstraintType, ConstraintSeverity,
    validate_time_constraint, validate_budget_constraint
)
from datetime import timedelta

# Create agent
agent = ConstraintReasoningAgent()

# Add constraints
agent.add_constraint(Constraint(
    type=ConstraintType.BUDGET,
    name="project_budget",
    description="Maximum project budget",
    severity=ConstraintSeverity.BLOCKING,
    validator=validate_budget_constraint,
    metadata={'max_budget': 100000}
))

# Validate a plan
plan = Plan(
    name="AI Integration",
    description="Integrate AI into existing systems",
    estimated_duration=timedelta(days=90),
    estimated_cost=75000,
    required_permissions=['read_data', 'write_reports'],
    regulatory_domains=['finance']
)

is_valid, violations = agent.validate_plan(plan)
print(f"Plan valid: {is_valid}")
```

### 2. Scenario Simulation

```python
from strategic_scenario_simulator import (
    StrategicScenarioSimulator, Action
)
from datetime import timedelta

# Create simulator
simulator = StrategicScenarioSimulator(risk_tolerance=0.6)

# Define actions
actions = [
    Action(
        name="design",
        description="Design system",
        duration=timedelta(days=21),
        cost=15000,
        success_probability=0.85,
        dependencies=[]
    ),
    Action(
        name="implement",
        description="Build system",
        duration=timedelta(days=60),
        cost=50000,
        success_probability=0.75,
        dependencies=["design"]
    )
]

# Run simulation
result = simulator.simulate_scenario(
    scenario_name="Development Project",
    actions=actions,
    num_simulations=1000
)

print(simulator.get_simulation_report(result))
```

### 3. Tool Monitoring

```python
from tool_reliability_agent import (
    ToolReliabilityAgent, Tool, ToolType
)
from datetime import timedelta

# Create agent
agent = ToolReliabilityAgent(drift_threshold=0.2)

# Register tools
agent.register_tool(Tool(
    name="payment_api",
    tool_type=ToolType.API,
    endpoint="https://api.payment.com/v1",
    expected_response_time=0.5,
    max_error_rate=0.02
))

# Record metrics
agent.record_metric(
    "payment_api",
    success=True,
    response_time=0.45
)

# Get health report
print(agent.get_system_health_report())
```

### 4. Human Approvals

```python
from human_in_loop_agent import (
    HumanInLoopAgent, Approver, Decision,
    DecisionType, UrgencyLevel
)

# Create agent
agent = HumanInLoopAgent()

# Register approvers
agent.register_approver(Approver(
    name="Alice Manager",
    email="alice@company.com",
    role="Engineering Manager",
    expertise_areas=["operational", "financial"],
    approval_authority={
        DecisionType.OPERATIONAL: 50000,
        DecisionType.FINANCIAL: 25000
    }
))

# Request approval
decision = Decision(
    id="DEC-001",
    decision_type=DecisionType.OPERATIONAL,
    title="Upgrade infrastructure",
    description="Server upgrade for scalability",
    urgency=UrgencyLevel.MEDIUM,
    financial_impact=35000,
    risk_score=0.4
)

result = agent.request_approval(decision)
```

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Planning Layer                    │
│  ┌──────────────────────────────────────────────┐   │
│  │     Strategic Scenario Simulator              │   │
│  │  • Multi-path simulation                      │   │
│  │  • Second-order effects                       │   │
│  │  • Risk-weighted outcomes                     │   │
│  └──────────────────────────────────────────────┘   │
│                       ↓                              │
│  ┌──────────────────────────────────────────────┐   │
│  │     Constraint Reasoning Agent                │   │
│  │  • Time validation                            │   │
│  │  • Budget validation                          │   │
│  │  • Permission validation                      │   │
│  │  • Regulatory compliance                      │   │
│  └──────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│                  Execution Layer                    │
│  ┌──────────────────────────────────────────────┐   │
│  │   Human-in-the-Loop Decision Agent            │   │
│  │  • Intelligent approver selection             │   │
│  │  • Auto-approval rules                        │   │
│  │  • Context adaptation                         │   │
│  └──────────────────────────────────────────────┘   │
│                       ↓                              │
│  ┌──────────────────────────────────────────────┐   │
│  │     Tool Reliability & Drift Agent            │   │
│  │  • API health monitoring                      │   │
│  │  • Data drift detection                       │   │
│  │  • Performance tracking                       │   │
│  └──────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

## Features

### Constraint Reasoning Agent
- ✅ Multiple constraint types (time, budget, permissions, regulations)
- ✅ Configurable severity levels (blocking, warning, info)
- ✅ Suggested fixes for violations
- ✅ Violation history tracking
- ✅ Extensible validator system

### Strategic Scenario Simulator
- ✅ Monte Carlo simulation
- ✅ Deterministic path exploration
- ✅ Dependency management
- ✅ Second-order effect modeling
- ✅ Risk-adjusted value calculation
- ✅ Multiple outcome types
- ✅ Recommended path selection

### Tool Reliability & Drift Agent
- ✅ Multi-tool monitoring
- ✅ Performance drift detection
- ✅ Error rate tracking
- ✅ Health status classification
- ✅ Alert callbacks
- ✅ Historical metric retention
- ✅ Actionable recommendations

### Human-in-the-Loop Agent
- ✅ Auto-approval rules
- ✅ Intelligent approver selection
- ✅ Context adaptation
- ✅ Escalation rules
- ✅ Historical learning
- ✅ Analytics and reporting
- ✅ Response time tracking

## Use Cases

### Software Development Planning
- Validate project timelines and budgets
- Simulate development paths with different team compositions
- Monitor API and service health
- Get approval for architecture decisions

### Business Operations
- Validate operational plans against budget constraints
- Simulate market scenarios
- Monitor vendor API reliability
- Automate routine approvals

### Compliance & Security
- Enforce regulatory constraints
- Simulate security incident responses
- Monitor data access patterns
- Route security decisions to appropriate approvers

## Advanced Usage

### Custom Constraint Validators

```python
def validate_custom_constraint(plan: Plan, metadata: Dict) -> tuple[bool, str]:
    # Your custom validation logic
    if some_condition:
        return False, "Validation failed because..."
    return True, "Validation passed"

agent.add_constraint(Constraint(
    type=ConstraintType.CUSTOM,
    name="my_constraint",
    description="My custom constraint",
    severity=ConstraintSeverity.WARNING,
    validator=validate_custom_constraint,
    metadata={'custom_param': value}
))
```

### Custom Second-Order Effects

```python
def my_side_effect(action, executed_actions, all_actions):
    # Calculate cascading effects
    return SecondOrderEffect(
        source_action=action.name,
        effect_description="Custom effect",
        probability=0.7,
        impact_magnitude=-0.2,
        affected_actions=[...]
    )

action = Action(
    name="deploy",
    # ... other params ...
    side_effects=[my_side_effect]
)
```

### Alert Callbacks

```python
def alert_handler(tool: Tool, drift: DriftDetection):
    # Send to monitoring system
    print(f"ALERT: {tool.name} - {drift.description}")
    # Could send email, Slack message, etc.

agent.add_alert_callback(alert_handler)
```

## Best Practices

1. **Start with constraints**: Always validate plans before simulation
2. **Use multiple simulations**: Run 1000+ Monte Carlo simulations for statistical validity
3. **Monitor continuously**: Set up regular tool health checks
4. **Learn from history**: Let the approval agent build history for better decisions
5. **Combine agents**: Use all four agents together for robust planning

## File Structure

```
PLANNING REALITY AND EXECUTION/
├── README.md
├── constraint_reasoning_agent.py
├── strategic_scenario_simulator.py
├── tool_reliability_agent.py
├── human_in_loop_agent.py
├── integrated_example.py
└── requirements.txt
```

## Contributing

This is a reference implementation. Feel free to:
- Add new constraint types
- Implement new simulation strategies
- Add monitoring for additional tool types
- Enhance the learning algorithms

## License

MIT License - Use freely in your projects

## Support

For issues or questions, please review the example usage in each file's `__main__` section.

---

**Remember**: Without these agents, planning is just wishful thinking. With them, it becomes executable reality.
