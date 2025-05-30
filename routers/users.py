from fastapi import APIRouter, Depends, HTTPException,status,Form,Response
from sqlalchemy.orm import Session
from database import get_db 
from Models.models import UserModel,AddressModel
from schemas.schemas import UserSchema,CustomOAuth2PasswordRequestForm,ForgetPasswordRequest,ResetPassword,UserAddressSchema
from utils import *
from datetime import timedelta
from random import randint
from datetime import datetime, timedelta, timezone
from config import send_email
from fastapi.responses import JSONResponse

User = APIRouter()



@User.post("/SignUp")
def create_user(body: UserSchema, db: Session = Depends(get_db)):
    try:
        exits = db.query(UserModel).filter(UserModel.email == body.email.strip().lower()).first()
        if exits:
            raise HTTPException(status_code=400, detail="User already exists")
        if body.password != body.confirm_password:
            raise HTTPException(status_code=400, detail="Password and confirm password do not match")
        hashed_password = hash_password(body.password)
        new_user = UserModel(f_name=body.f_name, l_name=body.l_name, email=body.email.strip().lower(), password=hashed_password, confirm_password=hashed_password, created_at=body.created_at, updated_at=body.updated_at)  
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"Body": new_user}   
    except Exception as e:
        # print(e)
        return {"detail": e.detail }
    

@User.post("/SignIn")
def Login(form_data: CustomOAuth2PasswordRequestForm = Form(...), db: Session = Depends(get_db),response: Response = None):
    try:

        user = authenticate_user(db, form_data.Email.strip().lower(), form_data.password)
        if not user or not verify_password(form_data.password, user.password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email or password")
        else:
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
            response.set_cookie(key="access_token", value=access_token, httponly=True, max_age=ACCESS_TOKEN_EXPIRE_MINUTES*60)
            return {"access_token": access_token, "token_type": "bearer"}
            # return {"Body": user, "message": "Login successful"}
    except Exception as e:
        # print(e)
        return {"detail": e.detail }

@User.get("/user")
def get_user(user: UserModel = Depends(verify_token)):
    return {"user": user}



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
        normalized_email = data.email.strip().lower()
        user = db.query(UserModel).filter(UserModel.email == normalized_email).first()
        # print("DB email:", user.email)
        # print("DB otp_code:", user.otp_code)
        # print("Input email:", data.email)
        # print("Input otp:", data.otp)


        if not user:
            raise HTTPException(status_code=400, detail="Invalid email")

        if not user.otp_code or user.otp_code != data.otp:
            raise HTTPException(status_code=400, detail="Invalid  OTP")

        otp_expiry = user.otp_expiry
        if otp_expiry is None or (
            otp_expiry.replace(tzinfo=timezone.utc) if otp_expiry.tzinfo is None else otp_expiry
        ) < datetime.now(timezone.utc):
            raise HTTPException(status_code=400, detail="OTP expired")

        user.password = hash_password(data.new_password)
        user.otp_code = None
        user.otp_expiry = None

        db.commit()

        return {"msg": "Password reset successful"}

    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    

@User.post("/UserAddress")
def AddAddress(body:UserAddressSchema,db:Session = Depends(get_db),token:UserModel = Depends(verify_token)):
    try:
        Address = AddressModel(**body.model_dump(),user_id=token.id)
        db.add(Address)
        db.commit()
        db.refresh(Address)
        return {"body":Address}
    except Exception as e:
        return e

@User.get("/address")
def data(current_user: UserModel = Depends(verify_token), db: Session = Depends(get_db)):
    try:
        users = db.query(AddressModel).filter(AddressModel.user_id == current_user.id).all()
        if not users:
            raise HTTPException(status_code=404, detail="Address not Found")
        return {"body": users}
    except Exception as e:
        return {"detail": str(e)}

@User.delete("/address")
def delete_address(db: Session = Depends(get_db), token: UserModel = Depends(verify_token)):
    try:
        address = db.query(AddressModel).filter(AddressModel.user_id == token.id).first()
        if not address:
            raise HTTPException(status_code=404, detail="Address not found")
        
        db.delete(address)
        db.commit()
        return {"detail": "Address deleted successfully"}
    except Exception as e:
        return {"detail": str(e)}