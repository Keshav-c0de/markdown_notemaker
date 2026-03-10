from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from datetime import datetime

class UserRead(BaseModel):
    id: int
    account_name: str 
    email: EmailStr

class Notepad(BaseModel):
    id: int
    user_id: int
    notes: str
    time: datetime

class  UserCreate(UserRead):
    password: str = Field(...,min_length = 8)

class Token(BaseModel):
    access_token: str
    token_type: str