from fastapi import APIRouter,Depends,Query,HTTPException
from sqlalchemy.orm import Session
from database import get_db 
from Models.Prodmodel import ProductModel,ProductHistoryModel
from schemas.Prodschema import ProductSChema,PurchaseRequest,PurchaseResponse,AddToCartRequest,RemoveFromCartRequest
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

@router_products.get("/products/")
def get_products(category_id: int = Query(None),limit: int = Query(10),db: Session = Depends(get_db)):
    query = db.query(ProductModel)
    if category_id is not None:
        query = query.filter(ProductModel.category_id == category_id)
    products = query.limit(limit).all()
    return products

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
    
@router_products.post("/cart/remove")
def remove_from_cart(data: RemoveFromCartRequest):
    try:
        with conn.cursor() as cur:
            # Rollback any previous failed state
            conn.rollback()

            cur.execute("""
                SELECT Products.remove_from_cart(%s, %s);
            """, (data.product_id, data.user_id))

            result = cur.fetchone()[0]
            return {"message": result}

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    

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
