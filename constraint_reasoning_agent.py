"""
Constraint Reasoning Agent
This agent gates all plans by validating against real-world constraints.
Most planning agents fail because this is missing.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime, timedelta


class ConstraintType(Enum):
    TIME = "time"
    BUDGET = "budget"
    PERMISSIONS = "permissions"
    REGULATIONS = "regulations"


class ConstraintSeverity(Enum):
    BLOCKING = "blocking"  # Plan cannot proceed
    WARNING = "warning"    # Plan can proceed with risk
    INFO = "info"          # Informational only


@dataclass
class Constraint:
    """Represents a single constraint"""
    type: ConstraintType
    name: str
    description: str
    severity: ConstraintSeverity
    validator: callable
    metadata: Dict[str, Any] = None


@dataclass
class ConstraintViolation:
    """Represents a constraint violation"""
    constraint: Constraint
    severity: ConstraintSeverity
    message: str
    suggested_fix: Optional[str] = None


@dataclass
class Plan:
    """Represents a plan to be validated"""
    name: str
    description: str
    estimated_duration: timedelta
    estimated_cost: float
    required_permissions: List[str]
    regulatory_domains: List[str]
    metadata: Dict[str, Any] = None


class ConstraintReasoningAgent:
    """
    Gates all plans by validating against constraints.
    """
    
    def __init__(self):
        self.constraints: List[Constraint] = []
        self.violation_history: List[ConstraintViolation] = []
        
    def add_constraint(self, constraint: Constraint):
        """Add a constraint to the system"""
        self.constraints.append(constraint)
        
    def remove_constraint(self, constraint_name: str):
        """Remove a constraint by name"""
        self.constraints = [c for c in self.constraints if c.name != constraint_name]
        
    def validate_plan(self, plan: Plan) -> tuple[bool, List[ConstraintViolation]]:
        """
        Validate a plan against all constraints.
        Returns: (is_valid, violations)
        """
        violations = []
        
        for constraint in self.constraints:
            try:
                is_valid, message = constraint.validator(plan, constraint.metadata)
                
                if not is_valid:
                    violation = ConstraintViolation(
                        constraint=constraint,
                        severity=constraint.severity,
                        message=message,
                        suggested_fix=self._generate_fix_suggestion(constraint, plan)
                    )
                    violations.append(violation)
                    self.violation_history.append(violation)
                    
            except Exception as e:
                # Constraint validation failed - treat as blocking
                violation = ConstraintViolation(
                    constraint=constraint,
                    severity=ConstraintSeverity.BLOCKING,
                    message=f"Constraint validation error: {str(e)}"
                )
                violations.append(violation)
        
        # Plan is valid only if there are no BLOCKING violations
        blocking_violations = [v for v in violations if v.severity == ConstraintSeverity.BLOCKING]
        is_valid = len(blocking_violations) == 0
        
        return is_valid, violations
    
    def _generate_fix_suggestion(self, constraint: Constraint, plan: Plan) -> Optional[str]:
        """Generate a suggested fix for a constraint violation"""
        if constraint.type == ConstraintType.TIME:
            return f"Consider extending timeline or reducing scope"
        elif constraint.type == ConstraintType.BUDGET:
            return f"Reduce costs or request budget increase"
        elif constraint.type == ConstraintType.PERMISSIONS:
            return f"Request necessary permissions: {', '.join(plan.required_permissions)}"
        elif constraint.type == ConstraintType.REGULATIONS:
            return f"Ensure compliance with: {', '.join(plan.regulatory_domains)}"
        return None
    
    def get_violation_report(self) -> str:
        """Generate a report of all violations"""
        if not self.violation_history:
            return "No violations recorded."
        
        report = "Constraint Violation Report\n" + "="*50 + "\n\n"
        
        by_severity = {}
        for violation in self.violation_history:
            severity = violation.severity.value
            if severity not in by_severity:
                by_severity[severity] = []
            by_severity[severity].append(violation)
        
        for severity in [ConstraintSeverity.BLOCKING, ConstraintSeverity.WARNING, ConstraintSeverity.INFO]:
            if severity.value in by_severity:
                report += f"\n{severity.value.upper()} ({len(by_severity[severity.value])}):\n"
                for v in by_severity[severity.value]:
                    report += f"  - {v.constraint.name}: {v.message}\n"
                    if v.suggested_fix:
                        report += f"    Fix: {v.suggested_fix}\n"
        
        return report


# Example constraint validators

def validate_time_constraint(plan: Plan, metadata: Dict) -> tuple[bool, str]:
    """Validate time constraints"""
    max_duration = metadata.get('max_duration', timedelta(days=365))
    deadline = metadata.get('deadline')
    
    if plan.estimated_duration > max_duration:
        return False, f"Plan duration ({plan.estimated_duration}) exceeds maximum ({max_duration})"
    
    if deadline and datetime.now() + plan.estimated_duration > deadline:
        return False, f"Plan cannot complete before deadline ({deadline})"
    
    return True, "Time constraint satisfied"


def validate_budget_constraint(plan: Plan, metadata: Dict) -> tuple[bool, str]:
    """Validate budget constraints"""
    max_budget = metadata.get('max_budget', float('inf'))
    
    if plan.estimated_cost > max_budget:
        return False, f"Plan cost (${plan.estimated_cost:,.2f}) exceeds budget (${max_budget:,.2f})"
    
    return True, "Budget constraint satisfied"


def validate_permissions_constraint(plan: Plan, metadata: Dict) -> tuple[bool, str]:
    """Validate permission constraints"""
    available_permissions = set(metadata.get('available_permissions', []))
    required_permissions = set(plan.required_permissions)
    
    missing = required_permissions - available_permissions
    
    if missing:
        return False, f"Missing permissions: {', '.join(missing)}"
    
    return True, "Permission constraint satisfied"


def validate_regulations_constraint(plan: Plan, metadata: Dict) -> tuple[bool, str]:
    """Validate regulatory constraints"""
    approved_domains = set(metadata.get('approved_domains', []))
    required_domains = set(plan.regulatory_domains)
    
    unapproved = required_domains - approved_domains
    
    if unapproved:
        return False, f"Unapproved regulatory domains: {', '.join(unapproved)}"
    
    return True, "Regulatory constraint satisfied"


# Example usage
if __name__ == "__main__":
    # Initialize agent
    agent = ConstraintReasoningAgent()
    
    # Add constraints
    agent.add_constraint(Constraint(
        type=ConstraintType.TIME,
        name="max_project_duration",
        description="Projects cannot exceed 6 months",
        severity=ConstraintSeverity.BLOCKING,
        validator=validate_time_constraint,
        metadata={'max_duration': timedelta(days=180)}
    ))
    
    agent.add_constraint(Constraint(
        type=ConstraintType.BUDGET,
        name="department_budget",
        description="Department budget limit",
        severity=ConstraintSeverity.BLOCKING,
        validator=validate_budget_constraint,
        metadata={'max_budget': 100000}
    ))
    
    agent.add_constraint(Constraint(
        type=ConstraintType.PERMISSIONS,
        name="required_access",
        description="Required system access",
        severity=ConstraintSeverity.BLOCKING,
        validator=validate_permissions_constraint,
        metadata={'available_permissions': ['read_data', 'write_reports']}
    ))
    
    agent.add_constraint(Constraint(
        type=ConstraintType.REGULATIONS,
        name="compliance_check",
        description="Regulatory compliance",
        severity=ConstraintSeverity.WARNING,
        validator=validate_regulations_constraint,
        metadata={'approved_domains': ['finance', 'healthcare']}
    ))
    
    # Create a test plan
    test_plan = Plan(
        name="AI Integration Project",
        description="Integrate AI into existing systems",
        estimated_duration=timedelta(days=90),
        estimated_cost=75000,
        required_permissions=['read_data', 'write_reports', 'admin_access'],
        regulatory_domains=['finance', 'healthcare']
    )
    
    # Validate plan
    is_valid, violations = agent.validate_plan(test_plan)
    
    print(f"Plan: {test_plan.name}")
    print(f"Valid: {is_valid}\n")
    
    if violations:
        print("Violations:")
        for v in violations:
            print(f"  [{v.severity.value.upper()}] {v.constraint.name}: {v.message}")
            if v.suggested_fix:
                print(f"    → {v.suggested_fix}")
    
    print("\n" + agent.get_violation_report())
