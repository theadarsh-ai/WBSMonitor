# Autonomous Agentic AI Project Monitoring System

## Overview
This project is a 100% AI-agentic system designed for autonomous monitoring of project Work Breakdown Structures (WBS). It utilizes a multi-agent AI architecture built with Python, LangGraph, and Azure AI to continuously assess risks, reallocate tasks, manage escalations, analyze dependencies, and predict timelines without any hardcoded rules or thresholds. The system also features an intelligent digest system that delivers daily email summaries focusing on priorities, risks, and overall project health. Its core purpose is to provide fully autonomous project management and oversight, eliminating the need for manual intervention and ensuring proactive issue resolution.

## User Preferences
- Focus on **proactive alerts** (upcoming deadlines), NOT reactive (overdue)
- Email only for **current month** deadlines approaching
- **Once per day** per task to avoid spam
- **End-of-day summary** at 6 PM only
- Gmail SMTP preferred (no domain verification)
- Realistic November & December 2025 data
- Combined API + monitoring in single file (main.py)
- Stakeholder: adarsh.velmurugan@verint.com (PM)
- Recipients: adarsh.arvr@gmail.com, adarshprvt@gmail.com

## System Architecture
The system employs a LangGraph-based multi-agent orchestration supervised by a `Master Supervisor Agent`. All decision-making is powered by Azure AI, ensuring 100% AI-driven logic without hardcoded thresholds for risk assessment, task reallocation, or escalation management.

**UI/UX Decisions:**
- An interactive TypeScript/React dashboard (Vite frontend) provides real-time data visualization and project health metrics.
- Notifications for self-healing agent decisions (task reallocations) are displayed in a dashboard bell icon.
- Automated HTML email templates are used for all digests (Morning Priority, Afternoon Risk Alert, Evening Summary).

**Technical Implementations:**
- **AI Decision Engine:** A central AI brain, utilizing Azure AI, makes all project decisions (risk, reallocation, escalation, planning) with confidence scoring. It learns from past decisions and includes resilient fallbacks for when AI is unavailable.
- **Risk Analysis Agent:** AI-powered dynamic risk categorization (critical_escalation, alert, at_risk, on_track) based on holistic analysis of completion, deadline, and dependencies.
- **Self-Healing Agent:** Autonomously reallocates tasks based on workload, skills, and deadlines, selecting optimal team members.
- **Escalation Manager:** AI-driven decisions on whether to escalate, escalation level, and recipient/timing to prevent alert fatigue.
- **Plan Update Agent:** AI predicts realistic completion dates, adjusts schedules, and provides buffer recommendations considering dependencies and historical patterns.
- **Dependency Tracker:** AI analyzes complex dependency chains, identifies cascading impacts, and prioritizes critical paths.
- **Intelligent Digest System:** Three AI-generated email digests (Morning Priority, Afternoon Risk, Evening Summary) are scheduled by a Smart Scheduler background thread. Each digest independently fetches data, performs AI analysis, and sends emails.
- **Email Sending Logic:** Employs a JSON-based tracker to ensure each task receives only one email per day, focusing on proactive alerts for tasks due in the current month with approaching deadlines. A comprehensive end-of-day summary is sent once daily.
- **Combined System:** The Flask API and monitoring logic are integrated into a single `main.py` for streamlined deployment.

**System Design Choices:**
- **Zero Hardcoded Rules:** All traditional thresholds and business rules (`ALERT_DEADLINE_APPROACHING_DAYS`, `ALERT_THRESHOLD_COMPLETION_PERCENT`, etc.) have been deprecated and replaced by AI-driven decision-making.
- **Resilience:** The system includes graceful error handling and resilient fallbacks to ensure continuous operation even if AI services are temporarily unavailable.
- **Data Handling:** WBS data is ingested from Excel/SharePoint, processed by pandas and openpyxl. NetworkX is used for dependency graph analysis.

## External Dependencies
- **LLM/AI:** Azure AI (via `azure-ai-inference`)
- **Framework:** LangGraph (for multi-agent orchestration)
- **Frontend:** React with Vite (TypeScript)
- **Backend API:** Flask
- **Data Visualization:** Recharts
- **Data Processing:** pandas, openpyxl
- **Graph Analysis:** NetworkX
- **Email:** Gmail SMTP (for sending emails)
- **Email Tracking:** JSON-based local tracking
- **Scheduling:** `schedule` library
- **SharePoint/OneDrive Integration (Optional):** Office365-REST-Python-Client