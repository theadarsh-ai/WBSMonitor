"""
Email Generation Agent - Creates professional stakeholder communications.
Enhanced with AI for personalized, context-aware emails.
"""
from typing import List, Dict, Optional
from jinja2 import Template
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.date_calculator import DateCalculator
from utils.azure_ai_client import get_ai_client


class EmailGenerationAgent:
    """Agent responsible for generating professional emails with AI enhancement."""
    
    def __init__(self):
        self.date_calc = DateCalculator()
        self.ai_client = get_ai_client()
    
    def generate_escalation_email(self, task: Dict) -> Dict[str, str]:
        """
        Generate escalation email for critical task.
        
        Returns:
            Dictionary with 'subject', 'body', 'to', 'cc' keys
        """
        subject = self._generate_subject(task, 'URGENT ESCALATION')
        body = self._generate_body(task, is_escalation=True)
        
        return {
            'subject': subject,
            'body': body,
            'to': self._extract_emails(task),
            'cc': []
        }
    
    def generate_alert_email(self, task: Dict) -> Dict[str, str]:
        """
        Generate alert email for at-risk task.
        
        Returns:
            Dictionary with 'subject', 'body', 'to', 'cc' keys
        """
        subject = self._generate_subject(task, 'ALERT')
        body = self._generate_body(task, is_escalation=False)
        
        return {
            'subject': subject,
            'body': body,
            'to': self._extract_emails(task),
            'cc': []
        }
    
    def generate_morning_digest(self, categorized_tasks: Dict[str, List[Dict]], 
                                pm_email: str) -> Dict[str, str]:
        """
        Generate morning digest (9 AM) - Focus on overdue tasks.
        
        Returns:
            Dictionary with 'subject', 'body', 'to' keys
        """
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Count overdue tasks
        all_tasks = []
        for tasks in categorized_tasks.values():
            all_tasks.extend(tasks)
        
        overdue_tasks = [t for t in all_tasks if t.get('days_overdue', 0) > 0]
        overdue_count = len(overdue_tasks)
        
        subject = f"🌅 Morning Priority: {overdue_count} Overdue Tasks Require Attention - {today}"
        body = self._generate_morning_digest_body(overdue_tasks, categorized_tasks)
        
        return {
            'subject': subject,
            'body': body,
            'to': [pm_email],
            'cc': []
        }
    
    def generate_afternoon_digest(self, categorized_tasks: Dict[str, List[Dict]], 
                                   pm_email: str) -> Dict[str, str]:
        """
        Generate afternoon digest (2 PM) - Focus on risk updates.
        
        Returns:
            Dictionary with 'subject', 'body', 'to' keys
        """
        today = datetime.now().strftime("%Y-%m-%d")
        
        critical_tasks = categorized_tasks.get('critical_escalation', [])
        alert_tasks = categorized_tasks.get('alert', [])
        risk_count = len(critical_tasks) + len(alert_tasks)
        
        subject = f"⚠️ Afternoon Risk Alert: {risk_count} Issues Detected - {today}"
        body = self._generate_afternoon_digest_body(categorized_tasks)
        
        return {
            'subject': subject,
            'body': body,
            'to': [pm_email],
            'cc': []
        }
    
    def generate_daily_summary(self, categorized_tasks: Dict[str, List[Dict]], 
                              pm_email: str) -> Dict[str, str]:
        """
        Generate daily PM summary report (6 PM) - Full summary.
        
        Returns:
            Dictionary with 'subject', 'body', 'to' keys
        """
        today = datetime.now().strftime("%Y-%m-%d")
        subject = f"📊 Daily Project Summary: Complete Overview - {today}"
        
        body = self._generate_summary_body(categorized_tasks)
        
        return {
            'subject': subject,
            'body': body,
            'to': [pm_email],
            'cc': []
        }
    
    def _generate_subject(self, task: Dict, urgency: str) -> str:
        """Generate urgency-based subject line."""
        task_name = task.get('task_name', 'Unknown Task')
        module = task.get('module', '')
        
        return f"[{urgency}] {module} - {task_name}"
    
    def _extract_emails(self, task: Dict) -> List[str]:
        """Extract email addresses from task."""
        emails = []
        
        mail_id = task.get('mail_id', '')
        if mail_id and '@' in mail_id:
            emails.append(mail_id.strip())
        
        assigned_to = task.get('assigned_to', '')
        if assigned_to and '@' in assigned_to:
            emails.append(assigned_to.strip())
        
        # Remove duplicates
        return list(set(emails))
    
    def _generate_body(self, task: Dict, is_escalation: bool) -> str:
        """Generate email body HTML."""
        
        template_str = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .header { background-color: {{ header_color }}; color: white; padding: 20px; }
        .content { padding: 20px; }
        .task-details { background-color: #f4f4f4; padding: 15px; margin: 15px 0; border-left: 4px solid {{ border_color }}; }
        .detail-row { margin: 8px 0; }
        .label { font-weight: bold; }
        .action-items { background-color: #fff3cd; padding: 15px; margin: 15px 0; border-left: 4px solid #ffc107; }
        .footer { margin-top: 20px; font-size: 12px; color: #666; }
    </style>
</head>
<body>
    <div class="header">
        <h2>{{ header_title }}</h2>
    </div>
    
    <div class="content">
        <p>Dear {{ assigned_to }},</p>
        
        <p>{{ opening_message }}</p>
        
        <div class="task-details">
            <h3>Task Details</h3>
            <div class="detail-row"><span class="label">Task Name:</span> {{ task_name }}</div>
            <div class="detail-row"><span class="label">Module:</span> {{ module }}</div>
            <div class="detail-row"><span class="label">Product Owner:</span> {{ product_owner }}</div>
            <div class="detail-row"><span class="label">Start Date:</span> {{ start_date }}</div>
            <div class="detail-row"><span class="label">End Date:</span> {{ end_date }}</div>
            <div class="detail-row"><span class="label">Completion:</span> {{ completion }}%</div>
            <div class="detail-row"><span class="label">Status:</span> {{ status }}</div>
            <div class="detail-row"><span class="label">Days Overdue:</span> {{ days_overdue }}</div>
        </div>
        
        <div class="action-items">
            <h3>⚠️ Required Actions</h3>
            <ul>
                {{ action_items }}
            </ul>
        </div>
        
        <p><strong>Impact Analysis:</strong><br>
        {{ impact_analysis }}</p>
        
        <p>{{ closing_message }}</p>
        
        <div class="footer">
            <p>This is an automated message from the Project Monitoring AI System.<br>
            Generated on: {{ timestamp }}</p>
        </div>
    </div>
</body>
</html>
        """
        
        template = Template(template_str)
        
        days_overdue = self.date_calc.days_overdue(task.get('end_date'))
        
        if is_escalation:
            header_color = "#dc3545"
            border_color = "#dc3545"
            header_title = "URGENT: Task Escalation Required"
            opening_message = "This task requires immediate attention and escalation due to critical delays."
            action_items = """
                <li>Provide immediate status update on current blockers</li>
                <li>Submit revised completion timeline within 24 hours</li>
                <li>Schedule emergency review meeting with stakeholders</li>
                <li>Identify resources needed to expedite completion</li>
            """
            impact_analysis = f"This task is {days_overdue} days overdue and is blocking dependent tasks in the project timeline. Immediate action is required to prevent cascade delays across the {task.get('module', 'project')} module."
            closing_message = "Please treat this as highest priority and respond within 4 hours."
        else:
            header_color = "#ffc107"
            border_color = "#ffc107"
            header_title = "ALERT: Task Requires Attention"
            opening_message = "This task has been flagged for attention due to potential schedule risk."
            action_items = """
                <li>Review current task progress and update completion percentage</li>
                <li>Identify any blockers or dependencies preventing completion</li>
                <li>Provide estimated completion date</li>
                <li>Escalate if additional support is needed</li>
            """
            impact_analysis = f"This task is approaching its deadline with low completion ({task.get('completion_percent', 0)}%). Early intervention can prevent escalation and maintain project schedule."
            closing_message = "Please provide an update within 24 hours."
        
        return template.render(
            header_color=header_color,
            border_color=border_color,
            header_title=header_title,
            opening_message=opening_message,
            task_name=task.get('task_name', 'N/A'),
            module=task.get('module', 'N/A'),
            product_owner=task.get('product_owner', 'N/A'),
            assigned_to=task.get('assigned_to', 'Team Member'),
            start_date=self.date_calc.format_date(task.get('start_date')),
            end_date=self.date_calc.format_date(task.get('end_date')),
            completion=task.get('completion_percent', 0),
            status=task.get('status', 'N/A'),
            days_overdue=max(0, days_overdue),
            action_items=action_items,
            impact_analysis=impact_analysis,
            closing_message=closing_message,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    
    def _generate_summary_body(self, categorized_tasks: Dict[str, List[Dict]]) -> str:
        """Generate daily summary body HTML."""
        
        template_str = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .header { background-color: #007bff; color: white; padding: 20px; }
        .content { padding: 20px; }
        .summary-section { margin: 20px 0; }
        .task-list { background-color: #f8f9fa; padding: 15px; margin: 10px 0; }
        .critical { border-left: 4px solid #dc3545; }
        .alert { border-left: 4px solid #ffc107; }
        .at-risk { border-left: 4px solid #fd7e14; }
        .on-track { border-left: 4px solid #28a745; }
        .task-item { margin: 10px 0; padding: 10px; background: white; }
        .stats { display: flex; justify-content: space-around; margin: 20px 0; }
        .stat-box { text-align: center; padding: 15px; background: #e9ecef; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="header">
        <h2>Daily Project Status Summary</h2>
        <p>{{ date }}</p>
    </div>
    
    <div class="content">
        <div class="stats">
            <div class="stat-box">
                <h3 style="color: #dc3545;">{{ critical_count }}</h3>
                <p>Critical Escalation</p>
            </div>
            <div class="stat-box">
                <h3 style="color: #ffc107;">{{ alert_count }}</h3>
                <p>Alerts</p>
            </div>
            <div class="stat-box">
                <h3 style="color: #fd7e14;">{{ at_risk_count }}</h3>
                <p>At Risk</p>
            </div>
            <div class="stat-box">
                <h3 style="color: #28a745;">{{ on_track_count }}</h3>
                <p>On Track</p>
            </div>
        </div>
        
        {% if critical_tasks or alert_tasks %}
        <div style="background: #fff3cd; border: 2px solid #dc3545; border-radius: 8px; padding: 20px; margin: 20px 0;">
            <h2 style="color: #dc3545; margin-top: 0;">⚠️ TASKS REQUIRING IMMEDIATE ATTENTION ({{ immediate_attention }})</h2>
            <p style="font-weight: bold;">The following tasks need your immediate action to prevent project delays:</p>
        </div>
        {% endif %}
        
        {% if critical_tasks %}
        <div class="summary-section">
            <h3>🔴 Critical Escalation Tasks ({{ critical_count }})</h3>
            <div class="task-list critical">
                {% for task in critical_tasks %}
                <div class="task-item">
                    <strong>{{ task.task_name }}</strong> ({{ task.module }})<br>
                    Assigned to: {{ task.assigned_to }} | Owner: {{ task.product_owner }}<br>
                    Start: {{ task.start_date or 'N/A' }} | End: {{ task.end_date or 'N/A' }}<br>
                    Completion: {{ task.completion_percent }}% | Days Overdue: {{ task.days_overdue or 0 }}<br>
                    <em>{{ task.risk_reason }}</em>
                </div>
                {% endfor %}
            </div>
        </div>
        {% endif %}
        
        {% if alert_tasks %}
        <div class="summary-section">
            <h3>🟡 Alert Tasks ({{ alert_count }})</h3>
            <div class="task-list alert">
                {% for task in alert_tasks %}
                <div class="task-item">
                    <strong>{{ task.task_name }}</strong> ({{ task.module }})<br>
                    Assigned to: {{ task.assigned_to }} | Owner: {{ task.product_owner }}<br>
                    Start: {{ task.start_date or 'N/A' }} | End: {{ task.end_date or 'N/A' }}<br>
                    Completion: {{ task.completion_percent }}%<br>
                    <em>{{ task.risk_reason }}</em>
                </div>
                {% endfor %}
            </div>
        </div>
        {% endif %}
        
        <div class="summary-section">
            <h3>📊 Overall Project Health</h3>
            <p>Total Tasks: {{ total_tasks }}</p>
            <p>Completion Rate: {{ completion_rate }}%</p>
            <p>Tasks Requiring Immediate Attention: {{ immediate_attention }}</p>
        </div>
        
        <p style="margin-top: 30px; font-size: 12px; color: #666;">
            This automated summary was generated by the Project Monitoring AI System on {{ timestamp }}.
        </p>
    </div>
</body>
</html>
        """
        
        template = Template(template_str)
        
        critical_tasks = categorized_tasks.get('critical_escalation', [])
        alert_tasks = categorized_tasks.get('alert', [])
        at_risk_tasks = categorized_tasks.get('at_risk', [])
        on_track_tasks = categorized_tasks.get('on_track', [])
        
        total_tasks = sum(len(tasks) for tasks in categorized_tasks.values())
        total_completion = sum(task.get('completion_percent', 0) for tasks in categorized_tasks.values() for task in tasks)
        completion_rate = round(total_completion / total_tasks if total_tasks > 0 else 0, 1)
        
        return template.render(
            date=datetime.now().strftime("%Y-%m-%d"),
            critical_count=len(critical_tasks),
            alert_count=len(alert_tasks),
            at_risk_count=len(at_risk_tasks),
            on_track_count=len(on_track_tasks),
            critical_tasks=critical_tasks,
            alert_tasks=alert_tasks,
            total_tasks=total_tasks,
            completion_rate=completion_rate,
            immediate_attention=len(critical_tasks) + len(alert_tasks),
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    
    def _generate_morning_digest_body(self, overdue_tasks: List[Dict], 
                                      categorized_tasks: Dict[str, List[Dict]]) -> str:
        """Generate morning digest body HTML - Focus on overdue tasks."""
        
        template_str = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .header { background-color: #ff6b6b; color: white; padding: 20px; }
        .content { padding: 20px; }
        .priority-banner { background: #ffe5e5; border: 2px solid #ff6b6b; border-radius: 8px; padding: 20px; margin: 20px 0; }
        .task-list { background-color: #f8f9fa; padding: 15px; margin: 10px 0; border-left: 4px solid #ff6b6b; }
        .task-item { margin: 10px 0; padding: 15px; background: white; border-left: 3px solid #ff6b6b; }
        .stats-row { display: flex; justify-content: space-around; margin: 20px 0; }
        .stat-box { text-align: center; padding: 15px; background: #e9ecef; border-radius: 5px; min-width: 100px; }
    </style>
</head>
<body>
    <div class="header">
        <h2>🌅 Morning Priority Digest</h2>
        <p>{{ date }} - Start Your Day Right</p>
    </div>
    
    <div class="content">
        <div class="priority-banner">
            <h2 style="color: #ff6b6b; margin-top: 0;">⚠️ {{ overdue_count }} OVERDUE TASKS NEED YOUR ATTENTION TODAY</h2>
            <p style="font-size: 16px;"><strong>These tasks are past their deadline and require immediate action to minimize project impact.</strong></p>
        </div>
        
        <div class="stats-row">
            <div class="stat-box">
                <h3 style="color: #ff6b6b;">{{ overdue_count }}</h3>
                <p>Overdue Tasks</p>
            </div>
            <div class="stat-box">
                <h3 style="color: #dc3545;">{{ critical_count }}</h3>
                <p>Critical</p>
            </div>
            <div class="stat-box">
                <h3 style="color: #ffc107;">{{ alert_count }}</h3>
                <p>Alerts</p>
            </div>
        </div>
        
        <h3>🔴 Today's Priority Tasks (Overdue)</h3>
        <p><strong>Take action on these tasks today to get back on track:</strong></p>
        
        <div class="task-list">
            {% for task in overdue_tasks[:10] %}
            <div class="task-item">
                <strong style="font-size: 16px; color: #dc3545;">{{ task.task_name }}</strong><br>
                <span style="color: #666;">Module: {{ task.module }} | Assigned: {{ task.assigned_to }}</span><br>
                <span style="color: #666;">Due Date: {{ task.end_date }} | Completion: {{ task.completion_percent }}%</span><br>
                <span style="background: #ffe5e5; padding: 4px 8px; border-radius: 3px; color: #dc3545; font-weight: bold;">
                    ⏰ {{ task.days_overdue }} days overdue
                </span><br>
                {% if task.risk_reason %}
                <em style="color: #666;">Issue: {{ task.risk_reason }}</em>
                {% endif %}
            </div>
            {% endfor %}
            
            {% if overdue_count > 10 %}
            <p style="text-align: center; color: #666; margin-top: 15px;">
                <em>... and {{ overdue_count - 10 }} more overdue tasks. See full dashboard for complete list.</em>
            </p>
            {% endif %}
        </div>
        
        <div style="background: #fff3cd; padding: 15px; margin: 20px 0; border-radius: 5px;">
            <h4>💡 Recommended Morning Actions:</h4>
            <ul>
                <li>Review the top 5 overdue tasks and prioritize for today</li>
                <li>Contact task assignees to understand blockers</li>
                <li>Reallocate resources if needed to accelerate completion</li>
                <li>Update task progress before the afternoon check-in</li>
            </ul>
        </div>
        
        <p style="margin-top: 30px; font-size: 12px; color: #666;">
            Next update: Afternoon Risk Alert at 2:00 PM<br>
            This automated digest was generated by the AI Monitoring System on {{ timestamp }}.
        </p>
    </div>
</body>
</html>
        """
        
        template = Template(template_str)
        
        critical_tasks = categorized_tasks.get('critical_escalation', [])
        alert_tasks = categorized_tasks.get('alert', [])
        
        return template.render(
            date=datetime.now().strftime("%A, %B %d, %Y"),
            overdue_count=len(overdue_tasks),
            critical_count=len(critical_tasks),
            alert_count=len(alert_tasks),
            overdue_tasks=sorted(overdue_tasks, key=lambda x: x.get('days_overdue', 0), reverse=True),
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    
    def _generate_afternoon_digest_body(self, categorized_tasks: Dict[str, List[Dict]]) -> str:
        """Generate afternoon digest body HTML - Focus on risk updates."""
        
        template_str = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .header { background-color: #ffa500; color: white; padding: 20px; }
        .content { padding: 20px; }
        .risk-banner { background: #fff4e5; border: 2px solid #ffa500; border-radius: 8px; padding: 20px; margin: 20px 0; }
        .task-list { background-color: #f8f9fa; padding: 15px; margin: 10px 0; }
        .critical { border-left: 4px solid #dc3545; }
        .alert { border-left: 4px solid #ffc107; }
        .task-item { margin: 10px 0; padding: 15px; background: white; }
        .stats-row { display: flex; justify-content: space-around; margin: 20px 0; }
        .stat-box { text-align: center; padding: 15px; background: #e9ecef; border-radius: 5px; min-width: 100px; }
        .status-badge { padding: 4px 12px; border-radius: 3px; font-weight: bold; font-size: 12px; }
        .critical-badge { background: #ffe5e5; color: #dc3545; }
        .alert-badge { background: #fff3cd; color: #856404; }
    </style>
</head>
<body>
    <div class="header">
        <h2>⚠️ Afternoon Risk Alert</h2>
        <p>{{ date }} - Mid-Day Risk Assessment</p>
    </div>
    
    <div class="content">
        <div class="risk-banner">
            <h2 style="color: #ffa500; margin-top: 0;">📊 {{ risk_count }} TASKS REQUIRE ATTENTION</h2>
            <p style="font-size: 16px;"><strong>AI has detected the following risks and issues that emerged or escalated since this morning.</strong></p>
        </div>
        
        <div class="stats-row">
            <div class="stat-box">
                <h3 style="color: #dc3545;">{{ critical_count }}</h3>
                <p>Critical Issues</p>
            </div>
            <div class="stat-box">
                <h3 style="color: #ffc107;">{{ alert_count }}</h3>
                <p>Active Alerts</p>
            </div>
            <div class="stat-box">
                <h3 style="color: #fd7e14;">{{ at_risk_count }}</h3>
                <p>At Risk</p>
            </div>
        </div>
        
        {% if critical_tasks %}
        <h3>🔴 Critical Escalations ({{ critical_count }})</h3>
        <p><strong>These tasks have reached critical status and need immediate intervention:</strong></p>
        <div class="task-list critical">
            {% for task in critical_tasks %}
            <div class="task-item">
                <span class="status-badge critical-badge">CRITICAL</span><br>
                <strong style="font-size: 16px; color: #dc3545;">{{ task.task_name }}</strong><br>
                <span style="color: #666;">Module: {{ task.module }} | Assigned: {{ task.assigned_to }}</span><br>
                <span style="color: #666;">Due: {{ task.end_date }} | Completion: {{ task.completion_percent }}%</span><br>
                {% if task.risk_reason %}
                <em style="color: #dc3545;">⚠️ {{ task.risk_reason }}</em>
                {% endif %}
            </div>
            {% endfor %}
        </div>
        {% endif %}
        
        {% if alert_tasks %}
        <h3>🟡 Active Alerts ({{ alert_count }})</h3>
        <p><strong>These tasks are showing warning signs and need monitoring:</strong></p>
        <div class="task-list alert">
            {% for task in alert_tasks %}
            <div class="task-item">
                <span class="status-badge alert-badge">ALERT</span><br>
                <strong style="font-size: 16px;">{{ task.task_name }}</strong><br>
                <span style="color: #666;">Module: {{ task.module }} | Assigned: {{ task.assigned_to }}</span><br>
                <span style="color: #666;">Due: {{ task.end_date }} | Completion: {{ task.completion_percent }}%</span><br>
                {% if task.risk_reason %}
                <em style="color: #856404;">{{ task.risk_reason }}</em>
                {% endif %}
            </div>
            {% endfor %}
        </div>
        {% endif %}
        
        <div style="background: #e7f3ff; padding: 15px; margin: 20px 0; border-radius: 5px; border-left: 4px solid #007bff;">
            <h4>🎯 Recommended Afternoon Actions:</h4>
            <ul>
                <li>Address critical issues before end of day</li>
                <li>Schedule urgent meetings with stakeholders for critical tasks</li>
                <li>Review alert tasks and implement preventive measures</li>
                <li>Update project status for transparency</li>
            </ul>
        </div>
        
        <p style="margin-top: 30px; font-size: 12px; color: #666;">
            Next update: Full Daily Summary at 6:00 PM<br>
            This automated digest was generated by the AI Monitoring System on {{ timestamp }}.
        </p>
    </div>
</body>
</html>
        """
        
        template = Template(template_str)
        
        critical_tasks = categorized_tasks.get('critical_escalation', [])
        alert_tasks = categorized_tasks.get('alert', [])
        at_risk_tasks = categorized_tasks.get('at_risk', [])
        
        return template.render(
            date=datetime.now().strftime("%A, %B %d, %Y"),
            risk_count=len(critical_tasks) + len(alert_tasks),
            critical_count=len(critical_tasks),
            alert_count=len(alert_tasks),
            at_risk_count=len(at_risk_tasks),
            critical_tasks=critical_tasks,
            alert_tasks=alert_tasks,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
