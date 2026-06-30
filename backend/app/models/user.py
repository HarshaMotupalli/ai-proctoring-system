# from sqlalchemy import Column, Integer, String
# from app.core.database import Base


# class User(Base):
#     __tablename__ = "users"

#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String, nullable=False)
#     email = Column(String, unique=True, nullable=False)
#     embedding_path = Column(String, nullable=True)



from sqlalchemy import Column, Integer, String, LargeBinary
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)
    reg_no = Column(String, unique=True, nullable=False)
    college = Column(String, nullable=False)

    # 🔥 IMPORTANT: stores face embedding
    embedding = Column(LargeBinary, nullable=False)