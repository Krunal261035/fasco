from pydantic import BaseModel,validator
from enum import Enum
from typing import List
class SizeEnum(str, Enum):
    M = "M"
    L = "L"
    XL = "XL"


class ProductSChema(BaseModel):
    id : int
    product_name:str
    price: float
    size: SizeEnum
    image:str
    stock:int
    description:str
    category_id:int

class CategoryBase(BaseModel):
    id: int
    name: str

class AddToCartRequest(BaseModel):
    product_id: int
    quantity: int
    user_id: int | None = None

    @validator("user_id")
    def validate_user_id(cls, v):
        if v == 0:
            return None  # or raise ValueError("user_id cannot be 0")
        return v

class RemoveFromCartRequest(BaseModel):
    product_id: int
    user_id: int | None = None  # Optional for guest cart

    @validator("user_id")
    def validate_user_id(cls, v):
        if v == 0:
            return None  # or raise ValueError("user_id cannot be 0")
        return v

