import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import settings


class EmailService:
    def _send(self, subject: str, receiver: str, html: str) -> None:
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = settings.smtp_email
        message["To"] = receiver
        message.attach(MIMEText(html, "html"))

        try:
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
                server.starttls()
                server.login(settings.smtp_email, settings.smtp_password)
                server.sendmail(settings.smtp_email, receiver, message.as_string())
        except Exception as e:
            import logging
            logging.error(f"Failed to send email to {receiver}: {e}")

    def send_user_ticket_email(self, user_email: str, ticket_id: str, localized_summary: str) -> None:
        html = f"""
        <h3>CyberGuard AI - Complaint Registered</h3>
        <p>Your complaint is registered successfully.</p>
        <p><b>Ticket ID:</b> {ticket_id}</p>
        <p><b>Summary:</b> {localized_summary}</p>
        """
        self._send("CyberGuard AI - Ticket Confirmation", user_email, html)

    def send_admin_complaint_email(self, admin_email: str, ticket_id: str, english_summary: str) -> None:
        html = f"""
        <h3>New Cyber Crime Complaint</h3>
        <p><b>Ticket ID:</b> {ticket_id}</p>
        <p><b>Complaint Summary (English):</b></p>
        <p>{english_summary}</p>
        """
        self._send("[CyberGuard AI] New Complaint Submitted", admin_email, html)


email_service = EmailService()
