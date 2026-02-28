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
        if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
            print("Email credentials not configured.")
            return False

        # 🔥 Create main message container
        msg = MIMEMultipart("related")
        msg["From"] = f"SkillDelta Alerts <{EMAIL_ADDRESS}>"
        msg["To"] = to_email
        msg["Subject"] = subject
        msg["Reply-To"] = EMAIL_ADDRESS

        # 🔥 Alternative part (HTML)
        msg_alternative = MIMEMultipart("alternative")
        msg.attach(msg_alternative)

        msg_alternative.attach(MIMEText(html_body, "html"))

        # 🔥 Attach logo inline (if exists)
        logo_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "assets",
                "skilldelta_logo.png"
            )
        )

        if os.path.exists(logo_path):
            with open(logo_path, "rb") as f:
                logo = MIMEImage(f.read())
                logo.add_header("Content-ID", "<skilldelta_logo>")
                logo.add_header(
                    "Content-Disposition",
                    "inline",
                    filename="skilldelta_logo.png"
                )
                msg.attach(logo)
        else:
            print("Logo file not found at:", logo_path)

        # 🔥 Use TLS (587) — Render friendly
        server = smtplib.SMTP("smtp.gmail.com", 587, timeout=30)
        server.ehlo()
        server.starttls()
        server.ehlo()

        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, to_email, msg.as_string())
        server.quit()

        print("SkillDelta Email sent successfully.")
        return True

    except Exception as e:
        print("SkillDelta Email Error:", str(e))
        return False
