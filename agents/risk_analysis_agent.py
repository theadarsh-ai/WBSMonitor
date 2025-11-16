"""
Risk Analysis Agent - Identifies critical issues and risks in tasks.
"""
from typing import List, Dict, Tuple
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.date_calculator import DateCalculator
import config


class RiskAnalysisAgent:
    """Agent responsible for analyzing task risks and identifying issues."""
    
    def __init__(self):
        self.date_calc = DateCalculator()
        self.critical_escalation_days = config.CRITICAL_ESCALATION_DAYS
        self.alert_deadline_days = config.ALERT_DEADLINE_APPROACHING_DAYS
        self.alert_threshold_completion = config.ALERT_THRESHOLD_COMPLETION_PERCENT
    
    def analyze_tasks(self, tasks: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Analyze all tasks and categorize by risk level.
        
        Args:
            tasks: List of task dictionaries
            
        Returns:
            Dictionary with categorized tasks: {
                'critical_escalation': [...],
                'alert': [...],
                'at_risk': [...],
                'on_track': [...]
            }
        """
        categorized = {
            'critical_escalation': [],
            'alert': [],
            'at_risk': [],
            'on_track': []
        }
        
        for task in tasks:
            risk_level, reason = self._assess_task_risk(task)
            task['risk_level'] = risk_level
            task['risk_reason'] = reason
            categorized[risk_level].append(task)
        
        return categorized
    
    def _assess_task_risk(self, task: Dict) -> Tuple[str, str]:
        """
        Assess task risk - ONLY send alerts for current month deadlines approaching.
        
        ALERT (sends email):
        - Task due THIS MONTH (November 2025)
        - Deadline approaching within 7 days
        - Completion < 30%
        
        NO overdue emails - only proactive alerts for upcoming deadlines.
        
        Returns:
            Tuple of (risk_level, reason)
        """
        end_date = task.get('end_date')
        completion = task.get('completion_percent', 0)
        
        # Skip completed tasks
        if completion >= 100:
            return ('on_track', f"Completed: 100%")
        
        if not end_date:
            return ('on_track', f"No deadline set")
        
        # Check if task is due in current month
        from datetime import datetime
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        task_end_date = end_date
        if isinstance(end_date, str):
            task_end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
        # Only process tasks due THIS MONTH
        if task_end_date.month != current_month or task_end_date.year != current_year:
            return ('on_track', f"Not due this month")
        
        # Calculate days until deadline
        days_overdue = self.date_calc.days_overdue(task_end_date)
        days_until_deadline = -days_overdue
        
        # ALERT: Deadline approaching within 7 days with low completion
        if days_until_deadline > 0 and days_until_deadline <= self.alert_deadline_days:
            if completion < self.alert_threshold_completion:
                return ('alert',
                        f"Due in {days_until_deadline} days (Nov {task_end_date.day}), only {completion}% complete")
        
        # AT RISK: Due this month but more than 7 days away, low progress
        if days_until_deadline > self.alert_deadline_days:
            if completion < 50:
                return ('at_risk', 
                        f"Due Nov {task_end_date.day}, progress: {completion}%")
        
        return ('on_track', f"On schedule, {completion}% complete")
    
    def get_critical_tasks(self, tasks: List[Dict]) -> List[Dict]:
        """Get only critical and alert tasks."""
        categorized = self.analyze_tasks(tasks)
        return categorized['critical_escalation'] + categorized['alert']
    
    def generate_risk_summary(self, categorized_tasks: Dict[str, List[Dict]]) -> str:
        """Generate a summary of risk analysis."""
        summary = f"""
Risk Analysis Summary:
- Critical Escalation: {len(categorized_tasks['critical_escalation'])} tasks
- Alert: {len(categorized_tasks['alert'])} tasks
- At Risk: {len(categorized_tasks['at_risk'])} tasks
- On Track: {len(categorized_tasks['on_track'])} tasks

Total Tasks: {sum(len(tasks) for tasks in categorized_tasks.values())}
        """
        return summary.strip()
