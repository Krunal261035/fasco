from fastapi import FastAPI
from routers.users import User
from routers.products import router_products
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.include_router(User, tags=["User"]) 
app.include_router(router_products,tags=["Product"])

origins = [
    "http://192.168.144.122:3000",
    "http://localhost:3000"
    
    
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
