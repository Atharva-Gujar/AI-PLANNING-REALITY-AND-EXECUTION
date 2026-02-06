#!/usr/bin/env python3
"""
Quick Start Guide
Run this script to see all agents in action!
"""

print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║         PLANNING, REALITY, AND EXECUTION                         ║
║         Quick Start Guide                                        ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝

This project contains four critical agents for real-world AI planning:

1. 🚫 Constraint Reasoning Agent
   - Validates plans against time, budget, permissions, regulations
   - Location: constraint_reasoning_agent.py

2. 🎯 Strategic Scenario Simulator  
   - Multi-path simulation with second-order effects
   - Location: strategic_scenario_simulator.py

3. 🔧 Tool Reliability & Drift Agent
   - Monitors API failures, data drift, system health
   - Location: tool_reliability_agent.py

4. 👤 Human-in-the-Loop Decision Agent
   - Intelligent approvals that learn preferences
   - Location: human_in_loop_agent.py

════════════════════════════════════════════════════════════════════

GETTING STARTED:

Option 1 - Run Complete Example:
    python integrated_example.py

Option 2 - Run Individual Agents:
    python constraint_reasoning_agent.py
    python strategic_scenario_simulator.py
    python tool_reliability_agent.py
    python human_in_loop_agent.py

Option 3 - Use in Your Code:
    from constraint_reasoning_agent import ConstraintReasoningAgent
    from strategic_scenario_simulator import StrategicScenarioSimulator
    from tool_reliability_agent import ToolReliabilityAgent
    from human_in_loop_agent import HumanInLoopAgent

════════════════════════════════════════════════════════════════════

DOCUMENTATION:
    See README.md for detailed documentation and examples

REQUIREMENTS:
    Python 3.7+ (no external dependencies required!)

════════════════════════════════════════════════════════════════════
""")

import sys

def main():
    print("\nWhat would you like to do?\n")
    print("1. Run integrated example (all 4 agents)")
    print("2. Run Constraint Reasoning Agent demo")
    print("3. Run Scenario Simulator demo")
    print("4. Run Tool Reliability Agent demo")
    print("5. Run Human-in-Loop Agent demo")
    print("6. Exit")
    
    choice = input("\nEnter choice (1-6): ").strip()
    
    if choice == '1':
        print("\n" + "="*70)
        print("Running Integrated Example...")
        print("="*70 + "\n")
        import integrated_example
    elif choice == '2':
        print("\n" + "="*70)
        print("Running Constraint Reasoning Agent...")
        print("="*70 + "\n")
        import constraint_reasoning_agent
    elif choice == '3':
        print("\n" + "="*70)
        print("Running Strategic Scenario Simulator...")
        print("="*70 + "\n")
        import strategic_scenario_simulator
    elif choice == '4':
        print("\n" + "="*70)
        print("Running Tool Reliability Agent...")
        print("="*70 + "\n")
        import tool_reliability_agent
    elif choice == '5':
        print("\n" + "="*70)
        print("Running Human-in-Loop Decision Agent...")
        print("="*70 + "\n")
        import human_in_loop_agent
    elif choice == '6':
        print("\nGoodbye!\n")
        sys.exit(0)
    else:
        print("\nInvalid choice. Please run again and select 1-6.\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
