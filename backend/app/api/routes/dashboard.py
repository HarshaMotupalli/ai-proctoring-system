from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.session import ExamSession
from app.models.violation import Violation

router = APIRouter()


# DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 🔹 Get all sessions
@router.get("/sessions")
def get_sessions(db: Session = Depends(get_db)):
    sessions = db.query(ExamSession).all()

    return [
        {
            "session_id": s.session_id,
            "status": s.final_status,
            "start_time": s.start_time,
            "end_time": s.end_time
        }
        for s in sessions
    ]


# 🔹 Get violations for a session
@router.get("/violations/{session_id}")
def get_violations(session_id: str, db: Session = Depends(get_db)):
    violations = db.query(Violation).filter(
        Violation.session_id == session_id
    ).all()

    return [
        {
            "type": v.type,
            "duration": v.duration,
            "timestamp": v.timestamp,
            "evidence": v.evidence_path
        }
        for v in violations
    ]