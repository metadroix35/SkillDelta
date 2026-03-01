import os
import base64
import requests
from skillrot_app.core.config import settings


SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
FROM_EMAIL = settings.EMAIL_ADDRESS


def send_email(to_email: str, subject: str, html_body: str) -> bool:
    try:
        if not SENDGRID_API_KEY:
            print("SendGrid API key missing.")
            return False

        # Attach logo as base64
        logo_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "assets",
                "skilldelta_logo.png"
            )
        )

        attachments = []

        if os.path.exists(logo_path):
            with open(logo_path, "rb") as f:
                encoded_logo = base64.b64encode(f.read()).decode()

            attachments.append({
                "content": encoded_logo,
                "type": "image/png",
                "filename": "skilldelta_logo.png",
                "disposition": "inline",
                "content_id": "skilldelta_logo"
            })

        data = {
            "personalizations": [
                {
                    "to": [{"email": to_email}],
                    "subject": subject
                }
            ],
            "from": {
                "email": FROM_EMAIL,
                "name": "SkillDelta Alerts"
            },
            "content": [
                {
                    "type": "text/html",
                    "value": html_body
                }
            ],
            "attachments": attachments
        }

        response = requests.post(
            "https://api.sendgrid.com/v3/mail/send",
            headers={
                "Authorization": f"Bearer {SENDGRID_API_KEY}",
                "Content-Type": "application/json"
            },
            json=data
        )

        if response.status_code in [200, 202]:
            print("SkillDelta Email sent via SendGrid.")
            return True
        else:
            print("SendGrid Error:", response.text)
            return False

    except Exception as e:
        print("SendGrid Exception:", str(e))
        return False
