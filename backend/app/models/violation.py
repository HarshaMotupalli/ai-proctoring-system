# from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
# from sqlalchemy.orm import relationship
# from datetime import datetime
# from app.core.database import Base


# class Violation(Base):
#     __tablename__ = "violations"

#     id = Column(Integer, primary_key=True, index=True)
#     session_id = Column(String, ForeignKey("exam_sessions.session_id"))
#     type = Column(String)
#     duration = Column(Float)
#     timestamp = Column(DateTime, default=datetime.utcnow)
#     evidence_path = Column(String)

#     session = relationship("ExamSession", back_populates="violations")


from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Violation(Base):
    __tablename__ = "violations"

    id = Column(Integer, primary_key=True, index=True)

    session_id = Column(String, ForeignKey("exam_sessions.session_id"))

    type = Column(String)  # e.g., looking_away, phone_detected

    duration = Column(Float)  # how long violation lasted

    confidence = Column(Float)  # 🔥 NEW (important)

    timestamp = Column(DateTime, default=datetime.utcnow)

    evidence_path = Column(String)

    session = relationship("ExamSession", back_populates="violations")