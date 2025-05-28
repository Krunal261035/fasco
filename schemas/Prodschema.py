from pydantic import BaseModel
from enum import Enum
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

class PurchaseRequest(BaseModel):
    product_id: int
    quantity: int

class PurchaseResponse(BaseModel):
    message: str
    remaining_stock: int

class CategoryBase(BaseModel):
    id: int
    name: str

class AddToCartRequest(BaseModel):
    product_id: int
    quantity: int
    user_id: int | None = None

class RemoveFromCartRequest(BaseModel):
    product_id: int
    user_id: int | None = None  # Optional for guest cart