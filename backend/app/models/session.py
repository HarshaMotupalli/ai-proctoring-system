from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class ExamSession(Base):
    __tablename__ = "exam_sessions"

    session_id = Column(String, primary_key=True, index=True)
    # user_id = Column(Integer, ForeignKey("users.id"))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    final_status = Column(String, default="ACTIVE")

    termination_reason = Column(String, nullable=True)

    violations = relationship("Violation", back_populates="session")