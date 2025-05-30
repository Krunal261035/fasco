from sqlalchemy import Column, Integer, String,DateTime,Text, TIMESTAMP
from database import Base
from datetime import datetime

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
    otp_code = Column(String, nullable=True)
    otp_expiry = Column(DateTime(timezone=True), nullable=True)


class AddressModel(Base):
    __tablename__ = "shipping_address"
    __table_args__ = {'schema': 'users'}
    address_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer,index=True)
    address_line = Column(String,index = True)
    city = Column(String,index = True)
    state = Column(String,index = True)
    postal_code = Column(String,index = True)
    country = Column(String,index = True)
    created_at = Column(DateTime, index=True)


    