"""
Excel WBS file parser utility.
Handles reading and parsing Excel files with task details.
"""
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional
import os


class ExcelParser:
    """Parser for Excel WBS files."""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        
    def parse_wbs(self) -> List[Dict]:
        """
        Parse the Excel WBS file and extract task details.
        
        Returns:
            List of dictionaries containing task information
        """
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"WBS file not found: {self.file_path}")
        
        # Read the Excel file
        df = pd.read_excel(self.file_path, sheet_name=0)
        
        # Standardize column names (handle various formats)
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
        
        tasks = []
        
        for idx, row in df.iterrows():
            try:
                task = {
                    'task_id': idx + 1,
                    'task_name': str(row.get('task_name', row.get('task', ''))),
                    'module': str(row.get('module', row.get('project_module', ''))),
                    'mail_id': str(row.get('mail_id', row.get('email', ''))),
                    'product_owner': str(row.get('product_owner', row.get('po', ''))),
                    'assigned_to': str(row.get('assigned_to', row.get('assignee', ''))),
                    'duration_days': self._parse_int(row.get('duration', row.get('duration_days', 0))),
                    'start_date': self._parse_date(row.get('start_date', row.get('start', ''))),
                    'end_date': self._parse_date(row.get('end_date', row.get('end', ''))),
                    'completion_percent': self._parse_int(row.get('completion_%', row.get('completion_percent', row.get('completion', 0)))),
                    'status': str(row.get('status', '')),
                    'dependencies': str(row.get('dependencies', '')),
                }
                tasks.append(task)
            except Exception as e:
                print(f"Error parsing row {idx}: {e}")
                continue
        
        return tasks
    
    def _parse_date(self, date_value) -> Optional[datetime]:
        """Parse date from various formats."""
        if pd.isna(date_value) or date_value == '':
            return None
        
        if isinstance(date_value, datetime):
            return date_value
        
        if isinstance(date_value, str):
            try:
                return pd.to_datetime(date_value)
            except:
                return None
        
        return None
    
    def _parse_int(self, value) -> int:
        """Parse integer from various formats."""
        if pd.isna(value) or value == '':
            return 0
        
        try:
            return int(float(value))
        except:
            return 0
    
    def save_wbs(self, tasks: List[Dict], output_path: str):
        """Save tasks back to Excel file."""
        df = pd.DataFrame(tasks)
        df.to_excel(output_path, index=False)
        print(f"WBS saved to {output_path}")
