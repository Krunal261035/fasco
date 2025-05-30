from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta    
from Models.models import UserModel
from datetime import UTC
from fastapi import HTTPException,status,Depends
from database import get_db
from sqlalchemy.orm import Session


from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()


SECRET_KEY = "jkdskfkjsdf"  
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30



# Initialize CryptContext to use bcrypt hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
def get_user_by_email(db, email: str):
    return db.query(UserModel).filter(UserModel.email == email).first()

def authenticate_user(db, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.password):
        return False
    return user

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

        user = get_user_by_email(db, email)
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")




import secrets
from datetime import datetime, timedelta
from datetime import datetime, timedelta, timezone
def generate_reset_token():
    return secrets.token_urlsafe(32)

def get_expiry(hours=1):
    return datetime.now(timezone.utc) + timedelta(hours=hours)


