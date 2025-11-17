"""
Risk Analysis Agent - 100% AI-Powered Risk Assessment
NO hardcoded rules - ALL decisions made by AI autonomously.
"""
from typing import List, Dict, Tuple, Optional
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.date_calculator import DateCalculator
from utils.azure_ai_client import get_ai_client
from utils.ai_decision_engine import get_decision_engine
import config


class RiskAnalysisAgent:
    """
    100% AI-Agentic Risk Analysis Agent.
    Uses AI Decision Engine for ALL risk assessments - NO hardcoded thresholds.
    """
    
    def __init__(self):
        self.date_calc = DateCalculator()
        self.ai_client = get_ai_client()
        self.decision_engine = get_decision_engine()
        print("🤖 Risk Analysis Agent initialized in FULLY AGENTIC mode")
    
    def analyze_tasks(self, tasks: List[Dict]) -> Dict[str, List[Dict]]:
        """
        AI-powered task analysis - NO hardcoded rules.
        Uses AI Decision Engine to intelligently categorize ALL tasks.
        
        Args:
            tasks: List of task dictionaries
            
        Returns:
            Dictionary with AI-categorized tasks: {
                'critical_escalation': [...],
                'alert': [...],
                'at_risk': [...],
                'on_track': [...]
            }
        """
        print(f"🤖 AI analyzing {len(tasks)} tasks autonomously...")
        
        if self.ai_client.is_available():
            # Use AI Decision Engine for batch analysis (more efficient)
            categorized = self.decision_engine.batch_assess_tasks_ai(tasks)
            print(f"✓ AI assessment complete:")
            print(f"  - Critical: {len(categorized['critical_escalation'])}")
            print(f"  - Alert: {len(categorized['alert'])}")
            print(f"  - At Risk: {len(categorized['at_risk'])}")
            print(f"  - On Track: {len(categorized['on_track'])}")
            return categorized
        else:
            # Fallback to conservative assessment when AI unavailable
            print("⚠️ AI unavailable - using conservative fallback")
            return self._conservative_fallback(tasks)
    
    def _assess_task_risk_ai(self, task: Dict) -> Tuple[str, str, float]:
        """
        Single task AI assessment (used when needed).
        
        Returns:
            Tuple of (risk_level, reason, confidence)
        """
        assessment = self.decision_engine.assess_task_risk_ai(task)
        return (
            assessment['risk_level'],
            assessment['risk_reason'],
            assessment.get('confidence', 0.75)
        )
    
    def get_critical_tasks(self, tasks: List[Dict]) -> List[Dict]:
        """Get only critical and alert tasks as determined by AI."""
        categorized = self.analyze_tasks(tasks)
        return categorized['critical_escalation'] + categorized['alert']
    
    def generate_risk_summary(self, categorized_tasks: Dict[str, List[Dict]]) -> str:
        """Generate AI-powered risk summary with insights."""
        base_summary = f"""
🤖 AI-Powered Risk Analysis Summary:
- Critical Escalation: {len(categorized_tasks['critical_escalation'])} tasks
- Alert: {len(categorized_tasks['alert'])} tasks
- At Risk: {len(categorized_tasks['at_risk'])} tasks
- On Track: {len(categorized_tasks['on_track'])} tasks

Total Tasks Analyzed: {sum(len(tasks) for tasks in categorized_tasks.values())}
        """
        
        # Get deep AI insights
        ai_insights = self.get_ai_risk_insights(categorized_tasks)
        if ai_insights:
            base_summary += f"\n\n🧠 AI Strategic Insights:\n{ai_insights}"
        
        return base_summary.strip()
    
    def get_ai_risk_insights(self, categorized_tasks: Dict[str, List[Dict]]) -> Optional[str]:
        """
        Get deep AI-powered strategic risk insights.
        Analyzes patterns, trends, and provides actionable recommendations.
        
        Args:
            categorized_tasks: Tasks categorized by AI
            
        Returns:
            AI-generated strategic insights
        """
        if not self.ai_client.is_available():
            return None
        
        # Collect all high-risk tasks
        high_risk_tasks = (
            categorized_tasks.get('critical_escalation', []) +
            categorized_tasks.get('alert', []) +
            categorized_tasks.get('at_risk', [])
        )
        
        if not high_risk_tasks:
            return "✓ No high-risk tasks identified. Project is on track."
        
        # Prepare comprehensive context
        task_details = []
        for task in high_risk_tasks[:15]:  # Analyze top 15 high-risk tasks
            task_details.append(
                f"- {task['task_name']}\n"
                f"  Module: {task.get('module', 'N/A')}\n"
                f"  Completion: {task.get('completion_percent', 0)}%\n"
                f"  Due: {task.get('end_date', 'N/A')}\n"
                f"  Assigned: {task.get('assigned_to', 'Unassigned')}\n"
                f"  Risk: {task.get('risk_level', 'N/A')} - {task.get('risk_reason', 'N/A')}\n"
                f"  AI Confidence: {task.get('ai_confidence', 0.75):.0%}"
            )
        
        context = "\n\n".join(task_details)
        
        system_prompt = """You are a senior AI project risk strategist with 20+ years of experience.
Analyze the high-risk tasks and provide STRATEGIC insights:

1. **Pattern Recognition**: Identify systemic issues across multiple tasks
2. **Root Cause Analysis**: Find underlying problems (not just symptoms)
3. **Cascading Risks**: Predict how current risks might compound
4. **Priority Actions**: Top 3 most impactful actions to take NOW
5. **Resource Recommendations**: Where to focus team attention

Be specific, actionable, and strategic. Focus on insights that aren't obvious from the data alone.
Limit response to 5-6 sentences."""
        
        user_message = f"""Analyze these {len(high_risk_tasks)} high-risk project tasks:

{context}

Provide strategic risk insights and priority recommendations."""
        
        try:
            insights = self.ai_client.generate_response(system_prompt, user_message)
            return insights
        except Exception as e:
            print(f"⚠️ AI strategic insights error: {e}")
            return None
    
    def predict_task_outcomes_ai(self, tasks: List[Dict]) -> Dict[str, any]:
        """
        AI predicts likely outcomes for tasks.
        
        Returns:
            Predictions about completion dates, blockers, and success probability
        """
        if not self.ai_client.is_available():
            return {'predictions_available': False}
        
        system_prompt = """You are an AI predictive analytics expert.
Analyze task data and predict:
- Likely completion dates (realistic, not optimistic)
- Potential blockers and bottlenecks
- Success probability for on-time delivery
- Early warning signs to monitor

Return JSON with predictions."""
        
        task_summary = "\n".join([
            f"- {t['task_name']}: {t.get('completion_percent', 0)}% complete, Due: {t.get('end_date')}"
            for t in tasks[:20]
        ])
        
        user_message = f"""Predict outcomes for these tasks:

{task_summary}

Provide predictions in JSON format."""
        
        try:
            response = self.ai_client.generate_response(system_prompt, user_message)
            # Parse predictions
            return {'predictions_available': True, 'raw_predictions': response}
        except Exception as e:
            print(f"⚠️ AI prediction error: {e}")
            return {'predictions_available': False}
    
    def _conservative_fallback(self, tasks: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Conservative fallback when AI is unavailable.
        Marks everything as on_track to avoid false alarms.
        """
        categorized = {
            'critical_escalation': [],
            'alert': [],
            'at_risk': [],
            'on_track': []
        }
        
        for task in tasks:
            completion = task.get('completion_percent', 0)
            
            # Very conservative rules when AI is off
            if completion >= 100:
                task['risk_level'] = 'on_track'
                task['risk_reason'] = 'Task completed'
            elif completion < 10:
                task['risk_level'] = 'at_risk'
                task['risk_reason'] = 'Low progress (AI unavailable for detailed analysis)'
            else:
                task['risk_level'] = 'on_track'
                task['risk_reason'] = 'In progress (AI unavailable for detailed analysis)'
            
            categorized[task['risk_level']].append(task)
        
        return categorized
