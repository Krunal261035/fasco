from fastapi import APIRouter,Depends,Query,HTTPException
from sqlalchemy.orm import Session
from database import get_db 
from Models.Prodmodel import ProductModel,ProductHistoryModel
from schemas.Prodschema import ProductSChema,PurchaseRequest,PurchaseResponse,AddToCartRequest
import psycopg2
from typing import List


router_products = APIRouter()

conn = psycopg2.connect(
    host="localhost",
    database="ecommerce",
    user="postgres",
    password="password",
    port="5432"
)
conn.set_session(autocommit=True)
@router_products.get("/products/data/category",response_model=list[ProductSChema])
def products_category(skip: int = Query(0, ge=0), limit: int = Query(10, le=100)
             ,category_id: int = Query(None, description="Category ID"),db:Session=Depends(get_db)):
    if category_id:
        products = db.query(ProductModel).filter(ProductModel.category_id == category_id).all()
    else:
        products = db.query(ProductModel).all()

    return products

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

@router_products.get("/products/data",response_model=list[ProductSChema])
def products(skip: int = Query(0, ge=0), limit: int = Query(10, le=100),db:Session=Depends(get_db)):
    product = db.query(ProductModel).offset(skip).limit(limit).all()
    return product

@router_products.post("/cart/add")
def add_to_cart(data: AddToCartRequest):
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT Products.add_to_cart(%s, %s, %s);
            """, (data.product_id, data.quantity, data.user_id))

            result = cur.fetchone()[0]
            return {"message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router_products.get("/cart/total")
def get_cart_total(user_id: int | None = None):
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT Products.get_cart_total(%s);
            """, (user_id,))
            total = cur.fetchone()[0]
            return {"user_id": user_id, "total": total}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))