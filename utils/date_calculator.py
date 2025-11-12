"""
Date calculation utilities for task analysis.
"""
from datetime import datetime, timedelta
from typing import Optional


class DateCalculator:
    """Utilities for date calculations and deadline analysis."""
    
    @staticmethod
    def days_overdue(end_date: Optional[datetime]) -> int:
        """
        Calculate how many days a task is overdue.
        
        Args:
            end_date: Task end date
            
        Returns:
            Number of days overdue (positive) or days remaining (negative)
        """
        if not end_date:
            return 0
        
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        delta = (today - end_date).days
        return delta
    
    @staticmethod
    def is_approaching_deadline(end_date: Optional[datetime], days_threshold: int = 3) -> bool:
        """
        Check if task deadline is approaching within threshold days.
        
        Args:
            end_date: Task end date
            days_threshold: Number of days to consider as "approaching"
            
        Returns:
            True if deadline is approaching, False otherwise
        """
        if not end_date:
            return False
        
        days_until = -DateCalculator.days_overdue(end_date)
        return 0 <= days_until <= days_threshold
    
    @staticmethod
    def recalculate_end_date(start_date: Optional[datetime], duration_days: int) -> Optional[datetime]:
        """
        Recalculate end date based on start date and duration.
        
        Args:
            start_date: Task start date
            duration_days: Duration in days
            
        Returns:
            Calculated end date
        """
        if not start_date or duration_days <= 0:
            return None
        
        return start_date + timedelta(days=duration_days)
    
    @staticmethod
    def format_date(date: Optional[datetime]) -> str:
        """Format date for display."""
        if not date:
            return "N/A"
        return date.strftime("%Y-%m-%d")
