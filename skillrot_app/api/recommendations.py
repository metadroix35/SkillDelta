from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from skillrot_app.db.database import get_db
from skillrot_app.models.skill import Skill
from skillrot_app.services.recommendation_service import generate_recommendation
from skillrot_app.api.analysis import get_skill_health
from skillrot_app.core.skill_analyzer import classify_skill

router = APIRouter(
    prefix="/recommendations",
    tags=["Recommendations"]
)

@router.get("/skills/{skill_id}")
def recommend_for_skill(skill_id: int, db: Session = Depends(get_db)):

    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    health_data = get_skill_health(skill_id, db)
    health = health_data["health"]
    status = classify_skill(health)

    return generate_recommendation(skill, health, status, db)