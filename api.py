"""
Flask API server for the Autonomous Project Monitoring System.
This file provides the REST API endpoints for the dashboard frontend.
"""
import os
import sys
from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
from dateutil import parser as date_parser
from datetime import datetime
import time

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.supervisor_agent import MasterSupervisorAgent
from agents.data_ingestion_agent import DataIngestionAgent
from agents.risk_analysis_agent import RiskAnalysisAgent
from agents.dependency_tracker_agent import DependencyTrackerAgent
from agents.self_healing_agent import SelfHealingAgent
import config

# Flask API
app = Flask(__name__)
CORS(app)

# Cache for AI analysis results (expires after 5 minutes)
_dashboard_cache = {
    'data': None,
    'timestamp': 0,
    'ttl': 300  # 5 minutes cache
}


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy"})


@app.route('/api/dashboard-data', methods=['GET'])
def get_dashboard_data():
    """Get all dashboard data with caching for AI results."""
    global _dashboard_cache
    
    try:
        current_time = time.time()
        force_refresh = request.args.get('refresh', 'false').lower() == 'true'
        
        # Check if cache is valid
        cache_valid = (
            _dashboard_cache['data'] is not None and
            current_time - _dashboard_cache['timestamp'] < _dashboard_cache['ttl'] and
            not force_refresh
        )
        
        if cache_valid:
            print("✓ Serving cached dashboard data")
            return jsonify(_dashboard_cache['data'])
        
        # Cache expired or refresh requested - run AI analysis
        print("🤖 Running fresh AI analysis...")
        data_agent = DataIngestionAgent()
        risk_agent = RiskAnalysisAgent()
        dep_agent = DependencyTrackerAgent()
        
        tasks = data_agent.fetch_wbs_data()
        categorized_tasks = risk_agent.analyze_tasks(tasks)
        dep_agent.build_dependency_graph(tasks)
        
        total_tasks = len(tasks)
        critical = len(categorized_tasks.get('critical_escalation', []))
        alerts = len(categorized_tasks.get('alert', []))
        at_risk = len(categorized_tasks.get('at_risk', []))
        on_track = len(categorized_tasks.get('on_track', []))
        
        avg_completion = sum(task.get('completion_percent', 0) for task in tasks) / total_tasks if total_tasks > 0 else 0
        
        risk_distribution = {
            'critical': critical,
            'alert': alerts,
            'at_risk': at_risk,
            'on_track': on_track
        }
        
        module_breakdown = {}
        for task in tasks:
            module = task.get('module', 'Unknown')
            if module not in module_breakdown:
                module_breakdown[module] = 0
            module_breakdown[module] += 1
        
        # Serialize tasks to include end_date
        critical_tasks_serialized = [serialize_task_for_json(task) for task in categorized_tasks.get('critical_escalation', [])[:10]]
        alerts_list_serialized = [serialize_task_for_json(task) for task in categorized_tasks.get('alert', [])[:10]]
        
        result = {
            'metrics': {
                'total_tasks': total_tasks,
                'critical_escalations': critical,
                'alerts': alerts,
                'at_risk': at_risk,
                'avg_completion': round(avg_completion, 1)
            },
            'risk_distribution': risk_distribution,
            'module_breakdown': module_breakdown,
            'critical_tasks': critical_tasks_serialized,
            'alerts_list': alerts_list_serialized,
            'dependency_stats': {
                'nodes': dep_agent.dependency_graph.number_of_nodes(),
                'edges': dep_agent.dependency_graph.number_of_edges()
            },
            'cached_at': datetime.now().isoformat(),
            'cache_expires_in': _dashboard_cache['ttl']
        }
        
        # Update cache
        _dashboard_cache['data'] = result
        _dashboard_cache['timestamp'] = current_time
        print(f"✓ AI analysis complete - cache updated (expires in {_dashboard_cache['ttl']}s)")
        
        return jsonify(result)
    except Exception as e:
        print(f"❌ Dashboard error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/trigger-monitoring', methods=['POST'])
def trigger_monitoring():
    """Trigger a monitoring cycle."""
    try:
        supervisor = MasterSupervisorAgent()
        result = supervisor.execute_monitoring_cycle()
        return jsonify({
            'success': True,
            'result': str(result)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/chatbot', methods=['POST'])
def chatbot():
    """Handle chatbot interactions."""
    try:
        data = request.get_json()
        user_message = data.get('message', '').lower()
        
        data_agent = DataIngestionAgent()
        tasks = data_agent.fetch_wbs_data()
        
        response = process_chatbot_message(user_message, tasks)
        
        return jsonify({
            'response': response.get('message'),
            'tasks': response.get('tasks', []),
            'action': response.get('action', None)
        })
    except Exception as e:
        return jsonify({'error': str(e), 'response': 'Sorry, I encountered an error processing your request.'}), 500


@app.route('/api/notifications', methods=['GET'])
def get_notifications():
    """Get all notifications from self-healing agent."""
    try:
        healing_agent = SelfHealingAgent()
        notifications = healing_agent.get_notifications()
        
        unread_count = sum(1 for n in notifications if not n.get('read', False))
        
        return jsonify({
            'notifications': notifications,
            'unread_count': unread_count,
            'total_count': len(notifications)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/notifications/<notification_id>/read', methods=['POST'])
def mark_notification_read(notification_id):
    """Mark a notification as read."""
    try:
        healing_agent = SelfHealingAgent()
        healing_agent.mark_notification_read(notification_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/notifications/clear', methods=['POST'])
def clear_notifications():
    """Clear all notifications."""
    try:
        healing_agent = SelfHealingAgent()
        healing_agent.clear_all_notifications()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/tasks/by-date', methods=['POST'])
def get_tasks_by_date():
    """Get tasks by date range."""
    try:
        data = request.get_json()
        target_date_str = data.get('date')
        
        if not target_date_str:
            return jsonify({'error': 'Date parameter is required'}), 400
        
        target_date = date_parser.parse(target_date_str)
        
        data_agent = DataIngestionAgent()
        tasks = data_agent.fetch_wbs_data()
        
        matching_tasks = []
        for task in tasks:
            end_date = task.get('end_date')
            if end_date is not None and end_date.date() <= target_date.date():
                matching_tasks.append(serialize_task_for_json(task))
        
        return jsonify({
            'tasks': matching_tasks,
            'count': len(matching_tasks),
            'query_date': target_date.strftime('%Y-%m-%d')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task by ID."""
    try:
        from utils.excel_parser import ExcelParser
        
        wbs_file = os.path.join(config.DATA_DIR, 'project_wbs.xlsx')
        if not os.path.exists(wbs_file):
            return jsonify({'error': 'WBS file not found'}), 404
        
        parser = ExcelParser(wbs_file)
        tasks = parser.parse_wbs()
        
        task_found = False
        updated_tasks = []
        for task in tasks:
            if task.get('task_id') != task_id:
                updated_tasks.append(task)
            else:
                task_found = True
        
        if not task_found:
            return jsonify({'error': f'Task {task_id} not found'}), 404
        
        backup_file = os.path.join(config.DATA_DIR, f'project_wbs_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx')
        os.rename(wbs_file, backup_file)
        
        parser.save_wbs(updated_tasks, wbs_file)
        
        return jsonify({
            'success': True,
            'message': f'Task {task_id} deleted successfully',
            'backup_file': backup_file
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def serialize_task_for_json(task):
    """Serialize a task dict with datetime objects to JSON-safe format."""
    serialized = task.copy()
    for key, value in serialized.items():
        if hasattr(value, 'strftime'):
            serialized[key] = value.strftime('%Y-%m-%d')
        elif value is None or (isinstance(value, float) and pd.isna(value)):
            serialized[key] = None
    return serialized


def process_chatbot_message(message, tasks):
    """Process chatbot message and return appropriate response."""
    message = message.lower()
    
    if 'before' in message or 'due' in message or 'deadline' in message:
        try:
            import re
            date_patterns = re.findall(r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b|\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]* \d{1,2}(?:,? \d{4})?\b', message, re.IGNORECASE)
            
            if date_patterns:
                target_date = date_parser.parse(date_patterns[0])
                matching_tasks = []
                
                for task in tasks:
                    end_date = task.get('end_date')
                    if end_date is not None and end_date.date() <= target_date.date():
                        matching_tasks.append({
                            'task_id': task.get('task_id'),
                            'task_name': task.get('task_name'),
                            'module': task.get('module'),
                            'end_date': end_date.strftime('%Y-%m-%d'),
                            'completion_percent': task.get('completion_percent'),
                            'status': task.get('status')
                        })
                
                if matching_tasks:
                    return {
                        'message': f'Found {len(matching_tasks)} tasks due before {target_date.strftime("%B %d, %Y")}:',
                        'tasks': matching_tasks,
                        'action': 'show_tasks'
                    }
                else:
                    return {
                        'message': f'No tasks found due before {target_date.strftime("%B %d, %Y")}.',
                        'tasks': []
                    }
        except Exception as e:
            return {
                'message': 'I had trouble parsing the date. Please try using a format like "Oct 9" or "10/09/2025".',
                'tasks': []
            }
    
    elif 'delete' in message or 'remove' in message:
        import re
        task_id_match = re.search(r'(?:task\s+)?(\d+)', message)
        
        if task_id_match:
            task_id = int(task_id_match.group(1))
            
            task_to_delete = None
            for task in tasks:
                if task.get('task_id') == task_id:
                    task_to_delete = task
                    break
            
            if task_to_delete:
                return {
                    'message': f'⚠️ Are you sure you want to delete task #{task_id}: "{task_to_delete.get("task_name")}"?\n\nPlease use the delete button (🗑️) next to the task to confirm deletion.',
                    'tasks': [{
                        'task_id': task_to_delete.get('task_id'),
                        'task_name': task_to_delete.get('task_name'),
                        'module': task_to_delete.get('module'),
                        'completion_percent': task_to_delete.get('completion_percent'),
                        'status': task_to_delete.get('status')
                    }],
                    'action': 'confirm_delete'
                }
            else:
                return {
                    'message': f'Task #{task_id} not found. Please check the task ID and try again.',
                    'action': 'error'
                }
        else:
            return {
                'message': 'To delete a task, please provide the task ID. For example: "delete task 5"',
                'action': 'delete_instruction'
            }
    
    elif 'critical' in message or 'escalation' in message:
        risk_agent = RiskAnalysisAgent()
        categorized = risk_agent.analyze_tasks(tasks)
        critical_tasks = categorized.get('critical_escalation', [])
        
        if critical_tasks:
            return {
                'message': f'There are {len(critical_tasks)} critical escalations that need immediate attention:',
                'tasks': critical_tasks[:10],
                'action': 'show_tasks'
            }
        else:
            return {
                'message': '✅ Great news! There are no critical escalations at the moment.',
                'tasks': []
            }
    
    elif 'alert' in message:
        risk_agent = RiskAnalysisAgent()
        categorized = risk_agent.analyze_tasks(tasks)
        alert_tasks = categorized.get('alert', [])
        
        if alert_tasks:
            return {
                'message': f'There are {len(alert_tasks)} tasks on alert status:',
                'tasks': alert_tasks[:10],
                'action': 'show_tasks'
            }
        else:
            return {
                'message': '✅ No alerts at this time. All tasks are progressing well.',
                'tasks': []
            }
    
    elif 'module' in message or 'project' in message:
        module_breakdown = {}
        for task in tasks:
            module = task.get('module', 'Unknown')
            if module not in module_breakdown:
                module_breakdown[module] = []
            module_breakdown[module].append(task)
        
        summary = "Here's the breakdown by module:\n"
        for module, module_tasks in module_breakdown.items():
            avg_completion = sum(t.get('completion_percent', 0) for t in module_tasks) / len(module_tasks) if module_tasks else 0
            summary += f"\n• {module}: {len(module_tasks)} tasks ({avg_completion:.1f}% avg completion)"
        
        return {
            'message': summary,
            'tasks': []
        }
    
    elif 'overdue' in message:
        from datetime import datetime
        today = datetime.now().date()
        overdue_tasks = []
        
        for task in tasks:
            end_date = task.get('end_date')
            if end_date is not None and end_date.date() < today and task.get('completion_percent', 0) < 100:
                overdue_tasks.append(task)
        
        if overdue_tasks:
            return {
                'message': f'Found {len(overdue_tasks)} overdue tasks:',
                'tasks': overdue_tasks[:10],
                'action': 'show_tasks'
            }
        else:
            return {
                'message': '✅ No overdue tasks! Everything is on schedule.',
                'tasks': []
            }
    
    elif 'help' in message or 'what can you do' in message:
        return {
            'message': """I can help you with:
            
• **Task Queries**: Ask about tasks by date (e.g., "Show tasks due before Oct 15")
• **Risk Analysis**: Ask about critical tasks, alerts, or overdue items
• **Module Information**: Get breakdown by project module
• **Task Management**: Delete tasks (e.g., "delete task 5")

Try asking me something like:
- "What tasks are overdue?"
- "Show critical escalations"
- "Tasks due before next week"
- "Module breakdown"
            """,
            'tasks': []
        }
    
    else:
        return {
            'message': f'I understand you\'re asking about "{message}". Try asking about critical tasks, alerts, overdue tasks, or tasks by date. Say "help" for more options.',
            'tasks': []
        }


if __name__ == "__main__":
    print("🚀 Starting Flask API server on http://0.0.0.0:3001")
    app.run(host='0.0.0.0', port=3001, debug=False)
