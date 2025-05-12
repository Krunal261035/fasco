from sqlalchemy import Column, Integer, String,DateTime,ForeignKey,Text, TIMESTAMP
from database import Base
from datetime import datetime
from sqlalchemy.orm import relationship

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
    reset_token = Column(Text, nullable=True)
    reset_token_expiry = Column(TIMESTAMP(timezone=True), nullable=True)



    