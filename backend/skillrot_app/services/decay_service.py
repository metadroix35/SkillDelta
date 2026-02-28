from datetime import date
from sqlalchemy.orm import Session
from skillrot_app.models.skill_history import SkillHistory
from skillrot_app.models.skill import Skill
from skillrot_app.models.skill_health_history import SkillHealthHistory
from skillrot_app.models.subtopic import Subtopic
from skillrot_app.core.decay_engine import compute_decay_score


def recalculate_skill_decay(skill: Skill, db: Session):

    today = date.today()

    # -----------------------------------------------------
    # 1️⃣ Get Practice History
    # -----------------------------------------------------
    history = (
        db.query(SkillHistory)
        .filter(SkillHistory.skill_id == skill.id)
        .order_by(SkillHistory.date)
        .all()
    )

    if not history:
        last_used = skill.learned_date
        usage_freq = 0
    else:
        used_dates = [h.date for h in history if h.usage == 1]

        if used_dates:
            last_used = max(used_dates)
        else:
            last_used = skill.learned_date

        total_sessions = len(history)
        usage_count = len(used_dates)
        usage_freq = usage_count / max(total_sessions, 1)

    days_since = (today - last_used).days

    # -----------------------------------------------------
    # 2️⃣ Practiced Today
    # -----------------------------------------------------
    practiced_today = days_since == 0

    # -----------------------------------------------------
    # 3️⃣ Get Previous Health
    # -----------------------------------------------------
    latest_health_entry = (
        db.query(SkillHealthHistory)
        .filter(SkillHealthHistory.skill_id == skill.id)
        .order_by(SkillHealthHistory.recorded_at.desc())
        .first()
    )

    previous_health = (
        latest_health_entry.health if latest_health_entry else None
    )

    # ✅ DEBUG PRINT
    print("DEBUG → previous_health:", previous_health)

    # -----------------------------------------------------
    # 4️⃣ Clean Level
    # -----------------------------------------------------
    level = skill.level.lower() if skill.level else "intermediate"

    # -----------------------------------------------------
    # 5️⃣ Compute New Score
    # -----------------------------------------------------
    score = compute_decay_score(
        days_since_last_use=days_since,
        usage_frequency=usage_freq,
        skill_level=level,
        previous_health=previous_health,
        
    )

    # -----------------------------------------------------
    # 6️⃣ Avoid duplicate same-day entry
    # -----------------------------------------------------
    db.add(SkillHealthHistory(
     skill_id=skill.id,
     health=score
    ))

    # -----------------------------------------------------
    # 7️⃣ Subtopic Auto Decay
    # -----------------------------------------------------
    subtopics = (
        db.query(Subtopic)
        .filter(Subtopic.skill_id == skill.id)
        .all()
    )

    for sub in subtopics:

        if sub.last_practiced:
            sub_days = (today - sub.last_practiced).days
        else:
            sub_days = (today - skill.learned_date).days

        daily_decay_rate = 0.02
        decay = min(sub_days * daily_decay_rate, 50)

        new_health = max(0, sub.health_score - decay)
        sub.health_score = round(new_health, 2)

    db.commit()

    return score