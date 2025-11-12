"""
Master Supervisor Agent - Orchestrates all sub-agents using LangGraph.
"""
from typing import Annotated, Sequence, TypedDict, Literal
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import create_react_agent
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.data_ingestion_agent import DataIngestionAgent
from agents.risk_analysis_agent import RiskAnalysisAgent
from agents.email_generation_agent import EmailGenerationAgent
from agents.escalation_manager_agent import EscalationManagerAgent
from agents.dependency_tracker_agent import DependencyTrackerAgent
from agents.plan_update_agent import PlanUpdateAgent
from agents.self_healing_agent import SelfHealingAgent
from utils.email_tracker import has_email_been_sent_today, mark_email_sent


class SupervisorState(TypedDict):
    """State for the supervisor agent workflow."""
    messages: Sequence[BaseMessage]
    tasks: list
    categorized_tasks: dict
    healing_results: dict
    escalation_results: dict
    dependency_analysis: dict
    updated_plan_path: str
    next_action: str


class MasterSupervisorAgent:
    """
    Master Supervisor Agent using LangGraph for multi-agent orchestration.
    Coordinates all specialized agents for autonomous project monitoring.
    """
    
    def __init__(self):
        self.data_agent = DataIngestionAgent()
        self.risk_agent = RiskAnalysisAgent()
        self.email_agent = EmailGenerationAgent()
        self.escalation_agent = EscalationManagerAgent()
        self.dependency_agent = DependencyTrackerAgent()
        self.plan_agent = PlanUpdateAgent()
        self.healing_agent = SelfHealingAgent()
        
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow for agent orchestration."""
        
        # Create workflow graph
        workflow = StateGraph(SupervisorState)
        
        # Add nodes for each agent
        workflow.add_node("ingest_data", self._ingest_data_node)
        workflow.add_node("analyze_risks", self._analyze_risks_node)
        workflow.add_node("track_dependencies", self._track_dependencies_node)
        workflow.add_node("self_heal", self._self_heal_node)
        workflow.add_node("manage_escalations", self._manage_escalations_node)
        workflow.add_node("update_plan", self._update_plan_node)
        workflow.add_node("finalize", self._finalize_node)
        
        # Define workflow edges
        workflow.set_entry_point("ingest_data")
        workflow.add_edge("ingest_data", "analyze_risks")
        workflow.add_edge("analyze_risks", "track_dependencies")
        workflow.add_edge("track_dependencies", "self_heal")
        workflow.add_edge("self_heal", "manage_escalations")
        workflow.add_edge("manage_escalations", "update_plan")
        workflow.add_edge("update_plan", "finalize")
        workflow.add_edge("finalize", END)
        
        return workflow.compile()
    
    def _ingest_data_node(self, state: SupervisorState) -> SupervisorState:
        """Node: Data Ingestion Agent."""
        print("\n🔄 Step 1/6: Data Ingestion Agent - Fetching WBS data...")
        
        try:
            tasks = self.data_agent.fetch_wbs_data()
            state["tasks"] = tasks
            state["messages"].append(HumanMessage(content=f"Ingested {len(tasks)} tasks successfully"))
            print(f"✓ Successfully ingested {len(tasks)} tasks")
        except Exception as e:
            print(f"✗ Error in data ingestion: {e}")
            state["tasks"] = []
            state["messages"].append(HumanMessage(content=f"Error: {e}"))
        
        return state
    
    def _analyze_risks_node(self, state: SupervisorState) -> SupervisorState:
        """Node: Risk Analysis Agent."""
        print("\n🔄 Step 2/6: Risk Analysis Agent - Analyzing task risks...")
        
        tasks = state.get("tasks", [])
        if not tasks:
            print("⚠️ No tasks to analyze")
            state["categorized_tasks"] = {}
            return state
        
        categorized = self.risk_agent.analyze_tasks(tasks)
        state["categorized_tasks"] = categorized
        
        summary = self.risk_agent.generate_risk_summary(categorized)
        print(summary)
        state["messages"].append(HumanMessage(content=summary))
        
        return state
    
    def _track_dependencies_node(self, state: SupervisorState) -> SupervisorState:
        """Node: Dependency Tracker Agent."""
        print("\n🔄 Step 3/6: Dependency Tracker Agent - Building dependency graph...")
        
        tasks = state.get("tasks", [])
        if not tasks:
            print("⚠️ No tasks to track")
            state["dependency_analysis"] = {}
            return state
        
        self.dependency_agent.build_dependency_graph(tasks)
        
        # Analyze module dependencies
        module_deps = self.dependency_agent.analyze_module_dependencies(tasks)
        
        # Get critical path
        critical_path = self.dependency_agent.get_critical_path()
        
        state["dependency_analysis"] = {
            "module_dependencies": module_deps,
            "critical_path": critical_path
        }
        
        print(f"✓ Module Dependencies: {module_deps}")
        print(f"✓ Critical Path Length: {len(critical_path)} tasks")
        
        return state
    
    def _self_heal_node(self, state: SupervisorState) -> SupervisorState:
        """Node: Self-Healing Agent."""
        print("\n🔄 Step 4/6: Self-Healing Agent - Analyzing tasks for automatic healing...")
        
        tasks = state.get("tasks", [])
        categorized = state.get("categorized_tasks", {})
        
        if not tasks or not categorized:
            print("⚠️ No tasks to heal")
            state["healing_results"] = {}
            return state
        
        # Perform self-healing analysis and actions
        healing_results = self.healing_agent.analyze_and_heal(tasks, categorized)
        state["healing_results"] = healing_results
        
        # Update tasks in state with healed data so downstream nodes use updated info
        state["tasks"] = tasks
        
        # Log healing summary
        if healing_results.get('actions_taken'):
            print(f"✓ Healing actions: {len(healing_results['actions_taken'])} tasks modified")
            print(f"  - Reallocated: {healing_results['tasks_reallocated']}")
            print(f"  - Timeline adjusted: {healing_results['timelines_adjusted']}")
        else:
            print("✓ No healing actions required")
        
        return state
    
    def _manage_escalations_node(self, state: SupervisorState) -> SupervisorState:
        """Node: Escalation Manager Agent."""
        print("\n🔄 Step 5/6: Escalation Manager Agent - Processing escalations...")
        
        categorized = state.get("categorized_tasks", {})
        if not categorized:
            print("⚠️ No categorized tasks")
            state["escalation_results"] = {}
            return state
        
        results = self.escalation_agent.process_escalations(categorized)
        state["escalation_results"] = results
        
        print(f"✓ Escalations sent: {results['escalations_sent']}")
        print(f"✓ Alerts sent: {results['alerts_sent']}")
        if results['failed'] > 0:
            print(f"⚠️ Failed: {results['failed']}")
        
        # Send daily summary only at end of day (6 PM - 7 PM) and only once per day
        if categorized and self._is_end_of_day() and not has_email_been_sent_today('daily_summary', 'summary'):
            self.escalation_agent.send_daily_summary(categorized)
            mark_email_sent('daily_summary', 'summary')
            print("✓ Daily summary sent to PM (end-of-day report)")
        elif categorized and self._is_end_of_day():
            print("⏭️  Daily summary already sent today")
        elif categorized:
            print("ℹ️  Daily summary will be sent at 6 PM")
        
        return state
    
    def _is_end_of_day(self) -> bool:
        """Check if current time is end of day (6 PM - 7 PM)."""
        current_hour = datetime.now().hour
        return 18 <= current_hour < 19  # 6 PM to 7 PM
    
    def _update_plan_node(self, state: SupervisorState) -> SupervisorState:
        """Node: Plan Update Agent."""
        print("\n🔄 Step 6/6: Plan Update Agent - Updating project plan...")
        
        tasks = state.get("tasks", [])
        categorized = state.get("categorized_tasks", {})
        
        if not tasks:
            print("⚠️ No tasks to update")
            state["updated_plan_path"] = ""
            return state
        
        # Update task statuses
        updated_tasks = self.plan_agent.update_task_statuses(tasks, categorized)
        
        # Recalculate timelines
        updated_tasks = self.plan_agent.recalculate_timelines(updated_tasks)
        
        # Save updated plan
        plan_path = self.plan_agent.save_updated_plan(updated_tasks)
        state["updated_plan_path"] = plan_path
        
        # Generate timeline report
        timeline_report = self.plan_agent.generate_timeline_report(updated_tasks)
        print(timeline_report)
        
        return state
    
    def _finalize_node(self, state: SupervisorState) -> SupervisorState:
        """Node: Finalize and summarize."""
        print("\n" + "="*60)
        print("✓ AUTONOMOUS MONITORING CYCLE COMPLETED")
        print("="*60)
        
        escalation_results = state.get("escalation_results", {})
        plan_path = state.get("updated_plan_path", "")
        
        summary = f"""
Cycle Summary:
- Critical Escalations: {escalation_results.get('escalations_sent', 0)}
- Alerts: {escalation_results.get('alerts_sent', 0)}
- Updated Plan: {plan_path}
        """
        print(summary)
        
        state["messages"].append(HumanMessage(content="Monitoring cycle completed successfully"))
        return state
    
    def execute_monitoring_cycle(self, wbs_file_path: str = None) -> dict:
        """
        Execute a complete monitoring cycle.
        
        Args:
            wbs_file_path: Optional path to WBS file
            
        Returns:
            Final state dictionary
        """
        print("\n" + "="*60)
        print("🚀 STARTING AUTONOMOUS PROJECT MONITORING CYCLE")
        print("="*60)
        
        # Initialize state
        initial_state = {
            "messages": [HumanMessage(content=f"Starting monitoring cycle")],
            "tasks": [],
            "categorized_tasks": {},
            "escalation_results": {},
            "dependency_analysis": {},
            "updated_plan_path": "",
            "next_action": ""
        }
        
        # If specific WBS file provided, fetch it first
        if wbs_file_path:
            try:
                tasks = self.data_agent.fetch_wbs_data(wbs_file_path)
                initial_state["tasks"] = tasks
            except Exception as e:
                print(f"Error loading WBS file: {e}")
        
        # Execute workflow
        final_state = self.workflow.invoke(initial_state)
        
        return final_state
