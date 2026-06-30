from app.core.database import SessionLocal
from app.models.session import ExamSession
from app.models.violation import Violation

db = SessionLocal()

print("Exam Sessions:")
for s in db.query(ExamSession).all():
    print(s.session_id, s.start_time, s.end_time, s.final_status)

print("\nViolations:")
for v in db.query(Violation).all():
    print(v.session_id, v.type, v.duration, v.timestamp)

db.close()

