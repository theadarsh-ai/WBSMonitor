"""
SharePoint/OneDrive client for file access.
"""
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.client_credential import ClientCredential
import os
from typing import Optional


class SharePointClient:
    """Client for accessing SharePoint/OneDrive files."""
    
    def __init__(self, site_url: str, client_id: str, client_secret: str):
        self.site_url = site_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.ctx = None
        
    def connect(self):
        """Establish connection to SharePoint."""
        try:
            credentials = ClientCredential(self.client_id, self.client_secret)
            self.ctx = ClientContext(self.site_url).with_credentials(credentials)
            print("Successfully connected to SharePoint")
            return True
        except Exception as e:
            print(f"Failed to connect to SharePoint: {e}")
            return False
    
    def download_file(self, file_path: str, local_path: str) -> bool:
        """
        Download file from SharePoint to local path.
        
        Args:
            file_path: Path to file in SharePoint (e.g., /Shared Documents/file.xlsx)
            local_path: Local path to save the file
            
        Returns:
            True if successful, False otherwise
        """
        if not self.ctx:
            if not self.connect():
                return False
        
        try:
            # Get the file from SharePoint
            file = self.ctx.web.get_file_by_server_relative_url(file_path)
            
            # Download file content
            with open(local_path, 'wb') as local_file:
                file.download(local_file).execute_query()
            
            print(f"File downloaded successfully to {local_path}")
            return True
        except Exception as e:
            print(f"Failed to download file: {e}")
            return False
    
    def upload_file(self, local_path: str, file_path: str) -> bool:
        """
        Upload file from local path to SharePoint.
        
        Args:
            local_path: Local file path
            file_path: Path in SharePoint to upload to
            
        Returns:
            True if successful, False otherwise
        """
        if not self.ctx:
            if not self.connect():
                return False
        
        try:
            with open(local_path, 'rb') as local_file:
                folder = self.ctx.web.get_folder_by_server_relative_url(os.path.dirname(file_path))
                folder.upload_file(os.path.basename(file_path), local_file.read()).execute_query()
            
            print(f"File uploaded successfully to {file_path}")
            return True
        except Exception as e:
            print(f"Failed to upload file: {e}")
            return False
