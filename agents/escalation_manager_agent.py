"""
Escalation Manager Agent - 100% AI-Powered Escalation Decisions
AI autonomously decides when, how, and to whom to escalate issues.
NO hardcoded rules - ALL escalation decisions made by AI.
"""
from typing import List, Dict, Any, Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.email_sender import EmailSender
from agents.email_generation_agent import EmailGenerationAgent
from utils.email_tracker import has_email_been_sent_today, mark_email_sent, get_emails_sent_today
from utils.ai_decision_engine import get_decision_engine
from utils.azure_ai_client import get_ai_client
import config


class EscalationManagerAgent:
    """
    100% AI-Agentic Escalation Manager.
    AI autonomously decides ALL escalation strategies.
    """
    
    def __init__(self):
        self.email_generator = EmailGenerationAgent()
        self.email_sender = None
        self.decision_engine = get_decision_engine()
        self.ai_client = get_ai_client()
        
        if config.SMTP_USERNAME and config.SMTP_PASSWORD:
            self.email_sender = EmailSender(
                smtp_server=config.SMTP_SERVER,
                smtp_port=config.SMTP_PORT,
                smtp_username=config.SMTP_USERNAME,
                smtp_password=config.SMTP_PASSWORD,
                from_email=config.EMAIL_FROM
            )
        
        print("🤖 Escalation Manager initialized in FULLY AUTONOMOUS AI mode")
    
    def process_escalations(self, categorized_tasks: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """
        AI autonomously processes escalations - decides WHAT, WHEN, and WHO.
        NO individual emails sent - all alerts saved for daily digest at 6 PM.
        
        Returns:
            Summary of AI-driven escalations
        """
        results = {
            'escalations_sent': 0,
            'alerts_sent': 0,
            'ai_decisions': [],
            'failed': 0,
            'skipped_by_ai': 0,
            'skipped_already_sent': 0
        }
        
        print("\n🤖 AI analyzing tasks for daily digest (no individual emails)...")
        
        # AI decides which tasks need escalation (not based on hardcoded categories)
        all_tasks = []
        for category, tasks in categorized_tasks.items():
            all_tasks.extend(tasks)
        
        # For each potential escalation, AI decides
        for task in all_tasks:
            ai_decision = self._ai_should_escalate(task)
            
            if ai_decision and ai_decision.get('should_escalate'):
                # Track for daily summary (NO immediate email)
                if ai_decision['escalation_level'] in ['immediate', 'urgent']:
                    results['escalations_sent'] += 1
                else:
                    results['alerts_sent'] += 1
                
                results['ai_decisions'].append({
                    'task': task['task_name'],
                    'level': ai_decision['escalation_level'],
                    'reason': ai_decision.get('reason'),
                    'confidence': ai_decision.get('confidence', 0.75)
                })
            else:
                # AI decided not to escalate
                if ai_decision:
                    results['skipped_by_ai'] += 1
        
        # Print AI decision summary
        if results['ai_decisions']:
            avg_confidence = sum(d['confidence'] for d in results['ai_decisions']) / len(results['ai_decisions'])
            print(f"\n✓ AI Escalation Analysis:")
            print(f"  - Tasks for daily digest: {results['escalations_sent'] + results['alerts_sent']}")
            print(f"  - Critical: {results['escalations_sent']}, Alerts: {results['alerts_sent']}")
            print(f"  - AI Confidence: {avg_confidence:.0%}")
            print(f"  ℹ️  Daily digest will be sent at 6 PM")
        
        return results
    
    def _ai_should_escalate(self, task: Dict) -> Optional[Dict]:
        """
        AI autonomously decides whether to escalate a task.
        
        Returns:
            AI decision dict or None
        """
        if not self.ai_client.is_available():
            # Fallback: only escalate critical tasks
            if task.get('risk_level') == 'critical_escalation':
                return {
                    'should_escalate': True,
                    'escalation_level': 'urgent',
                    'recipients': [task.get('mail_id', task.get('assigned_to'))],
                    'reason': 'Fallback escalation (AI unavailable)',
                    'confidence': 0.5
                }
            return None
        
        # Get potential recipients
        recipients = self._get_potential_recipients(task)
        
        # AI makes escalation decision
        ai_decision = self.decision_engine.should_escalate_ai(task, recipients)
        
        return ai_decision if ai_decision.get('should_escalate') else None
    
    def _get_potential_recipients(self, task: Dict) -> List[str]:
        """Get potential email recipients for a task."""
        recipients = []
        
        # Task assignee
        if task.get('mail_id'):
            recipients.append(task['mail_id'])
        elif task.get('assigned_to'):
            recipients.append(task['assigned_to'])
        
        # Module lead (if available)
        # PM (if available)
        
        return [r for r in recipients if r and '@' in r]
    
    def _send_ai_escalation(self, task: Dict, ai_decision: Dict) -> bool:
        """
        Send AI-decided escalation email.
        
        Args:
            task: Task dictionary
            ai_decision: AI's escalation decision
            
        Returns:
            Success boolean
        """
        escalation_level = ai_decision.get('escalation_level', 'routine')
        
        # AI generates email content
        email_data = self._generate_ai_email(task, ai_decision)
        
        if not email_data:
            print(f"⚠️ Could not generate email for '{task['task_name']}'")
            return False
        
        print(f"📧 AI sending {escalation_level} escalation: '{task['task_name']}'")
        print(f"   Reason: {ai_decision.get('reason')}")
        print(f"   Confidence: {ai_decision.get('confidence', 0.75):.0%}")
        print(f"   Recipients: {', '.join(email_data['to'])}")
        
        return self._send_email(email_data)
    
    def _generate_ai_email(self, task: Dict, ai_decision: Dict) -> Optional[Dict]:
        """
        Generate email content based on AI decision.
        Uses AI to create personalized, context-aware emails.
        """
        recipients = ai_decision.get('recipients', [])
        if not recipients:
            return None
        
        # AI generates email subject and body
        if not self.ai_client.is_available():
            # Fallback to template
            return self.email_generator.generate_alert_email(task)
        
        system_prompt = f"""You are an expert AI business communication writer.
Generate a professional escalation email for a project task issue.

Escalation Level: {ai_decision.get('escalation_level', 'routine')}
Task Issue: {ai_decision.get('reason')}

Create an email that is:
- Professional and respectful
- Clear about the issue and impact
- Actionable with specific next steps
- Appropriate urgency for {ai_decision.get('escalation_level')} level

Return JSON:
{{
    "subject": "email subject line",
    "body_html": "<html email body with formatting>"
}}"""
        
        task_details = f"""Task: {task.get('task_name')}
Module: {task.get('module', 'N/A')}
Completion: {task.get('completion_percent', 0)}%
Due Date: {task.get('end_date', 'N/A')}
Assigned To: {task.get('assigned_to', 'Unassigned')}
Risk Level: {task.get('risk_level', 'N/A')}
Issue: {ai_decision.get('reason')}"""
        
        try:
            response = self.ai_client.generate_response(system_prompt, task_details)
            
            # Parse JSON
            import json
            response_clean = response.strip()
            if '```json' in response_clean:
                response_clean = response_clean.split('```json')[1].split('```')[0].strip()
            elif '```' in response_clean:
                response_clean = response_clean.split('```')[1].split('```')[0].strip()
            
            email_content = json.loads(response_clean)
            
            return {
                'to': recipients,
                'cc': [],
                'subject': email_content['subject'],
                'body': email_content['body_html']
            }
            
        except Exception as e:
            print(f"⚠️ AI email generation error: {e}")
            # Fallback to template
            return self.email_generator.generate_alert_email(task)
    
    def _send_email(self, email_data: Dict) -> bool:
        """Send email using configured sender."""
        if not self.email_sender:
            print(f"ℹ️  Email not configured. AI would send: {email_data['subject']}")
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
        """Send AI-generated daily summary to project manager."""
        email_data = self.email_generator.generate_daily_summary(categorized_tasks, pm_email)
        return self._send_email(email_data)
