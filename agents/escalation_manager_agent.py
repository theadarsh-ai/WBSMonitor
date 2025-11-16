"""
Escalation Manager Agent - Handles severity-based routing and escalation.
"""
from typing import List, Dict, Any
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.email_sender import EmailSender
from agents.email_generation_agent import EmailGenerationAgent
from utils.email_tracker import has_email_been_sent_today, mark_email_sent, get_emails_sent_today
import config


class EscalationManagerAgent:
    """Agent responsible for intelligent escalation management."""
    
    def __init__(self):
        self.email_generator = EmailGenerationAgent()
        self.email_sender = None
        
        if config.SMTP_USERNAME and config.SMTP_PASSWORD:
            self.email_sender = EmailSender(
                smtp_server=config.SMTP_SERVER,
                smtp_port=config.SMTP_PORT,
                smtp_username=config.SMTP_USERNAME,
                smtp_password=config.SMTP_PASSWORD,
                from_email=config.EMAIL_FROM
            )
    
    def process_escalations(self, categorized_tasks: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """
        Process all escalations and alerts, sending appropriate emails.
        Only sends each email once per day to avoid spam.
        
        Returns:
            Summary of escalations processed
        """
        # Show daily email status
        sent_today_count, sent_task_ids = get_emails_sent_today()
        if sent_today_count > 0:
            print(f"📧 Already sent {sent_today_count} emails today for {len(sent_task_ids)} tasks")
        
        results = {
            'escalations_sent': 0,
            'alerts_sent': 0,
            'failed': 0,
            'skipped_already_sent': 0,
            'details': []
        }
        
        # Process critical escalations
        for task in categorized_tasks.get('critical_escalation', []):
            success = self._send_escalation(task)
            if success:
                results['escalations_sent'] += 1
                results['details'].append({
                    'task': task['task_name'],
                    'type': 'escalation',
                    'status': 'sent'
                })
            else:
                results['failed'] += 1
                results['details'].append({
                    'task': task['task_name'],
                    'type': 'escalation',
                    'status': 'failed'
                })
        
        # Process alerts
        for task in categorized_tasks.get('alert', []):
            success = self._send_alert(task)
            if success:
                results['alerts_sent'] += 1
                results['details'].append({
                    'task': task['task_name'],
                    'type': 'alert',
                    'status': 'sent'
                })
            else:
                results['failed'] += 1
                results['details'].append({
                    'task': task['task_name'],
                    'type': 'alert',
                    'status': 'failed'
                })
        
        return results
    
    def _send_escalation(self, task: Dict) -> bool:
        """Send escalation email for critical task (once per day)."""
        task_id = task.get('task_id', task.get('task_name', 'unknown'))
        
        # Check if already sent today
        if has_email_been_sent_today(task_id, 'escalation'):
            print(f"⏭️  Skipped escalation for '{task['task_name']}' (already sent today)")
            return True  # Return True to not count as failed
        
        email_data = self.email_generator.generate_escalation_email(task)
        success = self._send_email(email_data)
        
        if success:
            mark_email_sent(task_id, 'escalation')
        
        return success
    
    def _send_alert(self, task: Dict) -> bool:
        """Send alert email for at-risk task (once per day)."""
        task_id = task.get('task_id', task.get('task_name', 'unknown'))
        
        # Check if already sent today
        if has_email_been_sent_today(task_id, 'alert'):
            print(f"⏭️  Skipped alert for '{task['task_name']}' (already sent today)")
            return True  # Return True to not count as failed
        
        email_data = self.email_generator.generate_alert_email(task)
        success = self._send_email(email_data)
        
        if success:
            mark_email_sent(task_id, 'alert')
        
        return success
    
    def _send_email(self, email_data: Dict) -> bool:
        """Send email using configured sender."""
        if not self.email_sender:
            print(f"⚠️ Email not configured. Would send: {email_data['subject']}")
            print(f"   To: {', '.join(email_data['to'])}")
            return True  # Return True for demo mode
        
        if not email_data['to']:
            print(f"⚠️ No recipients for email: {email_data['subject']}")
            return False
        
        return self.email_sender.send_email(
            to_emails=email_data['to'],
            subject=email_data['subject'],
            body_html=email_data['body'],
            cc_emails=email_data.get('cc', [])
        )
    
    def send_daily_summary(self, categorized_tasks: Dict[str, List[Dict]], 
                          pm_email: str = "adarsh.velmurugan@verint.com") -> bool:
        """Send daily summary to project manager."""
        email_data = self.email_generator.generate_daily_summary(categorized_tasks, pm_email)
        return self._send_email(email_data)
