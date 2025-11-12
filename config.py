"""
Configuration module for the autonomous agentic AI system.
Loads environment variables and provides configuration settings.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Azure AI Configuration
AZURE_INFERENCE_ENDPOINT = os.getenv("AZURE_INFERENCE_ENDPOINT", "")
AZURE_INFERENCE_CREDENTIAL = os.getenv("AZURE_INFERENCE_CREDENTIAL", "")
AZURE_DEPLOYMENT_NAME = os.getenv("AZURE_DEPLOYMENT_NAME", "")
AZURE_API_VERSION = os.getenv("AZURE_API_VERSION", "")

# SharePoint/OneDrive Configuration
SHAREPOINT_SITE_URL = os.getenv("SHAREPOINT_SITE_URL", "")
SHAREPOINT_CLIENT_ID = os.getenv("SHAREPOINT_CLIENT_ID", "")
SHAREPOINT_CLIENT_SECRET = os.getenv("SHAREPOINT_CLIENT_SECRET", "")
SHAREPOINT_TENANT_ID = os.getenv("SHAREPOINT_TENANT_ID", "")
WBS_FILE_PATH = os.getenv("WBS_FILE_PATH", "/Shared Documents/project_wbs.xlsx")

# Email Configuration (SMTP)
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
EMAIL_FROM = os.getenv("FROM_EMAIL", "") or SMTP_USERNAME

# Project Monitoring Configuration
MONITORING_INTERVAL_MINUTES = int(os.getenv("MONITORING_INTERVAL_MINUTES", "30"))

# Email sending thresholds - Smart filtering to avoid spam
CRITICAL_ESCALATION_DAYS = int(os.getenv("CRITICAL_ESCALATION_DAYS", "7"))  # Only send email if 7+ days overdue
ALERT_DEADLINE_APPROACHING_DAYS = int(os.getenv("ALERT_DEADLINE_APPROACHING_DAYS", "7"))  # Alert if deadline within 7 days
ALERT_THRESHOLD_COMPLETION_PERCENT = int(os.getenv("ALERT_THRESHOLD_COMPLETION_PERCENT", "30"))  # Alert if <30% complete

# Legacy threshold for risk categorization (not for email sending)
ESCALATION_THRESHOLD_DAYS = int(os.getenv("ESCALATION_THRESHOLD_DAYS", "2"))

# Project Modules
PROJECT_MODULES = [
    "Employee Information Portal (EIP)",
    "L&A Module",
    "Employee Separation (ES)",
    "Compensation & Benefits (C&B)",
    "Payroll & Taxation"
]

# File Paths
DATA_DIR = "data"
REPORTS_DIR = "reports"
TEMPLATES_DIR = "templates"
