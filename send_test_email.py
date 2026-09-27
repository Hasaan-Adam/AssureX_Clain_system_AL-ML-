import sys
import os

# Set environment explicitly
os.environ["EMAIL_ENABLED"] = "true"
os.environ["SMTP_HOST"] = "smtp.gmail.com"
os.environ["SMTP_PORT"] = "587"
os.environ["SMTP_USERNAME"] = "ahmedbilalkhangl09@gmail.com"
os.environ["SMTP_PASSWORD"] = "pvrahwujjucsqwlo"
os.environ["EMAIL_FROM"] = "ahmedbilalkhangl09@gmail.com"
os.environ["EMAIL_FROM_NAME"] = "AssureX Claim Engine"

from src.services.email_service import send_email, _get_base_html

def main():
    to_email = "huntergaming5555566@gmail.com"
    subject = "AssureX Claim Engine - Test Email Verification"
    
    content = """
      <h2 style="font-size: 18px; margin-top: 0; color: #0f172a;">AssureX Live Email Notification Test</h2>
      <p style="font-size: 14px; line-height: 1.6; color: #475569;">
        Hello! This is an official live test email from the <strong>AssureX AI Claim Adjudication Engine</strong>.
      </p>
      
      <div class="card">
        <table style="width: 100%; font-size: 13px; border-collapse: collapse;">
          <tr style="border-bottom: 1px solid #e2e8f0; height: 32px;">
            <td style="color: #64748b; font-weight: 500;">SMTP Server:</td>
            <td style="text-align: right; color: #0f172a; font-weight: 700;">smtp.gmail.com:587</td>
          </tr>
          <tr style="border-bottom: 1px solid #e2e8f0; height: 32px;">
            <td style="color: #64748b; font-weight: 500;">Sender:</td>
            <td style="text-align: right; color: #0f172a; font-weight: 600;">ahmedbilalkhangl09@gmail.com</td>
          </tr>
          <tr style="border-bottom: 1px solid #e2e8f0; height: 32px;">
            <td style="color: #64748b; font-weight: 500;">Recipient:</td>
            <td style="text-align: right; color: #0f172a; font-weight: 600;">huntergaming5555566@gmail.com</td>
          </tr>
          <tr style="height: 32px;">
            <td style="color: #64748b; font-weight: 500;">System Status:</td>
            <td style="text-align: right;"><span class="badge badge-valid">ACTIVE &amp; VERIFIED</span></td>
          </tr>
        </table>
      </div>

      <p style="font-size: 13px; color: #64748b;">
        All automated emails for Claim Submissions, Review Approvals/Rejections, and Warranty Expiry Alerts are now fully integrated and operational.
      </p>
    """
    
    html = _get_base_html("AssureX Test Notification", "System Email Test", content)
    success = send_email(to_email=to_email, subject=subject, html_body=html)
    print(f"EMAIL_SENT_RESULT: {success}")
    if success:
        print("SUCCESS: Test email was successfully sent to huntergaming5555566@gmail.com!")
    else:
        print("FAILURE: Email could not be sent. Please check credentials or network.")

if __name__ == "__main__":
    main()
