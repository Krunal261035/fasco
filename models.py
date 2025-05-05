from sqlalchemy import Column, Integer, String,DateTime
from database import Base

class UserModel(Base):
    __tablename__ = "user"
    __table_args__ = {'schema': 'users'}
    id = Column(Integer, primary_key=True, index=True)
    f_name = Column(String, index=True)
    l_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String, index=True)
    confirm_password = Column(String, index=True)
    created_at = Column(DateTime, index=True)
    updated_at = Column(DateTime, index=True)

    
