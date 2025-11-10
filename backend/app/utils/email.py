import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
from typing import List

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM = os.getenv("SMTP_FROM", "noreply@voiceagent.com")
SMTP_TLS = os.getenv("SMTP_TLS", "True").lower() == "true"
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")


async def send_email(
    to_email: str,
    subject: str,
    html_content: str,
    text_content: str = None
):
    """Send an email"""
    if not SMTP_USER or not SMTP_PASSWORD:
        print(f"⚠️  Email not configured. Would send to {to_email}: {subject}")
        return
    
    message = MIMEMultipart("alternative")
    message["From"] = SMTP_FROM
    message["To"] = to_email
    message["Subject"] = subject
    
    # Add plain text version
    if text_content:
        text_part = MIMEText(text_content, "plain")
        message.attach(text_part)
    
    # Add HTML version
    html_part = MIMEText(html_content, "html")
    message.attach(html_part)
    
    try:
        if SMTP_TLS:
            await aiosmtplib.send(
                message,
                hostname=SMTP_HOST,
                port=SMTP_PORT,
                username=SMTP_USER,
                password=SMTP_PASSWORD,
                start_tls=True
            )
        else:
            await aiosmtplib.send(
                message,
                hostname=SMTP_HOST,
                port=SMTP_PORT,
                username=SMTP_USER,
                password=SMTP_PASSWORD,
            )
        print(f"✅ Email sent to {to_email}: {subject}")
    except Exception as e:
        print(f"❌ Failed to send email to {to_email}: {str(e)}")


async def send_welcome_email(to_email: str, full_name: str, company_name: str):
    """Send welcome email to new user"""
    subject = f"Welcome to {company_name} Voice Agent Platform"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #4F46E5; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; background-color: #f9f9f9; }}
            .button {{ display: inline-block; padding: 12px 24px; background-color: #4F46E5; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
            .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Welcome to Voice Agent Platform</h1>
            </div>
            <div class="content">
                <h2>Hello {full_name}!</h2>
                <p>Welcome to <strong>{company_name}</strong> on Voice Agent Platform.</p>
                <p>Your account has been successfully created. You can now access your dashboard and manage your voice agents.</p>
                <p>For enhanced security, we strongly recommend enabling Multi-Factor Authentication (MFA) in your account settings.</p>
                <a href="{FRONTEND_URL}/dashboard" class="button">Go to Dashboard</a>
                <p>If you have any questions, please don't hesitate to contact our support team.</p>
            </div>
            <div class="footer">
                <p>&copy; 2025 Voice Agent Platform. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
    Welcome to Voice Agent Platform
    
    Hello {full_name}!
    
    Welcome to {company_name} on Voice Agent Platform.
    
    Your account has been successfully created. You can now access your dashboard at:
    {FRONTEND_URL}/dashboard
    
    For enhanced security, we strongly recommend enabling Multi-Factor Authentication (MFA) in your account settings.
    
    If you have any questions, please don't hesitate to contact our support team.
    """
    
    await send_email(to_email, subject, html_content, text_content)


async def send_mfa_enabled_email(to_email: str, full_name: str):
    """Send notification when MFA is enabled"""
    subject = "Multi-Factor Authentication Enabled"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #10B981; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; background-color: #f9f9f9; }}
            .alert {{ background-color: #FEF3C7; padding: 15px; border-left: 4px solid #F59E0B; margin: 20px 0; }}
            .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔒 MFA Enabled</h1>
            </div>
            <div class="content">
                <h2>Hello {full_name}!</h2>
                <p>Multi-Factor Authentication has been successfully enabled on your account.</p>
                <div class="alert">
                    <strong>Important:</strong> From now on, you'll need to enter a verification code from your authenticator app when logging in.
                </div>
                <p>Make sure to save your backup codes in a secure location. You can use them to access your account if you lose your authenticator device.</p>
                <p>If you didn't enable MFA, please contact support immediately.</p>
            </div>
            <div class="footer">
                <p>&copy; 2025 Voice Agent Platform. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
    Multi-Factor Authentication Enabled
    
    Hello {full_name}!
    
    Multi-Factor Authentication has been successfully enabled on your account.
    
    From now on, you'll need to enter a verification code from your authenticator app when logging in.
    
    Make sure to save your backup codes in a secure location.
    
    If you didn't enable MFA, please contact support immediately.
    """
    
    await send_email(to_email, subject, html_content, text_content)


async def send_login_notification(to_email: str, full_name: str, ip_address: str, location: str = "Unknown"):
    """Send notification for new login"""
    subject = "New Login to Your Account"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #3B82F6; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; background-color: #f9f9f9; }}
            .info {{ background-color: #EFF6FF; padding: 15px; border-left: 4px solid #3B82F6; margin: 20px 0; }}
            .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>New Login Detected</h1>
            </div>
            <div class="content">
                <h2>Hello {full_name}!</h2>
                <p>We detected a new login to your account:</p>
                <div class="info">
                    <p><strong>IP Address:</strong> {ip_address}</p>
                    <p><strong>Location:</strong> {location}</p>
                    <p><strong>Time:</strong> Just now</p>
                </div>
                <p>If this was you, no action is needed.</p>
                <p>If you don't recognize this login, please secure your account immediately by changing your password.</p>
            </div>
            <div class="footer">
                <p>&copy; 2025 Voice Agent Platform. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
    New Login Detected
    
    Hello {full_name}!
    
    We detected a new login to your account:
    
    IP Address: {ip_address}
    Location: {location}
    Time: Just now
    
    If this was you, no action is needed.
    
    If you don't recognize this login, please secure your account immediately.
    """
    
    await send_email(to_email, subject, html_content, text_content)
