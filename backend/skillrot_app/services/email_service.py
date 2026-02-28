import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from skillrot_app.core.config import settings


EMAIL_ADDRESS = settings.EMAIL_ADDRESS
EMAIL_PASSWORD = settings.EMAIL_PASSWORD


def send_email(to_email: str, subject: str, html_body: str) -> bool:
    try:
        msg = MIMEMultipart("related")
        msg['From'] = f"SkillDelta Alerts <{EMAIL_ADDRESS}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        msg['Reply-To'] = EMAIL_ADDRESS

        # HTML body
        msg_alternative = MIMEMultipart("alternative")
        msg.attach(msg_alternative)

        msg_alternative.attach(MIMEText(html_body, "html"))

        # 🔥 Attach logo inline
        logo_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "assets",
            "skilldelta_logo.png"
        )

        with open(logo_path, "rb") as f:
            logo = MIMEImage(f.read())
            logo.add_header("Content-ID", "<skilldelta_logo>")
            logo.add_header("Content-Disposition", "inline", filename="skilldelta_logo.png")
            msg.attach(logo)

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, to_email, msg.as_string())
        server.quit()

        return True

    except Exception as e:
        print("Email Error:", e)
        return False