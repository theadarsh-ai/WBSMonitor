"""
Main application for autonomous project monitoring system with embedded Flask API.
"""
import os
import sys
import schedule
import time
from datetime import datetime
from threading import Thread
from flask import Flask, jsonify, request
from flask_cors import CORS
import json
from dateutil import parser as date_parser
import pandas as pd

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.supervisor_agent import MasterSupervisorAgent
from agents.data_ingestion_agent import DataIngestionAgent
from agents.risk_analysis_agent import RiskAnalysisAgent
from agents.dependency_tracker_agent import DependencyTrackerAgent
import config

# Flask API
app = Flask(__name__)
CORS(app)


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy"})

@app.route('/api/dashboard-data', methods=['GET'])
def get_dashboard_data():
    """Get all dashboard data."""
    try:
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
        
        return jsonify({
            'metrics': {
                'total_tasks': total_tasks,
                'critical_escalations': critical,
                'alerts': alerts,
                'at_risk': at_risk,
                'avg_completion': round(avg_completion, 1)
            },
            'risk_distribution': risk_distribution,
            'module_breakdown': module_breakdown,
            'critical_tasks': categorized_tasks.get('critical_escalation', [])[:10],
            'alerts_list': categorized_tasks.get('alert', [])[:10],
            'dependency_stats': {
                'nodes': dep_agent.dependency_graph.number_of_nodes(),
                'edges': dep_agent.dependency_graph.number_of_edges()
            }
        })
    except Exception as e:
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
    
    elif 'help' in message:
        return {
            'message': '''I can help you with:
• Query tasks by date: "Show me tasks due before Oct 9"
• Delete tasks: "Delete task 5"
• View task status: "Show me all tasks"
• Ask about project metrics
What would you like to do?''',
            'tasks': []
        }
    
    elif 'all tasks' in message or 'show tasks' in message:
        task_list = [{
            'task_id': task.get('task_id'),
            'task_name': task.get('task_name'),
            'module': task.get('module'),
            'completion_percent': task.get('completion_percent')
        } for task in tasks[:20]]
        
        return {
            'message': f'Showing {len(task_list)} of {len(tasks)} total tasks:',
            'tasks': task_list,
            'action': 'show_tasks'
        }
    
    else:
        return {
            'message': f'''Hello! I'm your project monitoring assistant. I can help you with:

• Query tasks by date: "Show me tasks due before Oct 9"
• View all tasks: "Show me all tasks"
• Delete tasks: "Delete task <id>"

You have {len(tasks)} total tasks. What would you like to know?''',
            'tasks': []
        }


class AutonomousMonitoringSystem:
    """Main system orchestrator for 24/7 autonomous monitoring."""
    
    def __init__(self):
        self.supervisor = MasterSupervisorAgent()
        self.monitoring_interval = config.MONITORING_INTERVAL_MINUTES
        
        # Ensure directories exist
        os.makedirs(config.DATA_DIR, exist_ok=True)
        os.makedirs(config.REPORTS_DIR, exist_ok=True)
        os.makedirs(config.TEMPLATES_DIR, exist_ok=True)
        
        print("\n" + "="*70)
        print("🤖 AUTONOMOUS AGENTIC AI PROJECT MONITORING SYSTEM")
        print("="*70)
        print(f"Monitoring Interval: Every {self.monitoring_interval} minutes")
        print("AI-Powered Decision Making: ALL escalations decided by AI")
        print("No Hardcoded Thresholds: AI analyzes context autonomously")
        print("="*70)
    
    def run_monitoring_cycle(self):
        """Run a single monitoring cycle."""
        try:
            print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting monitoring cycle...")
            
            # Execute the supervisor workflow
            result = self.supervisor.execute_monitoring_cycle()
            
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Monitoring cycle completed\n")
            
        except Exception as e:
            print(f"❌ Error in monitoring cycle: {e}")
            import traceback
            traceback.print_exc()
    
    def start_autonomous_mode(self):
        """Start 24/7 autonomous monitoring with scheduling."""
        print("\n🚀 Starting 24/7 Autonomous Monitoring Mode...")
        print("Press Ctrl+C to stop\n")
        
        # Run immediately on start
        self.run_monitoring_cycle()
        
        # Schedule recurring monitoring
        schedule.every(self.monitoring_interval).minutes.do(self.run_monitoring_cycle)
        
        # Keep running
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def run_once(self, wbs_file_path: str = None):
        """Run a single monitoring cycle (for testing)."""
        print("\n🔍 Running Single Monitoring Cycle...\n")
        
        result = self.supervisor.execute_monitoring_cycle(wbs_file_path)
        
        print("\n✓ Single cycle completed. Check the reports directory for outputs.")


def start_flask_api():
    """Start Flask API server in background thread."""
    app.run(host='0.0.0.0', port=3001, debug=False, use_reloader=False)


def main():
    """Main entry point - runs both Flask API and monitoring system."""
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--once":
            # Run once for testing
            system = AutonomousMonitoringSystem()
            wbs_file = sys.argv[2] if len(sys.argv) > 2 else None
            system.run_once(wbs_file)
        elif sys.argv[1] == "--help":
            print("""
Autonomous Project Monitoring System
=====================================

Usage:
  python main.py              - Start 24/7 monitoring + Flask API
  python main.py --once       - Run a single monitoring cycle
  python main.py --once <file> - Run once with specific WBS file
  python main.py --help       - Show this help message

Configuration:
  Edit .env file to configure Azure AI, SharePoint, and email settings.
  Place your WBS Excel file in the data/ directory.

            """)
        else:
            print(f"Unknown argument: {sys.argv[1]}")
            print("Use --help for usage information")
    else:
        # Start Flask API in background thread
        api_thread = Thread(target=start_flask_api, daemon=True)
        api_thread.start()
        print("✓ Flask API started on http://0.0.0.0:3001")
        
        # Start autonomous monitoring in main thread
        system = AutonomousMonitoringSystem()
        try:
            system.start_autonomous_mode()
        except KeyboardInterrupt:
            print("\n\n👋 Autonomous monitoring stopped by user")


if __name__ == "__main__":
    main()
