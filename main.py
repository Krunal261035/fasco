from fastapi import FastAPI
from routers.users import User
from routers.products import router_products
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.include_router(User, tags=["User"]) 
app.include_router(router_products,tags=["Product"])

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
