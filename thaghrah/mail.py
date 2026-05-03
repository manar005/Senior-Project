"""Password reset email delivery."""
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import smtplib


def send_reset_link_email(to_email, reset_link):
    """Send password reset link. Uses SMTP from env or prints to console."""
    subject = "Thaghrah – Reset your password"
    body = (
        f"Hello,\n\nYou requested a password reset for your Thaghrah account.\n\n"
        f"Click the link below to set a new password (link expires in 15 minutes):\n\n{reset_link}\n\n"
        f"If you did not request this, please ignore this email.\n\n— Thaghrah\n"
    )
    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = os.environ.get("MAIL_FROM", "noreply@thaghrah.local")
    msg["To"] = to_email
    msg.attach(MIMEText(body, "plain"))
    server = os.environ.get("MAIL_SERVER")
    if not server:
        print(f"[MAIL] No MAIL_SERVER set. Password reset link for {to_email}:\n{reset_link}")
        return True
    try:
        port = int(os.environ.get("MAIL_PORT", "587"))
        use_tls = os.environ.get("MAIL_USE_TLS", "1").lower() in ("1", "true", "yes")
        username = os.environ.get("MAIL_USERNAME")
        password = os.environ.get("MAIL_PASSWORD")
        with smtplib.SMTP(server, port) as smtp:
            if use_tls:
                smtp.starttls()
            if username and password:
                smtp.login(username, password)
            smtp.sendmail(msg["From"], [to_email], msg.as_string())
        return True
    except Exception as e:
        print(f"[MAIL] Failed to send reset email: {e}")
        return False
