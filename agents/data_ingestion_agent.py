"""
Data Ingestion Agent - Responsible for reading and parsing WBS data.
Enhanced with AI for data quality validation and anomaly detection.
"""
from typing import List, Dict, Optional
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.excel_parser import ExcelParser
from utils.sharepoint_client import SharePointClient
from utils.azure_ai_client import get_ai_client
import config


class DataIngestionAgent:
    """Agent responsible for ingesting WBS data with AI-powered quality validation."""
    
    def __init__(self):
        self.sharepoint_client = None
        if config.SHAREPOINT_SITE_URL and config.SHAREPOINT_CLIENT_ID:
            self.sharepoint_client = SharePointClient(
                config.SHAREPOINT_SITE_URL,
                config.SHAREPOINT_CLIENT_ID,
                config.SHAREPOINT_CLIENT_SECRET
            )
        self.ai_client = get_ai_client()
    
    def fetch_wbs_data(self, local_file_path: Optional[str] = None) -> List[Dict]:
        """
        Fetch WBS data from SharePoint or local file.
        
        Args:
            local_file_path: Optional local file path. If not provided, tries SharePoint.
            
        Returns:
            List of task dictionaries
        """
        file_to_parse = local_file_path
        
        # If no local file provided, try to fetch from SharePoint
        if not file_to_parse:
            if self.sharepoint_client:
                local_download_path = os.path.join(config.DATA_DIR, "project_wbs.xlsx")
                
                if self.sharepoint_client.download_file(config.WBS_FILE_PATH, local_download_path):
                    file_to_parse = local_download_path
                    print(f"✓ Downloaded WBS from SharePoint")
                else:
                    print("✗ Failed to download from SharePoint. Looking for local file...")
                    file_to_parse = self._find_local_wbs_file()
            else:
                print("SharePoint not configured. Looking for local file...")
                file_to_parse = self._find_local_wbs_file()
        
        if not file_to_parse or not os.path.exists(file_to_parse):
            raise FileNotFoundError(
                "No WBS file found. Please provide a local file or configure SharePoint access."
            )
        
        # Parse the WBS file
        parser = ExcelParser(file_to_parse)
        tasks = parser.parse_wbs()
        
        print(f"✓ Successfully parsed {len(tasks)} tasks from WBS")
        
        # Optional: AI-powered data quality validation
        if self.ai_client.is_available():
            quality_insights = self._validate_data_quality_with_ai(tasks)
            if quality_insights:
                print(f"🤖 AI Data Quality Check: {quality_insights}")
        
        return tasks
    
    def _find_local_wbs_file(self) -> Optional[str]:
        """Search for WBS file in data directory."""
        data_dir = config.DATA_DIR
        
        if not os.path.exists(data_dir):
            return None
        
        # Look for Excel files in data directory
        for file in os.listdir(data_dir):
            if file.endswith(('.xlsx', '.xls')) and 'wbs' in file.lower():
                return os.path.join(data_dir, file)
        
        # Return first Excel file found
        for file in os.listdir(data_dir):
            if file.endswith(('.xlsx', '.xls')):
                return os.path.join(data_dir, file)
        
        return None
    
    def _validate_data_quality_with_ai(self, tasks: List[Dict]) -> Optional[str]:
        """
        Use AI to validate data quality and detect anomalies in ingested tasks.
        
        Args:
            tasks: List of ingested task dictionaries
            
        Returns:
            AI-generated quality insights or None
        """
        if not self.ai_client.is_available() or len(tasks) == 0:
            return None
        
        # Sample tasks for AI analysis (limit to avoid token limits)
        sample_size = min(10, len(tasks))
        sample_tasks = tasks[:sample_size]
        
        # Prepare data summary
        task_summary = []
        missing_data_count = 0
        for task in sample_tasks:
            issues = []
            if not task.get('assigned_to'):
                issues.append("no assignee")
                missing_data_count += 1
            if not task.get('end_date'):
                issues.append("no deadline")
                missing_data_count += 1
            if task.get('completion_percent', 0) == 0 and task.get('start_date'):
                issues.append("started but 0% complete")
            
            if issues:
                task_summary.append(f"- {task['task_name']}: {', '.join(issues)}")
        
        if not task_summary:
            return "All data appears complete"
        
        context = f"Total tasks: {len(tasks)}, Sampled: {sample_size}\nIssues found:\n" + "\n".join(task_summary[:5])
        
        system_prompt = """You are a data quality analyst. Review the WBS data issues and provide a 1-2 sentence assessment of data quality risks."""
        
        try:
            insights = self.ai_client.generate_response(system_prompt, context)
            return insights
        except Exception as e:
            print(f"⚠️ AI data quality check error: {e}")
            return None
    
    def update_wbs_file(self, tasks: List[Dict], output_path: Optional[str] = None):
        """
        Update WBS file with modified task data.
        
        Args:
            tasks: List of task dictionaries
            output_path: Optional output path. If not provided, uses default.
        """
        if not output_path:
            output_path = os.path.join(config.DATA_DIR, "project_wbs_updated.xlsx")
        
        parser = ExcelParser(output_path)
        parser.save_wbs(tasks, output_path)
        
        print(f"✓ WBS file updated: {output_path}")
