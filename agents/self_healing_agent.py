"""
Self-Healing Agent - 100% AI-Powered Autonomous Task Reallocation
NO hardcoded rules - AI decides when and how to reallocate tasks.
"""
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.excel_parser import ExcelParser
from utils.date_calculator import DateCalculator
from utils.azure_ai_client import get_ai_client
from utils.ai_decision_engine import get_decision_engine
import config


class SelfHealingAgent:
    """
    100% AI-Agentic Self-Healing Agent.
    Uses AI Decision Engine to autonomously reallocate tasks and prevent delays.
    NO hardcoded thresholds - AI makes ALL decisions.
    """
    
    def __init__(self):
        self.date_calc = DateCalculator()
        self.notification_file = os.path.join(config.DATA_DIR, 'healing_notifications.json')
        self.wbs_file = os.path.join(config.DATA_DIR, 'project_wbs.xlsx')
        self.ai_client = get_ai_client()
        self.decision_engine = get_decision_engine()
        print("🤖 Self-Healing Agent initialized in FULLY AUTONOMOUS mode")
        
    def analyze_and_heal(self, tasks: List[Dict], categorized_tasks: Dict) -> Dict:
        """
        AI-powered autonomous healing - analyzes and fixes tasks without human intervention.
        
        Args:
            tasks: List of all tasks
            categorized_tasks: Dictionary of tasks categorized by AI risk assessment
            
        Returns:
            Dictionary with healing results and notifications
        """
        healing_results = {
            'actions_taken': [],
            'tasks_reallocated': 0,
            'timelines_adjusted': 0,
            'notifications': [],
            'ai_decisions': []
        }
        
        print("\n🤖 AI Self-Healing Agent - Autonomous task optimization...")
        
        # AI identifies which tasks need healing (no hardcoded categories)
        problem_tasks = self._ai_identify_healing_candidates(tasks, categorized_tasks)
        
        if not problem_tasks:
            print("✓ AI determined no healing actions needed - system optimized")
            return healing_results
        
        print(f"🧠 AI identified {len(problem_tasks)} tasks for autonomous healing")
        
        # AI performs healing actions
        for task in problem_tasks:
            ai_decision = self._ai_determine_healing_action(task, tasks)
            
            if ai_decision and ai_decision.get('should_reallocate'):
                success = self._apply_ai_healing_action(task, ai_decision, tasks)
                
                if success:
                    healing_results['actions_taken'].append({
                        'task_name': task.get('task_name'),
                        'action': 'ai_reallocate',
                        'details': ai_decision,
                        'timestamp': datetime.now().isoformat()
                    })
                    
                    healing_results['tasks_reallocated'] += 1
                    healing_results['ai_decisions'].append(ai_decision)
                    
                    # Create notification
                    notification = {
                        'id': f"ai_heal_{task.get('task_id', 0)}_{datetime.now().timestamp()}",
                        'type': 'ai_self_healing',
                        'severity': 'info',
                        'task_name': task.get('task_name'),
                        'action': 'autonomous_reallocation',
                        'message': f"🤖 AI autonomously reallocated '{task.get('task_name')}' from {ai_decision.get('from_assignee')} to {ai_decision['recommended_assignee']}",
                        'ai_reason': ai_decision.get('reason'),
                        'ai_confidence': ai_decision.get('confidence', 0.75),
                        'timestamp': datetime.now().isoformat(),
                        'read': False
                    }
                    healing_results['notifications'].append(notification)
        
        # Save results
        if healing_results['actions_taken']:
            self._save_healing_results(healing_results)
            self._save_notifications(healing_results['notifications'])
            
            # Update Excel file with AI changes
            self._update_excel_file(tasks)
            
            print(f"✓ AI autonomous healing complete: {healing_results['tasks_reallocated']} task(s) optimized")
            print(f"  AI Confidence Average: {self._calculate_average_confidence(healing_results):.0%}")
        else:
            print("ℹ️  AI determined no healing actions needed")
        
        return healing_results
    
    def _ai_identify_healing_candidates(self, tasks: List[Dict], categorized_tasks: Dict) -> List[Dict]:
        """
        AI identifies which tasks are candidates for healing.
        NO hardcoded categories - AI decides what needs attention.
        """
        if not self.ai_client.is_available():
            # Conservative fallback
            return categorized_tasks.get('critical_escalation', [])[:3]
        
        # AI analyzes ALL tasks and decides which need healing
        system_prompt = """You are an autonomous AI task optimization system.
Analyze all tasks and identify which ones would benefit from immediate intervention (task reallocation).

Consider:
- Risk of deadline miss
- Current assignee workload
- Task progress velocity
- Business impact
- Resource availability

Return JSON array of task IDs that need healing (max 10):
["task_1", "task_2", ...]

Be selective - only choose tasks where intervention will have significant impact."""
        
        task_summary = "\n".join([
            f"{t.get('task_id', t.get('task_name'))}: {t.get('task_name')} - "
            f"{t.get('completion_percent', 0)}% complete, "
            f"Due: {t.get('end_date')}, "
            f"Assigned: {t.get('assigned_to', 'Unassigned')}, "
            f"Risk: {t.get('risk_level', 'unknown')}"
            for t in tasks[:50]  # Limit to 50 for token efficiency
        ])
        
        user_message = f"""Identify tasks needing autonomous healing:

{task_summary}

Return JSON array of task IDs."""
        
        try:
            response = self.ai_client.generate_response(system_prompt, user_message)
            
            # Parse response
            response_clean = response.strip()
            if '```json' in response_clean:
                response_clean = response_clean.split('```json')[1].split('```')[0].strip()
            elif '```' in response_clean:
                response_clean = response_clean.split('```')[1].split('```')[0].strip()
            
            task_ids = json.loads(response_clean)
            
            # Map IDs to tasks
            task_map = {str(t.get('task_id', t.get('task_name'))): t for t in tasks}
            return [task_map[tid] for tid in task_ids if tid in task_map]
            
        except Exception as e:
            print(f"⚠️ AI healing identification error: {e}")
            return categorized_tasks.get('critical_escalation', [])[:3]
    
    def _ai_determine_healing_action(self, task: Dict, all_tasks: List[Dict]) -> Optional[Dict]:
        """
        AI autonomously determines optimal healing action.
        NO hardcoded rules - AI makes all decisions.
        
        Returns:
            AI decision dictionary or None
        """
        if not self.ai_client.is_available():
            return None
        
        # Get available resources from all tasks
        available_resources = self._extract_available_resources(all_tasks, task)
        
        # Use AI Decision Engine
        ai_decision = self.decision_engine.suggest_task_reallocation_ai(
            task, 
            available_resources
        )
        
        if ai_decision:
            # Add current assignee info
            ai_decision['from_assignee'] = task.get('assigned_to', 'Unassigned')
        
        return ai_decision
    
    def _extract_available_resources(self, all_tasks: List[Dict], current_task: Dict) -> List[Dict]:
        """Extract available resources with workload analysis."""
        task_module = current_task.get('module')
        
        # Analyze workload per person
        workload = {}
        for t in all_tasks:
            if t.get('completion_percent', 0) < 100:
                assignee = t.get('assigned_to', 'Unknown')
                if assignee not in workload:
                    workload[assignee] = {
                        'name': assignee,
                        'task_count': 0,
                        'module': t.get('module'),
                        'avg_completion': []
                    }
                workload[assignee]['task_count'] += 1
                workload[assignee]['avg_completion'].append(t.get('completion_percent', 0))
        
        # Calculate average completion for each person
        for person in workload.values():
            if person['avg_completion']:
                person['avg_completion'] = sum(person['avg_completion']) / len(person['avg_completion'])
            else:
                person['avg_completion'] = 0
        
        return list(workload.values())
    
    def _apply_ai_healing_action(self, task: Dict, ai_decision: Dict, all_tasks: List[Dict]) -> bool:
        """
        Apply AI's autonomous healing decision.
        """
        try:
            if ai_decision.get('should_reallocate'):
                new_assignee = ai_decision['recommended_assignee']
                old_assignee = task.get('assigned_to', 'Unassigned')
                
                # Update task with AI decision
                task['assigned_to'] = new_assignee
                task['mail_id'] = new_assignee
                
                # Add AI decision tracking
                current_status = task.get('status', '')
                task['status'] = f"AI-OPTIMIZED: Reallocated to {new_assignee} (Confidence: {ai_decision.get('confidence', 0.75):.0%})"
                task['ai_healing_timestamp'] = datetime.now().isoformat()
                task['ai_healing_reason'] = ai_decision.get('reason')
                
                print(f"  ✓ AI reallocated: {task.get('task_name')}")
                print(f"    From: {old_assignee} → To: {new_assignee}")
                print(f"    Reason: {ai_decision.get('reason')}")
                print(f"    Confidence: {ai_decision.get('confidence', 0.75):.0%}")
                
                return True
                
        except Exception as e:
            print(f"✗ Error applying AI healing: {e}")
            return False
        
        return False
    
    def _update_excel_file(self, tasks: List[Dict]):
        """
        Update the Excel file with AI-optimized tasks.
        """
        try:
            if not os.path.exists(self.wbs_file):
                print(f"⚠️ WBS file not found: {self.wbs_file}")
                return
            
            # Create backup
            backup_file = os.path.join(
                config.DATA_DIR, 
                f'project_wbs_ai_healing_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
            )
            import shutil
            shutil.copy(self.wbs_file, backup_file)
            
            # Update the Excel file
            parser = ExcelParser(self.wbs_file)
            parser.save_wbs(tasks, self.wbs_file)
            
            print(f"✓ Excel file updated with AI optimizations (backup: {os.path.basename(backup_file)})")
            
        except Exception as e:
            print(f"✗ Error updating Excel file: {e}")
    
    def _save_healing_results(self, results: Dict):
        """
        Save AI healing results for analysis and learning.
        """
        try:
            history_file = os.path.join(config.DATA_DIR, 'ai_healing_history.json')
            
            history = []
            if os.path.exists(history_file):
                with open(history_file, 'r') as f:
                    history = json.load(f)
            
            history.append({
                'timestamp': datetime.now().isoformat(),
                'results': results,
                'ai_powered': True
            })
            
            # Keep only last 100 entries
            history = history[-100:]
            
            with open(history_file, 'w') as f:
                json.dump(history, f, indent=2)
                
        except Exception as e:
            print(f"⚠️ Could not save AI healing history: {e}")
    
    def _save_notifications(self, notifications: List[Dict]):
        """
        Save AI healing notifications for dashboard.
        """
        try:
            existing_notifications = []
            if os.path.exists(self.notification_file):
                with open(self.notification_file, 'r') as f:
                    existing_notifications = json.load(f)
            
            # Add new AI notifications
            existing_notifications.extend(notifications)
            
            # Keep notifications from last 7 days
            cutoff_date = datetime.now() - timedelta(days=7)
            existing_notifications = [
                n for n in existing_notifications
                if datetime.fromisoformat(n['timestamp']) > cutoff_date
            ]
            
            with open(self.notification_file, 'w') as f:
                json.dump(existing_notifications, f, indent=2)
                
        except Exception as e:
            print(f"⚠️ Could not save notifications: {e}")
    
    def _calculate_average_confidence(self, results: Dict) -> float:
        """Calculate average AI confidence from decisions."""
        confidences = [d.get('confidence', 0.75) for d in results.get('ai_decisions', [])]
        return sum(confidences) / len(confidences) if confidences else 0.75
    
    def get_notifications(self) -> List[Dict]:
        """Get all current AI healing notifications."""
        try:
            if os.path.exists(self.notification_file):
                with open(self.notification_file, 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"⚠️ Could not load notifications: {e}")
            return []
    
    def mark_notification_read(self, notification_id: str):
        """Mark a notification as read."""
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
        """Clear all notifications."""
        try:
            if os.path.exists(self.notification_file):
                with open(self.notification_file, 'w') as f:
                    json.dump([], f)
        except Exception as e:
            print(f"⚠️ Could not clear notifications: {e}")
