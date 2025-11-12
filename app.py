"""
Streamlit Dashboard for Autonomous Project Monitoring System
"""
import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time

st.set_page_config(
    page_title="Project Monitoring Dashboard",
    page_icon="🤖",
    layout="wide"
)

API_BASE_URL = "http://localhost:3001/api"

def check_api_health():
    """Check if Flask API is running."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def fetch_dashboard_data():
    """Fetch dashboard data from Flask API."""
    try:
        response = requests.get(f"{API_BASE_URL}/dashboard-data", timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

def trigger_monitoring():
    """Trigger a monitoring cycle."""
    try:
        response = requests.post(f"{API_BASE_URL}/trigger-monitoring", timeout=30)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

st.title("🤖 Autonomous Project Monitoring Dashboard")
st.markdown("Real-time monitoring of project Work Breakdown Structure (WBS)")

api_status = check_api_health()

if not api_status:
    st.warning("⚠️ Backend API is not running. Starting the monitoring system...")
    st.info("The Flask API should start automatically. Please wait...")
    
    with st.spinner("Waiting for API to start..."):
        for i in range(10):
            time.sleep(2)
            if check_api_health():
                st.success("✅ API is now running!")
                st.rerun()
                break
    
    if not check_api_health():
        st.error("❌ Could not connect to the backend API. Please ensure main.py is running.")
        st.code("python main.py", language="bash")
        st.stop()

col1, col2, col3 = st.columns([2, 2, 1])

with col1:
    st.markdown("### Status")
    st.success("🟢 System Active")

with col2:
    st.markdown("### Last Updated")
    st.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

with col3:
    if st.button("🔄 Trigger Monitoring", use_container_width=True):
        with st.spinner("Running monitoring cycle..."):
            result = trigger_monitoring()
            if "error" in result:
                st.error(f"Error: {result['error']}")
            else:
                st.success("Monitoring cycle completed!")
                st.rerun()

st.markdown("---")

data = fetch_dashboard_data()

if data and "metrics" in data:
    metrics = data["metrics"]
    
    st.markdown("### 📊 Key Metrics")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Tasks", metrics.get("total_tasks", 0))
    
    with col2:
        critical = metrics.get("critical_escalations", 0)
        st.metric("Critical Escalations", critical, delta=None if critical == 0 else f"⚠️ {critical}")
    
    with col3:
        alerts = metrics.get("alerts", 0)
        st.metric("Alerts", alerts, delta=None if alerts == 0 else f"⚠️ {alerts}")
    
    with col4:
        at_risk = metrics.get("at_risk", 0)
        st.metric("At Risk", at_risk)
    
    with col5:
        st.metric("Avg Completion", f"{metrics.get('avg_completion', 0)}%")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎯 Risk Distribution")
        risk_dist = data.get("risk_distribution", {})
        if risk_dist:
            risk_df = pd.DataFrame([
                {"Category": "Critical", "Count": risk_dist.get("critical", 0)},
                {"Category": "Alert", "Count": risk_dist.get("alert", 0)},
                {"Category": "At Risk", "Count": risk_dist.get("at_risk", 0)},
                {"Category": "On Track", "Count": risk_dist.get("on_track", 0)}
            ])
            st.dataframe(risk_df, use_container_width=True, hide_index=True)
    
    with col2:
        st.markdown("### 📦 Module Breakdown")
        module_breakdown = data.get("module_breakdown", {})
        if module_breakdown:
            module_df = pd.DataFrame([
                {"Module": k, "Tasks": v} for k, v in module_breakdown.items()
            ])
            st.dataframe(module_df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    st.markdown("### 🚨 Critical Tasks")
    critical_tasks = data.get("critical_tasks", [])
    if critical_tasks:
        critical_df = pd.DataFrame(critical_tasks)
        display_cols = []
        if "task_name" in critical_df.columns:
            display_cols.append("task_name")
        if "module" in critical_df.columns:
            display_cols.append("module")
        if "completion_percent" in critical_df.columns:
            display_cols.append("completion_percent")
        if "days_overdue" in critical_df.columns:
            display_cols.append("days_overdue")
        
        if display_cols:
            st.dataframe(critical_df[display_cols], use_container_width=True, hide_index=True)
        else:
            st.dataframe(critical_df, use_container_width=True, hide_index=True)
    else:
        st.info("No critical tasks at the moment ✅")
    
    st.markdown("---")
    
    st.markdown("### ⚠️ Alerts")
    alerts_list = data.get("alerts_list", [])
    if alerts_list:
        alerts_df = pd.DataFrame(alerts_list)
        display_cols = []
        if "task_name" in alerts_df.columns:
            display_cols.append("task_name")
        if "module" in alerts_df.columns:
            display_cols.append("module")
        if "completion_percent" in alerts_df.columns:
            display_cols.append("completion_percent")
        
        if display_cols:
            st.dataframe(alerts_df[display_cols], use_container_width=True, hide_index=True)
        else:
            st.dataframe(alerts_df, use_container_width=True, hide_index=True)
    else:
        st.info("No alerts at the moment ✅")
    
    st.markdown("---")
    
    dep_stats = data.get("dependency_stats", {})
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Dependency Nodes", dep_stats.get("nodes", 0))
    
    with col2:
        st.metric("Dependency Edges", dep_stats.get("edges", 0))

else:
    st.warning("Unable to load dashboard data. Please ensure the monitoring system is properly configured.")
    st.info("Make sure you have a WBS Excel file in the data/ directory and configured your .env file.")

st.markdown("---")
st.markdown("### 📖 System Information")
st.info("""
This autonomous monitoring system continuously analyzes your project Work Breakdown Structure (WBS) 
and automatically manages escalations, alerts, and project updates using AI agents.

**Key Features:**
- 24/7 autonomous monitoring
- Risk analysis and dependency tracking
- Automatic email notifications
- Multi-agent AI orchestration
""")

if st.button("🔄 Refresh Dashboard"):
    st.rerun()
