from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from skillrot_app.db.database import get_db
from skillrot_app.models.skill import Skill
from skillrot_app.models.skill_history import SkillHistory
from skillrot_app.core.skill_analyzer import classify_skill
from skillrot_app.services.decay_service import recalculate_skill_decay

router = APIRouter(prefix="/analysis", tags=["Skill Analysis"])

# -------------------------
# Skill Health API
# -------------------------
@router.get("/skills/{skill_id}/health")
def get_skill_health(skill_id: int, db: Session = Depends(get_db)):
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    score = recalculate_skill_decay(skill, db)
    status = classify_skill(score)

    return {
        "skill_id": skill_id,
        "health": score,
        "status": status
    }

# -------------------------
# Decay Curve API
# -------------------------
@router.get("/skills/{skill_id}/decay-curve")
def get_decay_curve(skill_id: int, db: Session = Depends(get_db)):
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    # Ensure decay exists
    recalculate_skill_decay(skill, db)

    history = (
        db.query(SkillHistory)
        .filter(SkillHistory.skill_id == skill_id)
        .order_by(SkillHistory.date)
        .all()
    )

    return [
        {"date": h.date, "score": h.decay_score}
        for h in history
    ]

# -------------------------
# Manual Refresh API
# -------------------------
@router.post("/skills/{skill_id}/refresh")
def refresh_skill(skill_id: int, db: Session = Depends(get_db)):
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    score = recalculate_skill_decay(skill, db)
    return {
        "message": "Skill refreshed successfully",
        "health": score
    }
