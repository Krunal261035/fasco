from sqlalchemy import Column, Integer, String,DECIMAL,Enum,ForeignKey,DateTime,func
from database import Base
import enum

class SizeEnum(str, enum.Enum):
    M = "M"
    L = "L"
    XL = "XL"

class ProductModel(Base):
    __tablename__ = "product"
    __table_args__ = {'schema': 'products'}
    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String,index=True)
    price = Column(DECIMAL(10,2),index=True)
    size = Column(Enum(SizeEnum, name="size", create_type=False), nullable=False)
    image = Column(String,index=True)
    stock = Column(Integer,index=True)
    description = Column(String,index=True)
    category_id = Column(Integer,index=True)


class ProductCategoryModel(Base):
    __tablename__ = "product_category"
    __table_args__ = {'schema': 'products'}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    description = Column(String(1000))