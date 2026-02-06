"""
Human-in-the-Loop Decision Agent
Makes approvals intelligent by learning when to ask, who to ask,
and how much context to show.
This is the difference between annoying and usable AI.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Callable
from datetime import datetime, timedelta
from enum import Enum


class DecisionType(Enum):
    FINANCIAL = "financial"
    STRATEGIC = "strategic"
    OPERATIONAL = "operational"
    SECURITY = "security"
    COMPLIANCE = "compliance"


class UrgencyLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ApprovalStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ESCALATED = "escalated"
    AUTO_APPROVED = "auto_approved"


@dataclass
class Approver:
    """Represents a person who can approve decisions"""
    name: str
    email: str
    role: str
    expertise_areas: List[str]
    approval_authority: Dict[DecisionType, float]  # Max $ amount or importance score
    availability_hours: List[int] = field(default_factory=lambda: list(range(9, 17)))  # 9am-5pm
    response_time_avg: timedelta = field(default_factory=lambda: timedelta(hours=2))


@dataclass
class Decision:
    """Represents a decision requiring approval"""
    id: str
    decision_type: DecisionType
    title: str
    description: str
    context: Dict[str, Any]
    urgency: UrgencyLevel
    financial_impact: float = 0.0
    risk_score: float = 0.0  # 0.0 to 1.0
    created_at: datetime = field(default_factory=datetime.now)
    required_approvers: List[str] = field(default_factory=list)
    approvals: Dict[str, ApprovalStatus] = field(default_factory=dict)
    final_status: ApprovalStatus = ApprovalStatus.PENDING
    auto_approved: bool = False


@dataclass
class ApprovalHistory:
    """Historical approval for learning"""
    decision: Decision
    approver: str
    status: ApprovalStatus
    response_time: timedelta
    context_viewed: bool
    feedback: Optional[str] = None


class HumanInLoopAgent:
    """
    Intelligent approval system that learns when to ask, who to ask,
    and how much context to provide.
    """
    
    def __init__(self):
        self.approvers: Dict[str, Approver] = {}
        self.decisions: Dict[str, Decision] = {}
        self.approval_history: List[ApprovalHistory] = []
        self.auto_approval_rules: List[Callable] = []
        self.escalation_rules: List[Callable] = []
        
    def register_approver(self, approver: Approver):
        """Register an approver"""
        self.approvers[approver.email] = approver
        
    def add_auto_approval_rule(self, rule: Callable[[Decision], bool]):
        """Add a rule for automatic approval"""
        self.auto_approval_rules.append(rule)
        
    def add_escalation_rule(self, rule: Callable[[Decision], Optional[str]]):
        """Add a rule for escalation (returns approver email or None)"""
        self.escalation_rules.append(rule)
    
    def request_approval(self, decision: Decision) -> Decision:
        """
        Request approval for a decision.
        Intelligently determines if auto-approval is possible,
        who should approve, and what context to show.
        """
        # Check auto-approval rules
        if self._can_auto_approve(decision):
            decision.auto_approved = True
            decision.final_status = ApprovalStatus.AUTO_APPROVED
            self.decisions[decision.id] = decision
            return decision
        
        # Select appropriate approvers
        approvers = self._select_approvers(decision)
        decision.required_approvers = [a.email for a in approvers]
        
        # Initialize approval statuses
        for approver in approvers:
            decision.approvals[approver.email] = ApprovalStatus.PENDING
        
        # Check if escalation needed
        escalated_to = self._check_escalation(decision)
        if escalated_to:
            decision.required_approvers.append(escalated_to)
            decision.approvals[escalated_to] = ApprovalStatus.PENDING
        
        self.decisions[decision.id] = decision
        
        # Prepare context for each approver
        for approver in approvers:
            context = self._prepare_context_for_approver(decision, approver)
            self._notify_approver(approver, decision, context)
        
        return decision
    
    def _can_auto_approve(self, decision: Decision) -> bool:
        """Determine if decision can be auto-approved"""
        for rule in self.auto_approval_rules:
            try:
                if rule(decision):
                    return True
            except Exception:
                pass
        return False
    
    def _select_approvers(self, decision: Decision) -> List[Approver]:
        """
        Intelligently select who should approve based on:
        - Decision type and expertise
        - Financial authority
        - Historical performance
        - Current availability
        """
        candidates = []
        
        for approver in self.approvers.values():
            # Check expertise match
            expertise_match = any(
                area in approver.expertise_areas
                for area in [decision.decision_type.value]
            )
            
            # Check financial authority
            has_authority = (
                decision.financial_impact <= 
                approver.approval_authority.get(decision.decision_type, 0)
            )
            
            # Check availability (simplified - just check if current hour is in their hours)
            current_hour = datetime.now().hour
            is_available = current_hour in approver.availability_hours
            
            if expertise_match and has_authority:
                # Score the approver
                score = 0.0
                score += 10 if is_available else 0
                score += 5 if expertise_match else 0
                score += self._get_historical_performance_score(approver, decision.decision_type)
                
                candidates.append((score, approver))
        
        # Sort by score and select top candidates
        candidates.sort(key=lambda x: x[0], reverse=True)
        
        # For high urgency, select just one best approver
        # For lower urgency, might select multiple
        if decision.urgency == UrgencyLevel.CRITICAL:
            return [candidates[0][1]] if candidates else []
        else:
            return [c[1] for c in candidates[:2]]
    
    def _get_historical_performance_score(
        self,
        approver: Approver,
        decision_type: DecisionType
    ) -> float:
        """Calculate approver's historical performance score"""
        relevant_history = [
            h for h in self.approval_history
            if h.approver == approver.email and h.decision.decision_type == decision_type
        ]
        
        if not relevant_history:
            return 0.0
        
        # Factors: response time, approval rate
        avg_response = sum(
            h.response_time.total_seconds() for h in relevant_history
        ) / len(relevant_history)
        
        approval_rate = sum(
            1 for h in relevant_history if h.status == ApprovalStatus.APPROVED
        ) / len(relevant_history)
        
        # Faster response and reasonable approval rate get higher scores
        time_score = max(0, 5 - (avg_response / 3600))  # Penalize if >5 hours
        approval_score = 2 if 0.3 < approval_rate < 0.9 else 0
        
        return time_score + approval_score
    
    def _check_escalation(self, decision: Decision) -> Optional[str]:
        """Check if decision needs escalation"""
        for rule in self.escalation_rules:
            try:
                escalated_to = rule(decision)
                if escalated_to:
                    return escalated_to
            except Exception:
                pass
        return None
    
    def _prepare_context_for_approver(
        self,
        decision: Decision,
        approver: Approver
    ) -> Dict[str, Any]:
        """
        Prepare appropriate context based on:
        - Approver's role and expertise
        - Decision urgency
        - Historical preferences
        """
        # Learn from history what level of detail this approver prefers
        detail_level = self._get_preferred_detail_level(approver)
        
        context = {
            "decision_id": decision.id,
            "title": decision.title,
            "urgency": decision.urgency.value
        }
        
        if detail_level >= 1:
            # Basic context
            context.update({
                "description": decision.description,
                "decision_type": decision.decision_type.value,
                "financial_impact": decision.financial_impact
            })
        
        if detail_level >= 2:
            # Detailed context
            context.update({
                "risk_score": decision.risk_score,
                "full_context": decision.context
            })
        
        if decision.urgency in [UrgencyLevel.HIGH, UrgencyLevel.CRITICAL]:
            # Always include critical info for urgent decisions
            context["urgency_note"] = "This decision requires immediate attention"
            context.update(decision.context)
        
        return context
    
    def _get_preferred_detail_level(self, approver: Approver) -> int:
        """Learn preferred detail level from history (0=minimal, 1=basic, 2=detailed)"""
        relevant_history = [
            h for h in self.approval_history
            if h.approver == approver.email
        ]
        
        if not relevant_history:
            return 1  # Default to basic
        
        # If they usually view context, they prefer detail
        context_view_rate = sum(
            1 for h in relevant_history if h.context_viewed
        ) / len(relevant_history)
        
        if context_view_rate > 0.7:
            return 2
        elif context_view_rate > 0.3:
            return 1
        else:
            return 0
    
    def _notify_approver(
        self,
        approver: Approver,
        decision: Decision,
        context: Dict[str, Any]
    ):
        """Notify approver (in real system, would send email/notification)"""
        print(f"\n📧 Notification to {approver.name} ({approver.email})")
        print(f"   Decision: {context['title']}")
        print(f"   Urgency: {context['urgency']}")
        if 'description' in context:
            print(f"   Description: {context['description']}")
        if 'financial_impact' in context:
            print(f"   Financial Impact: ${context['financial_impact']:,.2f}")
    
    def record_approval(
        self,
        decision_id: str,
        approver_email: str,
        status: ApprovalStatus,
        context_viewed: bool = False,
        feedback: Optional[str] = None
    ):
        """Record an approval decision"""
        if decision_id not in self.decisions:
            raise ValueError(f"Decision '{decision_id}' not found")
        
        decision = self.decisions[decision_id]
        
        if approver_email not in decision.approvals:
            raise ValueError(f"Approver '{approver_email}' not assigned to this decision")
        
        # Update decision
        decision.approvals[approver_email] = status
        
        # Record in history
        response_time = datetime.now() - decision.created_at
        history = ApprovalHistory(
            decision=decision,
            approver=approver_email,
            status=status,
            response_time=response_time,
            context_viewed=context_viewed,
            feedback=feedback
        )
        self.approval_history.append(history)
        
        # Check if decision is fully resolved
        self._update_decision_status(decision)
        
        return decision
    
    def _update_decision_status(self, decision: Decision):
        """Update final status based on all approvals"""
        if all(status == ApprovalStatus.APPROVED for status in decision.approvals.values()):
            decision.final_status = ApprovalStatus.APPROVED
        elif any(status == ApprovalStatus.REJECTED for status in decision.approvals.values()):
            decision.final_status = ApprovalStatus.REJECTED
        elif all(status != ApprovalStatus.PENDING for status in decision.approvals.values()):
            # All responded but mixed results
            decision.final_status = ApprovalStatus.ESCALATED
        else:
            decision.final_status = ApprovalStatus.PENDING
    
    def get_pending_decisions(self, approver_email: str) -> List[Decision]:
        """Get all pending decisions for an approver"""
        return [
            d for d in self.decisions.values()
            if approver_email in d.approvals and 
            d.approvals[approver_email] == ApprovalStatus.PENDING
        ]
    
    def get_decision_status(self, decision_id: str) -> Dict[str, Any]:
        """Get status of a decision"""
        if decision_id not in self.decisions:
            raise ValueError(f"Decision '{decision_id}' not found")
        
        decision = self.decisions[decision_id]
        
        return {
            "id": decision.id,
            "title": decision.title,
            "type": decision.decision_type.value,
            "urgency": decision.urgency.value,
            "final_status": decision.final_status.value,
            "auto_approved": decision.auto_approved,
            "created_at": decision.created_at,
            "approvals": {
                email: status.value
                for email, status in decision.approvals.items()
            },
            "financial_impact": decision.financial_impact,
            "risk_score": decision.risk_score
        }
    
    def get_analytics_report(self) -> str:
        """Generate analytics report on approval patterns"""
        report = "\nHuman-in-the-Loop Analytics Report\n"
        report += "="*60 + "\n\n"
        
        if not self.approval_history:
            report += "No approval history available.\n"
            return report
        
        # Overall statistics
        total_decisions = len(self.decisions)
        auto_approved = sum(1 for d in self.decisions.values() if d.auto_approved)
        manual_approved = sum(
            1 for d in self.decisions.values() 
            if d.final_status == ApprovalStatus.APPROVED and not d.auto_approved
        )
        rejected = sum(1 for d in self.decisions.values() if d.final_status == ApprovalStatus.REJECTED)
        
        report += f"Decision Statistics:\n"
        report += f"  Total Decisions: {total_decisions}\n"
        report += f"  Auto-Approved: {auto_approved} ({auto_approved/max(total_decisions,1)*100:.1f}%)\n"
        report += f"  Manually Approved: {manual_approved}\n"
        report += f"  Rejected: {rejected}\n\n"
        
        # Approver performance
        approver_stats = {}
        for history in self.approval_history:
            email = history.approver
            if email not in approver_stats:
                approver_stats[email] = {
                    "total": 0,
                    "approved": 0,
                    "rejected": 0,
                    "response_times": []
                }
            
            approver_stats[email]["total"] += 1
            approver_stats[email]["response_times"].append(history.response_time.total_seconds())
            
            if history.status == ApprovalStatus.APPROVED:
                approver_stats[email]["approved"] += 1
            elif history.status == ApprovalStatus.REJECTED:
                approver_stats[email]["rejected"] += 1
        
        report += "Approver Performance:\n"
        report += "-" * 60 + "\n"
        
        for email, stats in approver_stats.items():
            approver = self.approvers.get(email)
            name = approver.name if approver else email
            
            avg_response = sum(stats["response_times"]) / len(stats["response_times"])
            approval_rate = stats["approved"] / stats["total"] * 100
            
            report += f"\n{name}:\n"
            report += f"  Decisions: {stats['total']}\n"
            report += f"  Approval Rate: {approval_rate:.1f}%\n"
            report += f"  Avg Response Time: {timedelta(seconds=avg_response)}\n"
        
        return report
    
    def learn_and_improve(self):
        """
        Analyze approval history to improve future decisions.
        This method would update auto-approval rules and approver selection.
        """
        if len(self.approval_history) < 10:
            return "Not enough data to learn from yet."
        
        insights = []
        
        # Learn patterns for auto-approval
        auto_approved_decisions = [
            d for d in self.decisions.values() if d.auto_approved
        ]
        
        if auto_approved_decisions:
            avg_financial = sum(d.financial_impact for d in auto_approved_decisions) / len(auto_approved_decisions)
            insights.append(
                f"Auto-approval threshold could be set at ${avg_financial:,.2f}"
            )
        
        # Learn approver preferences
        for email, approver in self.approvers.items():
            relevant_history = [h for h in self.approval_history if h.approver == email]
            
            if relevant_history:
                context_view_rate = sum(1 for h in relevant_history if h.context_viewed) / len(relevant_history)
                
                if context_view_rate > 0.8:
                    insights.append(
                        f"{approver.name} prefers detailed context (views {context_view_rate*100:.0f}% of time)"
                    )
                elif context_view_rate < 0.2:
                    insights.append(
                        f"{approver.name} prefers minimal context (views only {context_view_rate*100:.0f}% of time)"
                    )
        
        return insights


# Example auto-approval rules

def low_risk_auto_approve(decision: Decision) -> bool:
    """Auto-approve low-risk, low-cost decisions"""
    return (
        decision.financial_impact < 1000 and
        decision.risk_score < 0.3 and
        decision.urgency != UrgencyLevel.CRITICAL
    )


def routine_operational_auto_approve(decision: Decision) -> bool:
    """Auto-approve routine operational decisions"""
    return (
        decision.decision_type == DecisionType.OPERATIONAL and
        decision.financial_impact < 5000 and
        decision.risk_score < 0.5
    )


# Example escalation rules

def high_value_escalation(decision: Decision) -> Optional[str]:
    """Escalate high-value decisions to senior management"""
    if decision.financial_impact > 100000:
        return "ceo@company.com"
    return None


def high_risk_escalation(decision: Decision) -> Optional[str]:
    """Escalate high-risk decisions"""
    if decision.risk_score > 0.8:
        return "risk-manager@company.com"
    return None


# Example usage
if __name__ == "__main__":
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
    
    agent.register_approver(Approver(
        name="Bob Director",
        email="bob@company.com",
        role="Director of Operations",
        expertise_areas=["strategic", "operational"],
        approval_authority={
            DecisionType.STRATEGIC: 100000,
            DecisionType.OPERATIONAL: 75000
        }
    ))
    
    # Add rules
    agent.add_auto_approval_rule(low_risk_auto_approve)
    agent.add_auto_approval_rule(routine_operational_auto_approve)
    agent.add_escalation_rule(high_value_escalation)
    agent.add_escalation_rule(high_risk_escalation)
    
    # Request approval for a decision
    decision = Decision(
        id="DEC-001",
        decision_type=DecisionType.OPERATIONAL,
        title="Upgrade server infrastructure",
        description="Upgrade servers to handle increased traffic",
        context={
            "current_capacity": "1000 req/s",
            "target_capacity": "5000 req/s",
            "downtime_required": "4 hours"
        },
        urgency=UrgencyLevel.MEDIUM,
        financial_impact=35000,
        risk_score=0.4
    )
    
    result = agent.request_approval(decision)
    
    print(f"\nDecision Status: {result.final_status.value}")
    print(f"Required Approvers: {result.required_approvers}")
    
    # Simulate approval
    if not result.auto_approved and result.required_approvers:
        agent.record_approval(
            decision_id="DEC-001",
            approver_email=result.required_approvers[0],
            status=ApprovalStatus.APPROVED,
            context_viewed=True,
            feedback="Looks good, approved"
        )
    
    # Get status
    status = agent.get_decision_status("DEC-001")
    print(f"\nFinal Status: {status['final_status']}")
    
    print(agent.get_analytics_report())
