import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any
import logging
import time
from datetime import datetime
import ssl
import dns.resolver
import socket

logger = logging.getLogger(__name__)

class ImprovedEmailService:
    def __init__(self):
        # Gmail SMTP configuration
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = os.getenv('EMAIL_SENDER', 'talkeasyofficial100@gmail.com')
        self.sender_password = os.getenv('EMAIL_PASSWORD', 'bnlrgxnrdmpxnidk')  # App Password
        self.max_retries = 3
        self.retry_delay = 2  # seconds
        
        # Cache for DNS lookups
        self._mx_cache: Dict[str, Any] = {}
        self._mx_cache_ttl = 3600  # 1 hour
        
    def _verify_email_domain(self, email: str) -> bool:
        """Verify if the email domain has valid MX records."""
        try:
            domain = email.split('@')[1]
            if domain in self._mx_cache:
                cache_time, is_valid = self._mx_cache[domain]
                if time.time() - cache_time < self._mx_cache_ttl:
                    return is_valid
            
            mx_records = dns.resolver.resolve(domain, 'MX')
            is_valid = len(mx_records) > 0
            self._mx_cache[domain] = (time.time(), is_valid)
            return is_valid
        except Exception as e:
            logger.warning(f"Failed to verify email domain {domain}: {str(e)}")
            return True  # Assume valid if verification fails
            
    def _create_smtp_connection(self) -> smtplib.SMTP:
        """Create and configure SMTP connection with proper security."""
        smtp = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10)
        context = ssl.create_default_context()
        smtp.starttls(context=context)
        smtp.login(self.sender_email, self.sender_password)
        return smtp
        
    def send_email(self, to_email: str, subject: str, text_content: str, html_content: Optional[str] = None, retry_count: int = 0) -> bool:
        """
        Send email with retry logic and proper error handling.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            text_content: Plain text content
            html_content: Optional HTML content
            retry_count: Current retry attempt (internal use)
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        if retry_count >= self.max_retries:
            logger.error(f"Maximum retry attempts ({self.max_retries}) reached for sending email to {to_email}")
            return False
            
        if not self._verify_email_domain(to_email):
            logger.error(f"Invalid email domain for {to_email}")
            return False
            
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = f"TalkEasy <{self.sender_email}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add timestamp to message ID for uniqueness
            msg['Message-ID'] = f"<{time.time()}.{hash(to_email)}@talkeasy.app>"
            
            # Always add plain text version
            msg.attach(MIMEText(text_content, 'plain'))
            
            # Add HTML version if provided
            if html_content:
                msg.attach(MIMEText(html_content, 'html'))
            
            smtp = None
            try:
                smtp = self._create_smtp_connection()
                smtp.send_message(msg)
                logger.info(f"✅ Email sent successfully to {to_email}")
                return True
                
            except smtplib.SMTPAuthenticationError as e:
                logger.error("❌ SMTP Authentication Failed!")
                logger.error("💡 For Gmail: Make sure you're using an App Password!")
                logger.error("1. Enable 2FA: https://myaccount.google.com/security")
                logger.error("2. Generate App Password: https://myaccount.google.com/apppasswords")
                return False
                
            except smtplib.SMTPServerDisconnected:
                logger.warning("SMTP Server disconnected. Retrying...")
                time.sleep(self.retry_delay)
                return self.send_email(to_email, subject, text_content, html_content, retry_count + 1)
                
            except smtplib.SMTPException as e:
                logger.error(f"SMTP Error: {str(e)}")
                if retry_count < self.max_retries:
                    time.sleep(self.retry_delay)
                    return self.send_email(to_email, subject, text_content, html_content, retry_count + 1)
                return False
                
            finally:
                if smtp:
                    try:
                        smtp.quit()
                    except Exception:
                        pass
                        
        except Exception as e:
            logger.error(f"Unexpected error sending email: {str(e)}")
            if retry_count < self.max_retries:
                time.sleep(self.retry_delay)
                return self.send_email(to_email, subject, text_content, html_content, retry_count + 1)
            return False
            
    def send_welcome_email(self, to_email: str, first_name: str, last_name: str) -> bool:
        """Send welcome email to new users."""
        subject = "🎉 Welcome to TalkEasy - Your Voice Assistant is Ready!"
        
        text_content = f"""
Welcome to TalkEasy, {first_name}!

Your account has been successfully created and is ready to use.

What you can do with TalkEasy:
- Real-time voice conversations with AI
- Stream audio responses instantly
- Get help with tasks using natural voice commands
- Seamless multi-turn conversations

Get started now at: https://talkeasy.app

Best regards,
The TalkEasy Team
        """
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 20px; font-family: Arial, sans-serif; background-color: #f5f5f5;">
    <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
        <div style="text-align: center; padding: 20px 0;">
            <h1 style="color: #4A90E2;">Welcome to TalkEasy! 🎉</h1>
        </div>
        
        <div style="padding: 20px 0;">
            <p style="font-size: 16px; line-height: 1.5;">Dear {first_name} {last_name},</p>
            <p style="font-size: 16px; line-height: 1.5;">Thank you for joining TalkEasy! Your account has been successfully created and is ready to use.</p>
            
            <div style="background-color: #f8f9fa; border-radius: 5px; padding: 15px; margin: 20px 0;">
                <h3 style="color: #2c3e50; margin-bottom: 15px;">What you can do with TalkEasy:</h3>
                <ul style="list-style-type: none; padding: 0;">
                    <li style="padding: 8px 0;">🎤 Real-time voice conversations with AI</li>
                    <li style="padding: 8px 0;">⚡ Stream audio responses instantly</li>
                    <li style="padding: 8px 0;">🤖 Get help with tasks using natural voice commands</li>
                    <li style="padding: 8px 0;">💬 Seamless multi-turn conversations</li>
                </ul>
            </div>
            
            <div style="text-align: center; padding: 20px 0;">
                <a href="https://talkeasy.app" style="background-color: #4A90E2; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; font-weight: bold;">Get Started Now</a>
            </div>
            
            <p style="font-size: 16px; line-height: 1.5;">If you have any questions or need assistance, don't hesitate to contact our support team.</p>
        </div>
        
        <div style="border-top: 1px solid #eee; padding-top: 20px; margin-top: 20px; text-align: center; color: #666;">
            <p style="font-size: 14px;">Best regards,<br>The TalkEasy Team</p>
            <div style="margin-top: 20px; font-size: 12px;">
                <a href="https://talkeasy.app/privacy" style="color: #666; text-decoration: none; margin: 0 10px;">Privacy Policy</a>
                <a href="https://talkeasy.app/terms" style="color: #666; text-decoration: none; margin: 0 10px;">Terms of Service</a>
            </div>
        </div>
    </div>
</body>
</html>
        """
        
        return self.send_email(to_email, subject, text_content, html_content)
        
    def send_verification_email(self, to_email: str, verification_link: str) -> bool:
        """Send email verification link."""
        subject = "Verify Your TalkEasy Email Address"
        
        text_content = f"""
Please verify your email address for TalkEasy

Click the link below to verify your email address:
{verification_link}

If you didn't create a TalkEasy account, please ignore this email.

Best regards,
The TalkEasy Team
        """
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 20px; font-family: Arial, sans-serif; background-color: #f5f5f5;">
    <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
        <div style="text-align: center; padding: 20px 0;">
            <h1 style="color: #4A90E2;">Verify Your Email</h1>
        </div>
        
        <div style="padding: 20px 0;">
            <p style="font-size: 16px; line-height: 1.5;">Please verify your email address to access all features of TalkEasy.</p>
            
            <div style="text-align: center; padding: 30px 0;">
                <a href="{verification_link}" style="background-color: #4A90E2; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; font-weight: bold;">Verify Email Address</a>
            </div>
            
            <p style="font-size: 14px; color: #666;">If you didn't create a TalkEasy account, please ignore this email.</p>
        </div>
        
        <div style="border-top: 1px solid #eee; padding-top: 20px; margin-top: 20px; text-align: center; color: #666;">
            <p style="font-size: 14px;">Best regards,<br>The TalkEasy Team</p>
        </div>
    </div>
</body>
</html>
        """
        
        return self.send_email(to_email, subject, text_content, html_content)

# Create a singleton instance
email_service = ImprovedEmailService()