"""
Data Ingestion Agent - Responsible for reading and parsing WBS data.
"""
from typing import List, Dict, Optional
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.excel_parser import ExcelParser
from utils.sharepoint_client import SharePointClient
import config


class DataIngestionAgent:
    """Agent responsible for ingesting WBS data from various sources."""
    
    def __init__(self):
        self.sharepoint_client = None
        if config.SHAREPOINT_SITE_URL and config.SHAREPOINT_CLIENT_ID:
            self.sharepoint_client = SharePointClient(
                config.SHAREPOINT_SITE_URL,
                config.SHAREPOINT_CLIENT_ID,
                config.SHAREPOINT_CLIENT_SECRET
            )
    
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
