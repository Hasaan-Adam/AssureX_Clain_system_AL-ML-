"""
AssureX Claim Engine - Email Service
Provides SMTP email delivery (Gmail App Password, Mailtrap, AWS SES) with responsive HTML templates.
"""

import os
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Optional, Union
from datetime import datetime

from src.config import settings

logger = logging.getLogger("assurex.email")


def _get_base_html(title: str, preheader: str, content_html: str) -> str:
    """Wrap content in a clean, modern AssureX branded email template."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      margin: 0;
      padding: 0;
      background-color: #f8fafc;
      color: #1e293b;
      -webkit-font-smoothing: antialiased;
    }}
    .wrapper {{
      width: 100%;
      background-color: #f8fafc;
      padding: 30px 15px;
    }}
    .container {{
      max-width: 580px;
      margin: 0 auto;
      background-color: #ffffff;
      border-radius: 16px;
      overflow: hidden;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
      border: 1px solid #e2e8f0;
    }}
    .header {{
      background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
      padding: 28px 32px;
      text-align: left;
    }}
    .header h1 {{
      margin: 0;
      color: #ffffff;
      font-size: 20px;
      font-weight: 700;
      letter-spacing: -0.5px;
    }}
    .header .subtitle {{
      margin: 4px 0 0 0;
      color: #94a3b8;
      font-size: 13px;
    }}
    .body {{
      padding: 32px;
    }}
    .badge {{
      display: inline-block;
      padding: 4px 12px;
      border-radius: 9999px;
      font-size: 12px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}
    .badge-valid {{ background-color: #ecfdf5; color: #059669; border: 1px solid #a7f3d0; }}
    .badge-invalid {{ background-color: #fff1f2; color: #e11d48; border: 1px solid #fecdd3; }}
    .badge-review {{ background-color: #fffbeb; color: #d97706; border: 1px solid #fde68a; }}
    .badge-info {{ background-color: #eff6ff; color: #2563eb; border: 1px solid #bfdbfe; }}
    .card {{
      background-color: #f8fafc;
      border-radius: 12px;
      padding: 16px 20px;
      margin: 20px 0;
      border: 1px solid #e2e8f0;
    }}
    .card-row {{
      display: flex;
      justify-content: space-between;
      padding: 8px 0;
      border-bottom: 1px solid #edf2f7;
      font-size: 13px;
    }}
    .card-row:last-child {{
      border-bottom: none;
    }}
    .card-label {{
      color: #64748b;
      font-weight: 500;
    }}
    .card-value {{
      color: #0f172a;
      font-weight: 600;
    }}
    .btn {{
      display: inline-block;
      background-color: #2563eb;
      color: #ffffff !important;
      text-decoration: none;
      padding: 12px 24px;
      border-radius: 10px;
      font-size: 14px;
      font-weight: 600;
      text-align: center;
      margin-top: 16px;
    }}
    .footer {{
      background-color: #f1f5f9;
      padding: 20px 32px;
      text-align: center;
      font-size: 12px;
      color: #94a3b8;
      border-top: 1px solid #e2e8f0;
    }}
  </style>
</head>
<body>
  <div class="wrapper">
    <div class="container">
      <div class="header">
        <h1>AssureX Claim Engine</h1>
        <div class="subtitle">Warranty Lifecycle & AI Adjudication System</div>
      </div>
      <div class="body">
        {content_html}
      </div>
      <div class="footer">
        &copy; {datetime.utcnow().year} AssureX Claims Inc. This is an automated notification.
      </div>
    </div>
  </div>
</body>
</html>
"""


def send_email(
    to_email: Union[str, List[str]],
    subject: str,
    html_body: str,
    text_body: Optional[str] = None,
) -> bool:
    """
    Send an email via SMTP with graceful fallback.
    Reads config from environment variables or settings.yaml.
    """
    email_enabled = os.getenv("EMAIL_ENABLED", "").lower() in ("true", "1", "yes") or settings.email.enabled
    smtp_host = os.getenv("SMTP_HOST", settings.email.smtp_host)
    smtp_port = int(os.getenv("SMTP_PORT", str(settings.email.smtp_port)))
    smtp_user = os.getenv("SMTP_USERNAME", settings.email.smtp_username)
    smtp_pass = os.getenv("SMTP_PASSWORD", settings.email.smtp_password)
    from_email = os.getenv("EMAIL_FROM", settings.email.from_email)
    from_name = os.getenv("EMAIL_FROM_NAME", settings.email.from_name)

    recipients = [to_email] if isinstance(to_email, str) else to_email

    if not email_enabled:
        logger.info(f"[Email Disabled] To: {recipients} | Subject: {subject}")
        return True

    if not smtp_user or not smtp_pass:
        logger.warning(f"[Email Config Missing] SMTP_USERNAME or SMTP_PASSWORD not set. Cannot send to {recipients}.")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{from_name} <{from_email}>"
        msg["To"] = ", ".join(recipients)

        if text_body:
            msg.attach(MIMEText(text_body, "plain", "utf-8"))
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        # Gmail standard TLS on port 587
        if smtp_port == 465:
            server = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=10)
        else:
            server = smtplib.SMTP(smtp_host, smtp_port, timeout=10)
            server.ehlo()
            server.starttls()
            server.ehlo()

        server.login(smtp_user, smtp_pass)
        server.sendmail(from_email, recipients, msg.as_string())
        server.quit()

        logger.info(f"Email successfully sent to {recipients} | Subject: {subject}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {recipients}: {e}", exc_info=False)
        return False


# ----------------------------------------------------------------------
# Specialized Lifecycle Notification Email Helpers
# ----------------------------------------------------------------------

def send_claim_submission_email(claim_number: str, user_email: str, user_name: str, product_name: str, fault_type: str) -> bool:
    """Notify customer that claim has been submitted."""
    title = f"Claim #{claim_number} Submitted Successfully"
    content = f"""
      <h2 style="font-size: 18px; margin-top: 0; color: #0f172a;">Hello {user_name},</h2>
      <p style="font-size: 14px; line-height: 1.6; color: #475569;">
        Your claim has been securely received by the AssureX Claim Engine and has entered the automated evaluation stage.
      </p>
      
      <div class="card">
        <table style="width: 100%; font-size: 13px; border-collapse: collapse;">
          <tr style="border-bottom: 1px solid #e2e8f0; height: 32px;">
            <td style="color: #64748b; font-weight: 500;">Claim ID:</td>
            <td style="text-align: right; color: #0f172a; font-weight: 700;">{claim_number}</td>
          </tr>
          <tr style="border-bottom: 1px solid #e2e8f0; height: 32px;">
            <td style="color: #64748b; font-weight: 500;">Product:</td>
            <td style="text-align: right; color: #0f172a; font-weight: 600;">{product_name}</td>
          </tr>
          <tr style="border-bottom: 1px solid #e2e8f0; height: 32px;">
            <td style="color: #64748b; font-weight: 500;">Reported Fault:</td>
            <td style="text-align: right; color: #0f172a; font-weight: 600;">{fault_type}</td>
          </tr>
          <tr style="height: 32px;">
            <td style="color: #64748b; font-weight: 500;">Status:</td>
            <td style="text-align: right;"><span class="badge badge-info">Under Evaluation</span></td>
          </tr>
        </table>
      </div>

      <p style="font-size: 13px; color: #64748b;">
        Our AI ensemble (Python ML Model + Computer Vision) and warranty rule engine will evaluate your submission. You will receive real-time notifications on any status change.
      </p>
    """
    html = _get_base_html(title, f"Claim {claim_number} received", content)
    return send_email(user_email, title, html)


def send_claim_decision_email(
    claim_number: str,
    user_email: str,
    user_name: str,
    decision: str,
    product_name: str,
    comments: Optional[str] = None
) -> bool:
    """Notify customer regarding final claim decision (Approved, Rejected, Info Required)."""
    decision_clean = decision.upper()
    
    if "APPROVE" in decision_clean:
        badge_class = "badge-valid"
        badge_text = "Approved"
        lead_text = "Great news! Your warranty claim has been approved."
    elif "REJECT" in decision_clean:
        badge_class = "badge-invalid"
        badge_text = "Rejected"
        lead_text = "Your warranty claim has been reviewed and rejected based on policy coverage terms."
    else:
        badge_class = "badge-review"
        badge_text = "Action Required"
        lead_text = "Additional information or documentation is required to complete your claim review."

    title = f"Update on Claim #{claim_number} - {badge_text}"
    content = f"""
      <h2 style="font-size: 18px; margin-top: 0; color: #0f172a;">Hello {user_name},</h2>
      <p style="font-size: 14px; line-height: 1.6; color: #475569;">
        {lead_text}
      </p>
      
      <div class="card">
        <table style="width: 100%; font-size: 13px; border-collapse: collapse;">
          <tr style="border-bottom: 1px solid #e2e8f0; height: 32px;">
            <td style="color: #64748b; font-weight: 500;">Claim ID:</td>
            <td style="text-align: right; color: #0f172a; font-weight: 700;">{claim_number}</td>
          </tr>
          <tr style="border-bottom: 1px solid #e2e8f0; height: 32px;">
            <td style="color: #64748b; font-weight: 500;">Product:</td>
            <td style="text-align: right; color: #0f172a; font-weight: 600;">{product_name}</td>
          </tr>
          <tr style="border-bottom: 1px solid #e2e8f0; height: 32px;">
            <td style="color: #64748b; font-weight: 500;">Outcome:</td>
            <td style="text-align: right;"><span class="badge {badge_class}">{badge_text}</span></td>
          </tr>
          {f'<tr style="height: 32px;"><td style="color: #64748b; font-weight: 500;">Reviewer Notes:</td><td style="text-align: right; color: #334155; font-style: italic;">{comments}</td></tr>' if comments else ''}
        </table>
      </div>

      <p style="font-size: 13px; color: #64748b;">
        You can log in to your AssureX dashboard at any time to view complete evaluation reports and download PDF summaries.
      </p>
    """
    html = _get_base_html(title, f"Claim {claim_number} status updated", content)
    return send_email(user_email, title, html)


def send_warranty_expiry_alert_email(
    user_email: str,
    user_name: str,
    product_name: str,
    serial_number: str,
    expiry_date: str,
    days_left: int
) -> bool:
    """Notify customer that a warranty is nearing expiration."""
    title = f"Warranty Expiring Soon: {product_name} ({days_left} days left)"
    content = f"""
      <h2 style="font-size: 18px; margin-top: 0; color: #0f172a;">Hello {user_name},</h2>
      <p style="font-size: 14px; line-height: 1.6; color: #475569;">
        This is a reminder that the warranty for your registered product is nearing expiration.
      </p>
      
      <div class="card">
        <table style="width: 100%; font-size: 13px; border-collapse: collapse;">
          <tr style="border-bottom: 1px solid #e2e8f0; height: 32px;">
            <td style="color: #64748b; font-weight: 500;">Product:</td>
            <td style="text-align: right; color: #0f172a; font-weight: 700;">{product_name}</td>
          </tr>
          <tr style="border-bottom: 1px solid #e2e8f0; height: 32px;">
            <td style="color: #64748b; font-weight: 500;">Serial Number:</td>
            <td style="text-align: right; color: #0f172a; font-mono font-weight: 600;">{serial_number}</td>
          </tr>
          <tr style="border-bottom: 1px solid #e2e8f0; height: 32px;">
            <td style="color: #64748b; font-weight: 500;">Expiry Date:</td>
            <td style="text-align: right; color: #dc2626; font-weight: 700;">{expiry_date}</td>
          </tr>
          <tr style="height: 32px;">
            <td style="color: #64748b; font-weight: 500;">Time Remaining:</td>
            <td style="text-align: right;"><span class="badge badge-review">{days_left} Days</span></td>
          </tr>
        </table>
      </div>

      <p style="font-size: 13px; color: #64748b;">
        If you are experiencing any issues with your device, please file a claim before the expiry date to ensure complete warranty coverage.
      </p>
    """
    html = _get_base_html(title, f"Warranty for {product_name} expiring", content)
    return send_email(user_email, title, html)
