from database import Base
from sqlalchemy import Column, String, Integer, Boolean

class UserAuth(Base):
    __tablename__ = "userauth"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)

class AppointmentBook(Base):
    __tablename__ = "appointmenttable"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    day = Column(String, nullable=False)
    time = Column(String, nullable=False)
    service = Column(String, nullable=False)
    isaccept = Column(Boolean, nullable=False)
    checkupdone = Column(Boolean, nullable=False)