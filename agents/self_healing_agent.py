"""
Self-Healing Task Reallocation Agent - Automatically reallocates tasks and updates the Excel file.
"""
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.excel_parser import ExcelParser
from utils.date_calculator import DateCalculator
import config


class SelfHealingAgent:
    """
    Agent responsible for automatically reallocating tasks to prevent project delays.
    Makes intelligent decisions about task reassignments and updates the Excel file.
    """
    
    def __init__(self):
        self.date_calc = DateCalculator()
        self.notification_file = os.path.join(config.DATA_DIR, 'healing_notifications.json')
        self.wbs_file = os.path.join(config.DATA_DIR, 'project_wbs.xlsx')
        
    def analyze_and_heal(self, tasks: List[Dict], categorized_tasks: Dict) -> Dict:
        """
        Analyze tasks and perform self-healing actions when needed.
        
        Args:
            tasks: List of all tasks
            categorized_tasks: Dictionary of tasks categorized by risk level
            
        Returns:
            Dictionary with healing results and notifications
        """
        healing_results = {
            'actions_taken': [],
            'tasks_reallocated': 0,
            'timelines_adjusted': 0,
            'notifications': []
        }
        
        print("\n🔧 Self-Healing Agent - Analyzing tasks for automatic reallocation...")
        
        # Identify tasks that need healing
        critical_tasks = categorized_tasks.get('critical_escalation', [])
        alert_tasks = categorized_tasks.get('alert', [])
        at_risk_tasks = categorized_tasks.get('at_risk', [])
        
        problem_tasks = critical_tasks + alert_tasks
        
        if not problem_tasks:
            print("✓ No tasks require healing - all on track")
            return healing_results
        
        print(f"🔍 Found {len(problem_tasks)} tasks that may need healing")
        
        # Perform healing actions
        for task in problem_tasks:
            healing_action = self._determine_healing_action(task, tasks)
            
            if healing_action:
                success = self._apply_healing_action(task, healing_action, tasks)
                
                if success:
                    healing_results['actions_taken'].append({
                        'task_name': task.get('task_name'),
                        'action': healing_action['type'],
                        'details': healing_action['details'],
                        'timestamp': datetime.now().isoformat()
                    })
                    
                    if healing_action['type'] == 'reallocate':
                        healing_results['tasks_reallocated'] += 1
                    
                    # Create notification
                    notification = {
                        'id': f"heal_{task.get('task_id', 0)}_{datetime.now().timestamp()}",
                        'type': 'self_healing',
                        'severity': 'warning' if healing_action['type'] == 'reallocate' else 'info',
                        'task_name': task.get('task_name'),
                        'action': healing_action['type'],
                        'message': healing_action['notification_message'],
                        'timestamp': datetime.now().isoformat(),
                        'read': False
                    }
                    healing_results['notifications'].append(notification)
        
        # Save results to file
        if healing_results['actions_taken']:
            self._save_healing_results(healing_results)
            self._save_notifications(healing_results['notifications'])
            
            # Update Excel file with changes
            self._update_excel_file(tasks)
            
            print(f"✓ Healing complete: {healing_results['tasks_reallocated']} task(s) reallocated")
        else:
            print("ℹ️  No healing actions needed at this time")
        
        return healing_results
    
    def _determine_healing_action(self, task: Dict, all_tasks: List[Dict]) -> Optional[Dict]:
        """
        Determine what healing action should be taken for a task.
        
        Returns:
            Dictionary with action details or None if no action needed
        """
        end_date = task.get('end_date')
        completion = task.get('completion_percent', 0)
        assigned_to = task.get('assigned_to', 'Unknown')
        
        if not end_date:
            return None
        
        # Calculate days until deadline
        days_overdue = self.date_calc.days_overdue(end_date)
        days_until_deadline = -days_overdue
        
        # Reallocate task if deadline is very close and completion is very low
        if days_until_deadline > 0 and days_until_deadline <= 3 and completion < 20:
            # Find team member with least workload
            new_assignee = self._find_best_assignee(task, all_tasks)
            
            if new_assignee and new_assignee != assigned_to:
                return {
                    'type': 'reallocate',
                    'details': {
                        'from': assigned_to,
                        'to': new_assignee,
                        'reason': f'Critical deadline in {days_until_deadline} days with only {completion}% complete'
                    },
                    'notification_message': f"Task '{task.get('task_name')}' reallocated from {assigned_to} to {new_assignee} due to critical deadline"
                }
        
        return None
    
    def _find_best_assignee(self, task: Dict, all_tasks: List[Dict]) -> Optional[str]:
        """
        Find the team member with the least current workload in the same module.
        """
        task_module = task.get('module')
        
        # Count tasks per assignee in the same module
        workload = {}
        for t in all_tasks:
            if t.get('module') == task_module and t.get('completion_percent', 0) < 100:
                assignee = t.get('assigned_to', 'Unknown')
                if assignee not in workload:
                    workload[assignee] = 0
                workload[assignee] += 1
        
        # Find assignee with least workload (excluding current assignee)
        current_assignee = task.get('assigned_to')
        candidates = {k: v for k, v in workload.items() if k != current_assignee}
        
        if candidates:
            best_assignee = min(candidates, key=candidates.get)
            return best_assignee
        
        return None
    
    def _apply_healing_action(self, task: Dict, action: Dict, all_tasks: List[Dict]) -> bool:
        """
        Apply the healing action to the task.
        """
        try:
            if action['type'] == 'reallocate':
                # Update assigned_to field
                task['assigned_to'] = action['details']['to']
                task['mail_id'] = action['details']['to']  # Update mail_id too
                
                # Add comment about reallocation
                current_status = task.get('status', '')
                task['status'] = f"AUTO-REALLOCATED to {action['details']['to']}"
                
                return True
                
        except Exception as e:
            print(f"✗ Error applying healing action: {e}")
            return False
        
        return False
    
    def _update_excel_file(self, tasks: List[Dict]):
        """
        Update the Excel file with the modified tasks.
        """
        try:
            if not os.path.exists(self.wbs_file):
                print(f"⚠️ WBS file not found: {self.wbs_file}")
                return
            
            # Create backup
            backup_file = os.path.join(
                config.DATA_DIR, 
                f'project_wbs_backup_healing_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
            )
            import shutil
            shutil.copy(self.wbs_file, backup_file)
            
            # Update the Excel file
            parser = ExcelParser(self.wbs_file)
            parser.save_wbs(tasks, self.wbs_file)
            
            print(f"✓ Excel file updated (backup: {os.path.basename(backup_file)})")
            
        except Exception as e:
            print(f"✗ Error updating Excel file: {e}")
    
    def _save_healing_results(self, results: Dict):
        """
        Save healing results to a JSON file for tracking.
        """
        try:
            history_file = os.path.join(config.DATA_DIR, 'healing_history.json')
            
            history = []
            if os.path.exists(history_file):
                with open(history_file, 'r') as f:
                    history = json.load(f)
            
            history.append({
                'timestamp': datetime.now().isoformat(),
                'results': results
            })
            
            # Keep only last 100 entries
            history = history[-100:]
            
            with open(history_file, 'w') as f:
                json.dump(history, f, indent=2)
                
        except Exception as e:
            print(f"⚠️ Could not save healing history: {e}")
    
    def _save_notifications(self, notifications: List[Dict]):
        """
        Save notifications to file for dashboard display.
        """
        try:
            existing_notifications = []
            if os.path.exists(self.notification_file):
                with open(self.notification_file, 'r') as f:
                    existing_notifications = json.load(f)
            
            # Add new notifications
            existing_notifications.extend(notifications)
            
            # Keep only unread notifications from last 7 days
            cutoff_date = datetime.now() - timedelta(days=7)
            existing_notifications = [
                n for n in existing_notifications
                if datetime.fromisoformat(n['timestamp']) > cutoff_date
            ]
            
            with open(self.notification_file, 'w') as f:
                json.dump(existing_notifications, f, indent=2)
                
        except Exception as e:
            print(f"⚠️ Could not save notifications: {e}")
    
    def get_notifications(self) -> List[Dict]:
        """
        Get all current notifications.
        """
        try:
            if os.path.exists(self.notification_file):
                with open(self.notification_file, 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"⚠️ Could not load notifications: {e}")
            return []
    
    def mark_notification_read(self, notification_id: str):
        """
        Mark a notification as read.
        """
        try:
            if os.path.exists(self.notification_file):
                with open(self.notification_file, 'r') as f:
                    notifications = json.load(f)
                
                for notif in notifications:
                    if notif['id'] == notification_id:
                        notif['read'] = True
                
                with open(self.notification_file, 'w') as f:
                    json.dump(notifications, f, indent=2)
                    
        except Exception as e:
            print(f"⚠️ Could not mark notification as read: {e}")
    
    def clear_all_notifications(self):
        """
        Clear all notifications.
        """
        try:
            if os.path.exists(self.notification_file):
                with open(self.notification_file, 'w') as f:
                    json.dump([], f)
        except Exception as e:
            print(f"⚠️ Could not clear notifications: {e}")
