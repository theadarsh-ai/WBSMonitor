"""
Test SMTP email sending configuration.
"""
import os
from utils.email_sender import EmailSender


def test_smtp():
    """Test SMTP configuration and send a test email."""
    
    print("=" * 60)
    print("SMTP CONFIGURATION CHECK")
    print("=" * 60)
    
    # Check configuration
    smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = os.environ.get('SMTP_PORT', '587')
    smtp_username = os.environ.get('SMTP_USERNAME')
    smtp_password = os.environ.get('SMTP_PASSWORD')
    from_email = os.environ.get('FROM_EMAIL') or smtp_username
    
    print(f"SMTP Server: {smtp_server}")
    print(f"SMTP Port: {smtp_port}")
    print(f"Username: {smtp_username or 'NOT SET'}")
    print(f"Password: {'SET' if smtp_password else 'NOT SET'}")
    print(f"From Email: {from_email or 'NOT SET'}")
    print("=" * 60)
    print()
    
    if not smtp_username or not smtp_password:
        print("❌ SMTP credentials not configured!")
        print()
        print("Please set these secrets in Replit:")
        print("  - SMTP_USERNAME (your Gmail address)")
        print("  - SMTP_PASSWORD (Gmail App Password)")
        print()
        print("How to get Gmail App Password:")
        print("1. Go to: https://myaccount.google.com/security")
        print("2. Enable 2-Step Verification (if not enabled)")
        print("3. Go to: https://myaccount.google.com/apppasswords")
        print("4. Create an app password for 'Mail'")
        print("5. Copy the 16-character password")
        print()
        return False
    
    print("✓ SMTP is configured")
    print()
    print("=" * 60)
    print("ATTEMPTING TEST EMAIL...")
    print("=" * 60)
    
    # Initialize email sender
    sender = EmailSender()
    
    # Test email content
    subject = "🤖 Test Email from Autonomous Monitoring System"
    body = """
    <html>
    <body style="font-family: Arial, sans-serif;">
        <h2 style="color: #2563eb;">✓ SMTP Configuration Successful!</h2>
        <p>This is a test email from your autonomous project monitoring system.</p>
        <p>If you received this email, SMTP is working correctly and your system can send emails autonomously.</p>
        <hr>
        <p style="color: #666; font-size: 12px;">
            <strong>Autonomous Agentic AI Project Monitoring System</strong><br>
            Powered by LangGraph & Azure AI
        </p>
    </body>
    </html>
    """
    
    # Send test email to both addresses
    recipients = ["adarsh.arvr@gmail.com", "adarshprvt@gmail.com"]
    
    success = sender.send_email(
        to_emails=recipients,
        subject=subject,
        body_html=body
    )
    
    print()
    if success:
        print("=" * 60)
        print("✅ TEST EMAIL SENT SUCCESSFULLY!")
        print("=" * 60)
        print(f"Check your inbox: {', '.join(recipients)}")
        print()
        return True
    else:
        print("=" * 60)
        print("❌ TEST EMAIL FAILED")
        print("=" * 60)
        print()
        return False


if __name__ == "__main__":
    test_smtp()
