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
    """Schedules and runs daily digest email at 6 PM."""
    
    def __init__(self):
        self.running = False
        self.thread = None
        print("📅 Daily Digest Scheduler initialized")
    
    def send_daily_digest(self):
        """Send the daily digest email - runs at 6 PM."""
        print(f"\n📧 [{ datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Running daily digest...")
        
        try:
            # Fetch and analyze data
            data_agent = DataIngestionAgent()
            risk_agent = RiskAnalysisAgent()
            escalation_agent = EscalationManagerAgent()
            
            tasks = data_agent.fetch_wbs_data()
            categorized_tasks = risk_agent.analyze_tasks(tasks)
            
            # Send daily summary
            pm_email = config.PM_EMAIL or "adarsh.velmurugan@verint.com"
            success = escalation_agent.send_daily_summary(categorized_tasks, pm_email)
            
            if success:
                print(f"✅ Daily digest sent successfully to {pm_email}")
            else:
                print("⚠️ Daily digest send failed (email not configured or error occurred)")
                
        except Exception as e:
            print(f"❌ Error sending daily digest: {e}")
    
    def start(self):
        """Start the scheduler in a background thread."""
        if self.running:
            print("⚠️ Scheduler already running")
            return
        
        # Schedule daily digest at 6 PM
        schedule.every().day.at("18:00").do(self.send_daily_digest)
        print("✅ Scheduled daily digest for 6:00 PM every day")
        
        # Also allow manual trigger for testing
        print("ℹ️  For testing: Call send_daily_digest() manually or wait until 6 PM")
        
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
