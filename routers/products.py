from fastapi import APIRouter,Depends,Query,HTTPException
from sqlalchemy.orm import Session
from database import get_db 
from Models.Prodmodel import ProductModel,ProductHistoryModel
from schemas.Prodschema import ProductSChema,PurchaseRequest,PurchaseResponse
import psycopg2

router_products = APIRouter()

conn = psycopg2.connect(
    host="localhost",
    database="ecommerce",
    user="postgres",
    password="password"
)
@router_products.get("/products/data",response_model=list[ProductSChema])
def products(skip: int = Query(0, ge=0), limit: int = Query(10, le=100),db:Session=Depends(get_db)):
    product = db.query(ProductModel).offset(skip).limit(limit).all()
    return product

@router_products.post("/purchase", response_model=PurchaseResponse)
def make_purchase(purchase: PurchaseRequest, db: Session = Depends(get_db)):
    product = db.query(ProductModel).filter(ProductModel.id == purchase.product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if product.stock < purchase.quantity:
        raise HTTPException(
            status_code=400,
            detail=f"Not enough stock. Available: {product.stock}, Requested: {purchase.quantity}"
        )

    # Update stock
    product.stock -= purchase.quantity
    db.add(product)

    # Record purchase
    history = ProductHistoryModel(product_id=purchase.product_id, quantity=purchase.quantity)
    db.add(history)

    db.commit()
    db.refresh(product)

    return PurchaseResponse(
        message="Purchase successful",
        remaining_stock=product.stock
    )