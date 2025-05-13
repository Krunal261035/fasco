from fastapi import APIRouter, Depends, HTTPException,status,Form
from sqlalchemy.orm import Session
from database import get_db 
from models import UserModel
from schemas import UserSchema,CustomOAuth2PasswordRequestForm,ForgetPasswordRequest,ResetPassword
from utils import *
from datetime import timedelta
from pydantic import BaseModel
from random import randint
from datetime import datetime, timedelta, timezone
from config import send_email

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

@User.post("/forget-password")
def forget_password(body: ForgetPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.email == body.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User Not Found")

    otp = f"{randint(100000, 999999)}"  # 6-digit numeric OTP
    expiry = datetime.now(timezone.utc) + timedelta(minutes=10)  # OTP valid for 10 minutes

    user.otp_code = otp
    user.otp_expiry = expiry
    db.commit()

    send_email(
        to_email=user.email,
        subject="Your OTP Code",
        body=f"Your OTP for password reset is: {otp}. It will expire in 10 minutes."
    )

    # Send OTP via email (you'll need to integrate email sending logic)
    # e.g., send_email(user.email, "Your OTP code", f"Your OTP is {otp}")

    return {"msg": "OTP sent to email"}

@User.post("/reset-password")
def reset_password(data: ResetPassword, db: Session = Depends(get_db)):
    try:
        user = db.query(UserModel).filter(UserModel.email == data.email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if user.otp_code != data.otp:
            raise HTTPException(status_code=400, detail="Invalid OTP")

        # if not user.otp_expiry or user.otp_expiry < datetime.now(timezone.utc):
        #     raise HTTPException(status_code=400, detail="OTP expired")
        otp_expiry = user.otp_expiry
        if otp_expiry.tzinfo is None:
            otp_expiry = otp_expiry.replace(tzinfo=timezone.utc)

        if otp_expiry < datetime.now(timezone.utc):
            raise HTTPException(status_code=400, detail="OTP expired")

        user.password_hash = hash_password(data.new_password)
        user.otp_code = None
        user.otp_expiry = None  
        db.commit()

        return {"msg": "Password reset successful"}
    except Exception as e:
        print(e)


