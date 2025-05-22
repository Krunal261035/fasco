from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta    
from Models.models import UserModel
from datetime import UTC
from fastapi import HTTPException,status


from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()


SECRET_KEY = "your_secret-key"  
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30



# Initialize CryptContext to use bcrypt hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.now(UTC) + expires_delta  
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

def verify_token(credentials: HTTPAuthorizationCredentials):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


import secrets
from datetime import datetime, timedelta
from datetime import datetime, timedelta, timezone
def generate_reset_token():
    return secrets.token_urlsafe(32)

def get_expiry(hours=1):
    return datetime.now(timezone.utc) + timedelta(hours=hours)


