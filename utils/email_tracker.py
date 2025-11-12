"""
Email Tracker - Prevents duplicate emails for the same task on the same day
"""
import json
import os
from datetime import datetime
from typing import Set, Tuple

TRACKER_FILE = 'data/email_tracker.json'

def load_email_tracker() -> dict:
    """Load the email tracker from file"""
    if os.path.exists(TRACKER_FILE):
        try:
            with open(TRACKER_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_email_tracker(tracker: dict):
    """Save the email tracker to file"""
    os.makedirs('data', exist_ok=True)
    with open(TRACKER_FILE, 'w') as f:
        json.dump(tracker, f, indent=2)

def get_today_key() -> str:
    """Get today's date key (YYYY-MM-DD)"""
    return datetime.now().strftime('%Y-%m-%d')

def has_email_been_sent_today(task_id: str, email_type: str = 'alert') -> bool:
    """
    Check if an email has already been sent for this task today
    
    Args:
        task_id: The task ID
        email_type: Type of email ('alert', 'escalation', etc.)
    
    Returns:
        True if email was already sent today, False otherwise
    """
    tracker = load_email_tracker()
    today = get_today_key()
    
    if today not in tracker:
        return False
    
    key = f"{task_id}_{email_type}"
    return key in tracker[today]

def mark_email_sent(task_id: str, email_type: str = 'alert'):
    """
    Mark that an email has been sent for this task today
    
    Args:
        task_id: The task ID
        email_type: Type of email ('alert', 'escalation', etc.)
    """
    tracker = load_email_tracker()
    today = get_today_key()
    
    if today not in tracker:
        tracker[today] = []
    
    key = f"{task_id}_{email_type}"
    if key not in tracker[today]:
        tracker[today].append(key)
    
    # Clean up old dates (keep only last 7 days)
    cleanup_old_entries(tracker)
    save_email_tracker(tracker)

def cleanup_old_entries(tracker: dict):
    """Remove entries older than 7 days"""
    from datetime import timedelta
    
    today = datetime.now()
    cutoff = (today - timedelta(days=7)).strftime('%Y-%m-%d')
    
    dates_to_remove = [date for date in tracker.keys() if date < cutoff]
    for date in dates_to_remove:
        del tracker[date]

def get_emails_sent_today() -> Tuple[int, Set[str]]:
    """
    Get count and list of emails sent today
    
    Returns:
        Tuple of (count, set of task_ids)
    """
    tracker = load_email_tracker()
    today = get_today_key()
    
    if today not in tracker:
        return 0, set()
    
    task_ids = set()
    for key in tracker[today]:
        task_id = key.split('_')[0]  # Extract task_id from "task_id_type"
        task_ids.add(task_id)
    
    return len(tracker[today]), task_ids

def reset_daily_tracker():
    """Reset tracker for new day (called automatically by cleanup)"""
    # Tracker auto-cleans, no manual reset needed
    pass
