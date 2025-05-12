from fastapi import APIRouter, Depends, HTTPException,status,Form
from sqlalchemy.orm import Session
from database import get_db 
from models import UserModel
from schemas import UserSchema,CustomOAuth2PasswordRequestForm,ForgetPasswordRequest,ResetPassword
from utils import *
from datetime import timedelta

User = APIRouter()



@User.post("/SignUp")
def create_user(body: UserSchema, db: Session = Depends(get_db)):
    try:
        exits = db.query(UserModel).filter(UserModel.email == body.email).first()
        if exits:
            raise HTTPException(status_code=400, detail="User already exists")
        if body.password != body.confirm_password:
            raise HTTPException(status_code=400, detail="Password and confirm password do not match")
        hashed_password = hash_password(body.password)
        new_user = UserModel(f_name=body.f_name, l_name=body.l_name, email=body.email, password=hashed_password, confirm_password=hashed_password, created_at=body.created_at, updated_at=body.updated_at)  
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"Body": new_user}   
    except Exception as e:
        # print(e)
        return {"detail": e.detail }
    

@User.post("/Sign In")
def Login(form_data: CustomOAuth2PasswordRequestForm = Form(...), db: Session = Depends(get_db)):
    try:

        user = authenticate_user(db, form_data.username, form_data.password)
        if not user or not verify_password(form_data.password, user.password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email or password")
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
        return {"access_token": access_token, "token_type": "bearer"}
        # return {"Body": user, "message": "Login successful"}
    except Exception as e:
        # print(e)
        return {"detail": e.detail }


@User.get("/users/")
def read_users(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        users = db.query(UserModel).all()
        return users
    except Exception as e:
        print(e)

@User.post("/forget Password")
def forget_password(body:ForgetPasswordRequest,db:Session = Depends(get_db),token: str = Depends(oauth2_scheme)):
    user = db.query(UserModel).filter(UserModel.email == body.email).first()
    if not user:
        raise HTTPException(status_code=404,detail="User Not Found")
    token = generate_reset_token()
    expiry = get_expiry()
    user.reset_token = token
    user.reset_token_expiry = expiry
    db.commit()
    # Here you’d email the token to the user
    return {"msg": "Password reset token created", "token": token}

from datetime import datetime, timezone

@User.post("/reset-password")
def reset_password(data: ResetPassword, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.reset_token == data.token).first()
    
    if not user:
        raise HTTPException(status_code=400, detail="Invalid token")

    # Safely convert to timezone-aware for comparison
    if not user.reset_token_expiry:
        raise HTTPException(status_code=400, detail="Token has no expiry set")

    expiry = user.reset_token_expiry
    if expiry.tzinfo is None:
        expiry = expiry.replace(tzinfo=timezone.utc)

    if expiry < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Expired token")

    # Proceed to reset the password
    user.password_hash = hash_password(data.new_password)
    user.reset_token = None
    user.reset_token_expiry = None
    db.commit()
    
    return {"msg": "Password reset successful"}


