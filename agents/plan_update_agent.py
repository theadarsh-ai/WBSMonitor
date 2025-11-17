"""
Plan Update Agent - 100% AI-Powered Timeline Predictions
AI autonomously predicts timelines and adjusts project plans.
NO hardcoded calculations - ALL predictions made by AI.
"""
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.date_calculator import DateCalculator
from utils.excel_parser import ExcelParser
from utils.azure_ai_client import get_ai_client
from utils.ai_decision_engine import get_decision_engine
import config


class PlanUpdateAgent:
    """
    100% AI-Agentic Plan Update Agent.
    Uses AI to predict timelines and optimize project plans.
    """
    
    def __init__(self):
        self.date_calc = DateCalculator()
        self.ai_client = get_ai_client()
        self.decision_engine = get_decision_engine()
        print("🤖 Plan Update Agent initialized in FULLY AI-PREDICTIVE mode")
    
    def update_task_statuses(self, tasks: List[Dict], categorized_tasks: Dict[str, List[Dict]]) -> List[Dict]:
        """
        Update task statuses based on AI risk analysis.
        
        Args:
            tasks: Original task list
            categorized_tasks: AI-categorized tasks by risk level
            
        Returns:
            Updated task list
        """
        # Create mapping of task_id to AI assessment
        ai_assessment_map = {}
        for risk_level, task_list in categorized_tasks.items():
            for task in task_list:
                ai_assessment_map[task['task_id']] = {
                    'risk_level': risk_level,
                    'risk_reason': task.get('risk_reason', ''),
                    'ai_confidence': task.get('ai_confidence', 0.75),
                    'urgency_score': task.get('urgency_score', 50)
                }
        
        # Update tasks with AI insights
        updated_tasks = []
        for task in tasks:
            task_id = task['task_id']
            if task_id in ai_assessment_map:
                assessment = ai_assessment_map[task_id]
                task['risk_level'] = assessment['risk_level']
                task['risk_reason'] = assessment['risk_reason']
                task['ai_confidence'] = assessment['ai_confidence']
                task['urgency_score'] = assessment['urgency_score']
                
                # Update status based on AI assessment
                if assessment['risk_level'] == 'critical_escalation':
                    task['status'] = f"AI-CRITICAL (Confidence: {assessment['ai_confidence']:.0%})"
                elif assessment['risk_level'] == 'alert':
                    task['status'] = f"AI-ALERT (Urgency: {assessment['urgency_score']})"
            
            updated_tasks.append(task)
        
        return updated_tasks
    
    def recalculate_timelines_ai(self, tasks: List[Dict], dependencies: List[Dict] = None) -> List[Dict]:
        """
        AI-powered timeline recalculation.
        Uses AI Decision Engine to predict realistic completion dates.
        
        Args:
            tasks: Task list
            dependencies: Optional dependency information
            
        Returns:
            Updated task list with AI predictions
        """
        print("\n🤖 AI analyzing timelines and predicting completion dates...")
        
        updated_tasks = []
        predictions_made = 0
        
        for task in tasks:
            completion = task.get('completion_percent', 0)
            
            # AI predicts timeline for incomplete tasks
            if completion < 100:
                ai_prediction = self._ai_predict_timeline(task, dependencies or [])
                
                if ai_prediction:
                    task['ai_predicted_completion'] = ai_prediction['predicted_completion_date']
                    task['ai_prediction_confidence'] = ai_prediction.get('confidence', 0.75)
                    task['ai_risk_factors'] = ai_prediction.get('risk_factors', [])
                    task['ai_buffer_days'] = ai_prediction.get('buffer_recommendation', 0)
                    
                    # Calculate if AI predicts a delay
                    if task.get('end_date'):
                        predicted_date = datetime.strptime(ai_prediction['predicted_completion_date'], '%Y-%m-%d')
                        original_date = task['end_date']
                        if isinstance(original_date, str):
                            original_date = datetime.strptime(original_date, '%Y-%m-%d')
                        
                        delay_days = (predicted_date - original_date).days
                        if delay_days > 0:
                            task['ai_predicted_delay_days'] = delay_days
                    
                    predictions_made += 1
            
            updated_tasks.append(task)
        
        if predictions_made > 0:
            print(f"✓ AI made {predictions_made} timeline predictions")
        
        return updated_tasks
    
    def _ai_predict_timeline(self, task: Dict, dependencies: List[Dict]) -> Optional[Dict]:
        """
        AI predicts realistic timeline for a task.
        
        Returns:
            Prediction dictionary or None
        """
        if not self.ai_client.is_available():
            return None
        
        # Use AI Decision Engine
        prediction = self.decision_engine.predict_timeline_ai(task, dependencies)
        
        return prediction
    
    def generate_ai_timeline_insights(self, tasks: List[Dict]) -> str:
        """
        Generate AI-powered insights about project timeline.
        
        Returns:
            AI-generated strategic insights
        """
        if not self.ai_client.is_available():
            return self._fallback_timeline_report(tasks)
        
        # Prepare task summary
        task_summary = []
        for task in tasks[:30]:  # Top 30 for token efficiency
            summary = {
                'name': task.get('task_name'),
                'module': task.get('module'),
                'completion': task.get('completion_percent', 0),
                'due_date': str(task.get('end_date', 'N/A')),
                'ai_prediction': task.get('ai_predicted_completion'),
                'ai_delay': task.get('ai_predicted_delay_days', 0)
            }
            task_summary.append(summary)
        
        system_prompt = """You are an expert AI project timeline analyst.
Analyze the project timeline data and provide strategic insights:

1. **Overall Project Health**: Timeline outlook (on-track/at-risk/critical)
2. **Key Bottlenecks**: Tasks causing timeline risks
3. **Cascading Impacts**: How delays might compound
4. **Priority Actions**: Top 3 actions to improve timeline
5. **Realistic Forecast**: When will the project actually complete?

Be specific, data-driven, and actionable. Limit to 6-7 sentences."""
        
        import json
        user_message = f"""Analyze this project timeline data:

{json.dumps(task_summary, indent=2)}

Provide strategic timeline insights."""
        
        try:
            insights = self.ai_client.generate_response(system_prompt, user_message)
            return f"🧠 AI Timeline Analysis:\n\n{insights}"
        except Exception as e:
            print(f"⚠️ AI timeline insights error: {e}")
            return self._fallback_timeline_report(tasks)
    
    def _fallback_timeline_report(self, tasks: List[Dict]) -> str:
        """Fallback timeline report when AI unavailable."""
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t.get('completion_percent', 0) == 100])
        
        report = f"""
Timeline Analysis (Fallback - AI Unavailable):
Total Tasks: {total_tasks}
Completed: {completed_tasks} ({round(completed_tasks/total_tasks*100, 1) if total_tasks > 0 else 0}%)
"""
        return report
    
    def save_updated_plan(self, tasks: List[Dict], output_path: Optional[str] = None) -> str:
        """
        Save AI-updated project plan to Excel.
        
        Args:
            tasks: AI-updated task list
            output_path: Optional output path
        """
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(config.REPORTS_DIR, f"ai_updated_plan_{timestamp}.xlsx")
        
        parser = ExcelParser("dummy.xlsx")
        parser.save_wbs(tasks, output_path)
        
        print(f"✓ AI-optimized plan saved to {output_path}")
        return output_path
    
    def generate_timeline_report(self, tasks: List[Dict]) -> str:
        """
        Generate comprehensive AI-powered timeline report.
        
        Returns:
            Formatted report string
        """
        # Get AI insights
        ai_insights = self.generate_ai_timeline_insights(tasks)
        
        # Calculate statistics
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t.get('completion_percent', 0) == 100])
        ai_predicted_delays = [t for t in tasks if t.get('ai_predicted_delay_days', 0) > 0]
        
        report = f"""
{'='*60}
AI-Powered Timeline Analysis Report
{'='*60}

Project Statistics:
- Total Tasks: {total_tasks}
- Completed: {completed_tasks} ({round(completed_tasks/total_tasks*100, 1) if total_tasks > 0 else 0}%)
- AI-Predicted Delays: {len(ai_predicted_delays)} tasks

{ai_insights}

"""
        
        if ai_predicted_delays:
            report += "\nTop AI-Predicted Delays:\n"
            sorted_delays = sorted(ai_predicted_delays, key=lambda x: x.get('ai_predicted_delay_days', 0), reverse=True)
            for task in sorted_delays[:10]:
                confidence = task.get('ai_prediction_confidence', 0.75)
                report += f"  - {task['task_name']}: +{task['ai_predicted_delay_days']} days (AI Confidence: {confidence:.0%})\n"
        
        return report
