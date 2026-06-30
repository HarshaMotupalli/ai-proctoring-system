from fastapi import APIRouter
from app.core.database import SessionLocal
from app.models.exam_log import ExamLog

router = APIRouter()

@router.get("/logs/{user_id}")
def get_logs(user_id: int):
    db = SessionLocal()

    try:
        logs = db.query(ExamLog).filter(ExamLog.user_id == user_id).all()

        return [
            {
                "type": log.violation_type,
                "timestamp": log.timestamp
            }
            for log in logs
        ]

    finally:
        db.close()