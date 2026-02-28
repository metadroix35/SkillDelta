from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from skillrot_app.db.database import get_db
from skillrot_app.models.assessment import Assessment
from skillrot_app.models.subtopic import Subtopic

from skillrot_app.services.file_parser_service import extract_text_from_file
from skillrot_app.services.assessment_analyzer_service import analyze_assessment_text

import json

router = APIRouter(prefix="/assessment", tags=["Assessment"])


@router.post("/{skill_id}")
async def upload_assessment(
    skill_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    file_bytes = await file.read()

    if not file_bytes:
        raise HTTPException(status_code=400, detail="Empty file")

    # --------------------------------------------------
    # 1️⃣ Extract Text (OCR / PDF / DOCX / CSV etc.)
    # --------------------------------------------------
    text = extract_text_from_file(file_bytes, file.filename)

    if not text or not text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text")

    print("========== OCR EXTRACTED TEXT ==========")
    print(text)
    print("========================================")

    # --------------------------------------------------
    # 2️⃣ MASTER ANALYSIS (Generalized)
    # --------------------------------------------------
    weak_topics = analyze_assessment_text(text)

    # If nothing weak → store empty result safely
    if not weak_topics:
        db.add(Assessment(
            skill_id=skill_id,
            parsed_result=json.dumps({})
        ))
        db.commit()

        return {
            "skill_id": skill_id,
            "weak_subtopics": [],
            "stored": True
        }

    # --------------------------------------------------
    # 3️⃣ SAFE SUBTOPIC UPDATE
    # --------------------------------------------------
    for topic, severity in weak_topics.items():

        # Safety check (prevent dict crash)
        if not isinstance(severity, (int, float)):
            continue

        existing = (
            db.query(Subtopic)
            .filter(
                Subtopic.skill_id == skill_id,
                Subtopic.name.ilike(topic)
            )
            .first()
        )

        health_value = round(severity * 100, 2)

        if existing:
            existing.health_score = health_value
        else:
            db.add(Subtopic(
                skill_id=skill_id,
                name=topic,
                health_score=health_value
            ))

    # Store raw analysis result
    db.add(Assessment(
        skill_id=skill_id,
        parsed_result=json.dumps(weak_topics)
    ))

    db.commit()

    return {
        "skill_id": skill_id,
        "weak_subtopics": list(weak_topics.keys()),
        "stored": True
    }