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

# ============================================================================
# LEGACY THRESHOLDS - NO LONGER USED IN 100% AI-AGENTIC SYSTEM
# ============================================================================
# These thresholds are kept for backward compatibility only but are NOT used
# by the AI agents. All decisions are now made by AI autonomously.
# ============================================================================
# CRITICAL_ESCALATION_DAYS = 7  # DEPRECATED - AI decides escalation timing
# ALERT_DEADLINE_APPROACHING_DAYS = 7  # DEPRECATED - AI assesses risk dynamically
# ALERT_THRESHOLD_COMPLETION_PERCENT = 30  # DEPRECATED - AI considers multiple factors
# ESCALATION_THRESHOLD_DAYS = 2  # DEPRECATED - AI makes nuanced decisions
# ============================================================================

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
