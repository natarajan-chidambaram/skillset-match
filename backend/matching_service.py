from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date

# Import your BESSER-generated models — adjust names if different
from sql_alchemy import SkillRequest, SkillMatch, UserSkill, Session as SessionModel, Review, Skill

router = APIRouter()

def get_db(): # added to avoid circular import issues. 
    from main_api import SessionLocal
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        print(f"Database session rollback due to exception: {e}")
        raise
    finally:
        db.close()

@router.post("/run-matching/")
def run_matching(database: Session = Depends(get_db)):
    open_requests = database.query(SkillRequest).filter(SkillRequest.status == "OPEN").all()
    matches_created = []

    for request in open_requests:
        capable_teachers = database.query(UserSkill).filter(
            UserSkill.skill_id == request.skill_1_id,
            UserSkill.user_id != request.user_1_id
        ).all()

        for teacher in capable_teachers:
            # Avoid duplicate matches
            existing = database.query(SkillMatch).filter(
                SkillMatch.user_2_id == teacher.user_id,
                SkillMatch.user_3_id == request.user_1_id
            ).first()
            if existing:
                continue

            match = SkillMatch(
                matchId=int(date.today().strftime("%Y%m%d")) + len(matches_created),
                status="PENDING",
                createdDate=date.today(),
                startDate=date.today(),
                user_2_id=teacher.user_id,
                user_3_id=request.user_1_id
            )
            database.add(match)
            database.flush()

            request.skillmatch_2_id = match.id
            request.status = "MATCHED"

            skill = database.query(Skill).filter(Skill.id == request.skill_1_id).first()

            session = SessionModel(
                sessionId=int(date.today().strftime("%Y%m%d")) + len(matches_created),
                sessionDate=date.today(),
                skillmatch_1_id=match.id,
                sessionType="ONLINE",
                duration=skill.estimatedDuration if skill else 0
            )
            database.add(session)
            database.flush()

            matches_created.append({
                "matchId": match.id,
                "teacher": teacher.user_id,
                "learner": request.user_1_id,
                "skill": request.skill_1_id
            })

    database.commit()
    return {"matches_created": matches_created}


@router.post("/complete-session/{session_id}/")
def complete_session(
    session_id: int,
    rating: int,
    comment: str,
    database: Session = Depends(get_db)
):
    session = database.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    review = Review(
        rating=rating,
        comments=comment,
        session_1_id=session.id
    )
    database.add(review)

    match = database.query(SkillMatch).filter(SkillMatch.matchId == session.skillmatch).first()
    if match:
        match.status = "COMPLETED"

    database.commit()
    return {"message": "Session completed, review submitted, match marked COMPLETED"}
