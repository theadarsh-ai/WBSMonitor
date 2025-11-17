# Autonomous Agentic AI Project Monitoring System

## Project Overview
**100% AI-AGENTIC SYSTEM** - Fully autonomous multi-agent AI system where ALL decisions are made by AI, not hardcoded rules. Built with Python, LangGraph, and Azure AI, this system continuously monitors project Work Breakdown Structure (WBS), uses AI to assess risks, autonomously reallocates tasks, intelligently manages escalations, analyzes dependencies, and predicts timelines - all with ZERO hardcoded thresholds or business rules.

## Latest Changes (2025-11-17) - 🎉 100% AI-AGENTIC TRANSFORMATION COMPLETE
- ✅ **AI Decision Engine** - Comprehensive AI brain for all decision-making across the system
  - NO hardcoded thresholds anywhere in the codebase
  - All decisions made by Azure AI with confidence scoring
  - Learning system that records all decisions for future improvements
  - Graceful fallbacks when AI unavailable
- ✅ **Risk Analysis Agent** - 100% AI-powered risk assessment
  - AI analyzes task completion %, deadline proximity, dependencies holistically
  - Dynamic risk categorization (critical_escalation, alert, at_risk, on_track)
  - Batch processing for efficient multi-task analysis
  - No more hardcoded 7-day or 30% thresholds
- ✅ **Self-Healing Agent** - Fully autonomous task reallocation
  - AI decides when to reallocate tasks based on workload, skills, deadlines
  - AI selects optimal team member for reassignment
  - Provides confidence scores and expected improvements
- ✅ **Escalation Manager** - AI-driven escalation decisions
  - AI decides whether to escalate (not rules)
  - AI sets escalation level (immediate/urgent/routine)
  - AI selects appropriate recipients and timing
  - Prevents alert fatigue intelligently
- ✅ **Plan Update Agent** - AI predicts timelines and adjusts schedules
  - AI forecasts realistic completion dates
  - Considers dependencies, historical patterns, current progress
  - Provides risk factors and buffer recommendations
- ✅ **Dependency Tracker** - AI analyzes complex dependency chains
  - AI identifies cascading impacts across modules
  - Predicts downstream effects of delays
  - Prioritizes critical paths intelligently
- ✅ **Resilient Fallbacks** - System continues operating when AI unavailable
  - All agents handle Azure API errors gracefully
  - Conservative fallback logic prevents data loss
  - No crashes, just degraded (but functional) operation
- ✅ **Zero Hardcoded Rules** - Removed all threshold constants from config.py
  - CRITICAL_ESCALATION_DAYS → DEPRECATED
  - ALERT_DEADLINE_APPROACHING_DAYS → DEPRECATED
  - ALERT_THRESHOLD_COMPLETION_PERCENT → DEPRECATED
  - All business logic now AI-driven

## Previous Changes (2025-11-12)
- ✅ **Replit Environment Setup** - Project configured and tested in Replit environment
- ✅ **Separate API Script** - Created api.py for standalone Flask API server on port 3001
- ✅ **Frontend Workflow** - Vite dev server running on port 5000 with proper host configuration
- ✅ **Dependency Management** - Using uv for Python packages, npm for Node.js packages
- ✅ **Deployment Configuration** - VM deployment with build and run commands configured
- ✅ **All Components Verified** - Dashboard, API, charts, and chatbot all working correctly
- ✅ **Notification System** - Added bell icon in dashboard header showing self-healing agent decisions
  - Real-time notification dropdown with unread count badge
  - Displays task reallocations only
  - Auto-refreshes every 30 seconds
  - Mark as read and clear all functionality
- ✅ **Self-Healing Agent Updates** - Simplified to task reallocation only
  - Removed timeline adjustment functionality (only reallocates tasks now)
  - When a task has deadline within 3 days and < 20% completion, reassigns to team member with less workload
  - Updates Excel file automatically with new assignment
  - Status field shows "AUTO-REALLOCATED to [name]"
- ✅ **Dashboard Enhancements** - Added deadline date column to Active Alerts table

## Previous Changes (2025-11-04)
- ✅ **Once-Per-Day Email Logic** - Each task gets email only ONCE per day, preventing spam
- ✅ **End-of-Day Summary** - Daily summary report sent only at 6 PM (not every cycle)
- ✅ **Email Tracking System** - JSON-based tracker prevents duplicate emails
- ✅ **SMTP Email Integration** - Gmail SMTP for reliable delivery without domain verification
- ✅ **Smart Email Filtering** - Only sends emails for tasks due THIS MONTH with approaching deadlines
- ✅ **Removed Overdue Logic** - Focus on proactive alerts, not reactive overdue notifications
- ✅ **Combined API + Monitoring** - Merged Flask API into main.py for streamlined deployment
- ✅ **November & December 2025 Data** - Updated Excel WBS with realistic dates

## Technology Stack
- **Framework**: LangGraph (multi-agent orchestration)
- **LLM**: Azure AI (via azure-ai-inference)
- **Frontend**: TypeScript/React with Vite
- **Backend API**: Flask with CORS
- **Dashboard**: Recharts visualization
- **Data**: pandas, openpyxl (Excel processing)
- **Graph**: NetworkX (dependency analysis)
- **Email**: Gmail SMTP (no domain verification needed)
- **Email Tracking**: JSON-based daily tracker
- **Scheduling**: schedule library
- **Integration**: Office365-REST-Python-Client (SharePoint/OneDrive)

## Architecture
```
main.py (Combined System)
├── Flask API (Background Thread)
│   ├── /api/health
│   ├── /api/dashboard-data
│   └── /api/trigger-monitoring
│
└── Master Supervisor Agent (LangGraph)
    ├── Data Ingestion Agent → Excel/SharePoint WBS parsing
    ├── Risk Analysis Agent → Current month deadline detection
    ├── Email Generation Agent → Professional stakeholder emails
    ├── Escalation Manager Agent → Smart email filtering (once/day)
    ├── Dependency Tracker Agent → Cross-module impact analysis
    └── Plan Update Agent → Timeline recalculation & updates
```

## Configuration
Environment variables (.env):
- `AZURE_INFERENCE_ENDPOINT` - Azure AI endpoint
- `AZURE_INFERENCE_CREDENTIAL` - Azure AI API key
- `SMTP_SERVER` - Gmail SMTP server (smtp.gmail.com)
- `SMTP_PORT` - SMTP port (587)
- `SMTP_USERNAME` - Gmail address
- `SMTP_PASSWORD` - Gmail App Password (not regular password)
- `FROM_EMAIL` - Sender email address
- `SHAREPOINT_*` - Optional SharePoint/OneDrive access
- `MONITORING_INTERVAL_MINUTES` - How often to monitor (default: 30)
- `ALERT_DEADLINE_APPROACHING_DAYS` - Alert if deadline within N days (default: 7)
- `ALERT_THRESHOLD_COMPLETION_PERCENT` - Completion % for alerts (default: 30)

## Email Sending Logic

### Individual Task Alerts (Throughout the Day)
**ONLY sends emails when ALL conditions met:**
- Task is due in **current month** (November 2025)
- Deadline approaching within **7 days**
- Completion **< 30%**
- **Email NOT already sent today** for this task

**Example behavior:**
- First monitoring cycle at 9 AM: 8 emails sent
- Second cycle at 9:30 AM: 0 emails (already sent today)
- Third cycle at 10 AM: 0 emails (already sent today)
- ...continues until next day

### Daily Summary Report (End of Day)
**Sent once per day at 6 PM:**
- Complete summary of all tasks
- Critical escalations
- At-risk tasks
- Project health metrics
- Only to PM (adarsh.velmurugan@verint.com)

**NO emails for:**
- Completed tasks (100%)
- Tasks not due this month
- Tasks with good progress (≥30% complete)
- Overdue tasks (no reactive notifications)
- Tasks that already got emails today

## Project Modules Monitored
1. Employee Information Portal (EIP)
2. L&A Module
3. Employee Separation (ES)
4. Compensation & Benefits (C&B)
5. Payroll & Taxation

## Usage

### Development Mode (Replit)
- **Frontend + API**: `bash start_ui.sh` - Starts both Flask API (port 3001) and Vite frontend (port 5000)
- **Frontend Only**: `npm run dev` - Vite development server
- **API Only**: `source .pythonlibs/bin/activate && python api.py` - Flask API server

### Standalone Monitoring
- **Production**: `python main.py` - Starts Flask API + 24/7 monitoring
- **Test mode**: `python main.py --once` - Runs single cycle
- **Custom WBS**: `python main.py --once data/custom_wbs.xlsx`

### Access Points
- **Frontend Dashboard**: http://localhost:5000 (or Replit webview)
- **API Endpoints**: http://localhost:3001/api/*

## File Structure
```
├── main.py             # Combined Flask API + Autonomous Monitoring
├── api.py              # Standalone Flask API server (for Replit/dev)
├── app.py              # Streamlit dashboard (alternative UI)
├── agents/             # Specialized AI agents
│   ├── supervisor_agent.py      # LangGraph orchestrator
│   ├── data_ingestion_agent.py
│   ├── risk_analysis_agent.py
│   ├── email_generation_agent.py
│   ├── escalation_manager_agent.py (once/day logic)
│   ├── dependency_tracker_agent.py
│   └── plan_update_agent.py
├── utils/              # Utility modules
│   ├── excel_parser.py
│   ├── sharepoint_client.py
│   ├── email_sender.py (SMTP)
│   ├── email_tracker.py (prevents duplicates)
│   └── date_calculator.py
├── src/                # TypeScript/React frontend
│   ├── App.tsx         # Main dashboard component
│   ├── Chatbot.tsx     # AI chatbot component
│   ├── main.tsx        # React entry point
│   ├── App.css         # Dashboard styles
│   └── Chatbot.css     # Chatbot styles
├── data/               # Input WBS files
│   ├── project_wbs.xlsx
│   └── email_tracker.json (daily tracking)
├── reports/            # Generated updated plans
├── config.py           # Configuration management
├── start_ui.sh         # UI startup script (Flask API + Vite frontend)
├── package.json        # Node.js dependencies
├── pyproject.toml      # Python dependencies (uv)
├── vite.config.ts      # Vite configuration (port 5000, host 0.0.0.0)
└── .pythonlibs/        # Python virtual environment (uv-managed)
```

## Key Features
✅ Autonomous WBS data ingestion from SharePoint/OneDrive/local files
✅ Smart risk analysis - only current month tasks with approaching deadlines
✅ Professional HTML email generation via Gmail SMTP
✅ **Once-per-day email sending** - prevents spam and duplicate notifications
✅ **End-of-day summary reports** - comprehensive daily overview at 6 PM
✅ Email tracking system with automatic cleanup (7-day history)
✅ Zero domain verification needed for email delivery
✅ Cross-module dependency tracking with NetworkX graph
✅ Critical path identification for project scheduling
✅ Autonomous project plan updates with timeline recalculation
✅ 24/7 operation with configurable monitoring intervals
✅ Zero human intervention
✅ Interactive TypeScript/React dashboard with real-time data
✅ Combined Flask API + monitoring in single process

## Latest Test Results (2025-11-04)
- ✓ 73 tasks parsed from WBS
- ✓ 8 alert emails sent (first cycle)
- ✓ 0 alert emails sent (second cycle - already sent today)
- ✓ Email tracking working perfectly
- ✓ Daily summary scheduled for 6 PM
- ✓ 72 tasks filtered (15 completed, 28 not due this month, 29 not urgent)
- ✓ Updated plan generated: reports/updated_plan_20251104_113938.xlsx
- ✓ Flask API running on port 3001
- ✓ SMTP emails delivered successfully

## Email Behavior Examples

**Scenario 1: First run of the day (9:00 AM)**
```
8 tasks need alerts
→ 8 emails sent
→ Tracker updated
→ Summary message: "Daily summary will be sent at 6 PM"
```

**Scenario 2: Second run of the day (9:30 AM)**
```
8 tasks still need alerts (same tasks)
→ 0 emails sent (already sent today)
→ Skipped: "Client to send completed EIP Master templates" (already sent today)
→ Summary message: "Daily summary will be sent at 6 PM"
```

**Scenario 3: End of day (6:30 PM)**
```
Daily summary sent to PM with:
- All critical escalations: 0
- All alerts: 8
- At-risk tasks: 8
- On-track tasks: 57
- Project health overview
```

**Scenario 4: Next day (9:00 AM)**
```
Tracker resets automatically
8 tasks still need alerts
→ 8 emails sent (fresh day, can send again)
```

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

## Notes
- Gmail App Password required (not regular Gmail password)
- Monitoring runs every 30 minutes automatically
- Dashboard auto-refreshes from Flask API
- Email filtering prevents spam - only truly urgent tasks get emails
- Each task gets email only ONCE per day
- Daily summary sent only at 6 PM (18:00-19:00)
- System automatically adjusts as calendar month changes
- Email tracker cleans up entries older than 7 days
