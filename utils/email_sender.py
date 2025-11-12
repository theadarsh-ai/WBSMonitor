"""
Email sending utility using SMTP (Gmail).
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional


class EmailSender:
    """Email sending utility using SMTP."""
    
    def __init__(self, smtp_server: Optional[str] = None, smtp_port: Optional[int] = None,
                 smtp_username: Optional[str] = None, smtp_password: Optional[str] = None,
                 from_email: Optional[str] = None):
        """
        Initialize SMTP email sender.
        
        Args:
            smtp_server: SMTP server address (e.g., smtp.gmail.com)
            smtp_port: SMTP port (587 for TLS, 465 for SSL)
            smtp_username: SMTP username (usually your email)
            smtp_password: SMTP password or app password
            from_email: From email address
        """
        # Load from environment variables with defaults
        self.smtp_server = smtp_server or os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = smtp_port or int(os.environ.get('SMTP_PORT', '587'))
        self.smtp_username = smtp_username or os.environ.get('SMTP_USERNAME')
        self.smtp_password = smtp_password or os.environ.get('SMTP_PASSWORD')
        self.from_email = from_email or os.environ.get('FROM_EMAIL') or self.smtp_username
        
        print(f"✓ SMTP configured: {self.smtp_server}:{self.smtp_port}")
        if self.smtp_username:
            print(f"✓ SMTP username: {self.smtp_username}")
        if self.from_email:
            print(f"✓ From email: {self.from_email}")
        
    def send_email(self, to_emails: List[str], subject: str, body_html: str, 
                   cc_emails: Optional[List[str]] = None) -> bool:
        """
        Send an email to recipients using SMTP.
        
        Args:
            to_emails: List of recipient email addresses
            subject: Email subject
            body_html: HTML body content
            cc_emails: Optional list of CC recipients
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.smtp_username or not self.smtp_password:
                print("✗ SMTP credentials not configured")
                return False
            
            if not self.from_email:
                print("✗ From email not configured")
                return False
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_email
            msg['To'] = ', '.join(to_emails)
            msg['Subject'] = subject
            
            if cc_emails:
                msg['Cc'] = ', '.join(cc_emails)
            
            # Attach HTML body
            html_part = MIMEText(body_html, 'html')
            msg.attach(html_part)
            
            # Combine all recipients
            all_recipients = to_emails.copy()
            if cc_emails:
                all_recipients.extend(cc_emails)
            
            # Connect to SMTP server and send
            if self.smtp_port == 465:
                # SSL connection
                with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, timeout=30) as server:
                    server.login(self.smtp_username, self.smtp_password)
                    server.sendmail(self.from_email, all_recipients, msg.as_string())
            else:
                # TLS connection (port 587)
                with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30) as server:
                    server.ehlo()
                    server.starttls()
                    server.ehlo()
                    server.login(self.smtp_username, self.smtp_password)
                    server.sendmail(self.from_email, all_recipients, msg.as_string())
            
            print(f"✓ Email sent successfully to {', '.join(to_emails)}")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            print(f"✗ SMTP Authentication failed: {e}")
            print("   Tip: For Gmail, use an App Password (not your regular password)")
            return False
        except smtplib.SMTPException as e:
            print(f"✗ SMTP error: {e}")
            return False
        except Exception as e:
            print(f"✗ Failed to send email: {e}")
            return False
