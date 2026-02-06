"""
Integrated Example: Complete Planning, Reality, and Execution System
Demonstrates all four agents working together.
"""

from datetime import datetime, timedelta
import random

# Import all agents
from constraint_reasoning_agent import (
    ConstraintReasoningAgent, Constraint, Plan,
    ConstraintType, ConstraintSeverity,
    validate_time_constraint, validate_budget_constraint,
    validate_permissions_constraint, validate_regulations_constraint
)

from strategic_scenario_simulator import (
    StrategicScenarioSimulator, Action, SecondOrderEffect
)

from tool_reliability_agent import (
    ToolReliabilityAgent, Tool, ToolType, DriftDetection
)

from human_in_loop_agent import (
    HumanInLoopAgent, Approver, Decision,
    DecisionType, UrgencyLevel, ApprovalStatus,
    low_risk_auto_approve, high_value_escalation
)


class IntegratedPlanningSystem:
    """
    Complete planning system integrating all four agents.
    """
    
    def __init__(self):
        # Initialize all agents
        self.constraint_agent = ConstraintReasoningAgent()
        self.scenario_simulator = StrategicScenarioSimulator(risk_tolerance=0.6)
        self.reliability_agent = ToolReliabilityAgent(drift_threshold=0.2)
        self.approval_agent = HumanInLoopAgent()
        
        # Setup basic configuration
        self._setup_constraints()
        self._setup_tools()
        self._setup_approvers()
        
    def _setup_constraints(self):
        """Setup standard constraints"""
        # Time constraints
        self.constraint_agent.add_constraint(Constraint(
            type=ConstraintType.TIME,
            name="max_project_duration",
            description="Projects cannot exceed 6 months",
            severity=ConstraintSeverity.BLOCKING,
            validator=validate_time_constraint,
            metadata={'max_duration': timedelta(days=180)}
        ))
        
        # Budget constraints
        self.constraint_agent.add_constraint(Constraint(
            type=ConstraintType.BUDGET,
            name="department_budget",
            description="Department budget limit",
            severity=ConstraintSeverity.BLOCKING,
            validator=validate_budget_constraint,
            metadata={'max_budget': 250000}
        ))
        
        # Permission constraints
        self.constraint_agent.add_constraint(Constraint(
            type=ConstraintType.PERMISSIONS,
            name="required_access",
            description="Required system access",
            severity=ConstraintSeverity.BLOCKING,
            validator=validate_permissions_constraint,
            metadata={
                'available_permissions': [
                    'read_data', 'write_data', 'read_reports',
                    'write_reports', 'deploy_staging'
                ]
            }
        ))
        
        # Regulatory constraints
        self.constraint_agent.add_constraint(Constraint(
            type=ConstraintType.REGULATIONS,
            name="compliance_check",
            description="Regulatory compliance",
            severity=ConstraintSeverity.WARNING,
            validator=validate_regulations_constraint,
            metadata={
                'approved_domains': ['finance', 'healthcare', 'general']
            }
        ))
    
    def _setup_tools(self):
        """Setup tools to monitor"""
        # API tool
        self.reliability_agent.register_tool(Tool(
            name="data_api",
            tool_type=ToolType.API,
            endpoint="https://api.data.com/v1",
            expected_response_time=0.5,
            max_error_rate=0.02
        ))
        
        # Database tool
        self.reliability_agent.register_tool(Tool(
            name="analytics_db",
            tool_type=ToolType.DATABASE,
            endpoint="postgresql://localhost:5432/analytics",
            expected_response_time=0.1,
            max_error_rate=0.01
        ))
        
        # External service
        self.reliability_agent.register_tool(Tool(
            name="ml_service",
            tool_type=ToolType.EXTERNAL_SERVICE,
            endpoint="https://ml.service.com/predict",
            expected_response_time=2.0,
            max_error_rate=0.05
        ))
    
    def _setup_approvers(self):
        """Setup approvers"""
        # Engineering Manager
        self.approval_agent.register_approver(Approver(
            name="Alice Johnson",
            email="alice@company.com",
            role="Engineering Manager",
            expertise_areas=["operational", "financial"],
            approval_authority={
                DecisionType.OPERATIONAL: 50000,
                DecisionType.FINANCIAL: 25000
            }
        ))
        
        # Director
        self.approval_agent.register_approver(Approver(
            name="Bob Smith",
            email="bob@company.com",
            role="Director of Engineering",
            expertise_areas=["strategic", "operational", "financial"],
            approval_authority={
                DecisionType.STRATEGIC: 150000,
                DecisionType.OPERATIONAL: 100000,
                DecisionType.FINANCIAL: 75000
            }
        ))
        
        # CEO
        self.approval_agent.register_approver(Approver(
            name="Carol Williams",
            email="carol@company.com",
            role="CEO",
            expertise_areas=["strategic", "financial", "compliance"],
            approval_authority={
                DecisionType.STRATEGIC: float('inf'),
                DecisionType.FINANCIAL: float('inf'),
                DecisionType.COMPLIANCE: float('inf')
            }
        ))
        
        # Add approval rules
        self.approval_agent.add_auto_approval_rule(low_risk_auto_approve)
        self.approval_agent.add_escalation_rule(high_value_escalation)
    
    def execute_plan_workflow(
        self,
        plan_name: str,
        plan_description: str,
        actions: list,
        estimated_cost: float,
        required_permissions: list,
        regulatory_domains: list
    ):
        """
        Execute complete planning workflow:
        1. Validate constraints
        2. Simulate scenarios
        3. Check tool reliability
        4. Request approvals
        """
        print("\n" + "="*70)
        print(f"EXECUTING PLAN WORKFLOW: {plan_name}")
        print("="*70)
        
        # Calculate total duration
        total_duration = sum(
            (action.duration for action in actions),
            timedelta()
        )
        
        # Step 1: Constraint Validation
        print("\n[STEP 1] CONSTRAINT VALIDATION")
        print("-" * 70)
        
        plan = Plan(
            name=plan_name,
            description=plan_description,
            estimated_duration=total_duration,
            estimated_cost=estimated_cost,
            required_permissions=required_permissions,
            regulatory_domains=regulatory_domains
        )
        
        is_valid, violations = self.constraint_agent.validate_plan(plan)
        
        if violations:
            print("\nConstraint Violations Found:")
            for v in violations:
                print(f"  [{v.severity.value.upper()}] {v.constraint.name}")
                print(f"    {v.message}")
                if v.suggested_fix:
                    print(f"    → Fix: {v.suggested_fix}")
        else:
            print("✓ All constraints satisfied")
        
        if not is_valid:
            print("\n❌ Plan rejected due to blocking constraint violations")
            return False
        
        # Step 2: Scenario Simulation
        print("\n[STEP 2] SCENARIO SIMULATION")
        print("-" * 70)
        
        result = self.scenario_simulator.simulate_scenario(
            scenario_name=plan_name,
            actions=actions,
            num_simulations=500,
            monte_carlo=True
        )
        
        print(f"\nSimulation Results:")
        print(f"  Success Rate: {result.success_rate*100:.1f}%")
        print(f"  Expected Value: ${result.expected_value:,.2f}")
        print(f"  Risk-Adjusted Value: ${result.risk_adjusted_value:,.2f}")
        print(f"  Average Cost: ${result.average_cost:,.2f}")
        print(f"  Average Duration: {result.average_duration}")
        
        if result.recommended_path:
            print(f"\n  Recommended Path:")
            print(f"    Outcome: {result.recommended_path.outcome_type.value}")
            print(f"    Probability: {result.recommended_path.probability*100:.1f}%")
            print(f"    Risk Score: {result.recommended_path.risk_score:.2f}")
        
        # Step 3: Tool Reliability Check
        print("\n[STEP 3] TOOL RELIABILITY CHECK")
        print("-" * 70)
        
        # Simulate some tool metrics
        self._simulate_tool_metrics()
        
        print(self.reliability_agent.get_system_health_report())
        
        recommendations = self.reliability_agent.get_recommendations()
        if recommendations:
            print("\nTool Recommendations:")
            for rec in recommendations[:3]:
                print(f"  • {rec}")
        
        # Step 4: Approval Request
        print("\n[STEP 4] APPROVAL REQUEST")
        print("-" * 70)
        
        # Calculate risk score based on simulation
        risk_score = 1.0 - result.success_rate
        
        decision = Decision(
            id=f"DEC-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            decision_type=DecisionType.STRATEGIC,
            title=plan_name,
            description=plan_description,
            context={
                "total_actions": len(actions),
                "estimated_duration": str(total_duration),
                "success_rate": f"{result.success_rate*100:.1f}%",
                "simulation_runs": 500
            },
            urgency=UrgencyLevel.MEDIUM,
            financial_impact=estimated_cost,
            risk_score=risk_score
        )
        
        approval_result = self.approval_agent.request_approval(decision)
        
        print(f"\nApproval Status: {approval_result.final_status.value}")
        
        if approval_result.auto_approved:
            print("✓ Auto-approved based on low risk and cost")
        else:
            print(f"Required Approvers: {', '.join(approval_result.required_approvers)}")
        
        # Step 5: Summary
        print("\n[SUMMARY]")
        print("-" * 70)
        print(f"Plan: {plan_name}")
        print(f"Constraints: {'✓ PASSED' if is_valid else '✗ FAILED'}")
        print(f"Simulation: {result.success_rate*100:.1f}% success rate")
        print(f"Tools: Health check complete")
        print(f"Approval: {approval_result.final_status.value}")
        
        print("\n" + "="*70)
        
        return True
    
    def _simulate_tool_metrics(self):
        """Simulate tool metrics for demonstration"""
        # Simulate healthy data API
        for _ in range(50):
            self.reliability_agent.record_metric(
                "data_api",
                success=random.random() < 0.98,
                response_time=random.gauss(0.5, 0.1)
            )
        
        # Simulate healthy database
        for _ in range(50):
            self.reliability_agent.record_metric(
                "analytics_db",
                success=random.random() < 0.995,
                response_time=random.gauss(0.1, 0.02)
            )
        
        # Simulate slightly degraded ML service
        for _ in range(50):
            self.reliability_agent.record_metric(
                "ml_service",
                success=random.random() < 0.92,
                response_time=random.gauss(2.5, 0.5)
            )


# Example usage
if __name__ == "__main__":
    # Create integrated system
    system = IntegratedPlanningSystem()
    
    # Define a sample project
    project_actions = [
        Action(
            name="requirements_analysis",
            description="Analyze and document requirements",
            duration=timedelta(days=14),
            cost=12000,
            success_probability=0.9,
            dependencies=[]
        ),
        Action(
            name="system_design",
            description="Design system architecture",
            duration=timedelta(days=21),
            cost=18000,
            success_probability=0.85,
            dependencies=["requirements_analysis"]
        ),
        Action(
            name="implementation",
            description="Implement core features",
            duration=timedelta(days=60),
            cost=75000,
            success_probability=0.75,
            dependencies=["system_design"]
        ),
        Action(
            name="testing",
            description="Comprehensive testing",
            duration=timedelta(days=21),
            cost=15000,
            success_probability=0.8,
            dependencies=["implementation"]
        ),
        Action(
            name="deployment",
            description="Deploy to production",
            duration=timedelta(days=7),
            cost=10000,
            success_probability=0.85,
            dependencies=["testing"]
        )
    ]
    
    # Execute workflow
    system.execute_plan_workflow(
        plan_name="AI-Powered Analytics Platform",
        plan_description="Build and deploy an AI-powered analytics platform for customer insights",
        actions=project_actions,
        estimated_cost=130000,
        required_permissions=['read_data', 'write_data', 'deploy_staging'],
        regulatory_domains=['finance', 'general']
    )
