from fastapi import APIRouter,Depends,Query,HTTPException
from sqlalchemy.orm import Session
from database import get_db 
from Models.Prodmodel import ProductModel,CartItemModel
from schemas.Prodschema import AddToCartRequest,RemoveFromCartRequest,CheckoutRequest
import psycopg2
from typing import List
from utils import verify_token
import json

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
def get_products(category_id: int = Query(None),limit: int = Query(),db: Session = Depends(get_db)):
    query = db.query(ProductModel)
    if category_id is not None:
        query = query.filter(ProductModel.category_id == category_id)
    products = query.limit(limit).all()
    return products

@router_products.post("/cart/add")
def add_to_cart(data: AddToCartRequest):
    try:
        with conn.cursor() as cur:
            # user_id = None if data.user_id == 0 else data.user_id
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
    
@router_products.delete("/cart/remove")
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




