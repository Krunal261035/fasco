from fastapi import FastAPI
from routers.users import User

app = FastAPI()
app.include_router(User, tags=["User"]) 


# curl -X 'POST' \
#   'http://127.0.0.1:8080/token' \
#   -H 'accept: application/json' \
#   -H 'Content-Type: application/x-www-form-urlencoded' \
#   -d 'grant_type=password&username=johndoe&password=secret&scope=&client_id=string&client_secret=string'