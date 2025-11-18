"""
Daily Digest Email Scheduler
Sends a single daily summary email at 6 PM with all immediate attention tasks.
"""
import schedule
import time
import threading
from datetime import datetime
from agents.data_ingestion_agent import DataIngestionAgent
from agents.risk_analysis_agent import RiskAnalysisAgent
from agents.escalation_manager_agent import EscalationManagerAgent
import config

class DailyDigestScheduler:
    """Schedules and runs daily digest emails at 9 AM, 2 PM, and 6 PM."""
    
    def __init__(self):
        self.running = False
        self.thread = None
        print("📅 Daily Digest Scheduler initialized (3 digests: 9 AM, 2 PM, 6 PM)")
    
    def send_morning_digest(self):
        """Send the morning digest email - runs at 9 AM (Overdue focus)."""
        print(f"\n🌅 [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Running morning digest (Overdue Tasks)...")
        
        try:
            # Fetch and analyze data
            data_agent = DataIngestionAgent()
            risk_agent = RiskAnalysisAgent()
            escalation_agent = EscalationManagerAgent()
            
            tasks = data_agent.fetch_wbs_data()
            categorized_tasks = risk_agent.analyze_tasks(tasks)
            
            # Send morning digest
            pm_email = config.PM_EMAIL or "adarsh.velmurugan@verint.com"
            success = escalation_agent.send_morning_digest(categorized_tasks, pm_email)
            
            if success:
                print(f"✅ Morning digest sent successfully to {pm_email}")
            else:
                print("⚠️ Morning digest send failed (email not configured or error occurred)")
                
        except Exception as e:
            print(f"❌ Error sending morning digest: {e}")
    
    def send_afternoon_digest(self):
        """Send the afternoon digest email - runs at 2 PM (Risk updates focus)."""
        print(f"\n⚠️ [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Running afternoon digest (Risk Updates)...")
        
        try:
            # Fetch and analyze data
            data_agent = DataIngestionAgent()
            risk_agent = RiskAnalysisAgent()
            escalation_agent = EscalationManagerAgent()
            
            tasks = data_agent.fetch_wbs_data()
            categorized_tasks = risk_agent.analyze_tasks(tasks)
            
            # Send afternoon digest
            pm_email = config.PM_EMAIL or "adarsh.velmurugan@verint.com"
            success = escalation_agent.send_afternoon_digest(categorized_tasks, pm_email)
            
            if success:
                print(f"✅ Afternoon digest sent successfully to {pm_email}")
            else:
                print("⚠️ Afternoon digest send failed (email not configured or error occurred)")
                
        except Exception as e:
            print(f"❌ Error sending afternoon digest: {e}")
    
    def send_daily_digest(self):
        """Send the evening digest email - runs at 6 PM (Full summary)."""
        print(f"\n📊 [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Running evening digest (Full Summary)...")
        
        try:
            # Fetch and analyze data
            data_agent = DataIngestionAgent()
            risk_agent = RiskAnalysisAgent()
            escalation_agent = EscalationManagerAgent()
            
            tasks = data_agent.fetch_wbs_data()
            categorized_tasks = risk_agent.analyze_tasks(tasks)
            
            # Send evening summary
            pm_email = config.PM_EMAIL or "adarsh.velmurugan@verint.com"
            success = escalation_agent.send_daily_summary(categorized_tasks, pm_email)
            
            if success:
                print(f"✅ Evening digest sent successfully to {pm_email}")
            else:
                print("⚠️ Evening digest send failed (email not configured or error occurred)")
                
        except Exception as e:
            print(f"❌ Error sending evening digest: {e}")
    
    def start(self):
        """Start the scheduler in a background thread."""
        if self.running:
            print("⚠️ Scheduler already running")
            return
        
        # Schedule three daily digests
        schedule.every().day.at("09:00").do(self.send_morning_digest)
        schedule.every().day.at("14:00").do(self.send_afternoon_digest)
        schedule.every().day.at("18:00").do(self.send_daily_digest)
        
        print("✅ Scheduled digests:")
        print("   🌅 9:00 AM - Morning Priority Digest (Overdue Tasks)")
        print("   ⚠️ 2:00 PM - Afternoon Risk Alert (Risk Updates)")
        print("   📊 6:00 PM - Evening Summary (Full Overview)")
        
        # Also allow manual trigger for testing
        print("ℹ️  For testing: Call send_morning_digest(), send_afternoon_digest(), or send_daily_digest() manually")
        
        self.running = True
        self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()
        print("✅ Scheduler started in background thread")
    
    def _run_scheduler(self):
        """Run the scheduler loop."""
        while self.running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def stop(self):
        """Stop the scheduler."""
        self.running = False
        schedule.clear()
        print("🛑 Scheduler stopped")
    
    def get_next_run(self):
        """Get next scheduled run time."""
        jobs = schedule.get_jobs()
        if jobs and jobs[0].next_run:
            next_run = jobs[0].next_run
            return next_run.strftime('%Y-%m-%d %H:%M:%S')
        return "No jobs scheduled"

# Global scheduler instance
_scheduler = None

def get_scheduler():
    """Get or create scheduler instance."""
    global _scheduler
    if _scheduler is None:
        _scheduler = DailyDigestScheduler()
    return _scheduler

def start_scheduler():
    """Start the daily digest scheduler."""
    scheduler = get_scheduler()
    scheduler.start()
    return scheduler
