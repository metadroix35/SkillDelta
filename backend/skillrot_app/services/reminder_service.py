from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
from skillrot_app.models.skill import Skill
from skillrot_app.models.skill_history import SkillHistory
from skillrot_app.models.reminder import Reminder
from skillrot_app.models.user import User
from skillrot_app.services.decay_service import recalculate_skill_decay
from skillrot_app.services.email_service import send_email


HEALTH_THRESHOLD = 50
INACTIVITY_DAYS = 14


def check_and_create_reminders(db: Session):

    skills = db.query(Skill).all()

    for skill in skills:

        user = db.query(User).filter(User.id == skill.user_id).first()
        if not user:
            continue

        # 🔥 Recalculate health
        health = recalculate_skill_decay(skill, db)

        # 🔥 Determine last usage
        history = (
            db.query(SkillHistory)
            .filter(SkillHistory.skill_id == skill.id)
            .order_by(SkillHistory.date.desc())
            .first()
        )

        last_used = history.date if history else skill.learned_date
        days_since = (date.today() - last_used).days

        print(f"SkillDelta Reminder → Skill: {skill.name}")
        print(f"Health: {health}, Days since: {days_since}")

        # 🔥 Trigger condition
        if health < HEALTH_THRESHOLD or days_since > INACTIVITY_DAYS:

            # ✅ Avoid duplicate reminder within 24h
            recent_reminder = (
                db.query(Reminder)
                .filter(
                    Reminder.skill_id == skill.id,
                    Reminder.created_at >= datetime.utcnow() - timedelta(hours=24),
                    Reminder.email_sent == True
                )
                .first()
            )

            if recent_reminder:
                print("Recent successful reminder exists. Skipping.")
                continue

            message = f"Skill '{skill.name}' needs attention. Health: {health}"

            reminder = Reminder(
                user_id=user.id,
                skill_id=skill.id,
                message=message,
                email_sent=False
            )

            db.add(reminder)
            db.commit()

            # 🔥 Professional SkillDelta HTML Email
            subject = f"⚠️ SkillDelta Alert: '{skill.name}' Needs Your Attention"

            html_body = f"""
<html>
  <body style="font-family: Arial, sans-serif;">

    <p>Hello {user.name},</p>

    <p>Your skill <strong>{skill.name}</strong> is at risk.</p>

    <p>
      <strong>Current Health:</strong> {round(health, 2)}<br>
      <strong>Days Since Last Practice:</strong> {days_since}
    </p>

    <p>Your retention is declining due to natural forgetting.</p>

    <p><strong>We recommend practicing soon.</strong></p>

    <hr>

    <p style="font-size:13px;">
      Best regards,<br>
      <strong>SkillDelta Team</strong>
    </p>

    <img src="cid:skilldelta_logo" width="180" style="margin-top:10px;" />

    <p style="font-size:11px; color:gray; margin-top:15px;">
      This is an automated email from SkillDelta.<br>
      Please do not reply to this message.<br><br>
      © {datetime.now().year} SkillDelta. All rights reserved.
    </p>

  </body>
</html>
"""

            success = send_email(user.email, subject, html_body)

            if success:
                reminder.email_sent = True
                db.commit()
                print("SkillDelta Email sent successfully.")
            else:
                print("SkillDelta Email sending failed.")