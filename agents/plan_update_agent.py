"""
Plan Update Agent - Updates project plans and recalculates timelines.
Enhanced with AI-powered timeline predictions.
"""
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.date_calculator import DateCalculator
from utils.excel_parser import ExcelParser
from utils.azure_ai_client import get_ai_client
import config


class PlanUpdateAgent:
    """Agent responsible for updating project plans with AI-powered predictions."""
    
    def __init__(self):
        self.date_calc = DateCalculator()
        self.ai_client = get_ai_client()
    
    def update_task_statuses(self, tasks: List[Dict], categorized_tasks: Dict[str, List[Dict]]) -> List[Dict]:
        """
        Update task statuses based on risk analysis.
        
        Args:
            tasks: Original task list
            categorized_tasks: Categorized tasks by risk level
            
        Returns:
            Updated task list
        """
        # Create mapping of task_id to risk level
        risk_map = {}
        for risk_level, task_list in categorized_tasks.items():
            for task in task_list:
                risk_map[task['task_id']] = {
                    'risk_level': risk_level,
                    'risk_reason': task.get('risk_reason', '')
                }
        
        # Update tasks
        updated_tasks = []
        for task in tasks:
            task_id = task['task_id']
            if task_id in risk_map:
                task['risk_level'] = risk_map[task_id]['risk_level']
                task['risk_reason'] = risk_map[task_id]['risk_reason']
                
                # Update status if needed
                if risk_map[task_id]['risk_level'] == 'critical_escalation':
                    if 'escalation' not in task['status'].lower():
                        task['status'] = 'escalation'
                elif risk_map[task_id]['risk_level'] == 'alert':
                    if 'alert' not in task['status'].lower():
                        task['status'] = 'alert'
            
            updated_tasks.append(task)
        
        return updated_tasks
    
    def recalculate_timelines(self, tasks: List[Dict]) -> List[Dict]:
        """
        Recalculate project timelines based on current progress.
        
        Args:
            tasks: Task list
            
        Returns:
            Updated task list with recalculated dates
        """
        updated_tasks = []
        
        for task in tasks:
            # If task is incomplete and overdue, recalculate
            completion = task.get('completion_percent', 0)
            
            if completion < 100 and task.get('end_date'):
                days_overdue = self.date_calc.days_overdue(task['end_date'])
                
                if days_overdue > 0:
                    # Estimate remaining work
                    remaining_percent = 100 - completion
                    original_duration = task.get('duration_days', 0)
                    
                    if completion > 0 and original_duration > 0:
                        # Calculate velocity
                        days_elapsed = original_duration + days_overdue
                        velocity = completion / days_elapsed if days_elapsed > 0 else 0
                        
                        if velocity > 0:
                            estimated_days_remaining = int(remaining_percent / velocity)
                            new_end_date = datetime.now() + timedelta(days=estimated_days_remaining)
                            
                            task['projected_end_date'] = new_end_date
                            task['projected_delay_days'] = (new_end_date - task['end_date']).days
            
            updated_tasks.append(task)
        
        return updated_tasks
    
    def save_updated_plan(self, tasks: List[Dict], output_path: Optional[str] = None) -> str:
        """
        Save updated project plan to Excel.
        
        Args:
            tasks: Updated task list
            output_path: Optional output path
        """
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(config.REPORTS_DIR, f"updated_plan_{timestamp}.xlsx")
        
        parser = ExcelParser("dummy.xlsx")  # Parser doesn't need input file for saving
        parser.save_wbs(tasks, output_path)
        
        print(f"✓ Updated plan saved to {output_path}")
        return output_path
    
    def generate_timeline_report(self, tasks: List[Dict]) -> str:
        """
        Generate timeline impact report.
        
        Returns:
            Formatted report string
        """
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t.get('completion_percent', 0) == 100])
        overdue_tasks = len([t for t in tasks if self.date_calc.days_overdue(t.get('end_date')) > 0 and t.get('completion_percent', 0) < 100])
        
        projected_delays = [t for t in tasks if t.get('projected_delay_days', 0) > 0]
        
        report = f"""
Timeline Analysis Report:
========================
Total Tasks: {total_tasks}
Completed: {completed_tasks} ({round(completed_tasks/total_tasks*100, 1)}%)
Currently Overdue: {overdue_tasks}
Tasks with Projected Delays: {len(projected_delays)}

"""
        
        if projected_delays:
            report += "Projected Delays:\n"
            for task in projected_delays[:10]:  # Top 10
                report += f"  - {task['task_name']}: {task['projected_delay_days']} days\n"
        
        return report
