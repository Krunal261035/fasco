from pydantic import BaseModel, EmailStr, field_validator,StringConstraints
from datetime import datetime
from typing import Annotated


OnlyAlphabets = Annotated[str, StringConstraints(pattern='^[A-Za-z]+$')]
class UserSchema(BaseModel):
    f_name: OnlyAlphabets
    l_name: OnlyAlphabets
    email: EmailStr
    password: str
    confirm_password: str
    created_at: datetime |None
    updated_at:  datetime| None

    @field_validator('password')
    def validate_password(cls, value):
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.isupper() for c in value):
            raise ValueError("Password must contain an uppercase letter")
        if not any(c.islower() for c in value):
            raise ValueError("Password must contain a lowercase letter")
        if not any(c.isdigit() for c in value):
            raise ValueError("Password must contain a number")
        if not any(c in '!@#$%^&*()-_=+[{]};:\'",<.>/?`~' for c in value):
            raise ValueError("Password must contain a special character")
        return value
    
    



class CustomOAuth2PasswordRequestForm(BaseModel):
    username: str 
    password: str 

class ForgetPasswordRequest(BaseModel):
    email: EmailStr



class ResetPassword(BaseModel):
    email: EmailStr
    otp: str
    new_password: str
