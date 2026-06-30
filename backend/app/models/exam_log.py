# from sqlalchemy import Column, Integer, String
# from app.core.database import Base

# class ExamLog(Base):
#     __tablename__ = "exam_logs"

#     id = Column(Integer, primary_key=True)
#     user_id = Column(Integer)
#     status = Column(String)
#     violations = Column(String)
#     timestamp = Column(String)



from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.core.database import Base


class ExamLog(Base):
    __tablename__ = "exam_logs"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer)
    session_id = Column(String)   

    status = Column(String)
    violation_type = Column(String)

    timestamp = Column(DateTime, default=datetime.utcnow)