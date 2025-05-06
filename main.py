from fastapi import FastAPI
from routers.users import User

app = FastAPI()
app.include_router(User, tags=["User"]) 

