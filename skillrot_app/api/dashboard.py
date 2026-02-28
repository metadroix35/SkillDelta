from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date

from skillrot_app.db.database import get_db
from skillrot_app.models.user import User
from skillrot_app.models.skill import Skill
from skillrot_app.models.skill_history import SkillHistory
from skillrot_app.models.reminder import Reminder
from skillrot_app.models.skill_health_history import SkillHealthHistory
from skillrot_app.services.decay_service import recalculate_skill_decay
from skillrot_app.core.skill_analyzer import classify_skill

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/user/{user_id}")
def get_user_dashboard(user_id: int, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    skills = db.query(Skill).filter(Skill.user_id == user_id).all()

    result = []

    for skill in skills:

        health = recalculate_skill_decay(skill, db)
        status = classify_skill(health)

        # Last practiced
        last_entry = (
            db.query(SkillHistory)
            .filter(SkillHistory.skill_id == skill.id)
            .order_by(SkillHistory.date.desc())
            .first()
        )

        last_practiced = last_entry.date if last_entry else skill.learned_date

        # Trend
        history = (
            db.query(SkillHealthHistory)
            .filter(SkillHealthHistory.skill_id == skill.id)
            .order_by(SkillHealthHistory.recorded_at.desc())
            .limit(2)
            .all()
        )

        trend = "stable"
        if len(history) == 2:
            if history[0].health > history[1].health:
                trend = "up"
            elif history[0].health < history[1].health:
                trend = "down"

        # Reminder count
        reminder_count = (
            db.query(Reminder)
            .filter(Reminder.skill_id == skill.id)
            .count()
        )

        result.append({
            "skill_id": skill.id,
            "skill": skill.name,
            "health": health,
            "status": status,
            "trend": trend,
            "last_practiced": last_practiced,
            "reminders": reminder_count
        })

    return result