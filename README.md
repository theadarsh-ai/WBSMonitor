# Autonomous Agentic AI Project Monitoring System

A fully autonomous multi-agent AI system built with Python and LangGraph that continuously monitors project Work Breakdown Structure (WBS) and autonomously manages escalations, alerts, and project updates.

## 🚀 Features

### Core Capabilities
- **📊 Automated WBS Data Ingestion**: Reads Excel files from SharePoint/OneDrive or local upload
- **🔍 Intelligent Risk Analysis**: Identifies critical issues, overdue tasks, and at-risk deliverables
- **📧 Automated Email Generation**: Creates professional stakeholder communications with urgency-based subjects
- **⚠️ Smart Escalation Management**: Severity-based routing (2+ days overdue = escalation, approaching deadlines = alert)
- **🔗 Cross-Module Dependency Tracking**: Monitors impacts across all 5 project modules
- **📈 Autonomous Plan Updates**: Recalculates timelines and generates daily PM summaries
- **🤖 24/7 Operation**: Zero human intervention except for strategic decisions
- **🧠 Multi-Agent Architecture**: LangGraph orchestrates 6 specialized agents
- **📊 Interactive Dashboard**: Real-time visualization and oversight with manual control options

### Project Modules Supported
1. Employee Information Portal (EIP)
2. L&A Module
3. Employee Separation (ES)
4. Compensation & Benefits (C&B)
5. Payroll & Taxation

## 🏗️ Architecture

### Multi-Agent System
```
Master Supervisor Agent (LangGraph Orchestrator)
├── Data Ingestion Agent (Excel/SharePoint parsing)
├── Risk Analysis Agent (Issue detection)
├── Email Generation Agent (Professional communications)
├── Escalation Manager Agent (Severity-based routing)
├── Dependency Tracker Agent (Cross-module analysis)
└── Plan Update Agent (Timeline recalculation)
```

### Technology Stack
- **Framework**: LangGraph for multi-agent orchestration
- **LLM**: Azure AI (OpenAI-compatible API)
- **Dashboard**: Streamlit with Plotly visualizations
- **Data Processing**: pandas, openpyxl
- **Graph Analysis**: NetworkX
- **Email**: Resend API with Jinja2 templates
- **Scheduling**: schedule library for 24/7 operation
- **Integration**: Office365-REST-Python-Client for SharePoint

## 📋 Setup Instructions

### 1. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Required configurations:
- **Azure AI**: Endpoint and credentials for LLM capabilities
- **SharePoint/OneDrive** (Optional): For automatic file fetching
- **Email**: Resend API key for automated communications

### 2. Prepare WBS File

Option A: Use the sample file (for testing)
```bash
python create_sample_wbs.py
```

Option B: Upload your own WBS Excel file to `data/` directory with columns:
- Task Name
- Module
- Mail ID
- Product Owner
- Assigned To
- Duration
- Start Date
- End Date
- Completion %
- Status
- Dependencies

### 3. Run the System

**Option A: TypeScript Dashboard (Recommended)**
```bash
bash start_ui.sh
```
Modern TypeScript/React dashboard at http://localhost:5000 with:
- Real-time project metrics and visualizations
- Interactive charts (Recharts)
- Manual trigger for on-demand monitoring cycles
- Risk distribution pie chart
- Module breakdowns and bar charts
- Responsive, modern UI design

**Option B: Command-line Autonomous Mode**

Single monitoring cycle (testing):
```bash
python main.py --once
```

24/7 Autonomous mode:
```bash
python main.py
```

With specific WBS file:
```bash
python main.py --once data/your_wbs_file.xlsx
```

## 🔧 Configuration

Edit `config.py` or `.env` to customize:

- `MONITORING_INTERVAL_MINUTES`: How often to check (default: 30)
- `ESCALATION_THRESHOLD_DAYS`: Days overdue before escalation (default: 2)
- `ALERT_THRESHOLD_COMPLETION_PERCENT`: Completion % threshold for alerts (default: 30)

## 📊 Output

The system generates:

1. **Email Alerts**: Sent to stakeholders for critical tasks
2. **Daily PM Summary**: Comprehensive status report
3. **Updated WBS Files**: In `reports/` directory with recalculated timelines
4. **Console Logs**: Real-time monitoring status

## 🎯 Use Cases

### Example Scenarios Handled Automatically:

**Scenario 1: Critical Escalation**
- Task: "Client to send completed EIP Master templates"
- Status: 40% complete, 2 days overdue, marked "escalation"
- Action: System sends urgent email to adarsh.velmurugan@verint.com with impact analysis

**Scenario 2: Alert**
- Task: "Data validation"
- Status: 10% complete, deadline approaching, marked "alert"
- Action: System sends alert email to Nihar with action items

**Scenario 3: Dependency Impact**
- Delayed Task: "EIP database schema design"
- Impact: System identifies downstream tasks blocked in L&A and ES modules
- Action: Emails sent to all affected stakeholders with dependency chain

## 🔒 Security Notes

- Never commit `.env` file to version control
- Use environment variables for all credentials
- SMTP app-specific passwords recommended over account passwords
- SharePoint client credentials should have minimal required permissions

## 📁 Project Structure

```
.
├── agents/                      # Specialized AI agents
│   ├── data_ingestion_agent.py
│   ├── risk_analysis_agent.py
│   ├── email_generation_agent.py
│   ├── escalation_manager_agent.py
│   ├── dependency_tracker_agent.py
│   ├── plan_update_agent.py
│   └── supervisor_agent.py      # LangGraph orchestrator
├── utils/                       # Utility modules
│   ├── excel_parser.py
│   ├── sharepoint_client.py
│   ├── email_sender.py
│   └── date_calculator.py
├── data/                        # WBS files (input)
├── reports/                     # Updated plans (output)
├── templates/                   # Email templates
├── config.py                    # Configuration
├── main.py                      # Main application
└── create_sample_wbs.py         # Sample data generator
```

## 🚨 Troubleshooting

**Issue**: No WBS file found
- **Solution**: Place Excel file in `data/` directory or configure SharePoint

**Issue**: Emails not sending
- **Solution**: Verify SMTP credentials in `.env` file

**Issue**: Azure AI errors
- **Solution**: Check AZURE_INFERENCE_ENDPOINT and AZURE_INFERENCE_CREDENTIAL

**Issue**: SharePoint connection failed
- **Solution**: Verify client ID, secret, and tenant ID. Ensure permissions are granted.

## 📝 License

This project is provided as-is for project monitoring and management purposes.

## 🤝 Support

For issues or questions, please contact your system administrator or refer to the configuration documentation.

---

**Built with ❤️ using LangGraph and Azure AI**
