"""
Strategic Scenario Simulator
Makes planning non-naive through multi-path simulation,
second-order effects analysis, and risk-weighted outcomes.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Callable
from enum import Enum
import random
from datetime import datetime, timedelta


class OutcomeType(Enum):
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILURE = "failure"
    CATASTROPHIC = "catastrophic"


class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Action:
    """Represents a single action in a plan"""
    name: str
    description: str
    duration: timedelta
    cost: float
    success_probability: float = 0.8
    dependencies: List[str] = field(default_factory=list)
    side_effects: List[Callable] = field(default_factory=list)


@dataclass
class SecondOrderEffect:
    """Represents cascading effects of an action"""
    source_action: str
    effect_description: str
    probability: float
    impact_magnitude: float  # -1.0 to 1.0
    affected_actions: List[str] = field(default_factory=list)


@dataclass
class SimulationPath:
    """Represents one possible execution path"""
    path_id: str
    actions_taken: List[Action]
    outcome_type: OutcomeType
    total_cost: float
    total_duration: timedelta
    probability: float
    second_order_effects: List[SecondOrderEffect] = field(default_factory=list)
    risk_score: float = 0.0


@dataclass
class ScenarioResult:
    """Results from simulating multiple scenarios"""
    scenario_name: str
    paths: List[SimulationPath]
    expected_value: float
    risk_adjusted_value: float
    success_rate: float
    average_cost: float
    average_duration: timedelta
    recommended_path: Optional[SimulationPath] = None


class StrategicScenarioSimulator:
    """
    Simulates multiple paths through a plan with second-order effects
    and risk-weighted outcomes.
    """
    
    def __init__(self, risk_tolerance: float = 0.5):
        self.risk_tolerance = risk_tolerance  # 0.0 (risk-averse) to 1.0 (risk-seeking)
        self.simulation_history: List[ScenarioResult] = []
        
    def simulate_scenario(
        self,
        scenario_name: str,
        actions: List[Action],
        num_simulations: int = 1000,
        monte_carlo: bool = True
    ) -> ScenarioResult:
        """
        Simulate multiple paths through a scenario.
        
        Args:
            scenario_name: Name of the scenario
            actions: List of possible actions
            num_simulations: Number of simulation runs
            monte_carlo: Use Monte Carlo simulation for probability
        """
        paths = []
        
        if monte_carlo:
            # Monte Carlo simulation - sample from probability distributions
            for i in range(num_simulations):
                path = self._run_monte_carlo_simulation(actions, i)
                paths.append(path)
        else:
            # Deterministic path exploration
            paths = self._explore_all_paths(actions)
        
        # Analyze results
        result = self._analyze_simulation_results(scenario_name, paths)
        self.simulation_history.append(result)
        
        return result
    
    def _run_monte_carlo_simulation(
        self,
        actions: List[Action],
        simulation_id: int
    ) -> SimulationPath:
        """Run a single Monte Carlo simulation"""
        executed_actions = []
        total_cost = 0.0
        total_duration = timedelta()
        second_order_effects = []
        
        # Topologically sort actions by dependencies
        sorted_actions = self._topological_sort(actions)
        
        for action in sorted_actions:
            # Check if dependencies succeeded
            dependencies_met = all(
                dep in [a.name for a in executed_actions]
                for dep in action.dependencies
            )
            
            if not dependencies_met:
                continue
            
            # Simulate action success/failure
            success = random.random() < action.success_probability
            
            if success:
                executed_actions.append(action)
                total_cost += action.cost
                total_duration += action.duration
                
                # Simulate second-order effects
                effects = self._simulate_second_order_effects(
                    action, executed_actions, sorted_actions
                )
                second_order_effects.extend(effects)
        
        # Determine outcome
        outcome_type = self._determine_outcome(executed_actions, actions)
        probability = self._calculate_path_probability(executed_actions)
        risk_score = self._calculate_risk_score(second_order_effects, total_cost)
        
        return SimulationPath(
            path_id=f"mc_{simulation_id}",
            actions_taken=executed_actions,
            outcome_type=outcome_type,
            total_cost=total_cost,
            total_duration=total_duration,
            probability=probability,
            second_order_effects=second_order_effects,
            risk_score=risk_score
        )
    
    def _explore_all_paths(self, actions: List[Action]) -> List[SimulationPath]:
        """Deterministically explore all possible paths (for small action sets)"""
        # This is a simplified version - full implementation would use graph traversal
        paths = []
        
        # For demonstration, create a few representative paths
        sorted_actions = self._topological_sort(actions)
        
        # Optimistic path - all succeed
        optimistic = self._create_deterministic_path(
            "optimistic",
            sorted_actions,
            success_rate=1.0
        )
        paths.append(optimistic)
        
        # Realistic path - expected success rates
        realistic = self._create_deterministic_path(
            "realistic",
            sorted_actions,
            success_rate=0.8
        )
        paths.append(realistic)
        
        # Pessimistic path - lower success rates
        pessimistic = self._create_deterministic_path(
            "pessimistic",
            sorted_actions,
            success_rate=0.5
        )
        paths.append(pessimistic)
        
        return paths
    
    def _create_deterministic_path(
        self,
        path_name: str,
        actions: List[Action],
        success_rate: float
    ) -> SimulationPath:
        """Create a deterministic path with given success rate"""
        executed_actions = []
        total_cost = 0.0
        total_duration = timedelta()
        
        for action in actions:
            if random.random() < success_rate:
                executed_actions.append(action)
                total_cost += action.cost
                total_duration += action.duration
        
        outcome_type = self._determine_outcome(executed_actions, actions)
        probability = success_rate ** len(executed_actions)
        
        return SimulationPath(
            path_id=path_name,
            actions_taken=executed_actions,
            outcome_type=outcome_type,
            total_cost=total_cost,
            total_duration=total_duration,
            probability=probability,
            second_order_effects=[],
            risk_score=1.0 - success_rate
        )
    
    def _simulate_second_order_effects(
        self,
        action: Action,
        executed_actions: List[Action],
        all_actions: List[Action]
    ) -> List[SecondOrderEffect]:
        """Simulate cascading effects of an action"""
        effects = []
        
        # Execute custom side effects if defined
        for side_effect_fn in action.side_effects:
            try:
                effect = side_effect_fn(action, executed_actions, all_actions)
                if effect:
                    effects.append(effect)
            except Exception:
                pass
        
        # Generic second-order effects based on action characteristics
        # Example: High-cost actions might reduce budget for future actions
        if action.cost > 10000:
            effects.append(SecondOrderEffect(
                source_action=action.name,
                effect_description="High cost reduces available budget",
                probability=0.8,
                impact_magnitude=-0.3,
                affected_actions=[a.name for a in all_actions if a not in executed_actions]
            ))
        
        return effects
    
    def _topological_sort(self, actions: List[Action]) -> List[Action]:
        """Sort actions by dependencies"""
        # Simple topological sort
        sorted_actions = []
        remaining = actions.copy()
        
        while remaining:
            # Find actions with no unmet dependencies
            ready = [
                a for a in remaining
                if all(dep in [s.name for s in sorted_actions] for dep in a.dependencies)
            ]
            
            if not ready:
                # Circular dependency or isolated actions
                ready = remaining
            
            sorted_actions.extend(ready)
            for action in ready:
                remaining.remove(action)
        
        return sorted_actions
    
    def _determine_outcome(
        self,
        executed_actions: List[Action],
        all_actions: List[Action]
    ) -> OutcomeType:
        """Determine the outcome type based on executed actions"""
        completion_rate = len(executed_actions) / max(len(all_actions), 1)
        
        if completion_rate >= 0.9:
            return OutcomeType.SUCCESS
        elif completion_rate >= 0.6:
            return OutcomeType.PARTIAL_SUCCESS
        elif completion_rate >= 0.3:
            return OutcomeType.FAILURE
        else:
            return OutcomeType.CATASTROPHIC
    
    def _calculate_path_probability(self, actions: List[Action]) -> float:
        """Calculate the probability of a specific path"""
        if not actions:
            return 0.0
        
        probability = 1.0
        for action in actions:
            probability *= action.success_probability
        
        return probability
    
    def _calculate_risk_score(
        self,
        second_order_effects: List[SecondOrderEffect],
        total_cost: float
    ) -> float:
        """Calculate overall risk score for a path"""
        if not second_order_effects:
            return 0.0
        
        risk = 0.0
        for effect in second_order_effects:
            # Negative impacts increase risk
            if effect.impact_magnitude < 0:
                risk += abs(effect.impact_magnitude) * effect.probability
        
        # Normalize by cost (higher cost = higher risk)
        risk_score = risk * (1 + total_cost / 100000)
        
        return min(risk_score, 1.0)
    
    def _analyze_simulation_results(
        self,
        scenario_name: str,
        paths: List[SimulationPath]
    ) -> ScenarioResult:
        """Analyze simulation results and recommend best path"""
        if not paths:
            return ScenarioResult(
                scenario_name=scenario_name,
                paths=[],
                expected_value=0.0,
                risk_adjusted_value=0.0,
                success_rate=0.0,
                average_cost=0.0,
                average_duration=timedelta()
            )
        
        # Calculate metrics
        success_paths = [p for p in paths if p.outcome_type in [OutcomeType.SUCCESS, OutcomeType.PARTIAL_SUCCESS]]
        success_rate = len(success_paths) / len(paths)
        
        average_cost = sum(p.total_cost for p in paths) / len(paths)
        average_duration = sum((p.total_duration.total_seconds() for p in paths), 0) / len(paths)
        average_duration = timedelta(seconds=average_duration)
        
        # Calculate expected value (probability-weighted outcomes)
        expected_value = 0.0
        for path in paths:
            value = self._calculate_path_value(path)
            expected_value += value * path.probability
        
        # Calculate risk-adjusted value
        risk_adjusted_value = 0.0
        for path in paths:
            value = self._calculate_path_value(path)
            risk_adjustment = 1.0 - (path.risk_score * (1.0 - self.risk_tolerance))
            risk_adjusted_value += value * path.probability * risk_adjustment
        
        # Find recommended path
        recommended_path = self._select_recommended_path(paths)
        
        return ScenarioResult(
            scenario_name=scenario_name,
            paths=paths,
            expected_value=expected_value,
            risk_adjusted_value=risk_adjusted_value,
            success_rate=success_rate,
            average_cost=average_cost,
            average_duration=average_duration,
            recommended_path=recommended_path
        )
    
    def _calculate_path_value(self, path: SimulationPath) -> float:
        """Calculate the value of a path (benefit - cost)"""
        # Simple value calculation - can be customized
        outcome_values = {
            OutcomeType.SUCCESS: 100000,
            OutcomeType.PARTIAL_SUCCESS: 50000,
            OutcomeType.FAILURE: -10000,
            OutcomeType.CATASTROPHIC: -50000
        }
        
        benefit = outcome_values.get(path.outcome_type, 0)
        value = benefit - path.total_cost
        
        return value
    
    def _select_recommended_path(self, paths: List[SimulationPath]) -> Optional[SimulationPath]:
        """Select the best path based on risk-adjusted value"""
        if not paths:
            return None
        
        scored_paths = []
        for path in paths:
            value = self._calculate_path_value(path)
            risk_adjustment = 1.0 - (path.risk_score * (1.0 - self.risk_tolerance))
            score = value * path.probability * risk_adjustment
            scored_paths.append((score, path))
        
        # Return path with highest score
        scored_paths.sort(key=lambda x: x[0], reverse=True)
        return scored_paths[0][1] if scored_paths else None
    
    def get_simulation_report(self, result: ScenarioResult) -> str:
        """Generate a detailed simulation report"""
        report = f"\nStrategic Scenario Simulation Report\n"
        report += f"{'='*60}\n\n"
        report += f"Scenario: {result.scenario_name}\n"
        report += f"Simulations Run: {len(result.paths)}\n\n"
        
        report += f"Key Metrics:\n"
        report += f"  Success Rate: {result.success_rate*100:.1f}%\n"
        report += f"  Expected Value: ${result.expected_value:,.2f}\n"
        report += f"  Risk-Adjusted Value: ${result.risk_adjusted_value:,.2f}\n"
        report += f"  Average Cost: ${result.average_cost:,.2f}\n"
        report += f"  Average Duration: {result.average_duration}\n\n"
        
        if result.recommended_path:
            report += f"Recommended Path: {result.recommended_path.path_id}\n"
            report += f"  Outcome: {result.recommended_path.outcome_type.value}\n"
            report += f"  Probability: {result.recommended_path.probability*100:.1f}%\n"
            report += f"  Cost: ${result.recommended_path.total_cost:,.2f}\n"
            report += f"  Duration: {result.recommended_path.total_duration}\n"
            report += f"  Risk Score: {result.recommended_path.risk_score:.2f}\n"
            report += f"  Actions: {len(result.recommended_path.actions_taken)}\n"
            
            if result.recommended_path.second_order_effects:
                report += f"\n  Second-Order Effects:\n"
                for effect in result.recommended_path.second_order_effects[:5]:
                    report += f"    - {effect.effect_description} "
                    report += f"(p={effect.probability:.2f}, impact={effect.impact_magnitude:+.2f})\n"
        
        # Outcome distribution
        report += f"\nOutcome Distribution:\n"
        outcome_counts = {}
        for path in result.paths:
            outcome_counts[path.outcome_type] = outcome_counts.get(path.outcome_type, 0) + 1
        
        for outcome_type in OutcomeType:
            count = outcome_counts.get(outcome_type, 0)
            percentage = (count / len(result.paths)) * 100 if result.paths else 0
            report += f"  {outcome_type.value}: {count} ({percentage:.1f}%)\n"
        
        return report


# Example usage
if __name__ == "__main__":
    # Create simulator
    simulator = StrategicScenarioSimulator(risk_tolerance=0.6)
    
    # Define actions for a project
    actions = [
        Action(
            name="requirements_gathering",
            description="Gather and document requirements",
            duration=timedelta(days=14),
            cost=10000,
            success_probability=0.9,
            dependencies=[]
        ),
        Action(
            name="design_phase",
            description="Create system design",
            duration=timedelta(days=21),
            cost=15000,
            success_probability=0.85,
            dependencies=["requirements_gathering"]
        ),
        Action(
            name="implementation",
            description="Implement the system",
            duration=timedelta(days=60),
            cost=50000,
            success_probability=0.75,
            dependencies=["design_phase"]
        ),
        Action(
            name="testing",
            description="Test the system",
            duration=timedelta(days=21),
            cost=12000,
            success_probability=0.8,
            dependencies=["implementation"]
        ),
        Action(
            name="deployment",
            description="Deploy to production",
            duration=timedelta(days=7),
            cost=8000,
            success_probability=0.85,
            dependencies=["testing"]
        )
    ]
    
    # Run simulation
    result = simulator.simulate_scenario(
        scenario_name="Software Development Project",
        actions=actions,
        num_simulations=1000,
        monte_carlo=True
    )
    
    # Print report
    print(simulator.get_simulation_report(result))
